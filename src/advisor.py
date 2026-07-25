"""Layer 3: AI semantic matching via DeepSeek API with offline fallback."""
import os, json, time, re, sys
import urllib.request, urllib.error
from config import DEEPSEEK_API_KEY as API_KEY, DEEPSEEK_BASE_URL as BASE_URL, DEEPSEEK_MODEL as MODEL

TIMEOUT = 30
FALLBACK_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data", "samples", "demo-result.json")


def _call_api(prompt: str) -> list:
    """Single batch API call. Returns list of result dicts."""
    body = json.dumps({
        "model": MODEL,
        "messages": [
            {"role": "system", "content": (
                "You are a bidding parameter analysis expert. "
                "Return ONLY a JSON array, no markdown code blocks, no extra text. "
                "Each element has: seq (int), match (bool), deviation (one of: positive, negative_wording, negative_real), "
                "explanation (short string in Chinese), suggestion (string in Chinese, or null if positive deviation)."
            )},
            {"role": "user", "content": prompt}
        ],
        "temperature": 0.1,
        "max_tokens": 2000,
        "stream": False
    }).encode("utf-8")

    req = urllib.request.Request(
        f"{BASE_URL}/v1/chat/completions",
        data=body,
        headers={"Content-Type": "application/json", "Authorization": f"Bearer {API_KEY}"},
        method="POST"
    )

    with urllib.request.urlopen(req, timeout=TIMEOUT) as resp:
        raw = json.loads(resp.read().decode("utf-8"))
        content = raw["choices"][0]["message"]["content"]

    match = re.search(r'\[.*\]', content, re.DOTALL)
    if match:
        return json.loads(match.group(0))
    match = re.search(r'\{.*\}', content, re.DOTALL)
    if match:
        return [json.loads(match.group(0))]
    return [{"raw": content}]


def _load_fallback() -> dict:
    """Load pre-generated offline fallback results."""
    try:
        with open(FALLBACK_PATH, "r", encoding="utf-8") as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        return {}


def batch_analyze(uncertain_items: list, xunfei_params: list = None) -> list:
    """Analyze uncertain parameters via AI (single batch call), with offline fallback.

    Args:
        uncertain_items: [{seq, bid_name, bid_req, xunfei_name, xunfei_spec, category}, ...]

    Returns:
        [{seq, match, deviation, explanation, suggestion}, ...]
    """
    if not uncertain_items:
        return []

    prompt_parts = []
    for i, item in enumerate(uncertain_items):
        prompt_parts.append(
            f"[{i}] seq={item['seq']}\n"
            f"Bidding requirement: {item['bid_req']}\n"
            f"iFLYTEK parameter: {item['xunfei_spec']}"
        )
    prompt = (
        "Analyze the following bidding requirements against iFLYTEK product parameters.\n"
        "For each item, judge:\n"
        "- positive: iFLYTEK meets or exceeds the requirement\n"
        "- negative_wording: iFLYTEK has the capability but description differs\n"
        "- negative_real: iFLYTEK genuinely cannot meet the requirement\n"
        "For negative items, provide a suggestion for response strategy (revise wording, challenge argument, or channel coordination).\n\n"
        + "\n---\n".join(prompt_parts) +
        "\n\nReturn a JSON array with one object per item (use the item index)."
    )

    if not API_KEY:
        print("[WARN] No DEEPSEEK_API_KEY set, using offline fallback")
        fallback = _load_fallback()
        return fallback.get("results", [])

    try:
        print(f"[INFO] Batch analyzing {len(uncertain_items)} items via AI...")
        start = time.time()
        results = _call_api(prompt)
        elapsed = time.time() - start
        print(f"[OK] AI analysis complete | time={elapsed:.1f}s | items={len(results)}")

        fallback = {
            "generated_at": time.strftime("%Y-%m-%d %H:%M:%S"),
            "model": MODEL,
            "item_count": len(uncertain_items),
            "results": results
        }
        os.makedirs(os.path.dirname(FALLBACK_PATH), exist_ok=True)
        with open(FALLBACK_PATH, "w", encoding="utf-8") as f:
            json.dump(fallback, f, ensure_ascii=False, indent=2)

        return results

    except Exception as e:
        print(f"[WARN] AI API failed: {e}, using offline fallback")
        fallback = _load_fallback()
        return fallback.get("results", [])
