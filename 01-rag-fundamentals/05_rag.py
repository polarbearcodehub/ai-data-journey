import os
import sys
import json
import urllib.request

os.environ["HF_ENDPOINT"] = "https://hf-mirror.com"
sys.stdout.reconfigure(encoding="utf-8")

import importlib

DocSearch = importlib.import_module("04_doc_search").DocSearch


def load_env(path=".env"):
    """极简 .env 读取：KEY=VALUE 每行一条"""
    env = {}
    for line in open(path, encoding="utf-8"):
        line = line.strip()
        if line and "=" in line:
            k, v = line.split("=", 1)
            env[k.strip()] = v.strip()
    return env


def chat(question, context_chunks, model="DeepSeek-V4-Flash"):
    """RAG 的 G：拼 prompt → 调 LLM → 返回回答"""
    env = load_env()
    context = "\n\n".join(f"【参考{i}】{c}" for i, c in enumerate(context_chunks, 1))
    prompt = (
        "你是设备维修助手。仅根据下面的参考资料回答问题，"
        "如果资料里没有答案，直接说'资料中未提及'，不要编造。\n\n"
        f"{context}\n\n"
        f"问题：{question}"
    )
    req = urllib.request.Request(
        env["LLM_BASE_URL"] + "/v1/chat/completions",
        method="POST",
        data=json.dumps({
            "model": model,
            "messages": [{"role": "user", "content": prompt}],
            "max_tokens": 500,
        }).encode(),
        headers={
            "Authorization": "Bearer " + env["LLM_API_KEY"],
            "Content-Type": "application/json",
        },
    )
    resp = json.load(urllib.request.urlopen(req, timeout=60))
    return resp["choices"][0]["message"]["content"]


if __name__ == "__main__":
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

    engine = DocSearch()
    engine.index_doc(manual, chunk_size=200, overlap=50)

    questions = [
        "皮带张紧度怎么检查",          # 可回答
        "换发电机要花多少钱",          # 不可回答（第4课的老朋友）
    ]

    for q in questions:
        print(f"\n{'='*50}\n问题: {q}")
        chunks = [c for c, _ in engine.search(q, top_k=3)]
        print(f"检索到 {len(chunks)} 块，交给 LLM...\n")
        for model_name in ["DeepSeek-V4-Flash", "maas-glm-5.3"]:
            print(f"--- {model_name} ---")
            print(chat(q, chunks, model=model_name), "\n")
