# 参数智能体 — 招投标参数智能比对与决策辅助

> 科大讯飞 2026 展翼校招培训大赛 | 第 X 组  
> 课题：基于大模型人机协作的标书参数分析 Agent

---

## 🎯 一句话说清楚

输入一份智慧黑板招标文件 → 识别是哪家竞品控的标 → 逐条对比讯飞参数 → 标出正/负偏离 → 给出应对建议。

---

## 📂 快速导航

| 想看什么 | 去这里 |
|----------|--------|
| 项目总指引（AI 也读这个） | [`CLAUDE.md`](./CLAUDE.md) |
| 产品需求文档 | [`docs/01-PRD.md`](./docs/01-PRD.md) |
| 技术方案设计 | [`docs/02-technical-design.md`](./docs/02-technical-design.md) |
| AI 协作记录（路演素材） | [`docs/03-ai-collaboration.md`](./docs/03-ai-collaboration.md) |
| 团队分工 & 时间线 | [`docs/04-team-division.md`](./docs/04-team-division.md) |
| PM 讨论纪要 | [`docs/05-meeting-notes.md`](./docs/05-meeting-notes.md) |

---

## 🚀 5 分钟跑起来

```bash
# 1. 安装依赖
pip install streamlit pandas openpyxl python-docx pdfplumber

# 2. 启动 Demo
cd src
streamlit run app.py

# 3. 浏览器打开 http://localhost:8501
```

---

## 🧱 三层架构

```
招标文件 → [程序粗筛] → [横向对比:控标识别] → [纵向对比:AI精判] → 结果页
             80%在此                 查表                   语义理解
             秒级完成              不需AI                 只有这调用AI
```

---

## 🛠 技术栈

| 层 | 选型 | 理由 |
|----|------|------|
| UI | Streamlit | Python 写网页，10 行出界面 |
| 后端 | Python 3 | AI 最擅长生成，零学习成本 |
| AI | Claude API（通过 Kooky） | 语义匹配 + 话术生成 |
| 存储 | JSON 文件 | 轻量，不需要数据库 |

---

## ⏱ 时间线

| 07.24 | 07.25 | 07.26 | 07.27 | 07.28 |
|-------|-------|-------|-------|-------|
| 组队+需求 | 核心链路 | 班级初选 | 彩排 | 🏆 PK |
