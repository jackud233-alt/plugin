---
name: mllm-data-infra-survey
description: Survey multimodal LLM data pipelines and training infra grounded in local PDFs. Reads papers from a topic folder, extracts MoE/sparse-attention/parallelism infra design, data collection & staged training tasks, then dispatches parallel deep-research agents (infra design, data processing, data vendor market) and synthesizes a cited Chinese report. Trigger: 数据采集调研 / infra调研 / 数据采买公司 / data infra survey / multimodal data pipeline survey.
---

# MLLM Data & Infra Survey

## Workflow
1. **Ground in local papers first.** `ls` the given folder (e.g. `data_infra/`); Read each PDF
   in ≤15-page batches. Extract along fixed dimensions:
   - Infra: MoE (总参/激活参, modality-specific routers), sparse attention (DSA/NSA, indexer,
     Top-k), ViT-LM heterogeneous parallelism, load balancing, I/O services, RL/distillation systems,
     inference optimizations (chunked ViT, KV dedup) — keep concrete numbers (context len, speedups).
   - Data: sources (open-source vs in-house vs synthetic), cleaning/dedup (Hash+CLIP), recaption,
     iterative self-evolving refinement, annotation pipelines.
   - Training tasks: per-stage curriculum (context length, token budget, data mixture ratios),
     SFT/RL task design, reward design, multi-teacher distillation.
2. **Deliver paper summaries BEFORE research agents finish** — user gets value early.
3. **Dispatch 3 parallel background `general-purpose` agents** (skills like deep-research are NOT
   agent types; only `general-purpose` etc. are valid `subagent_type`):
   - Agent A: infra design & deployment (MoE, sparse attention, training systems, RLHF infra,
     generative infra, inference serving).
   - Agent B: data collection/processing (datasets, cleaning pipelines, synthesis, stage-wise
     mixtures, annotation tooling).
   - Agent C: data vendor market (Scale AI/Surge/Appen; licensing deals Shutterstock/Reddit;
     中国: 海天瑞声/数据堂/云测/数据交易所; synthetic-data companies; pricing & compliance).
   Each prompt: 中文输出, require WebSearch/WebFetch, concrete companies/systems/URLs, 2024+ 动态.
4. **Synthesize** into one Chinese report: 论文知识点 → infra 调研 → 数据调研 → 采买公司 →
   共性主线与落地建议. Keep citations/URLs from agents.

## Notes
- Large PDFs: must pass `pages` param (≤20 pages/request).
- Common cross-paper themes to check: modality-specific routing, staged curriculum with
  context extension, dynamic modality balancing, verifiable-reward RL, on-policy distillation.
