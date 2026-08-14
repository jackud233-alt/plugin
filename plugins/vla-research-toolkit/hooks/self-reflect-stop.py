#!/usr/bin/env python3
"""Combined Stop-hook: Skill Evolution + Memory reflection.

Ported and extended from Qoder CLI's ~/.qoder/hooks/self-reflect-stop.py.
Two changes from the original:

1. No hardcoded single MEMFILE — Claude Code's memory is per-project
   (frontmatter fact files under that project's memory/ dir + a MEMORY.md
   index), so the reflection prompt tells the agent to follow its own
   memory convention for the current project instead of a fixed path.

2. Two ideas borrowed (in simplified form) from tashan-cursor-skills'
   cognitive-self-reflect / cognitive-task-reflector skills:
     - Contradiction check: before appending a new memory bullet, check it
       against existing entries and surface conflicts instead of silently
       stacking two contradictory facts.
     - Rumination guard: once self-reflect has fired several times for the
       same project, nudge the agent to look back for a theme that keeps
       being proposed but never actually saved, and force a real decision
       on it, instead of silently re-proposing it every time.
   Deliberately NOT ported: tashan's full multi-round Socratic
   interrogation (5 dimensions x 10+ questions) — that's built for personal
   habit/emotion reflection and would be far too heavy/interruptive for a
   coding assistant's end-of-session hook.

3. Isolated-review fallback: codex-review-gate-stop.py gets its isolation
   from spawning a genuinely separate process (Codex, a different model,
   with no access to this conversation) — that's what makes its second
   opinion valuable. This hook has no such isolation on its own: a
   Stop-hook `block` just re-wakes the SAME Claude in the SAME context, so
   asking it to grade its own code inline is self-review, not independent
   review. When the Codex runtime isn't found (plugin not installed, or a
   machine like a fresh DSW box that hasn't been set up yet) AND there are
   uncommitted git changes, this hook asks the agent to dispatch the
   `review-agent` subagent via the Task/Agent tool instead — a fresh,
   isolated context window that only sees the diff, not this conversation's
   rationale. That's a real (if lower-powered) substitute for Codex's
   isolation, rather than silently doing nothing.

Re-wakes the agent ONCE per session-stop with a unified review prompt.
Includes recursion guard via stop_hook_active flag, per-session counter,
and minimum-transcript-length check (all unchanged from the original).
"""
import glob, json, os, subprocess, sys, time

HOME = os.path.expanduser("~")
STATE = os.path.join(HOME, ".claude", "hooks", ".hook-state")
MAX_FIRES = 3
MIN_TRANSCRIPT_LINES = 20
RUMINATION_THRESHOLD = 3  # after this many fires for the same project, force the repetition check


def guard(data: dict) -> bool:
    """Return True if we should skip (recursion / too-short / over-cap)."""
    if data.get("stop_hook_active"):
        return True
    sid = data.get("session_id") or "unknown"
    os.makedirs(STATE, exist_ok=True)
    cfile = os.path.join(STATE, f"stop_{sid}.count")
    try:
        n = int(open(cfile).read().strip())
    except Exception:
        n = 0
    if n >= MAX_FIRES:
        return True
    open(cfile, "w").write(str(n + 1))
    once = os.path.join(STATE, f"reflect_{sid}.done")
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


def project_key(cwd: str) -> str:
    """Turn a cwd into a filesystem-safe key for the per-project fire counter."""
    safe = "".join(c if c.isalnum() else "-" for c in (cwd or "unknown"))
    return safe.strip("-") or "unknown"


def bump_project_fire_count(cwd: str) -> int:
    """Increment and return how many times self-reflect has actually fired for
    this project. Persists across sessions (unlike the per-session guard
    above), so it can detect a topic that keeps resurfacing over time."""
    os.makedirs(STATE, exist_ok=True)
    pfile = os.path.join(STATE, f"project-fires-{project_key(cwd)}.count")
    try:
        n = int(open(pfile).read().strip())
    except Exception:
        n = 0
    n += 1
    try:
        open(pfile, "w").write(str(n))
    except Exception:
        pass
    return n


def find_codex_companion() -> "str | None":
    """Same lookup as codex-review-gate-stop.py: is the openai-codex plugin's
    runtime script present? Presence is just a proxy for "Codex could
    plausibly run here" — this hook doesn't check auth, that's Codex's own
    hook's job when it actually tries to invoke it."""
    pattern = os.path.join(HOME, ".claude", "plugins", "cache", "openai-codex", "codex", "*", "scripts", "codex-companion.mjs")
    candidates = sorted(glob.glob(pattern))
    return candidates[-1] if candidates else None


