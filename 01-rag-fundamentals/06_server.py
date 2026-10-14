import os
import sys

os.environ["HF_ENDPOINT"] = "https://hf-mirror.com"
sys.stdout.reconfigure(encoding="utf-8")

import importlib
from contextlib import asynccontextmanager

from fastapi import FastAPI
from pydantic import BaseModel

DocSearch = importlib.import_module("04_doc_search").DocSearch
rag_chat = importlib.import_module("05_rag").chat
load_env = importlib.import_module("05_rag").load_env

MANUAL = (
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

# 全局单例：服务生命周期内只初始化一次
engine = None


@asynccontextmanager
async def lifespan(app):
    """服务启动/关闭钩子：重活（加载模型、建索引）只做一次"""
    global engine
    print("加载模型并建立索引...")
    engine = DocSearch()
    engine.index_doc(MANUAL, chunk_size=200, overlap=50)
    print("就绪")
    yield
    print("服务关闭")


app = FastAPI(title="维修手册 RAG 服务", lifespan=lifespan)


class AskRequest(BaseModel):
    question: str
    top_k: int = 3


class IndexDocRequest(BaseModel):
    text: str
    chunk_size: int = 200
    overlap: int = 50


@app.get("/health")
def health():
    return {"status": "ok"}


@app.post("/ask")
def ask(req: AskRequest):
    results = engine.search(req.question, top_k=req.top_k)
    chunks = [c for c, _ in results]
    sources = [
        {"chunk": c, "score": round(float(s), 4)} for c, s in results
    ]
    answer = rag_chat(req.question, chunks)
    return {"answer": answer, "sources": sources}


@app.post("/index_doc")
def index_doc(req: IndexDocRequest):
    n = engine.index_doc(req.text, chunk_size=req.chunk_size, overlap=req.overlap)
    return {"chunks": n, "corpus_size": len(engine.corpus)}


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)
