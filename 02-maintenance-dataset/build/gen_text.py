"""子集1：故障文本 200 条（衍生自语料库 + 规则合成扩充）"""
import json
import os
import random
import sys

sys.stdout.reconfigure(encoding="utf-8")
random.seed(42)

OUT = os.path.join(os.path.dirname(__file__), "..", "data", "text_faults.jsonl")

# 衍生自 12 篇语料库的故障-根因-处置知识对
CORPUS_KNOWLEDGE = [
    {"device": "发动机", "fault": "冷启动时发动机舱有尖锐摩擦声，热车后减轻", "cause": "皮带张紧轮或发电机轴承磨损", "action": "用听诊器定位声源，检查皮带张紧度并更换磨损件", "severity": "mid"},
    {"device": "发动机", "fault": "持续异响不随温度变化", "cause": "气门液压挺柱故障", "action": "排查气门液压挺柱，必要时更换", "severity": "mid"},
    {"device": "发动机", "fault": "皮带最长跨距中点施压后挠度超过十五毫米", "cause": "皮带张紧度不足，张紧轮失调", "action": "调整张紧轮使挠度回到十到十五毫米", "severity": "low"},
    {"device": "制动", "fault": "刹车踏板行程变长，制动距离增加", "cause": "制动液不足或管路密封失效", "action": "检查制动液液位与管路密封性", "severity": "high"},
    {"device": "制动", "fault": "刹车时方向盘抖动", "cause": "制动盘端面跳动超标", "action": "千分表测量跳动，超过零点零五毫米成对更换制动盘", "severity": "mid"},
    {"device": "制动", "fault": "制动液含水量超过百分之三", "cause": "制动液吸水老化", "action": "更换制动液，周期不超过两年", "severity": "mid"},
    {"device": "电池", "fault": "动力回路对车身绝缘电阻低于一百兆欧", "cause": "绝缘层破损或受潮", "action": "禁止上电，定位绝缘薄弱点并上报技术支持", "severity": "high"},
    {"device": "电池", "fault": "单体压差超过二十毫伏", "cause": "电池模组一致性劣化", "action": "执行被动均衡二至八小时，收敛至十毫伏以内", "severity": "mid"},
    {"device": "电池", "fault": "充放电循环中单体温度超过五十五摄氏度", "cause": "冷却回路异常", "action": "检查冷却回路，排除堵塞与泵故障", "severity": "high"},
    {"device": "空调", "fault": "完全无冷风", "cause": "压缩机离合器故障或制冷剂严重不足", "action": "先查离合器吸合，再用检漏仪定位制冷剂泄漏", "severity": "high"},
    {"device": "空调", "fault": "高低压侧压力均低于标准值", "cause": "制冷剂不足，冷凝器接口或干燥瓶泄漏", "action": "检漏后回收抽真空充注，误差不超过正负十五克", "severity": "mid"},
    {"device": "空调", "fault": "出风口温度高于十摄氏度（环境三十五度）", "cause": "冷凝器散热不良或充注量偏差", "action": "低压水枪冲洗冷凝器翅片，核对充注量", "severity": "mid"},
    {"device": "变速箱", "fault": "低速蠕行顿挫", "cause": "离合器接合曲线不适配", "action": "先刷新变速箱控制单元软件版本", "severity": "low"},
    {"device": "变速箱", "fault": "升降挡冲击伴异响且热车加重", "cause": "离合器片磨损或油温传感器故障", "action": "检查油温传感器，焦糊味明显时拆解检查离合器总成", "severity": "high"},
    {"device": "变速箱", "fault": "换挡拨叉位置传感器信号跳变", "cause": "传感器总成故障", "action": "直接更换传感器总成", "severity": "mid"},
    {"device": "轮胎", "fault": "胎侧鼓包", "cause": "胎体帘线断裂", "action": "禁止修补，直接报废更换", "severity": "high"},
    {"device": "轮胎", "fault": "同一轮胎修补已达三次且再次扎钉", "cause": "累计损伤超限", "action": "停止修补，更换轮胎", "severity": "mid"},
    {"device": "轮胎", "fault": "单轮动平衡配重总量超过六十克", "cause": "轮辋变形", "action": "检查轮辋径向跳动，校正或更换轮辋", "severity": "mid"},
    {"device": "电气", "fault": "多个不相关用电器同时间歇失效", "cause": "公共搭铁点锈蚀", "action": "拆下搭铁螺栓打磨至金属光泽，涂导电膏复紧", "severity": "mid"},
    {"device": "电气", "fault": "车辆休眠后静态电流超过五十毫安", "cause": "存在漏电回路", "action": "逐路拔保险丝定位漏电回路", "severity": "mid"},
    {"device": "电气", "fault": "CAN 网络电阻测得一百二十欧", "cause": "终端电阻脱落一个", "action": "检查总线两端终端电阻并复位", "severity": "mid"},
    {"device": "漆面", "fault": "新漆表面出现圆形凹坑（鱼眼）", "cause": "硅污染", "action": "彻底脱脂后重喷", "severity": "mid"},
    {"device": "漆面", "fault": "修复区边角露白", "cause": "喷涂遮蔽边界过近", "action": "遮蔽距离加大到三厘米以上重喷", "severity": "low"},
    {"device": "漆面", "fault": "修复区日光下可见色差", "cause": "色号批次差异或比对样板错误", "action": "以油箱盖背面喷涂样板重新调漆", "severity": "low"},
]

