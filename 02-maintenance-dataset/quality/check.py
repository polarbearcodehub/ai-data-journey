"""质量检查脚本：对四个子集执行统一质量规则
规则设计沿用数仓质量规范的四类：完整性 / 准确性 / 一致性 / 合理性（分布）
输出：quality_report.json + 控制台摘要
"""
import json
import os
import sys
from collections import Counter

sys.stdout.reconfigure(encoding="utf-8")

DATA = os.path.join(os.path.dirname(__file__), "..", "data")
REPORT = os.path.join(os.path.dirname(__file__), "..", "quality_report.json")

EXPECTED_COUNTS = {"text_faults": 200, "timeseries": 100, "image_text": 150, "video_meta": 50}
ALLOWED_SEVERITY = {"low", "mid", "high"}
ALLOWED_SIGNALS = {"temperature", "vibration", "current"}
ALLOWED_LABELS = {"normal", "anomaly"}
ALLOWED_ANOMALY = {None, "drift", "spike", "variance", "freq_shift"}
ALLOWED_TASKS = {"caption", "classification", "vqa"}
ALLOWED_SCENES = {"inspection", "operation", "assembly"}

issues = {"text_faults": [], "timeseries": [], "image_text": [], "video_meta": []}


def load(name):
    path = os.path.join(DATA, name + ".jsonl")
    return [json.loads(l) for l in open(path, encoding="utf-8")]


# ---------- 子集1：故障文本 ----------
def check_text(items):
    rules = []
    ids = [i["id"] for i in items]
    if len(set(ids)) != len(ids):
        rules.append(("一致性", "id 重复"))
    if len(items) < EXPECTED_COUNTS["text_faults"]:
        rules.append(("完整性", f"数量不足 {len(items)}/{EXPECTED_COUNTS['text_faults']}"))
    for it in items:
        for field in ["fault_desc", "root_cause", "action"]:
            if not it.get(field, "").strip():
                rules.append(("完整性", f"{it['id']}.{field} 为空"))
        if it["severity"] not in ALLOWED_SEVERITY:
            rules.append(("准确性", f"{it['id']} severity 非法值 {it['severity']}"))
        if it["source"] not in {"corpus", "synthetic"}:
            rules.append(("准确性", f"{it['id']} source 非法值"))
        if len(it["fault_desc"]) < 10:
            rules.append(("准确性", f"{it['id']} fault_desc 过短（<10字）"))
    return rules


# ---------- 子集2：设备时序 ----------
def check_timeseries(items):
    rules = []
    ids = [i["id"] for i in items]
    if len(set(ids)) != len(ids):
        rules.append(("一致性", "id 重复"))
    for it in items:
        pts = it["points"]
        if len(pts) != 60:
            rules.append(("完整性", f"{it['id']} 点数 {len(pts)} != 60"))
        if any(p is None for p in pts):
            rules.append(("完整性", f"{it['id']} 含空值点"))
        # 准确性：标签-数据一致性（标注异常的序列应确实偏离基线）
        import statistics
        sd = statistics.pstdev(pts)
        if it["label"] == "anomaly" and sd < 0.5:
            rules.append(("准确性", f"{it['id']} 标注 anomaly 但波动({sd:.2f})接近正常"))
        if it["label"] == "normal" and sd > 3.0:
            rules.append(("准确性", f"{it['id']} 标注 normal 但波动({sd:.2f})异常"))
        if it["anomaly_type"] not in ALLOWED_ANOMALY:
            rules.append(("准确性", f"{it['id']} anomaly_type 非法值"))
        if it["label"] == "anomaly" and it["anomaly_type"] is None:
            rules.append(("一致性", f"{it['id']} anomaly 但无 anomaly_type"))
        if it["label"] == "normal" and it["anomaly_type"] is not None:
            rules.append(("一致性", f"{it['id']} normal 却有 anomaly_type"))
    # 合理性：标签分布
    dist = Counter(i["label"] for i in items)
    ratio = dist.get("anomaly", 0) / len(items)
    if not (0.2 <= ratio <= 0.6):
        rules.append(("合理性", f"异常占比 {ratio:.0%} 超出 20%~60% 合理区间"))
    return rules


# ---------- 子集3：图文对 ----------
def check_image_text(items):
    rules = []
    for it in items:
        img = os.path.join(DATA, "images", os.path.basename(it["image_path"]))
        if not os.path.exists(img):
            rules.append(("完整性", f"{it['id']} 图片文件缺失 {it['image_path']}"))
        if it["task_type"] not in ALLOWED_TASKS:
            rules.append(("准确性", f"{it['id']} task_type 非法值"))
        # 一致性：标签与 caption 内容自洽
        if it["label"] == "normal" and "故障" in it["caption"]:
            rules.append(("一致性", f"{it['id']} 标签 normal 但 caption 含'故障'"))
        if it["label"].startswith("fault_") and "正常" in it["caption"] and "异常" not in it["caption"]:
            rules.append(("一致性", f"{it['id']} 标签 fault 但 caption 描述为正常"))
    return rules


# ---------- 子集4：视频元数据 ----------
def check_video(items):
    rules = []
    for it in items:
        if not it.get("license"):
            rules.append(("完整性", f"{it['id']} 缺 license 字段"))
        if not it.get("source_url"):
            rules.append(("完整性", f"{it['id']} 缺 source_url"))
        if it["scene"] not in ALLOWED_SCENES:
            rules.append(("准确性", f"{it['id']} scene 非法值"))
        if not (0 < it["duration"] <= 600):
            rules.append(("准确性", f"{it['id']} duration 超出合理范围"))
    return rules


CHECKERS = {
    "text_faults": check_text,
    "timeseries": check_timeseries,
    "image_text": check_image_text,
    "video_meta": check_video,
}


def main():
    report = {}
    for name, checker in CHECKERS.items():
        items = load(name)
        rules = checker(items)
        issues[name] = rules
        by_type = Counter(t for t, _ in rules)
        status = "PASS" if not rules else f"FAIL ({len(rules)} issues)"
        report[name] = {"count": len(items), "issues": len(rules), "by_type": dict(by_type)}
        print(f"{name:<14} {len(items):>4} 条  {status}")
        if by_type:
            print(f"  分类: {dict(by_type)}")
            for t, msg in rules[:5]:
                print(f"    - [{t}] {msg}")

    json.dump(report, open(REPORT, "w", encoding="utf-8"), ensure_ascii=False, indent=2)
    total = sum(len(v) for v in issues.values())
    print(f"\n总计: {total} 个问题 | 报告 → quality_report.json")
    sys.exit(1 if total else 0)


if __name__ == "__main__":
    main()
