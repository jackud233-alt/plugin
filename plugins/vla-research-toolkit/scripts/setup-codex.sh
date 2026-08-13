#!/usr/bin/env bash
# Automates the scriptable parts of installing openai/codex-plugin-cc on a new
# machine (e.g. DSW). Codex's own ChatGPT/OpenAI login is inherently
# interactive and machine-bound, so that one step is NOT automated here.
#
# Usage: bash setup-codex.sh
set -euo pipefail

echo "==> Adding openai-codex marketplace..."
claude plugin marketplace add openai/codex-plugin-cc

echo "==> Installing codex plugin..."
claude plugin install codex@openai-codex

if ! command -v codex >/dev/null 2>&1 && ! npx --yes @openai/codex --version >/dev/null 2>&1; then
  echo "==> Installing Codex CLI globally (npm install -g @openai/codex)..."
  npm install -g @openai/codex
fi

cat <<'EOF'

==> Scriptable setup done. Two manual steps remain:

1. Reload plugins in your Claude Code session: /reload-plugins
2. Authenticate Codex on THIS machine (credentials don't travel between
   machines): run `codex login` in a terminal, or run `/codex:setup` inside
   Claude Code and follow its guidance.

After that, /codex:review, /codex:adversarial-review, /codex:rescue, and
/codex:transfer are available, and the bundled codex-review-gate-stop.py
Stop hook (once-per-session, fail-open) will pick it up automatically.

Note: the official `/codex:setup --enable-review-gate` (fires on every
code-edit turn) is a SEPARATE toggle from this plugin's own
codex-review-gate-stop.py hook (fires once per session). Neither is on by
default from the official gate's side; the once-per-session one is already
wired into this plugin's hooks.json.
EOF
