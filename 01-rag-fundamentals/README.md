# P1: RAG 基础与多模态数据集（M2–M3）

## 目标

搭一个最小可用的 RAG 服务，并构建配套的多模态数据集。

## 验收标准

- [ ] 多模态数据集 500+ 条，附数据卡（来源/规模/字段/许可）
- [ ] 最小 RAG 服务化：FastAPI + 前端 + Docker，可访问 demo
- [ ] 自建 50 条 QA 评测集，RAG 命中率 ≥ 60%

## 进度日志

- 2026-10-13 项目启动
- 2026-10-13 [Lesson 01] embed_search.py：手写余弦相似度的最小语义检索（sentence-transformers + numpy）
