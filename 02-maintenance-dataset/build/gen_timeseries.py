"""子集2：设备时序 100 条
正常 = 基线 + 平稳噪声；异常 = 注入四类故障（漂移/尖峰/方差畸变/周期异常）
"""
import json
import math
import os
import random
import sys

sys.stdout.reconfigure(encoding="utf-8")
random.seed(7)

OUT = os.path.join(os.path.dirname(__file__), "..", "data", "timeseries.jsonl")

N = 60            # 每条 60 点（1 小时分钟级）
N_NORMAL = 60
ANOMALY_TYPES = {
    "drift": 10,        # 漂移：渐发性故障/传感器老化
    "spike": 10,        # 尖峰：电气干扰/突发故障
    "variance": 10,     # 方差畸变：机械松动
    "freq_shift": 10,   # 周期异常：轴承磨损
}

# 信号类型基线配置
SIGNALS = {
    "temperature": {"base": 45.0, "noise": 0.5, "unit_range": (35, 90)},
    "vibration": {"base": 2.0, "noise": 0.15, "unit_range": (0.5, 8)},
    "current": {"base": 12.0, "noise": 0.3, "unit_range": (8, 30)},
}

DEVICES = {"temperature": ["ENG", "BAT"], "vibration": ["BRG", "GBX"], "current": ["MTR", "ALT"]}


def gen_normal(signal):
    cfg = SIGNALS[signal]
    return [cfg["base"] + random.gauss(0, cfg["noise"]) for _ in range(N)]


def inject_drift(signal):
    cfg = SIGNALS[signal]
    pts = gen_normal(signal)
    start = random.randint(10, 25)
    drift_total = cfg["noise"] * random.uniform(15, 30)   # 漂移幅度随时间累积
    for i in range(start, N):
        pts[i] += drift_total * (i - start) / (N - start)
    return pts


def inject_spike(signal):
    pts = gen_normal(signal)
    cfg = SIGNALS[signal]
    for _ in range(random.randint(2, 4)):                  # 2~4 个尖峰
        pos = random.randint(5, N - 5)
        pts[pos] += random.choice([-1, 1]) * cfg["noise"] * random.uniform(20, 40)
    return pts


def inject_variance(signal):
    pts = gen_normal(signal)
    cfg = SIGNALS[signal]
    start = random.randint(15, 30)
    for i in range(start, N):
        pts[i] = cfg["base"] + random.gauss(0, cfg["noise"] * 4)   # 方差放大 4 倍
    return pts


def inject_freq_shift(signal):
    """振动信号特化：叠加周期分量，故障段频率改变"""
    cfg = SIGNALS[signal]
    pts = []
    f1, f2 = 0.2, 0.5                                     # 正常频率 vs 异常频率
    switch = random.randint(20, 35)
    amp = cfg["noise"] * 3
    for i in range(N):
        base = cfg["base"] + random.gauss(0, cfg["noise"])
        f = f2 if i >= switch else f1
        pts.append(base + amp * math.sin(2 * math.pi * f * i))
    return pts


INJECTORS = {"drift": inject_drift, "spike": inject_spike, "variance": inject_variance, "freq_shift": inject_freq_shift}


def main():
    items = []
    seq = 1
    # 正常样本
    for _ in range(N_NORMAL):
        signal = random.choice(list(SIGNALS))
        dev = random.choice(DEVICES[signal])
        items.append({
            "id": f"ts-{seq:04d}", "device_id": f"{dev}-{random.randint(1, 99):03d}",
            "signal_type": signal, "points": [round(p, 3) for p in gen_normal(signal)],
            "label": "normal", "anomaly_type": None,
            "window_start": f"2026-10-{random.randint(1, 15):02d}T{random.randint(0,23):02d}:00:00",
        })
        seq += 1
    # 异常样本
    for atype, count in ANOMALY_TYPES.items():
        for _ in range(count):
            signal = "vibration" if atype == "freq_shift" else random.choice(list(SIGNALS))
            dev = random.choice(DEVICES[signal])
            items.append({
                "id": f"ts-{seq:04d}", "device_id": f"{dev}-{random.randint(1, 99):03d}",
                "signal_type": signal, "points": [round(p, 3) for p in INJECTORS[atype](signal)],
                "label": "anomaly", "anomaly_type": atype,
                "window_start": f"2026-10-{random.randint(1, 15):02d}T{random.randint(0,23):02d}:00:00",
            })
            seq += 1

    random.shuffle(items)
    os.makedirs(os.path.dirname(OUT), exist_ok=True)
    with open(OUT, "w", encoding="utf-8") as f:
        for it in items:
            f.write(json.dumps(it, ensure_ascii=False) + "\n")

    print(f"生成 {len(items)} 条 → {os.path.basename(OUT)}")
    from collections import Counter
    print(f"  标签分布: {dict(Counter(i['label'] for i in items))}")
    print(f"  异常类型分布: {dict(Counter(i['anomaly_type'] for i in items if i['anomaly_type']))}")
    print(f"  信号类型分布: {dict(Counter(i['signal_type'] for i in items))}")


if __name__ == "__main__":
    main()
