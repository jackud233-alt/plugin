---
name: video-gen-survey
description: >
  Survey a video-generation / diffusion / flow-matching research topic by
  dispatching parallel research subagents along fixed technical axes
  (architecture, training loss, steerable editing, RL post-training, data
  engineering), then synthesize a layered Chinese report with arXiv-cited
  references. Use when the user asks 调研视频生成 / 视频模型综述 / 帧间一致性 /
  video generation survey / diffusion video literature map / flow matching video.
---

## Workflow
1. Decompose the topic into 4-6 orthogonal axes (default: 架构设计, 训练loss,
   steerable编辑, RL后训练, 数据工程). Adjust axes to the topic.
2. Fan out one general-purpose subagent per axis IN PARALLEL (single message,
   multiple Agent calls). Each prompt: demand specific paper titles + arXiv IDs
   + year, module-level mechanism detail, formulas where relevant, pros/cons.
3. Synthesize into a single Chinese .md with: a global "分层叠加" framing,
   per-axis sections, comparison tables, and a consolidated references list
   grouped by axis (title / arXiv / year).
4. Verify arXiv IDs are echoed from subagent web results, not invented.

## Conventions
- Output language: Chinese; keep English technical terms inline.
- Every claim ties to a citable paper; prefer tables for method comparison.
- Highlight cross-cutting tensions (e.g. consistency vs motion magnitude).
- Offer to reformat to slides / survey-paper after delivery.
