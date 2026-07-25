# 07 — 测试用例

> 版本：v1.0 | 日期：2026-07-25  
> 定位：**设计阶段**。核心引擎的测试用例集合，覆盖 Layer 1/2/3 及端到端场景。

---

## 1. 测试策略

| 层级 | 测试类型 | 覆盖目标 | 执行方式 |
|------|---------|---------|---------|
| Layer 1 (parser) | 单元测试 | 6 个核心函数 | Python 命令行自测 |
| Layer 2 (matcher) | 单元测试 | 控标识别逻辑 | Python 命令行自测 |
| Layer 3 (advisor) | 集成测试 | API 调用 + 降级 | Mock + 真实 API |
| Engine | 端到端测试 | 完整分析链路 | 跑 sample-bid.json |
| UI | 手动测试 | 页面交互 | 浏览器操作 |

---

## 2. Layer 1：parser.py 测试用例

### TC-1.1 extract_numeric() — 数值提取

| # | 输入 | 期望输出 | 说明 |
|----|------|---------|------|
| TC-1.1.1 | `">=500cd/m2"` | `[(500.0, 'cd_m2')]` | 亮度值 + 单位 |
| TC-1.1.2 | `"3840*2160"` | `[(3840.0, 'px'), (2160.0, 'px')]` | 分辨率乘法格式 |
| TC-1.1.3 | `"3840x2160"` | `[(3840.0, 'px'), (2160.0, 'px')]` | 分辨率 x 格式 |
| TC-1.1.4 | `"<=28mm"` | `[(28.0, 'mm')]` | 厚度上限 |
| TC-1.1.5 | `">=4800万像素"` | `[(4800.0, 'mp')]` | 中文单位 |
| TC-1.1.6 | `"≥86英寸"` | `[(86.0, 'inch')]` | 中文符号 + 中文单位 |
| TC-1.1.7 | `"支持50点触控"` | `[(50.0, 'touch_points')]` | 中文语境数字 |
| TC-1.1.8 | `">=8GB DDR4"` | `[(8.0, 'gb')]` | 内存规格 |
| TC-1.1.9 | `"无数字文本"` | `[]` | 空输入边界 |
| TC-1.1.10 | `">=60W"` | `[(60.0, 'watt')]` | 功率单位 |

### TC-1.2 normalize_unit() — 单位归一化

| # | 输入 | 期望输出 | 说明 |
|----|------|---------|------|
| TC-1.2.1 | `(100, 'px', 'pixel_width')` | `100` | 像素同义单位 |
| TC-1.2.2 | `(100, 'px', 'px')` | `100` | 相同单位直通 |
| TC-1.2.3 | `(86, 'inch', 'inch')` | `86` | 相同单位直通 |

### TC-1.3 keyword_overlap() — 关键词相似度

| # | 输入 (text1, text2) | 期望 | 说明 |
|----|---------------------|------|------|
| TC-1.3.1 | `("无线投屏", "屏幕镜像")` | < 0.3 | 说法不同，需 AI |
| TC-1.3.2 | `("护眼认证", "护眼认证")` | > 0.8 | 完全一致 |
| TC-1.3.3 | `("防眩玻璃", "防眩光玻璃")` | 0.3–0.7 | 部分重叠 |
| TC-1.3.4 | `("屏幕亮度", "摄像头像素")` | < 0.2 | 不相关 |
| TC-1.3.5 | `("", "something")` | 0.0 | 空字符串边界 |

### TC-1.4 compare_indicators() — 指标组比较

