import os
import sys

os.environ["HF_ENDPOINT"] = "https://hf-mirror.com"
sys.stdout.reconfigure(encoding="utf-8")

import importlib

DocSearch = importlib.import_module("04_doc_search").DocSearch

manual = (
    "发动机舱异响诊断作业指导书。第一步：确认异响发生条件。冷启动时异响明显、热车后减轻的，"
    "优先排查皮带张紧轮和发电机轴承；持续异响不随温度变化的，排查气门液压挺柱。第二步：准备工具，"
    "需要长杆听诊器、扭矩扳手、手电筒。第三步：安全事项。发动机运行状态下检查时严禁佩戴领带、围巾等"
    "悬挂物，长发必须盘起，确保与风扇和传动皮带的距离不少于三十厘米。第四步：诊断流程。打开发动机舱盖，"
    "用听诊器依次接触发电机、张紧轮、空调压缩机、转向助力泵四个部位，记录各部位异响特征，包括频率、"
    "节奏和与转速的关联。第五步：皮带张紧度的检查方法。在皮带最长跨距的中点施加十公斤压力，皮带挠度"
    "应在十到十五毫米之间，超出范围需调整张紧轮。第六步：发电机轴承的判断。断开皮带后单独运转发电机，"
    "若异响消失则确认轴承故障，更换发电机总成。第七步：完工确认。所有检查完成后恢复拆卸的部件，"
    "启动发动机怠速运转五分钟，确认异响消除，填写诊断记录单并由班组长签字确认。"
)

# 评测集：问题 → 正确答案块必须包含的关键词（命中任一即算对）
eval_set = [
    ("皮带张紧度怎么检查", ["十公斤压力", "挠度"]),
    ("检修的时候有什么安全要求", ["三十厘米", "严禁"]),
    ("需要带什么工具", ["听诊器", "手电筒"]),
    ("冷车响热车不响是什么毛病", ["冷启动", "张紧轮"]),
    ("怎么判断发电机坏了", ["断开皮带", "轴承"]),
]

print(f"{'chunk_size':>10} | 命中数 | 命中率 | 各题得分")
print("-" * 50)

engine = DocSearch()

for chunk_size in [100, 200, 400]:
    engine.index_doc(manual, chunk_size=chunk_size, overlap=50)

    hits = 0
    detail = []
    for question, keywords in eval_set:
        top1, _ = engine.search(question, top_k=1)[0]
        hit = any(kw in top1 for kw in keywords)
        hits += hit
        detail.append("✓" if hit else "✗")

    rate = hits / len(eval_set) * 100
    print(f"{chunk_size:>10} | {hits}/{len(eval_set)}   | {rate:>4.0f}%  | {' '.join(detail)}")
