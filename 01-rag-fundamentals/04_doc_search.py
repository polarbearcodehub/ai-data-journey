import os
import sys

os.environ["HF_ENDPOINT"] = "https://hf-mirror.com"
sys.stdout.reconfigure(encoding="utf-8")

import importlib

EmbeddingSearch = importlib.import_module("02_search_engine").EmbeddingSearch
chunk_text = importlib.import_module("03_chunker").chunk_text


class DocSearch(EmbeddingSearch):
    """继承 EmbeddingSearch：search/add 直接复用，只新增"吃长文档"的入口"""

    def index_doc(self, text, chunk_size=200, overlap=50):
        chunks = chunk_text(text, chunk_size, overlap)
        super().index(chunks)  # 复用父类：编码 + 存语料
        return len(chunks)     # 返回块数，方便观察


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
    n = engine.index_doc(manual, chunk_size=200, overlap=50)
    print(f"文档已索引：{len(manual)} 字 → {n} 块\n")

    for sentence, score in engine.search("皮带张紧度怎么检查", top_k=3):
        print(f"[{score:.4f}] {sentence}\n")
