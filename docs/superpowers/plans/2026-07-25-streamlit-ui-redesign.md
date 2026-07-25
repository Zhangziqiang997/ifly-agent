# 参数智能体 Streamlit UI 重写 Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** 将 `src/app.py` 重写为严格复刻 `prototype_design.html` 的样例驱动 Streamlit Demo。

**Architecture:** 使用单文件 Streamlit 应用承载页面路由和渲染，HTML/CSS 负责高保真视觉骨架，Streamlit 原生控件负责导航、筛选和状态。所有业务数据来自 `run_analysis("sample-bid.json")` 或现有四份产品 JSON，纯数据转换函数与渲染函数分离，以便单元测试。

**Tech Stack:** Python 3.10、Streamlit、标准库 `html`/`json`/`pathlib`/`collections`、pytest、Streamlit AppTest、浏览器手动验收。

## Global Constraints

- 分析入口必须固定调用 `run_analysis("sample-bid.json")`。
- 不读取或保存用户上传内容，不创建 `_uploaded.json`。
- 不修改 `src/engine.py`、分析算法或现有 JSON 数据。
- 参数知识库只能读取 `data/xunfei/xunfei.json` 与三份 `data/competitors/*.json`。
- 视觉令牌必须直接沿用 `prototype_design.html`：`#0A1628`、`#0F1E35`、`#162035`、`#1E3050`、`#00D4FF`、`#22C55E`、`#FFB547`、`#FF5C5C`、`#E8EDF5`、`#6B82A0`、`220px` 侧栏。
- 所有动态文本在 HTML 插值前必须通过 `html.escape()`。
- 不增加第三方依赖。
- 保留工作区中与本任务无关的未提交修改。

---

## File Map

- Modify: `src/app.py` — 页面状态、数据适配、全局样式、上传页、分析页、知识库页与入口。
- Create: `tests/test_app.py` — 纯函数、页面初始状态、样例分析入口、筛选与知识库读取测试。
- Reference only: `prototype_design.html` — 视觉系统与页面结构来源。
- Reference only: `src/engine.py` — `run_analysis(bid_filename: str) -> dict`。
- Reference only: `data/xunfei/xunfei.json`、`data/competitors/*.json` — 只读知识库数据。

### Required Internal Interfaces

`src/app.py` 必须提供以下可测试接口：

```python
def validate_result(result: object) -> tuple[bool, str]: ...
def aggregate_deviations(matching: list[dict]) -> dict[str, dict[str, int]]: ...
def filter_matching(matching: list[dict], deviation: str) -> list[dict]: ...
def load_knowledge_base() -> list[dict]: ...
def escape_text(value: object) -> str: ...
def render_sidebar(active_page: str, has_result: bool) -> None: ...
def render_upload_page() -> None: ...
def render_dashboard_page() -> None: ...
def render_knowledge_page() -> None: ...
def main() -> None: ...
```

---

### Task 1: 数据适配与安全边界

**Files:**
- Modify: `src/app.py`
- Create: `tests/test_app.py`

**Interfaces:**
- Consumes: `run_analysis("sample-bid.json")` 返回的结果契约及四份产品 JSON。
- Produces: `validate_result()`、`aggregate_deviations()`、`filter_matching()`、`load_knowledge_base()`、`escape_text()`。

- [ ] **Step 1: 写入数据适配失败测试**

在 `tests/test_app.py` 中加入：

```python
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

import app


def test_validate_result_accepts_engine_contract():
    result = {
        "project": "样例项目",
        "controller": {
            "vendor": "希沃",
            "confidence": 0.5,
            "scores": {"希沃": 2},
            "hits": [],
            "anomalies": [],
        },
        "matching": [],
        "summary": {
            "total": 0,
            "positive": 0,
            "negative_wording": 0,
            "negative_real": 0,
        },
    }
    assert app.validate_result(result) == (True, "")


def test_validate_result_rejects_missing_core_field():
    ok, message = app.validate_result({"project": "样例项目"})
    assert ok is False
    assert "controller" in message


def test_escape_text_escapes_html():
    assert app.escape_text("<script>alert(1)</script>") == (
        "&lt;script&gt;alert(1)&lt;/script&gt;"
    )


def test_aggregate_deviations_groups_category_and_status():
    matching = [
        {"category": "显示", "deviation": "positive"},
        {"category": "显示", "deviation": "negative_real"},
        {"category": "触控", "deviation": "negative_wording"},
    ]
    assert app.aggregate_deviations(matching) == {
        "显示": {"positive": 1, "negative_wording": 0, "negative_real": 1},
        "触控": {"positive": 0, "negative_wording": 1, "negative_real": 0},
    }


def test_filter_matching_keeps_original_order():
    matching = [
        {"seq": 1, "deviation": "positive"},
        {"seq": 2, "deviation": "negative_real"},
    ]
    assert app.filter_matching(matching, "negative_real") == [matching[1]]
    assert app.filter_matching(matching, "all") == matching


def test_load_knowledge_base_reads_four_vendors():
    records = app.load_knowledge_base()
    vendors = {record["vendor"] for record in records}
    assert len(vendors) == 4
    assert any(record["params"] for record in records)
```

