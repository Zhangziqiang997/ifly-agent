# 参数智能体核心引擎 — 实施计划

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** 一个人从零搭建完整 Demo：6 个 Python 文件 + 1 个样例招标 JSON，端到端跑通三层对比链路。

**Architecture:** 脚本式架构，每个文件一个独立职责。`data_loader` 读 JSON → `parser` 第一关粗筛 → `matcher` 第二关控标识别 → `advisor` 第三关 AI 精判 → `engine` 串联全部流程 → `app.py` Streamlit 两页面展示。所有文件之间通过函数调用传递 Python dict，不依赖数据库或外部服务。

**Tech Stack:** Python 3.10 (at `C:/Users/zqzhang47/AppData/Local/Programs/Python/Python310/python.exe`) + Streamlit + DeepSeek API (`deepseek-v4-flash`)

## Global Constraints

- Python 解释器: `C:/Users/zqzhang47/AppData/Local/Programs/Python/Python310/python.exe`
- DeepSeek API Key: 环境变量 `DEEPSEEK_API_KEY`
- DeepSeek Base URL: 默认 `https://api.deepseek.com`，可通过 `DEEPSEEK_BASE_URL` 覆盖
- DeepSeek Model: `deepseek-v4-flash`
- 数据格式: JSON Schema v3.0 (`indicators[]` 数组格式，见 `data/README.md`)
- 数据目录: `data/competitors/`（竞品 JSON）、`data/xunfei/`（讯飞 JSON）、`data/samples/`（样例招标 + 降级结果）
- AI 调用: 所有 uncertain 参数打包为 1 次批量请求（禁止逐条串行调用）
- 降级: API 超时 10 秒后自动切本地 `data/samples/demo-result.json`
- Streamlit: 2 个页面（上传&总览 / 对比表含建议详情）
- Windows 编码: 禁止使用 emoji 字符（GBK 编码不兼容）

---
## 文件结构总览

```
src/
├── data_loader.py    # Task 0: 读写 JSON、加载竞品/讯飞/招标数据
├── parser.py         # Task 1: 第一关 — quick_match() 程序粗筛
├── matcher.py        # Task 2: 第二关 — identify_controller() 控标识别
├── advisor.py        # Task 3: 第三关 — batch_analyze() AI 批量语义精判
├── engine.py         # Task 4: 串联三层 → run_analysis()
└── app.py            # Task 5: Streamlit 两页面 UI
```

---

### Task 0: data_loader — JSON 读写

**Files:**
- Create: `src/data_loader.py`

**Interfaces:**
- Produces: `load_competitors(base_dir)` → `dict[str, dict]`, `load_xunfei(base_dir)` → `dict`, `load_bid(base_dir, filename)` → `dict`, `save_json(data, filepath)` → `None`

- [ ] **Step 1: 编写 data_loader.py**

```python
"""Load and save JSON data files for the bidding analysis system."""
import json, os

DATA_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data")

def load_json(filepath: str) -> dict:
    """Load a single JSON file, return parsed dict. Returns empty dict if file not found."""
    try:
        with open(filepath, "r", encoding="utf-8") as f:
            return json.load(f)
    except FileNotFoundError:
        return {}

def load_competitors(base_dir: str = DATA_DIR) -> dict:
    """Load all competitor JSON files from data/competitors/.
    Returns dict keyed by vendor filename stem, e.g. {'xiwo': {...}, 'honghe': {...}}."""
    comp_dir = os.path.join(base_dir, "competitors")
    competitors = {}
    if not os.path.isdir(comp_dir):
        return competitors
    for fname in os.listdir(comp_dir):
        if fname.endswith(".json"):
            key = fname.replace(".json", "")
            data = load_json(os.path.join(comp_dir, fname))
            if data:
                competitors[key] = data
    return competitors

def load_xunfei(base_dir: str = DATA_DIR) -> dict:
    """Load iFLYTEK parameters from data/xunfei/xunfei.json."""
    return load_json(os.path.join(base_dir, "xunfei", "xunfei.json"))

def load_bid(base_dir: str = DATA_DIR, filename: str = "sample-bid.json") -> dict:
    """Load a bidding file from data/samples/."""
    return load_json(os.path.join(base_dir, "samples", filename))

def save_json(data: dict, filepath: str) -> None:
    """Save dict as JSON file."""
    os.makedirs(os.path.dirname(filepath), exist_ok=True)
    with open(filepath, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
```

- [ ] **Step 2: 验证 data_loader 能正确加载现有 JSON**

```bash
cd "C:/Users/zqzhang47/Desktop/参数智能体"
/c/Users/zqzhang47/AppData/Local/Programs/Python/Python310/python.exe -c "
import sys; sys.path.insert(0, 'src')
from data_loader import load_competitors, load_xunfei
comps = load_competitors()
print('Loaded competitors:', list(comps.keys()))
xf = load_xunfei()
print('Xunfei product:', xf.get('product'))
print('Xunfei params count:', len(xf.get('params', [])))
"
```

Expected: `Loaded competitors: ['xiwo', 'honghe', 'wenxiang']`, `Xunfei params count: 15`

- [ ] **Step 3: Commit**

---

### Task 1: parser — 第一关程序粗筛

**Files:**
- Create: `src/parser.py`

