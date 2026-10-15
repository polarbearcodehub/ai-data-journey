"""子集3：图文对 150 条
图 = matplotlib 程序化绘制设备状态曲线图（正常/四类异常，复用 gen_timeseries 的注入器逻辑）
文 = 与图内容严格对应的描述
task_type 三种：classification / vqa / caption
"""
import json
import math
import os
import random
import sys

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt

sys.stdout.reconfigure(encoding="utf-8")
random.seed(11)

BASE = os.path.join(os.path.dirname(__file__), "..")
IMG_DIR = os.path.join(BASE, "data", "images")
OUT = os.path.join(BASE, "data", "image_text.jsonl")

N = 60
SIGNALS = {
    "temperature": {"base": 45.0, "noise": 0.5, "unit": "℃", "cn": "温度"},
    "vibration": {"base": 2.0, "noise": 0.15, "unit": "mm/s", "cn": "振动"},
    "current": {"base": 12.0, "noise": 0.3, "unit": "A", "cn": "电流"},
}

ANOMALY_CN = {"drift": "读数漂移", "spike": "瞬时尖峰", "variance": "波动异常增大", "freq_shift": "振动频率改变"}


def gen_points(signal, atype=None):
    cfg = SIGNALS[signal]
    pts, switch = [], None
    if atype is None:
        pts = [cfg["base"] + random.gauss(0, cfg["noise"]) for _ in range(N)]
    elif atype == "drift":
        pts = [cfg["base"] + random.gauss(0, cfg["noise"]) for _ in range(N)]
        switch = random.randint(10, 25)
        total = cfg["noise"] * random.uniform(15, 30)
        for i in range(switch, N):
            pts[i] += total * (i - switch) / (N - switch)
    elif atype == "spike":
        pts = [cfg["base"] + random.gauss(0, cfg["noise"]) for _ in range(N)]
        for _ in range(random.randint(2, 4)):
            pts[random.randint(5, N - 5)] += random.choice([-1, 1]) * cfg["noise"] * random.uniform(20, 40)
    elif atype == "variance":
        switch = random.randint(15, 30)
        for i in range(N):
            sd = cfg["noise"] * 4 if i >= switch else cfg["noise"]
            pts.append(cfg["base"] + random.gauss(0, sd))
    elif atype == "freq_shift":
        switch = random.randint(20, 35)
        for i in range(N):
            f = 0.5 if i >= switch else 0.2
            pts.append(cfg["base"] + random.gauss(0, cfg["noise"]) + cfg["noise"] * 3 * math.sin(2 * math.pi * f * i))
    return pts, switch


def plot_curve(fig_path, signal, pts, atype, switch):
    cfg = SIGNALS[signal]
    fig, ax = plt.subplots(figsize=(6, 3), dpi=80)
    xs = list(range(N))
    ax.plot(xs, pts, lw=1.2, color="tab:blue")
    if atype and switch is not None:
        ax.axvline(switch, color="tab:red", ls="--", lw=0.8, alpha=0.6)
    ax.set_xlabel("time (min)")
    ax.set_ylabel(f"{signal} ({cfg['unit']})")
    title = "normal" if atype is None else f"anomaly: {atype}"
    ax.set_title(title, fontsize=10)
    fig.tight_layout()
    fig.savefig(fig_path)
    plt.close(fig)


def make_caption(signal, atype, dev_id):
    cfg = SIGNALS[signal]
    if atype is None:
        return (f"设备{dev_id}的{cfg['cn']}传感器一小时监测曲线，读数围绕{cfg['base']}{cfg['unit']}"
                f"平稳波动，波动幅度在正负{cfg['noise']*3:.1f}以内，设备运行状态正常。")
    desc = ANOMALY_CN[atype]
    return (f"设备{dev_id}的{cfg['cn']}传感器一小时监测曲线，出现{desc}异常，"
            f"偏离{cfg['base']}{cfg['unit']}的正常基线，判定设备存在故障，"
            f"对应异常类型为{atype}，建议结合故障知识库排查{ '渐发性磨损' if atype=='drift' else '电气干扰' if atype=='spike' else '机械松动' if atype=='variance' else '轴承磨损'}。")


DEVS = {"temperature": ["ENG", "BAT"], "vibration": ["BRG", "GBX"], "current": ["MTR", "ALT"]}

def main():
    os.makedirs(IMG_DIR, exist_ok=True)
    items = []
    plan = [("normal", None, 50), ("drift", "drift", 25), ("spike", "spike", 25),
            ("variance", "variance", 25), ("freq_shift", "freq_shift", 25)]
    # 150 条 = 50 正常 + 4 类异常各 25
    seq = 1
    for label, atype, count in plan:
        for _ in range(count):
            signal = "vibration" if atype == "freq_shift" else random.choice(list(SIGNALS))
            dev_id = f"{random.choice(DEVS[signal])}-{random.randint(1, 99):03d}"
            pts, switch = gen_points(signal, atype)
            img_name = f"img-{seq:04d}.png"
            plot_curve(os.path.join(IMG_DIR, img_name), signal, pts, atype, switch)

            # task_type 轮转：caption / classification / vqa
            task = ["caption", "classification", "vqa"][(seq - 1) % 3]
            label_str = "normal" if atype is None else f"fault_{atype}"
            caption = make_caption(signal, atype, dev_id)

            items.append({
                "id": f"img-{seq:04d}",
                "image_path": f"data/images/{img_name}",
                "caption": caption,
                "task_type": task,
                "label": label_str,
                "signal": signal,
                "device_id": dev_id,
            })
            seq += 1

    random.shuffle(items)
    with open(OUT, "w", encoding="utf-8") as f:
        for it in items:
            f.write(json.dumps(it, ensure_ascii=False) + "\n")

    print(f"生成 {len(items)} 条图文对 + {len(items)} 张图 → data/images/")
    from collections import Counter
    print(f"  标签分布: {dict(Counter(i['label'] for i in items))}")
    print(f"  任务分布: {dict(Counter(i['task_type'] for i in items))}")


if __name__ == "__main__":
    main()
