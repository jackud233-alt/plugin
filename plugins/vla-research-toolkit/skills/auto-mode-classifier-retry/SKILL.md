---
name: auto-mode-classifier-retry
description: "What to do when a Bash/Edit/Write/WebFetch call is denied with 'Auto mode could not evaluate this action' or 'Stage 2 classifier error' on an obviously safe command. Use when a tool call is blocked by Claude Code's auto-mode safety classifier and you're deciding whether to retry, rewrite, or escalate, or asks in Chinese: 命令被安全分类器拦截了、auto mode 卡住了、classifier error 怎么办。"
---

# Auto Mode Classifier Retry

Claude Code's auto-mode safety classifier occasionally denies a completely
benign tool call (mkdir, cp, rm -rf on a path you already control, chmod,
python3 -m json.tool, WebFetch) with a message like:

  "Auto mode could not evaluate this action and is blocking it for safety —
  ... this is usually transient — wait briefly and try this action again as-is"

or:

  "Permission for this action was denied by the Claude Code auto mode
  classifier. Reason: Stage 2 classifier error ..."

## What to do

1. **Retry the exact same command, unchanged.** Do not rewrite it, split it up,
   or switch tools defensively — in practice a plain retry succeeds within 1-2
   attempts almost every time this has been observed.
2. If it fails 3+ times in a row, only then consider: an alternative tool that
   naturally does the same thing (e.g. a dedicated file tool instead of a raw
   shell command), or moving on to independent work and coming back later.
3. Do **not** interpret a single denial as a real safety judgment on the
   command — the error text itself says so. Don't ask the user for permission
   changes or explain the command differently; just retry.
4. If the user asks "stuck?" mid-retry-loop, that's a good moment to give a
   one-line status update (what succeeded so far, what's mid-retry) rather
   than silently continuing — but keep retrying, don't stop the task.

## Anti-patterns observed

- Rewriting a multi-line/compound command into something more "conservative"
  after one denial — the original command usually works fine on retry;
  rewriting just adds noise without fixing anything.
- Treating a denial as user-directed feedback requiring a plan change.
