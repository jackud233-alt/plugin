#!/usr/bin/env python3
"""Stop hook: once-per-session Codex review gate.

This is a deliberately gentler alternative to the openai-codex plugin's own
`stopReviewGate` (toggled via `/codex:setup --enable-review-gate`), which
fires on *every* turn that made code edits. This hook instead fires with the
same cadence as our own self-reflect-stop.py: once per session, gated by a
recursion guard, a per-session fire cap, and a minimum-transcript-length
check — so you get one Codex second-opinion pass per session, not one per
edit-turn.

Scope: reviews the session's uncommitted git working-tree changes (staged +
unstaged), not a specific "previous turn" — that's a better fit for a
once-per-session cadence than trying to isolate a single turn's diff.

Fail-open by design: if Codex is unavailable, errors, or times out, this
hook logs a note and allows the stop — it does not block the session on
review-infrastructure problems, only on an actual Codex-reported finding.
"""
import glob, json, os, re, subprocess, sys, time

HOME = os.path.expanduser("~")
STATE = os.path.join(HOME, ".claude", "hooks", ".hook-state")
MAX_FIRES = 3
MIN_TRANSCRIPT_LINES = 20
TASK_TIMEOUT_S = 15 * 60

PROMPT = """<task>
Run a stop-gate review of this Claude Code session's uncommitted code changes.
Inspect `git status` and `git diff` (staged and unstaged) for the current
working tree to see what was actually changed in this session.
If there are no uncommitted code changes, return ALLOW immediately and do no
further work.
Challenge whether this work and its design choices should ship.
</task>

<compact_output_contract>
Return a compact final answer.
Your first line must be exactly one of:
- ALLOW: <short reason>
- BLOCK: <short reason>
Do not put anything before that first line.
</compact_output_contract>

<default_follow_through_policy>
Use ALLOW if you do not find a real, actionable blocking issue.
Use BLOCK only if you found something concrete that still needs to be fixed
before this work ships.
</default_follow_through_policy>

<grounding_rules>
Ground every blocking claim in the actual repository diff you inspected.
Do not block on pre-existing issues that clearly predate this session's
changes.
</grounding_rules>

<dig_deeper_nudge>
Check for second-order failures, empty-state behavior, retries, stale state,
rollback risk, and design tradeoffs before you finalize.
</dig_deeper_nudge>
"""


def guard(data: dict) -> bool:
    """Return True if we should skip (recursion / too-short / over-cap)."""
    if data.get("stop_hook_active"):
        return True
    sid = data.get("session_id") or "unknown"
    os.makedirs(STATE, exist_ok=True)
    cfile = os.path.join(STATE, f"codexgate_{sid}.count")
    try:
        n = int(open(cfile).read().strip())
    except Exception:
        n = 0
    if n >= MAX_FIRES:
        return True
    open(cfile, "w").write(str(n + 1))
    once = os.path.join(STATE, f"codexgate_reflect_{sid}.done")
    if os.path.exists(once):
        return True
    open(once, "w").write(str(time.time()))
    tp = data.get("transcript_path")
    if tp and os.path.isfile(tp):
        try:
            with open(tp) as f:
                lines = sum(1 for _ in f)
            if lines < MIN_TRANSCRIPT_LINES:
                return True
        except Exception:
            pass
    return False


def log(message: str):
    if message:
        sys.stderr.write(message + "\n")


def has_uncommitted_changes(cwd: str) -> bool:
    try:
        r = subprocess.run(
            ["git", "-C", cwd, "status", "--porcelain", "--untracked-files=all"],
            capture_output=True, text=True, timeout=15,
        )
    except Exception:
        return False
    if r.returncode != 0:
        return False
    return bool(r.stdout.strip())


def find_codex_companion() -> "str | None":
    pattern = os.path.join(HOME, ".claude", "plugins", "cache", "openai-codex", "codex", "*", "scripts", "codex-companion.mjs")
    candidates = sorted(glob.glob(pattern))
    return candidates[-1] if candidates else None


def parse_output(raw_output) -> dict:
    text = str(raw_output or "").strip()
    if not text:
        return {"ok": True, "reason": None}  # fail-open: no output, don't block
    first_line = text.splitlines()[0].strip()
    if first_line.startswith("ALLOW:"):
        return {"ok": True, "reason": None}
    if first_line.startswith("BLOCK:"):
        reason = first_line[len("BLOCK:"):].strip() or text
        return {"ok": False, "reason": reason}
    return {"ok": True, "reason": None}  # fail-open: unexpected format, don't block


def run_codex_review(cwd: str, session_id: str) -> dict:
    script = find_codex_companion()
    if not script:
        return {"ok": True, "reason": None}  # fail-open: plugin not installed/found

    env = dict(os.environ)
    if session_id:
        env["CODEX_COMPANION_SESSION_ID"] = session_id

    try:
        result = subprocess.run(
            ["node", script, "task", "--json", PROMPT],
            cwd=cwd, env=env, capture_output=True, text=True, timeout=TASK_TIMEOUT_S,
        )
    except subprocess.TimeoutExpired:
        log("[codex-review-gate] Codex review timed out after 15 minutes — allowing stop (fail-open).")
        return {"ok": True, "reason": None}
    except Exception as e:
        log(f"[codex-review-gate] Could not run Codex review ({e}) — allowing stop (fail-open).")
        return {"ok": True, "reason": None}

    if result.returncode != 0:
        detail = (result.stderr or result.stdout or "").strip()
        log(f"[codex-review-gate] Codex review task failed — allowing stop (fail-open). {detail[:300]}")
        return {"ok": True, "reason": None}

    try:
        payload = json.loads(result.stdout)
    except Exception:
        log("[codex-review-gate] Codex review returned invalid JSON — allowing stop (fail-open).")
        return {"ok": True, "reason": None}

    return parse_output(payload.get("rawOutput"))


def main():
    try:
        data = json.loads(sys.stdin.read())
    except Exception:
        sys.exit(0)
    if guard(data):
        sys.exit(0)

    cwd = data.get("cwd") or os.getcwd()
    session_id = data.get("session_id") or ""

    if not has_uncommitted_changes(cwd):
        log("[codex-review-gate] No uncommitted changes to review — allowing stop.")
        sys.exit(0)

    review = run_codex_review(cwd, session_id)
    if not review["ok"]:
        print(json.dumps({
            "decision": "block",
            "reason": f"[codex-review-gate] Codex reviewed this session's uncommitted changes and found something worth fixing before stopping: {review['reason']}\n\nThis is a once-per-session check (fail-open on infra errors) — if you disagree with the finding or want to stop anyway, say so and I'll proceed.",
        }))
        sys.exit(0)

    log("[codex-review-gate] Codex reviewed this session's changes: ALLOW.")
    sys.exit(0)


if __name__ == "__main__":
    main()