# 合成扩充的模板槽位（与语料库同域，字段组合生成）
DEVICES = ["发动机", "变速箱", "制动", "电池", "空调", "电气", "轮胎", "漆面"]
CONDITIONS = ["雨天", "冬季低温", "夏季高温", "满载", "长途行驶后", "怠速时", "高速行驶时", "倒车时"]
SEVERITIES = ["low", "mid", "high"]

FAULT_TEMPLATES = [
    ("{cond}{dev}出现间歇性异响，频率不规则", "{dev}内部部件松动或早期磨损", "听诊定位后紧固或更换松动部件"),
    ("{cond}{dev}工作效能下降，参数偏离标准值", "{dev}性能劣化达到维护阈值", "按维护规程执行专项检测"),
    ("{cond}{dev}报警灯点亮，诊断仪读出历史故障码", "{dev}传感器信号异常", "复现故障读取数据流，更换异常传感器"),
    ("{cond}{dev}运行时有焦糊气味", "{dev}过热或摩擦副异常磨损", "停机检查摩擦副与散热部件"),
    ("{cond}{dev}响应延迟明显", "{dev}控制信号或执行机构迟滞", "检查控制回路与执行器状态"),
]


def gen_corpus_items():
    items = []
    for i, k in enumerate(CORPUS_KNOWLEDGE, 1):
        items.append({
            "id": f"txt-{i:04d}",
            "device_type": k["device"],
            "fault_desc": k["fault"],
            "root_cause": k["cause"],
            "action": k["action"],
            "severity": k["severity"],
            "source": "corpus",
        })
    return items


def gen_synthetic_items(n):
    items = []
    for j in range(n):
        dev = random.choice(DEVICES)
        cond = random.choice(CONDITIONS)
        fault_t, cause_t, action_t = random.choice(FAULT_TEMPLATES)
        items.append({
            "id": f"txt-{len(CORPUS_KNOWLEDGE) + j + 1:04d}",
            "device_type": dev,
            "fault_desc": fault_t.format(cond=cond, dev=dev),
            "root_cause": cause_t.format(dev=dev),
            "action": action_t,
            "severity": random.choices(SEVERITIES, weights=[0.3, 0.5, 0.2])[0],
            "source": "synthetic",
        })
    return items


if __name__ == "__main__":
    items = gen_corpus_items() + gen_synthetic_items(200 - len(CORPUS_KNOWLEDGE))
    os.makedirs(os.path.dirname(OUT), exist_ok=True)
    with open(OUT, "w", encoding="utf-8") as f:
        for it in items:
            f.write(json.dumps(it, ensure_ascii=False) + "\n")
    print(f"生成 {len(items)} 条 → {os.path.basename(OUT)}")
    print(f"  corpus 衍生: {sum(1 for i in items if i['source']=='corpus')}")
    print(f"  synthetic 合成: {sum(1 for i in items if i['source']=='synthetic')}")
    from collections import Counter
    print(f"  设备分布: {dict(Counter(i['device_type'] for i in items))}")
    print(f"  严重度分布: {dict(Counter(i['severity'] for i in items))}")