- [ ] **Step 2: 运行测试并确认失败原因**

Run:

```powershell
C:/Users/zqzhang47/AppData/Local/Programs/Python/Python310/python.exe -m pytest tests/test_app.py -v
```

Expected: FAIL，提示 `app` 缺少上述数据适配函数。

- [ ] **Step 3: 在 `src/app.py` 实现最小数据适配层**

实现要求：

```python
REQUIRED_RESULT_KEYS = ("project", "controller", "matching", "summary")
VALID_DEVIATIONS = ("positive", "negative_wording", "negative_real")


def escape_text(value: object) -> str:
    return html.escape("" if value is None else str(value), quote=True)


def validate_result(result: object) -> tuple[bool, str]:
    if not isinstance(result, dict):
        return False, "分析结果不是有效对象"
    for key in REQUIRED_RESULT_KEYS:
        if key not in result:
            return False, f"分析结果缺少核心字段：{key}"
    if not isinstance(result["controller"], dict):
        return False, "分析结果字段 controller 格式错误"
    if not isinstance(result["matching"], list):
        return False, "分析结果字段 matching 格式错误"
    if not isinstance(result["summary"], dict):
        return False, "分析结果字段 summary 格式错误"
    return True, ""
```

`aggregate_deviations()` 必须按首次出现顺序保留类别，并为每个类别初始化三个偏离计数；`filter_matching()` 的 `"all"` 返回浅拷贝，其余值按 `deviation` 过滤；`load_knowledge_base()` 使用 `Path(__file__).resolve().parents[1]` 定位四份 JSON，并输出统一的 `{vendor, product, params}` 记录。

- [ ] **Step 4: 运行数据适配测试**

Run:

```powershell
C:/Users/zqzhang47/AppData/Local/Programs/Python/Python310/python.exe -m pytest tests/test_app.py -v
```

Expected: 6 tests PASS。

- [ ] **Step 5: 提交数据适配层**

```powershell
git add src/app.py tests/test_app.py
git commit -m "test: define Streamlit UI data adapters"
```

---

### Task 2: 全局视觉骨架、侧栏与样例分析入口

**Files:**
- Modify: `src/app.py`
- Modify: `tests/test_app.py`

**Interfaces:**
- Consumes: Task 1 的 `validate_result()`、`escape_text()` 和 `run_analysis()`。
- Produces: `render_sidebar()`、`render_upload_page()`、稳定的 `st.session_state` 页面路由。

- [ ] **Step 1: 写入页面初始状态与样例入口失败测试**

在 `tests/test_app.py` 中加入：

```python
from unittest.mock import patch
from streamlit.testing.v1 import AppTest


def test_initial_page_is_demo_upload():
    at = AppTest.from_file(str(ROOT / "src" / "app.py")).run()
    assert not at.exception
    assert at.session_state["page"] == "upload"
    assert at.session_state["result"] is None
    assert any("演示模式" in item.value for item in at.markdown)


def test_analyze_button_uses_sample_filename_only():
    fake_result = {
        "project": "样例项目",
        "controller": {
            "vendor": "希沃",
            "confidence": 0.5,
            "scores": {"希沃": 2},
            "hits": [],
            "anomalies": [],
        },
        "matching": [],
        "summary": {
            "total": 0,
            "positive": 0,
            "negative_wording": 0,
            "negative_real": 0,
        },
    }
    with patch("engine.run_analysis", return_value=fake_result) as mocked:
        at = AppTest.from_file(str(ROOT / "src" / "app.py")).run()
        analyze = next(button for button in at.button if button.label == "加载样例并开始分析")
        analyze.click().run()
        mocked.assert_called_once_with("sample-bid.json")
```

- [ ] **Step 2: 运行两个页面测试并确认失败**

Run:

```powershell
C:/Users/zqzhang47/AppData/Local/Programs/Python/Python310/python.exe -m pytest tests/test_app.py::test_initial_page_is_demo_upload tests/test_app.py::test_analyze_button_uses_sample_filename_only -v
```

Expected: FAIL，当前页面缺少中文演示模式和指定按钮。

- [ ] **Step 3: 重写全局 CSS 与页面状态**

在 `src/app.py` 中：

