# vla-plugin

Personal Claude Code marketplace/plugin bundle — skills, agents, hooks, and
MCP config, packaged for migrating between machines (built for moving from a
local Mac into a DSW notebook where only `git` access is available, no direct
file transfer).

Contains one plugin, `vla-research-toolkit`:

- **28 skills** — deep-research/arXiv/paper-reading/survey/interview-prep
  skills (from a Qoder CLI migration), dev-workflow skills (TDD, systematic
  debugging, worktrees, code review, ...), `review-agent` (ported from Codex
  CLI's built-in review skill), and `auto-mode-classifier-retry`.
- **7 agents** — `grant-writer`, `literature-reviewer`, `paper-writer`,
  `peer-reviewer`, `referee-responder`, `review-agent`, `scientific-critic`.
- **4 hooks**:
  - `skill-guard.py` (PreToolUse) — blocks secrets/dangerous content written
    into `~/.claude/skills/`.
  - `skill-snapshot.py` (PostToolUse) — versions a skill dir on every edit.
  - `self-reflect-stop.py` (Stop) — once-per-session proposal to save
    reusable skills/memory from the conversation. Never writes files itself;
    only proposes and waits for confirmation.
  - `codex-review-gate-stop.py` (Stop) — once-per-session Codex second-opinion
    review of uncommitted git changes. Fail-open (Codex unavailable/errors ⇒
    allow); only blocks on an actual `BLOCK:` finding from Codex. Requires
    the `openai/codex-plugin-cc` plugin to be installed and authenticated —
    no-ops gracefully if it isn't found.
- **Context7 MCP** (`.mcp.json`) — hosted remote docs-lookup server, works
  anonymously (set `CONTEXT7_API_KEY` for higher rate limits).

Deliberately **not** included: project-specific memory (that lives per-project
under `~/.claude/projects/<project>/memory/` and doesn't transfer meaningfully
to a different project path) and the `openai/codex-plugin-cc` plugin itself
(that's OpenAI's own plugin — install it fresh via the steps below rather
than re-bundling someone else's plugin).

## Install on a new machine (e.g. DSW)

```bash
claude plugin marketplace add jackud233-alt/plugin
claude plugin install vla-research-toolkit@vla-plugin
# reload the session (or restart Claude Code) to pick up skills/agents/hooks/MCP
```

## Also want live Codex review (`/codex:review`, etc.)?

The `codex-review-gate-stop.py` hook above degrades gracefully without it,
but if you also want the interactive `/codex:*` commands:

```bash
bash "$(claude plugin details vla-research-toolkit@vla-plugin | grep -o '/.*vla-research-toolkit')/scripts/setup-codex.sh"
```

or just run the three commands by hand — see `plugins/vla-research-toolkit/scripts/setup-codex.sh`.
This does **not** carry your Codex login over — `codex login` (or `/codex:setup`
inside Claude Code) has to be redone on the new machine.

## Updating this bundle later

This is a snapshot, not a live sync. If you change skills/agents/hooks on the
source machine and want DSW to pick it up, re-copy the changed files into
`plugins/vla-research-toolkit/`, commit, push, then on DSW run
`claude plugin marketplace update vla-plugin` (or remove + re-add).
