---
name: interview-prep-from-papers
description: >-
  Read local technical/research PDFs and produce an interviewer-tailored prep
  doc. Anchors depth on the interviewer's main direction (主攻方向), extracts
  papers along fixed dimensions (数据/架构/方法/评测), and builds a QA 弹药库
  with predicted questions, honest weaknesses, and reverse questions.
  Use when the user says 面试准备 / 面试文档 / interview prep / 准备和X面试 /
  帮我读这篇论文准备面试 / interview cheat sheet.
---

# Interview Prep from Papers

## Workflow
1. Identify the interviewer's 主攻方向 and re-weight the material toward it
   (e.g. LLM lead → make the language-base paper the main battlefield,
   treat multimodal papers as "base extended to X" cases).
2. Read each PDF fully in page batches (Read tool with `pages:`); check page
   count first via `pdfinfo`.
3. Per paper, extract along fixed dimensions the user favors:
   数据 / 架构 / router或核心创新 / token设计 / 任务配合 / 评测 (adapt to domain).
4. Capture concrete numbers verbatim (params, activation ratio, benchmark
   scores, token/FPS/hours) — the user always wants numerical specifics.
5. Build the doc sections:
   - Per-paper deep read (dimension breakdown)
   - Relationship table linking papers (base ↔ extension)
   - QA 弹药库: predicted questions + reference answers, grouped by topic
   - 反问面试官 (reverse questions)
   - Honest 短板/应对 (weaknesses)
   - 速记核心数字 (one-line number cheat sheet)
6. Write as a Chinese .md next to the source PDFs; offer PPT / one-page A4 follow-up.
