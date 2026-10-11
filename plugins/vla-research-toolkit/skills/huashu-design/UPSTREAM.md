# Upstream

- Source: https://github.com/alchaincyf/huashu-design
- Commit: `0830494ecb1c117e25b313a8114fe55a6bf2b125` (imported 2026-10-11; all 191 files verified against the upstream git blob SHAs)
- License: MIT, Copyright (c) 2026 alchaincyf (花叔 · 花生). See `LICENSE` in this directory.

## Local changes for plugin distribution

Everything else is byte-identical to the upstream commit above.

| File | Change |
|---|---|
| `SKILL.md` | Frontmatter `description` adds English trigger phrases and routes "every slide is an AI image" decks to `ppt-generation`. The "版本自检（静默）" section (git-based self-update check that writes `.last-update-check` into the skill directory) is replaced by "插件分发说明": no writes into the plugin directory, keys via environment variables only, no `npm install` inside the plugin. |
| `references/ai-video-review.md` | `~/.claude/skills/huashu-design/...` → `<skill根目录>/...`; recommend `ARK_API_KEY` via environment variable instead of skill-root `.env`. |
| `references/slide-decks.md` | Hardcoded `~/.claude/skills/huashu-design/scripts/` → skill-root-relative wording. |
| `references/verification.md` | Hardcoded `~/.claude/skills/huashu-design/scripts/verify.py` → `<skill根目录>/scripts/verify.py`. |

`scripts/design-gate-hook.sh` ships as-is but is **not** registered in the plugin's `hooks/hooks.json` (upstream deliberately keeps it opt-in). To enable it, see the plugin README.

## Re-syncing

Re-download the new upstream commit, re-apply the table above, and update the commit hash here.