| # | bid_indicators | our_indicators | 期望 |
|----|---------------|----------------|------|
| TC-1.4.1 | `[{value:86, unit:"inch", comp:"gte"}]` | `[{value:86, unit:"inch", comp:"gte"}]` | `("positive", "1/1")` |
| TC-1.4.2 | `[{value:100, unit:"inch", comp:"gte"}]` | `[{value:86, unit:"inch", comp:"gte"}]` | `("negative", "0/1")` |
| TC-1.4.3 | `[{value:86, unit:"inch"}, {value:3840, unit:"px"}]` | `[{value:86, unit:"inch"}, {value:3840, unit:"px"}]` | `("positive", "2/2")` |
| TC-1.4.4 | `[{value:true, unit:"cert"}]` | `[{value:true, unit:"cert"}]` | `("positive", "1/1")` |
| TC-1.4.5 | `[{value:true, unit:"cert"}]` | `[{value:false, unit:"cert"}]` | `("negative", "0/1")` |
| TC-1.4.6 | `[]` | `[{value:86, unit:"inch"}]` | `("uncertain", "no indicators")` |

### TC-1.5 quick_match() — 快速匹配

| # | 场景 | 期望状态 |
|----|------|---------|
| TC-1.5.1 | bid 和 our 的 indicators 完全匹配 | `positive` |
| TC-1.5.2 | bid 数值 > our 数值（不满足） | `negative` |
| TC-1.5.3 | 无 indicators，但关键词相似度 > 0.5 | `positive` |
| TC-1.5.4 | 无 indicators，关键词相似度 < 0.3 | `uncertain` |
| TC-1.5.5 | 有数值但部分不满足 | `uncertain` |

### TC-1.6 find_best_match() — 最佳匹配查找

| # | 场景 | 期望 |
|----|------|------|
| TC-1.6.1 | 存在完全匹配的参数 | 返回 `(positive, 正确参数, detail)` |
| TC-1.6.2 | "防眩玻璃"不应匹配到"亮度与色域" | matched_param.category == "护眼" |
| TC-1.6.3 | "Type-C"不应匹配到"屏幕尺寸" | matched_param.category == "连接" |
| TC-1.6.4 | 无任何匹配 | 返回 `(uncertain, top_scored_param, "low confidence")` |

---

## 3. Layer 2：matcher.py 测试用例

### TC-2.1 identify_controller() — 控标识别

| # | 场景 | 期望 |
|----|------|------|
| TC-2.1.1 | 所有 12 条全被海康独有 | vendor=海康, confidence=1.0, hits=12 |
| TC-2.1.2 | 3 家各命中 4 条 | confidence=0.33, vendor=任意（并列），无明显倾向 |
| TC-2.1.3 | 所有参数被多家满足 | confidence=0, hits=[] |
| TC-2.1.4 | 有一条所有厂商都不满足 | anomalies 包含该条, confidence 计算排除异常 |
| TC-2.1.5 | 空招标文件（items=[]） | confidence=0, hits=[], anomalies=[] |

### TC-2.2 当前 Demo 数据验证

| 指标 | 当前值 | 说明 |
|------|--------|------|
| 控标方 | 海康威视 | 样例招标为海康控标场景 |
| 置信度 | 55% | 6/11 条独有特征（排除 1 个 anomaly） |
| 独有特征命中 | 6 条 | 摄像/视频相关参数为主 |
| 异常 | 1 条 | 1 条参数所有厂商均不满足 |

---

## 4. Layer 3：advisor.py 测试用例

### TC-3.1 batch_analyze() — AI 批量分析

| # | 场景 | 期望 |
|----|------|------|
| TC-3.1.1 | 1 条明确正偏离参数 | `{match: true, deviation: "positive"}` |
| TC-3.1.2 | 1 条说法不同但能力有的参数 | `{match: true, deviation: "negative_wording"}` |
| TC-3.1.3 | 1 条确实不满足的参数 | `{match: false, deviation: "negative_real"}` |
| TC-3.1.4 | 空列表 `uncertain_items=[]` | 返回 `[]`，不调用 API |
| TC-3.1.5 | API Key 未设置 | 自动读取 demo-result.json 降级 |
| TC-3.1.6 | API 返回非 JSON 文本 | 正则兜底提取，至少返回 `[{raw: content}]` |
| TC-3.1.7 | API 超时 | 捕获异常，读取降级文件 |