def has_uncommitted_changes(cwd: str) -> bool:
    try:
        r = subprocess.run(
            ["git", "-C", cwd, "status", "--porcelain", "--untracked-files=all"],
            capture_output=True, text=True, timeout=15,
        )
    except Exception:
        return False
    return r.returncode == 0 and bool(r.stdout.strip())


def main():
    try:
        data = json.loads(sys.stdin.read())
    except Exception:
        sys.exit(0)
    if guard(data):
        sys.exit(0)

    cwd = data.get("cwd") or os.getcwd()
    fire_count = bump_project_fire_count(cwd)
    today = time.strftime("%Y-%m-%d")

    rumination_note = ""
    if fire_count >= RUMINATION_THRESHOLD:
        rumination_note = f"""
⚠️ Repetition check: this is self-reflect firing #{fire_count} for this project.
Before proposing anything new, skim the existing memory files under this
project's memory directory for a theme that has come up repeatedly but was
never actually saved (proposed before and declined, or the same friction
point recurring across sessions). If you find one, say so explicitly and
give the user a real choice instead of silently re-proposing it again:
  [Save it now] [Turn it into a concrete action item] [Drop it — not worth tracking]
Only fall through to a normal fresh proposal if nothing recurring is found.
"""

    need_isolated_review = not find_codex_companion() and has_uncommitted_changes(cwd)
    isolated_review_note = ""
    isolated_review_section = ""
    if need_isolated_review:
        isolated_review_note = """
⚠️ No Codex runtime found on this machine (openai-codex plugin isn't
installed, or its script wasn't found) — the isolated Codex review gate has
nothing to run. There are uncommitted git changes from this session, so get
a substitute isolated opinion instead: dispatch the `review-agent` subagent
via the Task/Agent tool (NOT an inline review in this context — the whole
point is a fresh context window that hasn't seen this conversation's
rationale). Report its findings in section 3 below.
"""
        isolated_review_section = """

## 3. Isolated Code Review (Codex unavailable — Claude-only fallback)
Dispatch the `review-agent` subagent (Task/Agent tool) to review this
session's uncommitted git changes in its own isolated context. Report its
findings verbatim, ordered by severity, or write exactly "No findings." if
it found nothing. Do not review the diff yourself inline instead of
dispatching — an inline review from this same context is self-review, not
independent review, and defeats the point."""

    sections_count = "three" if need_isolated_review else "two"

    reason = f"""[self-reflect] Before stopping, do ONE combined self-review pass and reply with a structured proposal. Do NOT write any files yet — only propose, then wait for user confirmation.
{rumination_note}{isolated_review_note}
Output exactly {sections_count} sections:

## 1. Skill Evolution
Scan this conversation for non-trivial, reusable knowledge worth saving as a Skill in ~/.claude/skills/. Examples: a successful workflow, an API contract, a domain heuristic, a debugging recipe.
- Use Glob to check whether a relevant skill already exists.
- Decide: create new / patch existing / full rewrite / nothing to save.
- If proposing a new skill, show the planned SKILL.md (hyphen-case folder name; frontmatter with name + description that includes both English and Chinese trigger phrases).
- If nothing qualifies, write exactly: "Nothing to save."

## 2. Memory Reflection
Follow your own memory-writing convention for this project (per-fact frontmatter files under this project's memory directory, indexed by that project's MEMORY.md). Read the existing memory files first — both to avoid duplicates and to check for contradictions.
- **Contradiction check**: if a candidate observation conflicts with an existing memory entry (a stated preference reversed, a path that moved, a decision superseded), do not just append a second, conflicting entry — call out the conflict explicitly and propose whether to update/replace the old entry or record it as a superseding note.
- Scan for STABLE preferences / recurring context worth persisting across sessions (tooling, conventions, style, domain). Propose 0-3 bullets in this exact format:
  - [{today}] <short observation, ≤ 25 words>
- If nothing qualifies, write exactly: "No memory updates."{isolated_review_section}

Hard constraints:
- Never include secrets, API keys, file contents, or one-off transient state.
- Never write files in this turn — only propose. Wait for explicit user confirmation ("yes" / "save" / "go ahead") before any Write/Edit.
- If neither/none of the sections has anything to save or report, reply on one line summarizing that and stop.
"""
    print(json.dumps({"decision": "block", "reason": reason}))
    sys.exit(0)


if __name__ == "__main__":
    main()