**Interfaces:**
- Consumes: competitor/xunfei/bid `params[]` (each with `{name, spec, indicators: [{name, value, unit, comparator}]}`)
- Produces: `extract_numeric(text)` → `list[(num, unit_str)]`, `normalize_unit(value, unit_from, unit_to)` → `float`, `compare_indicators(bid_inds, our_inds)` → `("positive"|"negative"|"uncertain", detail)`, `quick_match(bid_item, our_params)` → `("positive"|"negative"|"uncertain", matched_param|None, detail)`

- [ ] **Step 1: 编写 parser.py**

```python
"""Layer 1: Programmatic quick-match — numeric extraction, unit normalization, keyword matching."""
import re

# Unit conversion table: normalized_unit -> {other_unit: conversion_factor}
UNIT_CONVERSIONS = {
    "px":    {"pixel_width": 1},
    "inch":  {},
    "mm":    {},
    "cd_m2": {},
    "watt":  {},
    "mp":    {"pixel_width": None},  # cannot convert, use keyword
    "gb":    {},
    "count": {},
    "touch_points": {},
    "pressure_level": {},
    "degree": {},
    "pct":   {},
    "hour":  {},
    "platform_count": {},
    "second": {},
    "reflectivity_pct": {},
    "feature": {},  # boolean features skip numeric compare
    "cert": {},
    "spec": {},
    "type": {},
}


def extract_numeric(text: str) -> list:
    """Extract all (number, unit_hint) pairs from a text string.
    Example: '>=3840*2160' -> [(3840, 'px'), (2160, 'px')]
             '>=500cd/m2' -> [(500, 'cd_m2')]
             '<=28mm'     -> [(28, 'mm')]
    """
    results = []
    # Pattern 1: number + known unit text
    patterns = [
        (r'(\d+\.?\d*)\s*cd\s*/\s*m\s*[²2]', 'cd_m2'),
        (r'(\d+\.?\d*)\s*mm', 'mm'),
        (r'(\d+\.?\d*)\s*英寸', 'inch'),
        (r'(\d+\.?\d*)\s*inch', 'inch'),
        (r'(\d+\.?\d*)\s*万像素', 'mp'),
        (r'(\d+\.?\d*)\s*[Ww]', 'watt'),
        (r'(\d+\.?\d*)\s*GB', 'gb'),
        (r'(\d+\.?\d*)\s*[点個]', 'touch_points'),
        (r'(\d+\.?\d*)\s*[级級]', 'pressure_level'),
        (r'(\d+\.?\d*)\s*[°度]', 'degree'),
        (r'(\d+\.?\d*)\s*[%％]', 'pct'),
        (r'(\d+\.?\d*)\s*[米mM]\s', 'm'),
        (r'(\d+\.?\d*)\s*[条路個个]', 'count'),
    ]
    for pat, unit in patterns:
        for m in re.finditer(pat, text):
            results.append((float(m.group(1)), unit))

    # Pattern 2: bare numbers (resolution-like: 3840x2160 or 3840*2160)
    for m in re.finditer(r'(\d{3,5})\s*[xX\*×]\s*(\d{3,5})', text):
        results.append((float(m.group(1)), 'px'))
        results.append((float(m.group(2)), 'px'))

    # Pattern 3: bare numbers with comparison operators
    for m in re.finditer(r'[≥≤>＜>=]\s*(\d+\.?\d*)', text):
        num = float(m.group(1))
        if not any(abs(r[0] - num) < 0.01 for r in results):
            results.append((num, 'unknown'))

    return results


def normalize_unit(value: float, from_unit: str, to_unit: str) -> float:
    """Convert value from one unit to another. Returns same value if units are directly comparable."""
    if from_unit == to_unit:
        return value
    # units that are just different names for the same thing
    same_units = {
        'pixel_width': 'px', 'px': 'pixel_width',
        'inch': 'inch_inch',
        'cd_m2': 'cd_m2_cd',
    }
    if same_units.get(from_unit) == same_units.get(to_unit, ''):
        return value
    return value  # default: assume comparable units


def compare_indicators(bid_inds: list, our_inds: list) -> tuple:
    """Compare two indicator lists, return ('positive'|'negative'|'uncertain', explanation).
    bid_inds: [{'name','value','unit','comparator'}, ...]
    our_inds: [{'name','value','unit','comparator'}, ...]
    """
    if not bid_inds:
        return ("uncertain", "no indicators to compare")

    matches = 0
    total = 0
    for bi in bid_inds:
        total += 1
        matched_oi = None
        # Find matching indicator by unit
        for oi in our_inds:
            if bi.get('unit') == oi.get('unit'):
                matched_oi = oi
                break
        # Fallback: find by name keyword overlap
        if not matched_oi:
            for oi in our_inds:
                if bi.get('name', '') in oi.get('name', '') or oi.get('name', '') in bi.get('name', ''):
                    matched_oi = oi
                    break

        if matched_oi and isinstance(bi.get('value'), (int, float)) and isinstance(matched_oi.get('value'), (int, float)):
            bid_val = bi['value']
            our_val = normalize_unit(matched_oi['value'], matched_oi.get('unit', ''), bi.get('unit', ''))
            comp = bi.get('comparator', 'eq')

            if comp in ('gte', 'gt', 'eq') and our_val >= bid_val:
                matches += 1
            elif comp in ('lte', 'lt') and our_val <= bid_val:
                matches += 1
            elif comp == 'eq' and abs(our_val - bid_val) < 0.01:
                matches += 1
        elif matched_oi and isinstance(bi.get('value'), bool) and isinstance(matched_oi.get('value'), bool):
            if bi['value'] == matched_oi['value']:
                matches += 1
        # boolean features: if bid requires True and ours is True, match
        elif matched_oi and bi.get('value') == True and matched_oi.get('value') == True:
            matches += 1

    if total == 0:
        return ("uncertain", "no numeric indicators")
    if matches == total:
        return ("positive", f"{matches}/{total} indicators matched")
    elif matches == 0:
        return ("negative", f"0/{total} indicators matched")
    else:
        return ("uncertain", f"{matches}/{total} indicators matched, needs AI review")


def keyword_overlap(text1: str, text2: str) -> float:
    """Calculate Jaccard similarity between two texts based on 2-char bigrams."""
    if not text1 or not text2:
        return 0.0
    def bigrams(s):
        s = s.lower().replace(' ', '')
        return set(s[i:i+2] for i in range(len(s)-1))
    b1, b2 = bigrams(text1), bigrams(text2)
    if not b1 or not b2:
        return 0.0
    return len(b1 & b2) / len(b1 | b2)


def quick_match(bid_item: dict, our_param: dict) -> tuple:
    """Determine if our_param satisfies bid_item. Returns (status, detail).
    status: 'positive' | 'negative' | 'uncertain'
    detail: explanation string
    """
    bid_name = bid_item.get('name', '')
    bid_req = bid_item.get('requirement', '')
    our_spec = our_param.get('spec', '')

    # Step A: Try indicator-level comparison
    bid_inds = bid_item.get('indicators', [])
    our_inds = our_param.get('indicators', [])
    if bid_inds and our_inds:
        status, detail = compare_indicators(bid_inds, our_inds)
        if status != 'uncertain':
            return (status, detail)

    # Step B: Try numeric extraction from requirement text
    bid_nums = extract_numeric(bid_req)
    our_nums = extract_numeric(our_spec)
    if bid_nums and our_nums:
        matched = 0
        for bn, bu in bid_nums:
            for on_val, ou in our_nums:
                if bu == ou or normalize_unit(on_val, ou, bu) == on_val:
                    if on_val >= bn:
                        matched += 1
                        break
        if matched == len(bid_nums):
            return ("positive", f"numeric: {matched}/{len(bid_nums)} satisfied")
        elif matched > 0:
            return ("uncertain", f"numeric: {matched}/{len(bid_nums)} partial, needs AI")

    # Step C: Keyword / bigram overlap
    overlap = keyword_overlap(bid_req, our_spec)
    if overlap > 0.5:
        return ("positive", f"keyword similarity: {overlap:.0%}")
    elif overlap > 0.3:
        return ("uncertain", f"keyword similarity: {overlap:.0%}, needs AI")
    else:
        return ("uncertain", f"keyword similarity: {overlap:.0%}, needs AI")


def find_best_match(bid_item: dict, our_params: list) -> tuple:
    """Find the best matching param in our_params for bid_item. Returns (status, matched_param, detail)."""
    best_status, best_param, best_detail = ("uncertain", None, "no match found")
    for p in our_params:
        status, detail = quick_match(bid_item, p)
        if status == 'positive':
            return (status, p, detail)
        if status == 'uncertain' and best_status == 'uncertain' and p.get('category') == bid_item.get('category'):
            best_status, best_param, best_detail = (status, p, detail)
    if best_status == 'uncertain' and best_param is None and our_params:
        best_param = our_params[0]
    return (best_status, best_param, best_detail)
```

