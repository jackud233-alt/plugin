---
name: paper-code-cross-repro
description: Cross-read a model tech report against its released code, deep-research the unreleased parts, then build a reviewed reference implementation. Use when the user gives a paper (PDF) plus a partial code release and asks to 交叉理解/交叉解读/复现未开源模块/写详细解读文档+数据工程实现, or says "cross-understand paper and code", "reproduce the unreleased pipeline", 复现数据引擎、报告代码对照解读、论文代码交叉分析.
---

# Paper × Code Cross-Reproduction

## Workflow

1. **Ingest**: unzip/locate code; `pdftotext -layout` the report; grep section headings (`^[0-9]+\.` / `^Table` / `^Figure`) to map structure. Read core model files fully (transformer/pipeline/scheduler/config).
2. **Cross-verify, don't trust either side alone**: check report tables vs code defaults (e.g. head counts vs RoPE axis dims); note discrepancies explicitly in the doc and state which side is authoritative.
3. **Doc first (chapters 1–6)**: overview → data infra → captioner → architecture (with `file:line` evidence) → training → results. Use tables mapping report claims to code lines.
4. **Deep research in background**: launch ONE background general-purpose agent for the unreleased parts. Before launching, resolve citation numbers to actual works by grepping the references section (e.g. [68]=Leiden, [54]=CAGRA, [60]=cuGraph, [71]=Vo et al. hierarchical k-means) and pass those hypotheses to the agent for verification. Continue implementing while it runs; merge results into the doc as a dedicated chapter when the notification arrives.
5. **Reference implementation**: mirror the paper's module names 1:1 in package layout. Heavy learned models = pluggable Callable hooks with Optional scores (None = "not scored"; never sentinel values like 0.0/5.0). Light algorithms (pHash, BM25, k-means, community detection) = pure numpy, runnable without GPU. Provide 3-tier backend fallback (specialized lib → generic lib → deterministic stub) WITH `logging.warning` on downgrade.
6. **Test end-to-end** with synthetic images before review (PIL-generated: duplicates, flat/uniform, tiny, noisy) and per-module assertions.
7. **Code review loop**: dispatch a peer-reviewer agent (read-only) on the new package; fix all Critical/Major findings, rerun regression tests, then document the fixed issues in the doc.

## Pitfalls learned

- kNN graphs are asymmetric: dedupe edges by unordered-pair set, never `if j <= i: continue`.
- `Image.MAX_IMAGE_PIXELS = None` is a process-global decompression-bomb hole; use a bounded pre-load pixel check (e.g. 64MP) before `img.load()`.
- `hash(str)` is per-process random (PYTHONHASHSEED); use sha256 for reproducible stub seeds.
- Guard O(n²) brute-force fallbacks with a hard size limit + clear error, not silent allocation.
- Wire every implemented stage into the main pipeline — dead config fields and unused functions are guaranteed review findings.
- Split broad try/except by stage: only decode failures are "unreadable"; hook errors get a distinct label (e.g. REVIEW + `profiling_error`) so systematic model bugs don't silently drop the whole dataset.

## Domain quick-reference (T2I data engines, verified 2026-07)

- Semantic dedup at scale: CLIP/SSCD embeddings → cuVS CAGRA 100-NN graph → cuGraph Leiden; ~8h/1B items on 8×H800.
- Concept balancing: Wikipedia graph + PageRank pruning + hierarchical k-means (facebookresearch/ssl-data-curation) + BM25 rarity weights; compare MetaCLIP count-capping.
- Open-source stack: IQA-PyTorch (TOPIQ/MUSIQ), Q-Align, LAION-Aesthetics V2, ImageReward/HPSv2, LAION watermark/SAFETY, CN-CLIP/SigLIP2.
