import os
import sys

os.environ["HF_ENDPOINT"] = "https://hf-mirror.com"
sys.stdout.reconfigure(encoding="utf-8")

from search_engine import EmbeddingSearch

engine = EmbeddingSearch()

corpus = [
    "数仓分层数出现数据不一致，ODS与DWD层同一字段汇总值对不上",
    "调度任务连续三天延迟，基线告警频繁触发",
    "元数据平台中表的血缘关系缺失，下游影响分析无法执行",
    "数据质量规则命中率下降，空值率突增",
]

engine.index(corpus)

for sentence, score in engine.search("血缘断了怎么排查", top_k=3):
    print(f"[{score:.4f}] {sentence}")
