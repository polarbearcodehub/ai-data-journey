import os
import sys

os.environ["HF_ENDPOINT"] = "https://hf-mirror.com"
sys.stdout.reconfigure(encoding="utf-8")

import json
import importlib

DocSearch = importlib.import_module("04_doc_search").DocSearch
chunk_text = importlib.import_module("03_chunker").chunk_text

CORPUS_DIR = os.path.join(os.path.dirname(__file__), "corpus")
EVAL_PATH = os.path.join(os.path.dirname(__file__), "eval_v1.json")


def build_engine(chunk_size, overlap):
    """按指定参数构建全语料索引"""
    all_chunks = []
    for fname in sorted(os.listdir(CORPUS_DIR)):
        if fname.endswith(".txt"):
            text = open(os.path.join(CORPUS_DIR, fname), encoding="utf-8").read().strip()
            all_chunks.extend(chunk_text(text, chunk_size, overlap))
    engine = DocSearch()
    engine.index(all_chunks)
    return engine, len(all_chunks)


def run_eval(engine, eval_set):
    """跑一组评测，按题型分组返回命中明细"""
    results = {}
    for item in eval_set:
        qtype = item["type"]
        top1, score = engine.search(item["question"], top_k=1)[0]

        if qtype == "unanswerable":
            hit = not any(kw in top1 for kw in item["keywords"]) if item["keywords"] else None
            # 不可回答题的判定：不应该命中任何"看似答案"的块——用分数阈值近似
            hit = score < 0.55  # 低分=模型没找到强匹配，视为正确拒答倾向
        else:
            hit = any(kw in top1 for kw in item["keywords"])

        results.setdefault(qtype, []).append((item["id"], hit, round(float(score), 4)))
    return results


if __name__ == "__main__":
    eval_set = json.load(open(EVAL_PATH, encoding="utf-8"))
    answerable = [e for e in eval_set if e["type"] != "unanswerable"]
    unanswerable = [e for e in eval_set if e["type"] == "unanswerable"]

    print(f"评测集：{len(eval_set)} 题（可回答 {len(answerable)} / 不可回答 {len(unanswerable)}）\n")

    summary = []
    for chunk_size, overlap in [(100, 30), (200, 50), (300, 75), (400, 100)]:
        engine, n_chunks = build_engine(chunk_size, overlap)
        results = run_eval(engine, eval_set)

        print(f"\n===== chunk_size={chunk_size}, overlap={overlap}, {n_chunks} 块 =====")

        row = {"chunk_size": chunk_size, "overlap": overlap, "chunks": n_chunks}
        for qtype, items in results.items():
            hits = sum(1 for _, h, _ in items if h)
            rate = hits / len(items) * 100
            row[qtype] = f"{hits}/{len(items)}"
            print(f"  {qtype:<14} {hits}/{len(items)}  ({rate:.0f}%)")
            # 错题明细
            misses = [f"{qid}({s})" for qid, h, s in items if not h]
            if misses:
                print(f"    未命中: {', '.join(misses)}")
        summary.append(row)

    print("\n===== 汇总 =====")
    print(f"{'size':>5} {'overlap':>8} {'chunks':>7} {'direct':>8} {'reasoning':>10} {'confuse':>9} {'unans':>7}")
    for r in summary:
        print(f"{r['chunk_size']:>5} {r['overlap']:>8} {r['chunks']:>7} "
              f"{r.get('direct','—'):>8} {r.get('reasoning','—'):>10} "
              f"{r.get('confuse','—'):>9} {r.get('unanswerable','—'):>7}")