- [ ] **Step 2: 自测 extract_numeric**

```bash
/c/Users/zqzhang47/AppData/Local/Programs/Python/Python310/python.exe -c "
import sys; sys.path.insert(0, 'src')
from parser import extract_numeric, keyword_overlap
print(extract_numeric('>=500cd/m2'))        # Expected: [(500.0, 'cd_m2')]
print(extract_numeric('3840*2160'))          # Expected: [(3840.0, 'px'), (2160.0, 'px')]
print(extract_numeric('<=28mm'))             # Expected: [(28.0, 'mm')]
print(extract_numeric('>=4800万像素'))        # Expected: [(4800.0, 'mp')]
print(keyword_overlap('无线投屏', '屏幕镜像'))  # Expected: < 0.3
print(keyword_overlap('护眼认证', '护眼认证'))  # Expected: > 0.8
"
```

- [ ] **Step 3: Commit**

---

### Task 2: matcher — 第二关控标识别

**Files:**
- Create: `src/matcher.py`

**Interfaces:**
- Consumes: bid `items[]`, competitors dict from `data_loader`, `quick_match()` from `parser`
- Produces: `identify_controller(bid_items, competitors)` → `{vendor, confidence, scores: {vendor: count}, hits: [...], anomalies: [...]}`

- [ ] **Step 1: 编写 matcher.py**

