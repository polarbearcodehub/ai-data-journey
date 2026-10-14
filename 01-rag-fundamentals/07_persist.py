import os
import sys

os.environ["HF_ENDPOINT"] = "https://hf-mirror.com"
sys.stdout.reconfigure(encoding="utf-8")

import json
import importlib

DocSearch = importlib.import_module("04_doc_search").DocSearch

INDEX_DIR = "index_store"


def build_corpus_index(chunk_size=200, overlap=50):
    """扫描 corpus/ 全部文档 → 收集所有块 → 一次性编码 → 存盘"""
    importlib.import_module("03_chunker")  # noqa: 确保模块可导入
    chunk_text = importlib.import_module("03_chunker").chunk_text

    corpus_dir = os.path.join(os.path.dirname(__file__), "corpus")
    all_chunks = []
    for fname in sorted(os.listdir(corpus_dir)):
        if not fname.endswith(".txt"):
            continue
        text = open(os.path.join(corpus_dir, fname), encoding="utf-8").read().strip()
        chunks = chunk_text(text, chunk_size, overlap)
        print(f"{fname}: {len(chunks)} 块")
        all_chunks.extend(chunks)

    engine = DocSearch()
    engine.index(all_chunks)  # 一次性索引，避免 index_doc 的覆盖问题
    print(f"\n共 {len(all_chunks)} 块")

    os.makedirs(INDEX_DIR, exist_ok=True)
    import numpy as np

    np.save(os.path.join(INDEX_DIR, "vectors.npy"), engine.corpus_vectors)
    meta = {
        "chunk_size": chunk_size,
        "overlap": overlap,
        "corpus": engine.corpus,
        "count": len(engine.corpus),
    }
    json.dump(meta, open(os.path.join(INDEX_DIR, "meta.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=2)
    print(f"索引已保存 → {INDEX_DIR}/")


def load_corpus_index():
    """从磁盘加载持久化索引，返回就绪的 DocSearch（不重新编码）"""
    import numpy as np

    engine = DocSearch()
    engine.corpus_vectors = np.load(os.path.join(INDEX_DIR, "vectors.npy"))
    meta = json.load(open(os.path.join(INDEX_DIR, "meta.json"), encoding="utf-8"))
    engine.corpus = meta["corpus"]
    print(f"索引已加载：{meta['count']} 块 (chunk_size={meta['chunk_size']}, overlap={meta['overlap']})")
    return engine


if __name__ == "__main__":
    import time

    t0 = time.time()
    build_corpus_index(chunk_size=200, overlap=50)
    print(f"建索引耗时: {time.time()-t0:.1f}s")

    t1 = time.time()
    engine = load_corpus_index()
    print(f"加载耗时: {time.time()-t1:.1f}s\n")

    for sentence, score in engine.search("强规则占比有什么限制", top_k=3):
        print(f"[{score:.4f}] {sentence[:80]}...")
