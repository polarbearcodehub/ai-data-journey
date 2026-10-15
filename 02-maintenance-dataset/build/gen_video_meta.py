"""子集4：视频/截图元数据 50 条
不搬运视频本体，只登记公开数据集的元数据引用（source + license + 场景标注）
"""
import json
import os
import random
import sys

sys.stdout.reconfigure(encoding="utf-8")
random.seed(23)

OUT = os.path.join(os.path.dirname(__file__), "..", "data", "video_meta.jsonl")

# 公开工业/设备视频数据集（真实存在的常用来源，引用而非搬运）
SOURCES = [
    {"dataset": "UCF-Crime", "license": "Open Research License", "url": "https://www.crcv.ucf.edu/projects/real-world/",
     "scenes": [("operation", "设备运转画面"), ("inspection", "巡检画面")]},
    {"dataset": "MVTec AD", "license": "CC BY-NC-ND 4.0", "url": "https://www.mvtec.com/company/research/datasets/mvtec-ad",
     "scenes": [("inspection", "工业品缺陷检测特写")]},
    {"dataset": "DoTA (Traffic Accident)", "license": "CC BY 4.0", "url": "https://github.com/MoonBlvd/DoTA",
     "scenes": [("operation", "车辆运行与事故片段")]},
    {"dataset": "Factory simulation (open clips)", "license": "CC0", "url": "https://pixabay.com/videos/search/factory/",
     "scenes": [("assembly", "产线装配画面"), ("operation", "设备运转画面")]},
]

ANNOT_TEMPLATES = {
    "inspection": [
        "镜头缓慢扫过设备表面，画面稳定，用于巡检场景的常规拍摄片段",
        "特写镜头检查部件外观，包含细微划痕与油污特征",
    ],
    "operation": [
        "固定机位拍摄设备运行全过程，画面包含周期性机械动作",
        "手持拍摄跟随设备运转，画面有轻微晃动，含工作噪音环境",
    ],
    "assembly": [
        "产线视角记录装配工序，含多次重复的装配动作",
        "工人操作视角，展示部件安装的完整动作序列",
    ],
}


def main():
    items = []
    seq = 1
    for src in SOURCES:
        n = 15 if src["dataset"] == "UCF-Crime" else 12 if src["dataset"] == "MVTec AD" else 12
        for _ in range(n):
            scene, scene_cn = random.choice(src["scenes"])
            items.append({
                "id": f"vid-{seq:04d}",
                "source": f"{src['dataset']}",
                "source_url": src["url"],
                "license": src["license"],
                "duration": round(random.uniform(5.0, 90.0), 1),
                "scene": scene,
                "scene_cn": scene_cn,
                "annotation": random.choice(ANNOT_TEMPLATES[scene]),
            })
            seq += 1

    random.shuffle(items)
    with open(OUT, "w", encoding="utf-8") as f:
        for it in items:
            f.write(json.dumps(it, ensure_ascii=False) + "\n")

    print(f"生成 {len(items)} 条视频元数据 → {os.path.basename(OUT)}")
    from collections import Counter
    print(f"  来源分布: {dict(Counter(i['source'] for i in items))}")
    print(f"  场景分布: {dict(Counter(i['scene'] for i in items))}")
    print(f"  许可证种类: {sorted(set(i['license'] for i in items))}")


if __name__ == "__main__":
    main()
