# 设备智能运维多模态数据集（Industrial Maintenance Multimodal Dataset）

> 一句话目标：证明能为制造业 AI 场景（设备故障诊断）构建多模态训练数据。

## 数据集结构

```
02-maintenance-dataset/
├── README.md               ← 本文件 + 数据卡
├── build/                  ← 生成管线（代码即数据来源说明）
│   ├── gen_text.py         ← 子集1：故障文本 200 条
│   ├── gen_timeseries.py   ← 子集2：设备时序 100 条
│   ├── gen_image_text.py   ← 子集3：图文对 150 条
│   └── gen_video_meta.py   ← 子集4：视频/截图元数据 50 条
├── data/                   ← 产出（jsonl，gitignore 大文件）
│   ├── text_faults.jsonl
│   ├── timeseries.jsonl
│   ├── image_text.jsonl
│   └── video_meta.jsonl
└── quality/
    └── check.py            ← 质量检查脚本
```

## 子集 1：故障文本（~200 条）

| 字段 | 类型 | 说明 |
|------|------|------|
| id | string | txt-0001 |
| device_type | enum | 发动机/变速箱/制动/电池/空调/电气/轮胎/漆面 |
| fault_desc | string | 故障现象描述（20~80 字） |
| root_cause | string | 根因（对应语料库的诊断结论） |
| action | string | 处置动作 |
| severity | enum | low/mid/high |
| source | enum | corpus（衍生自语料库）/ synthetic（合成） |

## 子集 2：设备时序（~100 条）

| 字段 | 类型 | 说明 |
|------|------|------|
| id | string | ts-0001 |
| device_id | string | 设备编号（如 ENG-014） |
| signal_type | enum | temperature / vibration / current |
| points | float[] | 传感器读数序列（60 点 = 1 小时/分钟级） |
| label | enum | normal / anomaly |
| anomaly_type | string | 异常类型（仅 anomaly 时有值） |
| window_start | string | 时间窗起点 |

## 子集 3：图文对（~150 条）

| 字段 | 类型 | 说明 |
|------|------|------|
| id | string | img-0001 |
| image_path | string | 图片文件相对路径 |
| caption | string | 描述（设备+状态+30~60 字） |
| task_type | enum | classification / vqa / caption |
| label | enum | 设备状态标签（normal/fault_xxx） |

## 子集 4：视频/截图元数据（~50 条）

| 字段 | 类型 | 说明 |
|------|------|------|
| id | string | vid-0001 |
| source | string | 公开数据集名称+原始 ID |
| license | string | 许可证类型 |
| duration | float | 秒 |
| scene | enum | inspection / operation / assembly |
| annotation | string | 场景级标注描述 |

## 数据卡（Data Card）

- **名称**：Industrial Maintenance Multimodal Dataset v1.0
- **目的**：制造业设备故障诊断的多模态训练/评测数据
- **构建方法**：子集 1/2/3 为程序化合成（生成脚本随数据集发布，可复现）；子集 4 为公开数据集元数据
- **不含任何雇主业务数据**；合成数据与真实分布存在差异，详见 limitations
- **规模**：500 条（200+100+150+50）
- **许可**：MIT（代码）/ CC-BY-4.0（数据）
- **limitations**：合成时序为规则生成（非真实物理模型）；图文对的图为程序绘制示意图非实拍；评测用途为主，直接训练需评估域差距

## 进度日志

- 2026-10-15 项目启动，schema 定稿