```python
"""Layer 2: Controller identification — find unique features, score each vendor."""
from parser import quick_match, find_best_match


def match_with_competitor(bid_item: dict, comp_params: list) -> bool:
    """Check if a competitor satisfies the bidding requirement. Returns True/False."""
    status, _, _ = find_best_match(bid_item, comp_params)
    return status == 'positive'


def identify_controller(bid_items: list, competitors: dict) -> dict:
    """Identify which competitor the bidding document is designed for.

    bid_items: [{seq, category, name, requirement, indicators, star_mark, triangle_mark}, ...]
    competitors: {'xiwo': {vendor, product, params: [...]}, 'honghe': {...}, ...}

    Returns:
        {vendor, confidence, scores: {vendor_name: unique_feature_count},
         hits: [{seq, param_name, hit_vendor, reason}],
         anomalies: [{seq, param_name, reason}]}
    """
    scores = {name: 0 for name in competitors}
    hits = []
    anomalies = []

    for item in bid_items:
        satisfied_by = []
        for comp_name, comp_data in competitors.items():
            if match_with_competitor(item, comp_data.get('params', [])):
                satisfied_by.append(comp_name)

        if len(satisfied_by) == 1:
            vendor = satisfied_by[0]
            scores[vendor] += 1
            hits.append({
                'seq': item.get('seq'),
                'param_name': item.get('name', ''),
                'hit_vendor': vendor,
                'reason': f'Only {vendor} satisfies this requirement'
            })
        elif len(satisfied_by) == 0:
            anomalies.append({
                'seq': item.get('seq'),
                'param_name': item.get('name', ''),
                'reason': 'No vendor in database satisfies this requirement'
            })

    total_valid = len(bid_items) - len(anomalies)
    total_hits = sum(scores.values())

    if total_hits > 0 and total_valid > 0:
        controller = max(scores, key=scores.get)
        confidence = total_hits / total_valid
        # Get full vendor name
        vendor_name = competitors.get(controller, {}).get('vendor', controller)
    else:
        vendor_idx = max(scores, key=scores.get)
        vendor_name = competitors.get(vendor_idx, {}).get('vendor', 'Unable to determine')
        confidence = 0

    return {
        'vendor': vendor_name,
        'confidence': round(confidence, 2),
        'scores': {competitors.get(k, {}).get('vendor', k): v for k, v in scores.items()},
        'hits': hits,
        'anomalies': anomalies
    }
```

- [ ] **Step 2: 自测 — 用 Mock 数据跑一遍**

```bash
/c/Users/zqzhang47/AppData/Local/Programs/Python/Python310/python.exe -c "
import sys, json
sys.path.insert(0, 'src')
from data_loader import load_competitors, load_bid
from matcher import identify_controller

comps = load_competitors()
bid = load_bid()
print('Competitors:', [c.get('vendor','?') for c in comps.values()])
print('Bid items:', len(bid.get('items',[])))
result = identify_controller(bid['items'], comps)
print('Controller:', result['vendor'])
print('Confidence:', result['confidence'])
print('Scores:', result['scores'])
print('Hits:', len(result['hits']))
print('Anomalies:', len(result['anomalies']))
"
```

Expected: 能输出控标方和置信度（因为是 Mock 数据，可能置信度为 0，这正常——Mock 参数故意写成了各厂商互相有差异）。

- [ ] **Step 3: Commit**

---

### Task 3: advisor — 第三关 AI 语义精判 + 建议生成

**Files:**
- Create: `src/advisor.py`

**Interfaces:**
- Consumes: list of uncertain params `[{bid_item, xunfei_param, detail}]`, API key from env
- Produces: `batch_analyze(uncertain_items, xunfei_params)` → list of analyzed results with `{match, deviation, explanation, suggestion}`

- [ ] **Step 1: 编写 advisor.py**

```python
"""Layer 3: AI semantic matching + suggestion generation via DeepSeek API with offline fallback."""
import os, json, time, re, sys
import urllib.request, urllib.error

API_KEY = os.getenv("DEEPSEEK_API_KEY", "")
BASE_URL = os.getenv("DEEPSEEK_BASE_URL", "https://api.deepseek.com")
MODEL = "deepseek-v4-flash"
TIMEOUT = 10  # seconds
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


def batch_analyze(uncertain_items: list, xunfei_params: list) -> list:
    """Analyze uncertain parameters via AI (batch call), with offline fallback.
    
    uncertain_items: [{seq, bid_name, bid_req, xunfei_name, xunfei_spec, category}, ...]
    Returns: [{seq, match, deviation, explanation, suggestion}, ...]
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

        # Save as fallback for offline demo
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
```

- [ ] **Step 2: 验证 — 用真实 API 跑一遍**

```bash
cd "C:/Users/zqzhang47/Desktop/参数智能体"
export DEEPSEEK_API_KEY="sk-your-key-here"
/c/Users/zqzhang47/AppData/Local/Programs/Python/Python310/python.exe -c "
import sys; sys.path.insert(0, 'src')
from advisor import batch_analyze
items = [{
    'seq': 1, 'bid_name': 'Camera', 'bid_req': 'Built-in camera >= 48MP, horizontal FOV >= 120 degrees',
    'xunfei_name': 'Camera', 'xunfei_spec': 'Built-in 48MP ultra-wide-angle camera, diagonal FOV >= 135 degrees, horizontal FOV >= 120 degrees',
    'category': 'Camera'
}]
results = batch_analyze(items, [])
print(results)
"
```

Expected: `[OK] AI analysis complete | time=~8s | items=1`, result shows `match: true, deviation: positive`.

- [ ] **Step 3: 验证降级 — 拔掉 API key 测试 fallback 读取**

```bash
cd "C:/Users/zqzhang47/Desktop/参数智能体"
unset DEEPSEEK_API_KEY
/c/Users/zqzhang47/AppData/Local/Programs/Python/Python310/python.exe -c "
import sys; sys.path.insert(0, 'src')
from advisor import batch_analyze
items = [{'seq': 1, 'bid_name': 'x', 'bid_req': 'x', 'xunfei_name': 'y', 'xunfei_spec': 'y', 'category': 'z'}]
results = batch_analyze(items, [])
print('Fallback results:', results)
"
```

Expected: `[WARN] No DEEPSEEK_API_KEY set, using offline fallback`, loads previous saved results.

- [ ] **Step 4: Commit**

---

