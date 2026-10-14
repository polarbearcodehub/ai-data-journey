import sys

sys.stdout.reconfigure(encoding="utf-8")


def chunk_text(text, chunk_size=200, overlap=50):
    """把长文本切成带重叠的块，返回 list[str]"""
    if overlap >= chunk_size:
        raise ValueError(f"overlap ({overlap}) 必须小于 chunk_size ({chunk_size})，否则起点无法前进")

    chunks = []
    start = 0
    while start < len(text):
        chunks.append(text[start : start + chunk_size])
        start += chunk_size - overlap
    return chunks


if __name__ == "__main__":
    text = (
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

    print(f"全文共 {len(text)} 字\n")

    chunks = chunk_text(text, chunk_size=200, overlap=50)
    for i, c in enumerate(chunks, 1):
        print(f"--- 块{i} ({len(c)}字) ---")
        print(c[:60] + " ...\n")

    print("重叠验证 (块1末尾50字 == 块2开头50字):", chunks[0][-50:] == chunks[1][:50])

    try:
        chunk_text("测试", chunk_size=100, overlap=100)
    except ValueError as e:
        print("边界报错生效:", e)
