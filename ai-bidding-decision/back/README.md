# AI 话术生成接口

在 `ai-bidding-decision/back` 目录执行：

```powershell
py -m pip install -r requirements.txt
$env:DEEPSEEK_API_KEY = "你的 DeepSeek API Key"
$env:DEEPSEEK_MODEL = "deepseek-chat" # 可选
py app.py
```

服务运行在 `http://127.0.0.1:5001`，允许来自 `http://127.0.0.1:8765` 的报告页跨域调用。

接口：`POST /api/analyses/<analysis_id>/items/<seq>/script`

请求体传入报告条款即可（推荐将条款放入 `item`，项目资料放入 `analysis`）：

```json
{
  "analysis": {"project": "智慧教室设备采购项目"},
  "item": {
    "name": "摄像头像素",
    "requirement": "摄像头像素≥1200万",
    "xunfeiSpec": "800万像素广角摄像头",
    "deviation": "negative_real",
    "explanation": "规格低于招标要求",
    "suggestion": "核验指标的必要性"
  }
}
```

响应中的 `source` 为 `llm` 表示 DeepSeek 成功生成；未设置密钥、网络或模型调用失败时为 `template`，仍返回可复制的 `script`，便于演示不中断。

密钥只从环境变量或 `ai-bidding-decision/.env` 读取，勿提交 `.env`。