- 设置 `page_title="参数智能体"`、`page_icon="⚡"`、`layout="wide"`；
- 使用原型中的十个颜色令牌和 `--sidebar-w:220px`；
- 隐藏 Streamlit 默认 header、footer 和侧栏；
- 建立固定 `.app-sidebar` 与左侧留白为 220px 的 `.main .block-container`；
- 初始化 `page="upload"`、`result=None`、`analysis_complete=False`、`analysis_time=None`、`comparison_filter="all"`；
- `render_sidebar()` 使用三个唯一键按钮切换页面；无结果时点击分析结果显示提示而不是空报告；
- `render_upload_page()` 显示原型上传区、格式标签、演示模式说明和唯一主按钮；
- 主按钮只执行 `run_analysis("sample-bid.json")`，校验成功后写入 session state 并切到 `"dashboard"`；
- 失败时清理结果并通过中文错误卡显示异常。

- [ ] **Step 4: 运行页面测试与全量数据测试**

Run:

```powershell
C:/Users/zqzhang47/AppData/Local/Programs/Python/Python310/python.exe -m pytest tests/test_app.py -v
```

Expected: 所有测试 PASS，且不存在 AppTest exception。

- [ ] **Step 5: 提交页面骨架**

```powershell
git add src/app.py tests/test_app.py
git commit -m "feat: add prototype-aligned demo shell"
```

---

### Task 3: 分析报告、动态分布图、筛选表与建议

**Files:**
- Modify: `src/app.py`
- Modify: `tests/test_app.py`

**Interfaces:**
- Consumes: `st.session_state.result`、`aggregate_deviations()`、`filter_matching()`、`escape_text()`。
- Produces: `render_dashboard_page()` 及 `_render_stats()`、`_render_verdict()`、`_render_distribution()`、`_render_comparison_table()`、`_render_suggestions()`。

- [ ] **Step 1: 写入报告渲染失败测试**

在 `tests/test_app.py` 中加入：

```python
def test_aggregate_counts_match_summary_contract():
    matching = [
        {"category": "显示", "deviation": "positive"},
        {"category": "显示", "deviation": "negative_wording"},
        {"category": "触控", "deviation": "negative_real"},
    ]
    grouped = app.aggregate_deviations(matching)
    assert sum(row["positive"] for row in grouped.values()) == 1
    assert sum(row["negative_wording"] for row in grouped.values()) == 1
    assert sum(row["negative_real"] for row in grouped.values()) == 1


def test_dashboard_source_contains_prototype_sections():
    source = (ROOT / "src" / "app.py").read_text(encoding="utf-8")
    for label in ("有效参数总计", "控标方判定", "参数偏离分布", "参数逐条对比", "应对建议"):
        assert label in source
```

- [ ] **Step 2: 运行报告测试并确认失败**

Run:

```powershell
C:/Users/zqzhang47/AppData/Local/Programs/Python/Python310/python.exe -m pytest tests/test_app.py::test_dashboard_source_contains_prototype_sections -v
```

Expected: FAIL，缺少至少一个原型区块。

- [ ] **Step 3: 实现分析报告**

实现要求：

- 四张统计卡严格读取 `summary`；
- 控标卡展示 `controller.vendor`、`confidence`、置信等级、`hits` 和 `anomalies`；
- 使用内联 SVG 绘制置信度环形图；
- `_render_distribution()` 将 `aggregate_deviations()` 输出渲染成每类别绿/黄/红堆叠柱；
- 表格列固定为序号、类别、招标要求、讯飞规格、偏离判定、判定方式；
- Streamlit 筛选控件使用 `"all"`、`"positive"`、`"negative_wording"`、`"negative_real"`，数量来自 `summary`；
- `negative_wording` 建议标记为 P0，`negative_real` 标记为 P1；
- 建议面板展示 `bid_req`、`xunfei_spec`、`detail`、`suggestion`；
- `suggestion is None` 时不渲染空面板；
- 任何引擎文本必须先经过 `escape_text()`。

- [ ] **Step 4: 运行全量测试**

Run:

```powershell
C:/Users/zqzhang47/AppData/Local/Programs/Python/Python310/python.exe -m pytest tests/test_app.py -v
```

Expected: 所有测试 PASS。

- [ ] **Step 5: 提交分析报告**

```powershell
git add src/app.py tests/test_app.py
git commit -m "feat: render analysis dashboard and advice"
```

---

### Task 4: 只读参数知识库

**Files:**
- Modify: `src/app.py`
- Modify: `tests/test_app.py`

**Interfaces:**
- Consumes: `load_knowledge_base()` 输出的 `{vendor, product, params}` 列表。
- Produces: `render_knowledge_page()`，支持关键词、厂商和品类的只读筛选。

- [ ] **Step 1: 写入知识库只读约束失败测试**

在 `tests/test_app.py` 中加入：

