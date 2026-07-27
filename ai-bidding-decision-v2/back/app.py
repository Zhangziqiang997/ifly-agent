"""AI 投标决策演示页的最小后端：生成单条风险应对话术。"""

import os
from pathlib import Path

from flask import Flask, jsonify, request
from flask_cors import CORS

try:
    from dotenv import load_dotenv
    load_dotenv(Path(__file__).resolve().parents[1] / ".env")
except ImportError:
    pass

app = Flask(__name__)
CORS(app, resources={r"/api/*": {"origins": ["http://127.0.0.1:8765", "http://localhost:8765"]}})


def _template_script(item: dict) -> str:
    """无模型或模型调用失败时的可复制兜底话术。"""
    seq = item.get("seq", "该")
    name = item.get("name") or item.get("category") or "技术参数"
    requirement = item.get("requirement") or item.get("bidRequirement") or "该项招标要求"
    explanation = item.get("explanation") or item.get("reason") or "该要求与现有产品规格存在差异"
    suggestion = item.get("suggestion") or "请说明设置该指标的必要性及相应国家或行业标准依据。"
    return (
        f"关于第{seq}项“{name}”（招标要求：{requirement}）：{explanation}。"
        "该指标可能形成对特定产品的倾向性限制，请招标方说明其教学场景必要性，"
        "并提供对应国家标准或行业标准依据；如无充分依据，建议调整为功能性、非排他性表述。"
        f"应对建议：{suggestion}"
    )


def _generate_with_deepseek(item: dict, analysis_context: dict) -> str | None:
    """通过 DeepSeek 生成话术；未配置或失败返回 None，由调用方使用模板。"""
    api_key = os.getenv("DEEPSEEK_API_KEY", "").strip()
    if not api_key:
        return None
    try:
        from openai import OpenAI

        client = OpenAI(api_key=api_key, base_url="https://api.deepseek.com")
        model = os.getenv("DEEPSEEK_MODEL", "deepseek-chat")
        prompt = (
            "你是教育装备采购投标专家。基于以下单条偏离分析，生成一段可直接复制提交的中文质疑/应对话术。"
            "语气专业、客观，不作无依据指控；要求说明技术必要性和标准依据；200字以内。"
            "只输出话术正文，不要标题、Markdown或解释。\n\n"
            f"项目上下文：{analysis_context.get('project', '智慧黑板采购项目')}\n"
            f"条款序号：{item.get('seq', '')}\n"
            f"条款名称：{item.get('name') or item.get('category') or ''}\n"
            f"招标要求：{item.get('requirement') or item.get('bidRequirement') or ''}\n"
            f"我方规格：{item.get('xunfeiSpec') or item.get('xunfei_spec') or item.get('ourSpec') or ''}\n"
            f"偏离结论：{item.get('deviation') or item.get('status') or ''}\n"
            f"偏离依据：{item.get('explanation') or item.get('reason') or ''}\n"
            f"已有建议：{item.get('suggestion') or ''}"
        )
        response = client.chat.completions.create(
            model=model,
            messages=[{"role": "user", "content": prompt}],
            temperature=0.3,
            max_tokens=500,
            timeout=20,
        )
        script = (response.choices[0].message.content or "").strip()
        return script or None
    except Exception as exc:  # API 网络、配额、格式异常均可继续演示
        app.logger.warning("DeepSeek script generation failed: %s", exc)
        return None


@app.get("/api/health")
def health():
    return jsonify({"status": "ok", "service": "ai-bidding-decision-script-api"})


@app.post("/api/analyses/<analysis_id>/items/<int:seq>/script")
def generate_script(analysis_id: str, seq: int):
    """生成话术。

    请求 JSON 支持 ``item``（推荐）或直接传递条款字段；``analysis`` 可提供项目上下文。
    这样静态报告页无需先在后端创建分析记录也能直接调用。
    """
    payload = request.get_json(silent=True) or {}
    item = payload.get("item") if isinstance(payload.get("item"), dict) else payload
    item = {**item, "seq": item.get("seq", seq)}
    analysis_context = payload.get("analysis") if isinstance(payload.get("analysis"), dict) else {}

    script = _generate_with_deepseek(item, analysis_context)
    source = "llm" if script else "template"
    if not script:
        script = _template_script(item)

    return jsonify({
        "analysisId": analysis_id,
        "seq": seq,
        "source": source,
        "script": script,
    })


if __name__ == "__main__":
    app.run(host="127.0.0.1", port=5001, debug=True)