### Task 4: engine — 串联三层架构

**Files:**
- Create: `src/engine.py`

**Interfaces:**
- Consumes: data_loader, parser (find_best_match, quick_match), matcher (identify_controller), advisor (batch_analyze)
- Produces: `run_analysis(bid_path)` → `{controller, matching[], anomalies[]}` dict matching SPEC §3.3 format

- [ ] **Step 1: 编写 engine.py**

```python
"""Orchestrator: ties Layer 1 (parser), Layer 2 (matcher), Layer 3 (advisor) together."""
import json, os
from data_loader import load_competitors, load_xunfei, load_bid, load_json
from parser import find_best_match
from matcher import identify_controller
from advisor import batch_analyze


def run_analysis(bid_filename: str = "sample-bid.json") -> dict:
    """Run the full 3-layer bidding analysis.
    
    Args:
        bid_filename: name of bid JSON file in data/samples/
    Returns:
        {controller: {vendor, confidence, scores, hits, anomalies},
         matching: [{seq, category, bid_req, xunfei_spec, deviation, match_method, suggestion}],
         summary: {total, positive, negative_wording, negative_real}}
    """
    competitors = load_competitors()
    xunfei = load_xunfei()
    bid = load_bid(filename=bid_filename)

    xunfei_params = xunfei.get('params', [])
    bid_items = bid.get('items', [])

    # Layer 2: Controller identification (programmatic)
    controller_result = identify_controller(bid_items, competitors)

    # Layer 1 + 3: For each bid item, try programmatic match first,
    # then send uncertain ones to AI (batched)
    matching = []
    uncertain_items = []

    for item in bid_items:
        status, matched_param, detail = find_best_match(item, xunfei_params)

        if status == 'positive':
            matching.append({
                'seq': item['seq'],
                'category': item.get('category', ''),
                'name': item.get('name', ''),
                'bid_req': item.get('requirement', ''),
                'xunfei_spec': matched_param.get('spec', '') if matched_param else '',
                'deviation': 'positive',
                'match_method': 'program',
                'detail': detail,
                'suggestion': None
            })
        elif status == 'negative':
            # Negative from program — still send to AI for suggestion generation
            matching.append({
                'seq': item['seq'],
                'category': item.get('category', ''),
                'name': item.get('name', ''),
                'bid_req': item.get('requirement', ''),
                'xunfei_spec': matched_param.get('spec', '') if matched_param else '',
                'deviation': 'negative_real',
                'match_method': 'program',
                'detail': detail,
                'suggestion': None  # AI will fill this
            })
            uncertain_items.append({
                'seq': item['seq'],
                'bid_name': item.get('name', ''),
                'bid_req': item.get('requirement', ''),
                'xunfei_name': matched_param.get('name', '') if matched_param else '',
                'xunfei_spec': matched_param.get('spec', '') if matched_param else '',
                'category': item.get('category', '')
            })
        else:  # uncertain
            uncertain_items.append({
                'seq': item['seq'],
                'bid_name': item.get('name', ''),
                'bid_req': item.get('requirement', ''),
                'xunfei_name': matched_param.get('name', '') if matched_param else '',
                'xunfei_spec': matched_param.get('spec', '') if matched_param else '',
                'category': item.get('category', '')
            })

    # Layer 3: AI batch analysis for uncertain items
    if uncertain_items:
        ai_results = batch_analyze(uncertain_items, xunfei_params)
        ai_map = {}
        for r in ai_results:
            ai_map[r.get('seq', 0)] = r

        for item in uncertain_items:
            seq = item['seq']
            ai = ai_map.get(seq, {})
            # Update or add to matching list
            existing = [m for m in matching if m['seq'] == seq]
            if existing:
                existing[0]['deviation'] = ai.get('deviation', 'negative_real')
                existing[0]['match_method'] = 'ai_semantic'
                existing[0]['suggestion'] = ai.get('suggestion', ai.get('explanation', ''))
            else:
                matching.append({
                    'seq': seq,
                    'category': item.get('category', ''),
                    'name': item.get('bid_name', ''),
                    'bid_req': item.get('bid_req', ''),
                    'xunfei_spec': item.get('xunfei_spec', ''),
                    'deviation': ai.get('deviation', 'negative_real'),
                    'match_method': 'ai_semantic',
                    'detail': ai.get('explanation', ''),
                    'suggestion': ai.get('suggestion', '')
                })

    # Sort by seq
    matching.sort(key=lambda m: m['seq'])

    # Summary
    summary = {
        'total': len(matching),
        'positive': sum(1 for m in matching if m['deviation'] == 'positive'),
        'negative_wording': sum(1 for m in matching if m['deviation'] == 'negative_wording'),
        'negative_real': sum(1 for m in matching if m['deviation'] == 'negative_real')
    }

    return {
        'project': bid.get('project', ''),
        'controller': controller_result,
        'matching': matching,
        'summary': summary
    }
```

- [ ] **Step 2: 端到端测试 — 用现有 Mock 数据跑 engine**

```bash
cd "C:/Users/zqzhang47/Desktop/参数智能体"
export DEEPSEEK_API_KEY="sk-your-key-here"
/c/Users/zqzhang47/AppData/Local/Programs/Python/Python310/python.exe -c "
import sys, json
sys.path.insert(0, 'src')
from engine import run_analysis

result = run_analysis('sample-bid.json')
print(json.dumps(result, ensure_ascii=False, indent=2))
"
```

