#!/usr/bin/env python3
"""Skill safety guard: PreToolUse on Write/Edit/MultiEdit under ~/.claude/skills/.
Blocks writes that contain obvious secrets, destructive commands, traversal,
or invisible/bidi characters. Outputs JSON to stdout on allow, exits 2 on deny.

Ported from Qoder CLI's ~/.qoder/hooks/skill-guard.py; only the skills-dir
path was repointed at Claude Code's layout, logic is unchanged.
"""
import json, os, re, sys

HOME = os.path.expanduser("~")
SKILLS = os.path.join(HOME, ".claude", "skills") + os.sep

DANGER = [
    (re.compile(r"AKIA[0-9A-Z]{16}"), "AWS access key"),
    (re.compile(r"sk-[A-Za-z0-9]{32,}"), "OpenAI-style API key"),
    (re.compile(r"xox[baprs]-[A-Za-z0-9-]{10,}"), "Slack token"),
    (re.compile(r"gh[pousr]_[A-Za-z0-9]{36,}"), "GitHub token"),
    (re.compile(r"BEGIN (RSA|OPENSSH|EC|PGP) PRIVATE KEY"), "private key block"),
    (re.compile(r"\brm\s+-rf\s+[/~]"), "rm -rf on root/home"),
    (re.compile(r":\(\)\s*\{\s*:\|:&\s*\}\s*;\s*:"), "fork bomb"),
]
INVIS = re.compile(r"[​-‏‪-‮⁠-⁯﻿]")


def main():
    raw = sys.stdin.read()
    try:
        data = json.loads(raw)
    except Exception:
        sys.exit(0)
    inp = data.get("tool_input", {})
    file = inp.get("file_path") or ""
    if not file.startswith(SKILLS):
        sys.exit(0)
    if ".." in file.split(os.sep):
        print(f"Skill guard: path traversal blocked: {file}", file=sys.stderr)
        sys.exit(2)
    content = inp.get("content") or inp.get("new_string") or ""
    if not content:
        # MultiEdit carries edits[]
        edits = inp.get("edits") or []
        content = "\n".join(e.get("new_string", "") for e in edits)
    if not content:
        sys.exit(0)
    for pat, label in DANGER:
        m = pat.search(content)
        if m:
            print(f"Skill guard: {label} detected in {file}: {m.group(0)[:40]}", file=sys.stderr)
            sys.exit(2)
    if INVIS.search(content):
        print(f"Skill guard: invisible/bidi characters in {file}", file=sys.stderr)
        sys.exit(2)
    sys.exit(0)


if __name__ == "__main__":
    main()
