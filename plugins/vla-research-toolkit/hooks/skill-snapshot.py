#!/usr/bin/env python3
"""Skill snapshot: PostToolUse on Write/Edit/MultiEdit under ~/.claude/skills/.
Stores a tar.gz of the skill directory in <skill>/.versions/v###_<ts>.tar.gz.
Always keeps v001; otherwise retains the most recent 50 snapshots.

Ported from Qoder CLI's ~/.qoder/hooks/skill-snapshot.py; only the skills-dir
path was repointed at Claude Code's layout, logic is unchanged.
"""
import json, os, re, sys, tarfile, time

HOME = os.path.expanduser("~")
SKILLS = os.path.join(HOME, ".claude", "skills")
VPAT = re.compile(r"^v(\d{3})_.*\.tar\.gz$")


def snapshot(skill_dir: str) -> str | None:
    vdir = os.path.join(skill_dir, ".versions")
    os.makedirs(vdir, exist_ok=True)
    existing = sorted(f for f in os.listdir(vdir) if VPAT.match(f))
    last = int(VPAT.match(existing[-1]).group(1)) if existing else 0
    nxt = f"{last + 1:03d}"
    ts = time.strftime("%Y%m%dT%H%M%S")
    out = os.path.join(vdir, f"v{nxt}_{ts}.tar.gz")
    with tarfile.open(out, "w:gz") as tar:
        for entry in os.listdir(skill_dir):
            if entry == ".versions":
                continue
            tar.add(os.path.join(skill_dir, entry), arcname=entry)
    # prune
    files = sorted(f for f in os.listdir(vdir) if VPAT.match(f))
    if len(files) > 51:
        keep_first = files[0]
        keep_recent = set(files[-50:])
        for f in files[:-50]:
            if f == keep_first or f in keep_recent:
                continue
            try:
                os.remove(os.path.join(vdir, f))
            except OSError:
                pass
    return nxt


def main():
    try:
        data = json.loads(sys.stdin.read())
    except Exception:
        sys.exit(0)
    file = (data.get("tool_input") or {}).get("file_path") or ""
    prefix = SKILLS + os.sep
    if not file.startswith(prefix):
        sys.exit(0)
    rel = file[len(prefix):]
    name = rel.split(os.sep, 1)[0]
    if not name:
        sys.exit(0)
    skill_dir = os.path.join(SKILLS, name)
    if not os.path.isdir(skill_dir):
        sys.exit(0)
    try:
        v = snapshot(skill_dir)
    except Exception as e:
        print(f"snapshot error: {e}", file=sys.stderr)
        sys.exit(0)
    print(json.dumps({"hookSpecificOutput": {"additionalContext": f"Skill {name} snapshot v{v} saved."}}))
    sys.exit(0)


if __name__ == "__main__":
    main()