Expected: 输出包含 controller、matching、summary 的完整结果 JSON。如果 sample-bid.json 不存在会报错（这是预期的，下一步创建它）。

- [ ] **Step 3: Commit**

---

### Task 5: 样例招标 JSON

**Files:**
- Create: `data/samples/sample-bid.json`

- [ ] **Step 1: 创建 sample-bid.json**

```json
{
  "project": "XX市教育局智慧教室建设项目",
  "date": "2026-07",
  "items": [
    {
      "seq": 1,
      "category": "显示",
      "name": "屏幕尺寸",
      "requirement": "整机屏幕采用UHD超高清A规LED液晶屏，屏幕显示尺寸>=86英寸，显示比例16:9，屏幕图像分辨率>=3840x2160",
      "indicators": [
        {"name": "屏幕尺寸", "value": 86, "unit": "inch", "comparator": "gte"},
        {"name": "水平分辨率", "value": 3840, "unit": "px", "comparator": "gte"}
      ],
      "star_mark": false,
      "triangle_mark": false
    },
    {
      "seq": 2,
      "category": "显示",
      "name": "屏幕亮度",
      "requirement": "整机屏体亮度>=350cd/m2，对比度>=4000:1，色彩覆盖率>=85%NTSC",
      "indicators": [
        {"name": "亮度", "value": 350, "unit": "cd_m2", "comparator": "gte"}
      ],
      "star_mark": false,
      "triangle_mark": false
    },
    {
      "seq": 3,
      "category": "触控",
      "name": "触控技术",
      "requirement": "采用电容触控技术，支持Windows和安卓系统下50点或以上触控，触摸响应时间<=4ms",
      "indicators": [
        {"name": "触控点数", "value": 50, "unit": "touch_points", "comparator": "gte"}
      ],
      "star_mark": true,
      "triangle_mark": false
    },
    {
      "seq": 4,
      "category": "摄像",
      "name": "内置摄像头",
      "requirement": "整机内置摄像头像素>=4800万，水平视场角>=120度，支持AI识别人像和远程巡课",
      "indicators": [
        {"name": "摄像头像素", "value": 4800, "unit": "mp", "comparator": "gte"},
        {"name": "视场角", "value": 120, "unit": "degree", "comparator": "gte"}
      ],
      "star_mark": true,
      "triangle_mark": false
    },
    {
      "seq": 5,
      "category": "音频",
      "name": "内置音响",
      "requirement": "整机内置2.2声道扬声器，额定总功率>=60W，内置>=8阵列麦克风，拾音距离>=12m",
      "indicators": [
        {"name": "扬声器功率", "value": 60, "unit": "watt", "comparator": "gte"},
        {"name": "麦克风阵列", "value": 8, "unit": "count", "comparator": "gte"}
      ],
      "star_mark": false,
      "triangle_mark": true
    },
    {
      "seq": 6,
      "category": "护眼",
      "name": "护眼认证",
      "requirement": "通过德国莱茵TUV低蓝光认证及无频闪认证，蓝光危害达到RG0级别",
      "indicators": [
        {"name": "TUV低蓝光认证", "value": true, "unit": "cert", "comparator": "eq"},
        {"name": "无频闪认证", "value": true, "unit": "cert", "comparator": "eq"}
      ],
      "star_mark": false,
      "triangle_mark": false
    },
    {
      "seq": 7,
      "category": "无线",
      "name": "无线投屏",
      "requirement": "支持多终端无线投屏与反向触控功能，兼容主流操作系统平台",
      "indicators": [
        {"name": "投屏平台数", "value": 3, "unit": "platform_count", "comparator": "gte"},
        {"name": "反向触控", "value": true, "unit": "feature", "comparator": "eq"}
      ],
      "star_mark": false,
      "triangle_mark": false
    },
    {
      "seq": 8,
      "category": "物理",
      "name": "整机厚度",
      "requirement": "整机厚度<=100mm（含壁挂支架），宽度>=4200mm，高度>=1200mm",
      "indicators": [
        {"name": "整机厚度", "value": 100, "unit": "mm", "comparator": "lte"}
      ],
      "star_mark": false,
      "triangle_mark": false
    },
    {
      "seq": 9,
      "category": "连接",
      "name": "接口配置",
      "requirement": "前置接口>=5个（含HDMI、双通道USB3.0、Type-C 65W PD快充），Type-C支持DP1.4视频输入",
      "indicators": [
        {"name": "前置USB3.0", "value": 2, "unit": "count", "comparator": "gte"},
        {"name": "前置Type-C", "value": 1, "unit": "count", "comparator": "gte"},
        {"name": "Type-C充电功率", "value": 65, "unit": "watt", "comparator": "gte"}
      ],
      "star_mark": true,
      "triangle_mark": false
    },
    {
      "seq": 10,
      "category": "计算",
      "name": "OPS电脑",
      "requirement": "CPU>=8核12线程，内存>=8GB DDR4，硬盘>=256GB SSD，独立HDMI输出>=1路",
      "indicators": [
        {"name": "内存", "value": 8, "unit": "gb", "comparator": "gte"},
        {"name": "硬盘", "value": 256, "unit": "gb", "comparator": "gte"}
      ],
      "star_mark": false,
      "triangle_mark": true
    },
    {
      "seq": 11,
      "category": "AI",
      "name": "语音交互",
      "requirement": "支持通过口语表达控制操作系统和应用软件，支持>=300条语音指令，支持模糊语义理解",
      "indicators": [
        {"name": "语音指令操控", "value": true, "unit": "feature", "comparator": "eq"}
      ],
      "star_mark": false,
      "triangle_mark": false
    },
    {
      "seq": 12,
      "category": "笔",
      "name": "智能笔",
      "requirement": "智能笔压感>=4096级，具备手笔分离防误触功能，支持语音控制和无线鼠标功能",
      "indicators": [
        {"name": "压感级别", "value": 4096, "unit": "pressure_level", "comparator": "gte"}
      ],
      "star_mark": false,
      "triangle_mark": false
    }
  ]
}
```

