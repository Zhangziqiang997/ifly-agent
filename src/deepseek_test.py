"""
DeepSeek API connectivity test + offline fallback result
Usage:
    export DEEPSEEK_API_KEY="sk-xxx"
    python deepseek_test.py
"""
import os, json, time, sys, re

API_KEY = os.getenv("DEEPSEEK_API_KEY", "")
BASE_URL = os.getenv("DEEPSEEK_BASE_URL", "https://api.deepseek.com")
MODEL = os.getenv("DEEPSEEK_MODEL", "deepseek-v4-flash")

if not API_KEY:
    print("[ERROR] Please set DEEPSEEK_API_KEY environment variable")
    sys.exit(1)

TEST_PROMPT = """You are a bidding parameter analysis expert. Judge whether the following bidding requirement and iFLYTEK product parameter refer to the same capability.

[Bidding Requirement]
Built-in camera >= 48MP, horizontal FOV >= 120 degrees

[iFLYTEK Parameter]
Built-in 48MP ultra-wide-angle camera, diagonal FOV >= 135 degrees, horizontal FOV >= 120 degrees

Return pure JSON only (no markdown code block):
{
  "match": true or false,
  "deviation": "positive" or "negative_wording" or "negative_real",
  "explanation": "one sentence explanation"
}"""


def call_deepseek(prompt: str, timeout: int = 15) -> dict:
    """Call DeepSeek Chat API, return parsed JSON"""
    import urllib.request, urllib.error

    body = json.dumps({
        "model": MODEL,
        "messages": [
            {"role": "system", "content": "You are a bidding parameter analysis expert. Return JSON only, no extra text."},
            {"role": "user", "content": prompt}
        ],
        "temperature": 0.1,
        "max_tokens": 500,
        "stream": False
    }).encode("utf-8")

    req = urllib.request.Request(
        f"{BASE_URL}/v1/chat/completions",
        data=body,
        headers={
            "Content-Type": "application/json",
            "Authorization": f"Bearer {API_KEY}"
        },
        method="POST"
    )

    start = time.time()
    try:
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            raw = json.loads(resp.read().decode("utf-8"))
            elapsed = time.time() - start
            content = raw["choices"][0]["message"]["content"]

            match = re.search(r'\{.*\}', content, re.DOTALL)
            result = json.loads(match.group(0)) if match else {"raw": content}

            print(f"[OK] API success | time={elapsed:.1f}s | tokens={raw.get('usage', {}).get('total_tokens', '?')}")
            return result

    except urllib.error.HTTPError as e:
        body = e.read().decode() if e.fp else ""
        print(f"[ERROR] HTTP {e.code}: {body}")
        raise


if __name__ == "__main__":
    print(f"[INFO] {BASE_URL} | model: {MODEL}")
    print("[INFO] Sending test prompt...")

    result = call_deepseek(TEST_PROMPT)

    print(f"\n[RESULT] AI response:")
    print(json.dumps(result, ensure_ascii=False, indent=2))

    out = {
        "test_time": time.strftime("%Y-%m-%d %H:%M:%S"),
        "model": MODEL,
        "prompt": TEST_PROMPT,
        "result": result
    }
    os.makedirs("data/samples", exist_ok=True)
    with open("data/samples/demo-result.json", "w", encoding="utf-8") as f:
        json.dump(out, f, ensure_ascii=False, indent=2)
    print(f"\n[OK] Offline fallback saved to data/samples/demo-result.json")
