---
name: skill-port
description: "Port Qoder/OpenCode/Aether-style SKILL.md packs into Claude Code's ~/.claude/skills/ layout. Use when the user wants to import, migrate, or adapt skill collections from .qoder/, .opencode/, .agents/, or .aether/ directories, or asks in Chinese: 移植skills、把这些skill搬到claude code、导入skill包、批量复制skill、适配skill到claude code。"
---

# Skill Port

Move external SKILL.md packs into Claude Code.

## Source layouts (compatible)

- `.qoder/skills/<name>/SKILL.md` (Qoder CLI)
- `.opencode/skills/<name>/SKILL.md` (OpenCode / Aether)
- `.agents/skills/<name>/SKILL.md` (some forks)

Frontmatter (`name` + `description`) maps 1:1. Other fields (`license`, `metadata`, `model`, `tools`) are tolerated.

## Decision rules

| Skill characteristic | Action |
|---|---|
| Already exists as a Claude Code built-in (e.g. built-in `security-review`, `init`) | Skip — would shadow built-in |
| References repo-specific paths/tooling (e.g. `aether-issue-pr`) | Skip |
| Pulls remote registries you don't trust (e.g. `clawhub`, `skill-market`) | Skip unless explicitly wanted |
| Otherwise | Copy whole folder |

## Procedure

1. `find <src> -name SKILL.md -not -path '*/node_modules/*' -not -path '*/test/*'`
2. Confirm scope with user: user-level (`~/.claude/skills/`) or project-level (`./.claude/skills/`).
3. Show the proposed selection with brief reasons; ask user to refine.
4. `cp -r <src>/<name> <dst>/` for each accepted skill (preserves `scripts/`, `references/`, `assets/`). Drop any `.versions/` snapshot subfolder — that's the origin tool's own version history and has no migration value.
5. Sanity pass on every copied SKILL.md:
   - `name` field MUST be hyphen-case `[a-z0-9-]+`. Fix if it's "Pretty Title Case" — Claude Code won't expose `/<name>` otherwise.
   - `description` should be a single-line string (collapse YAML block scalars `description: |`).
   - Add Chinese trigger phrases so 中文输入也能自动触发. Pattern: existing English + `, or asks in Chinese: <几个常见触发短语>。`
   - Scrub any hardcoded source-tool paths inside the body (e.g. `~/.qoder/...`, `~/.codex/...`) and repoint them at `~/.claude/...`.
6. List copied skills back to user. Tell them to restart the session (or start a new one) to pick up the new skills.

## Common pitfalls

- **Built-in shadowing**: don't overwrite Claude Code's own built-in skills.
- **Registry skills**: `clawhub`, `skill-market` need network registries that don't apply here.
- **Project-specific skills** (`aether-issue-pr`, `static-check-for-git-commit`): only meaningful inside their origin repo.
- **README claims ≠ shipped files**: some skill packs' README mentions more skills than are actually shipped as SKILL.md files; the rest may be pulled at runtime by the origin tool and won't port.
- **YAML block scalar `description: |`**: works but slightly less reliable for matching; convert to single-line quoted string.
