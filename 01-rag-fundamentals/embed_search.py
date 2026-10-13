import os
import sys

os.environ["HF_ENDPOINT"] = "https://hf-mirror.com"
sys.stdout.reconfigure(encoding="utf-8")

import numpy as np
from sentence_transformers import SentenceTransformer

corpus = [
    "AI",
    "数据",
    "数智化",
    "制造业",
]

query = "今天是什么课程内容AI吗"

model = SentenceTransformer("paraphrase-multilingual-MiniLM-L12-v2")

corpus_vectors = model.encode(corpus)
query_vector = model.encode(query)

print(f"corpus_vectors shape: {corpus_vectors.shape}")
print(f"query_vector shape: {query_vector.shape}")

# 余弦相似度 = A·B / (|A| * |B|)
corpus_norms = np.linalg.norm(corpus_vectors, axis=1)
query_norm = np.linalg.norm(query_vector)

scores = corpus_vectors @ query_vector / (corpus_norms * query_norm)

ranked = sorted(zip(corpus, scores), key=lambda x: x[1], reverse=True)

print(f"\n查询: {query}")
for i, (sentence, score) in enumerate(ranked[:3], 1):
    print(f"{i}. [{score:.4f}] {sentence}")