### TC-3.2 降级文件持久化

| # | 场景 | 期望 |
|----|------|------|
| TC-3.2.1 | API 调用成功后 | `demo-result.json` 被更新 |
| TC-3.2.2 | `demo-result.json` 不存在 + API 不可用 | 返回 `[]`，不崩溃 |

---

## 5. 端到端：engine.py 测试用例

### TC-4.1 run_analysis() — 完整分析链路

| # | 验证项 | 断言 |
|----|--------|------|
| TC-4.1.1 | 返回结构完整性 | `"controller" in result` and `"matching" in result` and `"summary" in result` |
| TC-4.1.2 | matching 数量 = 招标条目数 | `len(result["matching"]) == 12` |
| TC-4.1.3 | summary 统计一致 | `positive + negative_wording + negative_real == total` |
| TC-4.1.4 | controller 置信度范围 | `0 <= confidence <= 1` |
| TC-4.1.5 | matching 按 seq 排序 | `result["matching"][i]["seq"] <= result["matching"][i+1]["seq"]` |
| TC-4.1.6 | match_method 合法值 | 每个结果 method ∈ `{"program", "ai_semantic"}` |
| TC-4.1.7 | deviation 合法值 | 每个结果 deviation ∈ `{"positive", "negative_wording", "negative_real"}` |
| TC-4.1.8 | 正偏离无建议 | positive 项的 suggestion 应为 null |

---

## 6. UI：app.py 测试用例

### TC-5.1 页面导航

| # | 操作 | 期望 |
|----|------|------|
| TC-5.1.1 | 首次打开 | 显示 Page 1（上传&总览），无分析结果 |
| TC-5.1.2 | 点击 "Use Sample Bidding Document" | 显示分析结果卡片（控标方/置信度/命中数/异常数） |
| TC-5.1.3 | 点击 "View Detailed Comparison" | 跳转到 Page 2（对比表） |
| TC-5.1.4 | 在 Page 2 点击 "<- Back to Upload" | 返回 Page 1 |

### TC-5.2 筛选功能

| # | 操作 | 期望 |
|----|------|------|
| TC-5.2.1 | 选择 "All" | 显示全部 12 条 |
| TC-5.2.2 | 选择 "Green (Positive)" | 仅显示 positive 条目 |
| TC-5.2.3 | 选择 "Yellow (Fixable)" | 仅显示 negative_wording 条目 |
| TC-5.2.4 | 选择 "Red (Unsatisfied)" | 仅显示 negative_real 条目 |

### TC-5.3 建议卡片

| # | 操作 | 期望 |
|----|------|------|
| TC-5.3.1 | 查看负偏离展开卡片 | 显示 bid_req / xunfei_spec / analysis / suggestion |
| TC-5.3.2 | positive 条目 | 不出现在建议卡片区域 |

---

## 7. 边界和异常测试

### TC-6.1 空数据

| # | 场景 | 期望行为 |
|----|------|---------|
| TC-6.1.1 | 竞品目录为空 | `load_competitors()` 返回 `{}`，引擎不崩溃 |
| TC-6.1.2 | 讯飞 JSON 不存在 | `load_xunfei()` 返回 `{}` |
| TC-6.1.3 | 招标 items 为空 | `identify_controller` 返回 confidence=0 |
| TC-6.1.4 | 招标 JSON 不存在 | `load_bid()` 返回 `{}` |

### TC-6.2 数据格式异常

| # | 场景 | 期望行为 |
|----|------|---------|
| TC-6.2.1 | param 缺少 indicators 字段 | `get('indicators', [])` 兜底，不抛 KeyError |
| TC-6.2.2 | indicator.value 为 null | compare_indicators 跳过，不计入匹配 |
| TC-6.2.3 | indicator.unit 不在已知列表 | 不影响匹配，仍按 unit 字符串精确比较 |
