import os
import sys

os.environ["HF_ENDPOINT"] = "https://hf-mirror.com"
sys.stdout.reconfigure(encoding="utf-8")

import numpy as np
from sentence_transformers import SentenceTransformer


class EmbeddingSearch:
    def __init__(self, model_name="paraphrase-multilingual-MiniLM-L12-v2"):
        self.model = SentenceTransformer(model_name)

    def index(self, corpus):
        self.corpus = corpus
        self.corpus_vectors = self.model.encode(corpus)

    def search(self, query, top_k=3):
        if not hasattr(self, "corpus_vectors"):
            raise RuntimeError("请先调用 index() 建立索引，再进行查询")

        query_vector = self.model.encode(query)

        corpus_norms = np.linalg.norm(self.corpus_vectors, axis=1)
        query_norm = np.linalg.norm(query_vector)
        scores = self.corpus_vectors @ query_vector / (corpus_norms * query_norm)

        ranked = sorted(zip(self.corpus, scores), key=lambda x: x[1], reverse=True)
        return ranked[:top_k]

    def add(self, new_sentences):
        """向已有索引追加新句子，不用重新编码全部语料"""
        new_vectors = self.model.encode(new_sentences)  # ① 新句子编码
        self.corpus = self.corpus + new_sentences  # ② 原文拼接（list）
        self.corpus_vectors = np.concatenate(  # ③ 向量拼接（矩阵）
            [self.corpus_vectors, new_vectors], axis=0
        )


if __name__ == "__main__":
    corpus = [
        "车辆冷启动时发动机舱有尖锐摩擦声，热车后声音减轻",
        "发动机怠速不稳，转速表指针在600到900转之间跳动",
        "刹车片磨损严重，踩刹车时车轮位置有金属摩擦异响",
        "空调制冷效果差，出风口温度明显高于设定温度",
        "变速箱换挡顿挫明显，低速升降挡时有冲击感",
    ]
    corpusadd = [
        "发动机启动后异响，热车后声音减轻",
    ]
    engine = EmbeddingSearch()
    engine.index(corpus)

    engine.add(corpusadd)
    for sentence, score in engine.search("发动机启动后异响", top_k=3):
        print(f"[{score:.4f}] {sentence}")