```python
def test_knowledge_page_has_filters_but_no_mutation_copy():
    source = (ROOT / "src" / "app.py").read_text(encoding="utf-8")
    assert "搜索参数名称、型号" in source
    assert "全部厂商" in source
    assert "全部品类" in source
    assert "新增条目" not in source
    assert "保存条目" not in source
    assert "_uploaded.json" not in source
```

- [ ] **Step 2: 运行约束测试并确认失败**

Run:

```powershell
C:/Users/zqzhang47/AppData/Local/Programs/Python/Python310/python.exe -m pytest tests/test_app.py::test_knowledge_page_has_filters_but_no_mutation_copy -v
```

Expected: FAIL，页面尚未提供三个只读筛选控件。

- [ ] **Step 3: 实现知识库页面**

实现要求：

- 页面标题与副标题对齐原型；
- 使用文本框、厂商选择框和品类选择框筛选；
- 将参数扁平化为厂商卡片，显示厂商、产品、分类、参数名称和规格；
- 厂商颜色映射：讯飞 cyan、希沃 red、鸿合 amber、海康 purple；
- 无结果时显示“未找到符合条件的参数”；
- 文件读取异常时在知识库页显示中文错误；
- 不出现任何新增、编辑、删除或保存控件。

- [ ] **Step 4: 运行全量测试**

Run:

```powershell
C:/Users/zqzhang47/AppData/Local/Programs/Python/Python310/python.exe -m pytest tests/test_app.py -v
```

Expected: 所有测试 PASS。

- [ ] **Step 5: 提交知识库页面**

```powershell
git add src/app.py tests/test_app.py
git commit -m "feat: add read-only parameter knowledge page"
```

---

### Task 5: 启动验证与浏览器视觉验收

**Files:**
- Modify: `src/app.py`（只修复验收中发现的问题）
- Modify: `tests/test_app.py`（只补充验收中复现出的回归测试）

**Interfaces:**
- Consumes: 完整 Streamlit 应用。
- Produces: 可在端口 8501 演示且与原型视觉一致的最终 UI。

- [ ] **Step 1: 运行静态与单元验证**

Run:

```powershell
C:/Users/zqzhang47/AppData/Local/Programs/Python/Python310/python.exe -m py_compile src/app.py
C:/Users/zqzhang47/AppData/Local/Programs/Python/Python310/python.exe -m pytest tests/test_app.py -v
```

Expected: 语法检查退出码 0，所有测试 PASS。

- [ ] **Step 2: 单独验证引擎样例契约**

Run:

```powershell
C:/Users/zqzhang47/AppData/Local/Programs/Python/Python310/python.exe -c "import sys; sys.path.insert(0, 'src'); from engine import run_analysis; r=run_analysis('sample-bid.json'); assert {'project','controller','matching','summary'} <= r.keys(); print(r['summary'])"
```

Expected: 退出码 0，并打印包含 `total`、`positive`、`negative_wording`、`negative_real` 的摘要。

- [ ] **Step 3: 启动 Streamlit**

Run:

```powershell
C:/Users/zqzhang47/AppData/Local/Programs/Python/Python310/python.exe -m streamlit run src/app.py --server.headless true --server.port 8501
```

Expected: 输出 `Local URL: http://localhost:8501`，无 traceback。

- [ ] **Step 4: 浏览器逐页验收**

在 `http://127.0.0.1:8501` 检查：

1. 上传页：固定 220px 侧栏、深色背景、演示模式说明、样例按钮；
2. 点击样例：进入分析结果，统计卡数值与引擎 `summary` 一致；
3. 控标卡：厂商、置信度、命中列表完整；
4. 分类分布：每个类别的绿/黄/红段数与 `matching` 聚合一致；
5. 四种筛选：表格行数与筛选计数一致；
6. 建议：只出现负偏离项，并可展开阅读；
7. 知识库：四家厂商可筛选，无写入控件；
8. 侧栏往返：分析结果保留，不重复运行引擎；
9. 浏览器控制台：无影响交互的错误。

- [ ] **Step 5: 修复验收发现的问题并重复验证**

每个问题先在 `tests/test_app.py` 添加可复现测试，再修改 `src/app.py`，然后重跑：

```powershell
C:/Users/zqzhang47/AppData/Local/Programs/Python/Python310/python.exe -m py_compile src/app.py
C:/Users/zqzhang47/AppData/Local/Programs/Python/Python310/python.exe -m pytest tests/test_app.py -v
```

Expected: 所有新增回归测试 PASS。

- [ ] **Step 6: 检查最终差异并提交**

Run:

```powershell
git diff --check
git status --short
git diff -- src/app.py tests/test_app.py
```

确认差异只包含本次 UI 重写与测试，然后：

```powershell
git add src/app.py tests/test_app.py
git commit -m "fix: polish Streamlit demo against prototype"
```