- [ ] **Step 2: 验证 engine 能正确读取并分析**

```bash
cd "C:/Users/zqzhang47/Desktop/参数智能体"
export DEEPSEEK_API_KEY="sk-your-key-here"
/c/Users/zqzhang47/AppData/Local/Programs/Python/Python310/python.exe -c "
import sys, json
sys.path.insert(0, 'src')
from engine import run_analysis
result = run_analysis('sample-bid.json')
print('Controller:', result['controller']['vendor'])
print('Confidence:', result['controller']['confidence'])
print('Summary:', json.dumps(result['summary'], ensure_ascii=False))
for m in result['matching']:
    print(f'  #{m[\"seq\"]} {m[\"deviation\"]:20s} {m[\"match_method\"]:12s} | {m.get(\"name\",\"\")}')
"
```

Expected: 输出 12 条参数的分析结果，标注了每条是程序判定还是 AI 判定，正偏离/负偏离统计。

- [ ] **Step 3: Commit**

---

### Task 6: app.py — Streamlit 两页面 UI

**Files:**
- Create: `src/app.py`

**Interfaces:**
- Consumes: `run_analysis()` from engine
- Produces: Streamlit web app on `localhost:8501`

- [ ] **Step 1: 安装 Streamlit**

```bash
/c/Users/zqzhang47/AppData/Local/Programs/Python/Python310/python.exe -m pip install streamlit pandas
```

- [ ] **Step 2: 编写 app.py**

```python
"""Streamlit UI: 2 pages — (1) Upload + Controller Result, (2) Parameter Comparison Table with Advice."""
import sys, os, json
sys.path.insert(0, os.path.dirname(__file__))
import streamlit as st
import pandas as pd
from engine import run_analysis
from data_loader import load_bid

st.set_page_config(page_title="Parameter Agent", page_icon="[iflytek]", layout="wide")

DEVIATION_LABELS = {
    'positive': 'Green: Positive',
    'negative_wording': 'Yellow: Wording Fixable',
    'negative_real': 'Red: Genuinely Unsatisfied'
}


def page_upload():
    st.title("Parameter Agent — Bidding Analysis")
    st.caption("Upload a bidding document, identify the controlling vendor, and compare parameters against iFLYTEK.")

    uploaded = st.file_uploader("Upload bidding document (JSON)", type=["json"], key="bid_upload")
    use_sample = st.button("Use Sample Bidding Document", type="secondary")

    if not uploaded and not use_sample:
        st.info("Upload a JSON bidding file or click 'Use Sample Bidding Document' to start.")
        return

    if use_sample or uploaded:
        with st.spinner("Running 3-layer analysis..."):
            if uploaded:
                import tempfile
                with tempfile.NamedTemporaryFile(delete=False, suffix=".json", mode="w", encoding="utf-8") as f:
                    content = uploaded.getvalue().decode("utf-8")
                    f.write(content)
                    tmp_path = f.name
                result = run_analysis(os.path.basename(tmp_path))
            else:
                result = run_analysis("sample-bid.json")

    st.session_state.result = result
    st.session_state.page = "compare"

    # Controller result cards
    ctrl = result['controller']
    summary = result['summary']

    st.subheader("Analysis Result")
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("Controlling Vendor", ctrl['vendor'])
    with col2:
        st.metric("Confidence", f"{ctrl['confidence']:.0%}")
    with col3:
        st.metric("Unique Features Hit", f"{len(ctrl['hits'])}/{summary['total']}")
    with col4:
        st.metric("Anomalies", len(ctrl['anomalies']))

    # Vendor score distribution
    if ctrl['scores']:
        st.subheader("Vendor Unique Feature Distribution")
        score_df = pd.DataFrame(
            {'Vendor': list(ctrl['scores'].keys()), 'Unique Features': list(ctrl['scores'].values())}
        )
        st.bar_chart(score_df.set_index('Vendor'))

    # Deviations overview
    st.subheader("Deviation Overview")
    dev_col1, dev_col2, dev_col3 = st.columns(3)
    with dev_col1:
        st.metric("Green (Positive)", summary['positive'])
    with dev_col2:
        st.metric("Yellow (Fixable)", summary['negative_wording'])
    with dev_col3:
        st.metric("Red (Unsatisfied)", summary['negative_real'])

    if st.button("View Detailed Comparison ->", type="primary"):
        st.rerun()


def page_compare():
    st.title("Parameter Comparison")

    if 'result' not in st.session_state or st.session_state.result is None:
        st.warning("No analysis result. Please upload a bidding document first.")
        if st.button("<- Back to Upload"):
            st.session_state.page = "upload"
            st.rerun()
        return

    result = st.session_state.result

    if st.button("<- Back to Upload"):
        st.session_state.page = "upload"
        st.rerun()

    # Filter
    filter_option = st.selectbox("Filter:", ["All", "Green (Positive)", "Yellow (Fixable)", "Red (Unsatisfied)"])
    matching = result['matching']
    if filter_option.startswith("Green"):
        matching = [m for m in matching if m['deviation'] == 'positive']
    elif filter_option.startswith("Yellow"):
        matching = [m for m in matching if m['deviation'] == 'negative_wording']
    elif filter_option.startswith("Red"):
        matching = [m for m in matching if m['deviation'] == 'negative_real']

    # Build table data
    rows = []
    for m in matching:
        dev_icon = {'positive': ':green[Green]', 'negative_wording': ':orange[Yellow]', 'negative_real': ':red[Red]'}.get(m['deviation'], '?')
        rows.append({
            '#': m['seq'],
            'Category': m.get('category', ''),
            'Bidding Requirement': m.get('bid_req', ''),
            'iFLYTEK Parameter': m.get('xunfei_spec', ''),
            'Deviation': dev_icon,
            'Method': m.get('match_method', ''),
        })
    df = pd.DataFrame(rows)
    st.dataframe(df, use_container_width=True, hide_index=True,
                 column_config={
                     'Bidding Requirement': st.column_config.TextColumn(width='large'),
                     'iFLYTEK Parameter': st.column_config.TextColumn(width='large'),
                 })

    st.subheader("Advice Details (Click a negative deviation row)")
    st.caption("Click a row in the table above that has Yellow or Red deviation to see advice below.")

    # Show all negative items' advice below
    negative_items = [m for m in result['matching'] if m['deviation'] in ('negative_wording', 'negative_real')]
    if negative_items:
        for item in negative_items:
            with st.expander(f"#{item['seq']} {item.get('name', '')} — {item.get('deviation', '')} | Method: {item.get('match_method', '')}"):
                st.markdown(f"**Bidding Requirement:** {item.get('bid_req', '')}")
                st.markdown(f"**iFLYTEK Parameter:** {item.get('xunfei_spec', '')}")
                st.markdown(f"**Analysis:** {item.get('detail', '')}")
                if item.get('suggestion'):
                    st.info(f"**Suggestion:** {item['suggestion']}")


def main():
    if 'page' not in st.session_state:
        st.session_state.page = "upload"
    if 'result' not in st.session_state:
        st.session_state.result = None

    if st.session_state.page == "upload":
        page_upload()
    else:
        page_compare()


if __name__ == "__main__":
    main()
```

- [ ] **Step 3: 启动 Streamlit**

```bash
cd "C:/Users/zqzhang47/Desktop/参数智能体"
export DEEPSEEK_API_KEY="sk-your-key-here"
/c/Users/zqzhang47/AppData/Local/Programs/Python/Python310/python.exe -m streamlit run src/app.py
```

Expected: Open browser at http://localhost:8501, click "Use Sample Bidding Document" or upload a JSON, see controller result, click "View Detailed Comparison", see comparison table with advice expanders.

- [ ] **Step 4: Commit**

---

## 执行顺序 & 依赖图

```
Task 0 (data_loader) ── 无依赖，第一个写
    │
    ├── Task 1 (parser)     ── 依赖 Task 0 的数据格式理解
    ├── Task 2 (matcher)    ── 依赖 Task 1 (import quick_match)
    ├── Task 3 (advisor)    ── 依赖 Task 0 (需要知道 JSON 路径)
    │
    ├── Task 5 (sample-bid) ── 不依赖代码，任何时候都可创建
    │
    └── Task 4 (engine)     ── 依赖 Task 0+1+2+3+5
         │
         └── Task 6 (app.py) ── 依赖 Task 4
```

**推荐执行顺序**: Task 0 → Task 1 → Task 2 → Task 5 → Task 3 → Task 4 → Task 6

Task 5 可以穿插在任何时候做，不阻塞其他任务。

---

## 最终验证清单

全部完成后，运行这个命令验证端到端：

```bash
cd "C:/Users/zqzhang47/Desktop/参数智能体"
export DEEPSEEK_API_KEY="sk-your-key-here"
/c/Users/zqzhang47/AppData/Local/Programs/Python/Python310/python.exe -c "
import sys, json; sys.path.insert(0, 'src')
from engine import run_analysis
result = run_analysis('sample-bid.json')
assert 'controller' in result, 'Missing controller'
assert 'matching' in result, 'Missing matching'
assert 'summary' in result, 'Missing summary'
assert len(result['matching']) == 12, f'Expected 12 items, got {len(result[\"matching\"])}'
print('[PASS] All 6 checks passed!')
print(f'  Controller: {result[\"controller\"][\"vendor\"]} (confidence={result[\"controller\"][\"confidence\"]:.0%})')
print(f'  Program-matched: {sum(1 for m in result[\"matching\"] if m[\"match_method\"]==\"program\")}')
print(f'  AI-matched: {sum(1 for m in result[\"matching\"] if m[\"match_method\"]==\"ai_semantic\")}')
print(f'  Positive: {result[\"summary\"][\"positive\"]} | Fixable: {result[\"summary\"][\"negative_wording\"]} | Real: {result[\"summary\"][\"negative_real\"]}')
"
```

---

## 快速启动（给演示用）

```bash
# 查看引擎结果（JSON）
/c/Users/zqzhang47/AppData/Local/Programs/Python/Python310/python.exe -c "import sys,json; sys.path.insert(0,'src'); from engine import run_analysis; print(json.dumps(run_analysis('sample-bid.json'), ensure_ascii=False, indent=2))"

# 启动 Streamlit UI
export DEEPSEEK_API_KEY="sk-your-key-here"
/c/Users/zqzhang47/AppData/Local/Programs/Python/Python310/python.exe -m streamlit run src/app.py
```

