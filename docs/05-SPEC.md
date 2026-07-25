# 05 — 功能规格书（SPEC）

> 版本：v1.0 | 日期：2026-07-25  
> 定位：**设计阶段**。纯技术规格——模块功能定义、数据格式契约、算法伪代码、接口规范。  
> 用户场景和价值部分见 [`02-PRD.md`](./02-PRD.md)。  
> Demo 范围的取舍见 [`06-ai-task-plan.md`](./06-ai-task-plan.md)。

---

## 1. 模块功能规格

### 1.1 模块一：参数知识库（Data Layer）

**职责**：维护结构化的产品参数数据库，为上层分析提供数据支撑。

**输入**：无（系统内置数据）。

**数据范围**：
- 竞品厂商：希沃（SEEWO）、鸿合（HiteVision）、海康威视（HIKVISION）
- 讯飞自身产品：讯飞智慧黑板系列
- 每家 15 条核心硬件参数，覆盖 14 个参数分类

**参数分类枚举**：
`显示` / `触控` / `摄像` / `音频` / `护眼` / `无线` / `软件` / `物理` / `连接` / `计算` / `认证` / `AI` / `生态` / `特色`

**接口**：
```
load_competitors(base_dir) → dict[str, dict]   # 加载所有竞品 JSON
load_xunfei(base_dir) → dict                     # 加载讯飞参数 JSON
load_bid(base_dir, filename) → dict              # 加载招标文件 JSON
save_json(data, filepath) → None                 # 保存 JSON 文件
```

---

### 1.2 模块二：招标文件解析（Parser Input）

**职责**：将招标文件（PDF/Word/Excel）转化为归一化的结构化参数列表。

**支持的输入格式**：
- PDF（含扫描件 OCR，由 MinerU 提供解析能力）
- Word（.docx / .doc）
- Excel（.xlsx / .xls）

**处理步骤**：
1. 自动识别文件格式（magic bytes / 扩展名）
2. 提取参数文本（表格行 / 编号列表 / 段落中的参数声明）
3. 识别参数标记：
   - ★ 星号 → `star_mark: true`（废标项，不满足直接出局）
   - △ 三角 → `triangle_mark: true`（扣分项，不满足扣分但不废标）
   - ◆ 菱形 → `cert_required: true`（需提供检测报告/证明材料）
4. 归一化为统一 JSON 结构（见 §2.2）

**Demo 实现状态**：Demo 阶段跳过文件解析，直接使用预制的 `sample-bid.json`。文件解析（MinerU 集成）为后续迭代内容。

---

### 1.3 模块三：控标方识别 / 横向对比（Matcher — Layer 2）

**职责**：判定招标文件中哪些参数是"独有特征"——市面上仅某一家厂商能满足的规格，从而推断控标方。

**算法**（纯程序，不调 AI）：

```
输入：招标参数列表 B，竞品数据库 {厂商名: [参数列表]}
输出：{控标方, 置信度, 各厂商命中数, 独有特征清单, 异常项清单}

for each bid_item in B:
    satisfied_by = []
    for each (vendor_name, vendor_params) in 竞品数据库:
        if find_best_match(bid_item, vendor_params) → status == 'positive':
            satisfied_by.append(vendor_name)

    if len(satisfied_by) == 1:
        该厂商独有特征命中数 += 1
        记录命中详情
    elif len(satisfied_by) == 0:
        标记为异常（所有厂商均不满足）

置信度 = 总命中数 / (总参数数 - 异常数)
控标方 = argmax(各厂商命中数)
```

**置信度解读阈值**：

| 命中率 | 结论 | 行动建议 |
|--------|------|---------|
| > 60% | 高度可疑 | 强烈指向某一家，可启动质询流程 |
| 30-60% | 部分倾向 | 可能混合控标，需逐条分析 |
| < 30% | 无明显倾向 | 标书较公正，正常投标即可 |

---

### 1.4 模块四：参数匹配 / 纵向对比（Parser + Advisor — Layer 1 + 3）

**职责**：将招标要求逐条与讯飞产品参数对比，判定正偏离或负偏离。采用双层架构。

#### Layer 1：程序粗筛

| 匹配类型 | 方法 | 适用范围 |
|----------|------|---------|
| 数值直接比较 | 正则提取数字 + 单位 → 比大小 | 有明确数值+单位的参数 |
| 单位归一化 | 映射表统一单位后比较 | 同义不同名的单位（4K = 3840×2160） |
| 关键词匹配 | Jaccard bigram 相似度 > 0.5 | 文本描述型参数 |
| 指标组匹配 | 逐 indicator 按 name+unit 比对 | 复合参数（一条含多个子指标） |

```
quick_match(bid_item, our_param) → ('positive'|'negative'|'uncertain', detail)

Step A: 尝试 indicators[] 级别匹配（compare_indicators）
Step B: 尝试从 requirement/spec 文本提取数值比较（extract_numeric）
Step C: 关键词 bigram 相似度兜底（keyword_overlap）
```

#### Layer 2/3 分界规则

| 条件 | 走哪层 |
|------|--------|
| indicators 匹配成功（全部子指标满足） | Layer 1 → 直接判定 positive |
| indicators 匹配失败（0 匹配） | Layer 1 → 直接判定 negative |
| indicators 部分匹配 / 关键词相似度 0.3-0.5 | Layer 3 → 送 AI 精判 |
| 纯功能/软件描述，无 indicators 可提取 | Layer 3 → 送 AI 精判 |

#### Layer 3：AI 语义精判

**调用方式**：所有 uncertain 参数打包为 1 次批量请求（禁止逐条串行）。

**Prompt 结构**：
1. System prompt：招投标参数分析专家角色
2. 讯飞参数全量目录（供 AI 纠正程序错配）
3. 逐条参数对比请求
4. 要求 JSON 数组输出（{seq, match, deviation, explanation, suggestion}）

**输出分类**：

| 类型 | 标记 | 含义 | 下一步 |
|------|------|------|--------|
| `positive` | 🟢 正偏离 | 讯飞规格 ≥ 招标要求 | 标注优势 |
| `negative_wording` | 🟡 负偏离（可改） | 能力有但描述不同 | 改写参数说辞 |
| `negative_real` | 🔴 负偏离（真不满足） | 确实达不到 | 生成应对建议 |

**降级方案**：API 超时 30s 或调用失败 → 自动读取 `data/samples/demo-result.json`（上次成功调用的缓存）。

---

### 1.5 模块五：应对建议生成（Advisor — Layer 3 子功能）

**职责**：针对负偏离项，按优先级自动生成应对策略。

| 优先级 | 策略 | 适用场景 | 示例 |
|--------|------|---------|------|
| P0 | 改说辞 | 讯飞有能力，但参数文档描述不同 | "无线投屏" → "屏幕镜像" |
| P1 | 质疑话术 | 讯飞确实不满足 | 从教学实用性/生态完整性/法规标准三个角度生成 |
| P2 | 渠道协调 | 无法通过改说辞或质疑解决 | 联系招标代理机构、寻求联合体投标 |

**质疑话术三维度**：
1. **教学场景实用性**：该参数在日常教学中是否必要？是否过度规格？
2. **生态与功能完整性**：单一参数不达标不代表整体方案差，讯飞在其他维度有补偿优势
3. **法规与标准依据**：现行国标/行标是否有此强制要求？是否违反公平竞争原则？

---

## 2. 数据格式契约（JSON Schema）

> ⚠️ **这是产品组和开发组的共同契约。格式不统一 = 引擎读不到数据 = Demo 跑不起来。**

### 2.1 竞品 / 讯飞参数 JSON

```json
{
  "vendor": "厂商全称（如：鸿合（HiteVision））",
  "product": "产品型号（如：智慧黑板 HB-H868S）",
  "category": "产品品类（如：智慧黑板）",
  "updated": "数据更新日期（如：2026-07）",
  "params": [
    {
      "id": "唯一标识（如：HH-001），格式：厂商缩写-序号",
      "category": "参数分类（显示/触控/摄像/音频/护眼/无线/软件/物理/连接/计算/认证/AI/生态/特色）",
      "name": "参数名称（人可读）",
      "spec": "原始描述文本（从源文档直接复制）",
      "indicators": [
        {
          "name": "子指标名称",
          "value": "数值或布尔值",
          "unit": "单位（px/inch/cd_m2/watt/mp/mm/gb/count/touch_points/pressure_level/degree/pct/hour/platform_count/feature/cert/spec/type/second）",
          "comparator": "比较方式：eq/gte/lte/gt/lt"
        }
      ],
      "star_mark": "是否为★废标项：true/false",
      "cert_required": "是否需提供检测报告：true/false"
    }
  ]
}
```

**关键规则**：
1. 每个参数必须有 `indicators` 数组——即使是简单参数（单值），也用数组包一层
2. `indicators[].value` 可以是数字或布尔值——数值型填数字，特征型填 `true`/`false`
3. `comparator` 决定匹配方向——`gte` = 值 ≥ 招标要求才算满足
4. `spec` 必须保留原始文本——供 AI 语义匹配时参考，不能省略

### 2.2 招标参数 JSON（解析器输出）

```json
{
  "project": "项目名称",
  "date": "招标日期",
  "items": [
    {
      "seq": 1,
      "category": "参数分类",
      "name": "参数名称",
      "requirement": "原始招标要求文本",
      "indicators": [
        {"name": "子指标名", "value": "数值", "unit": "单位", "comparator": "比较方式"}
      ],
      "star_mark": false,
      "triangle_mark": true
    }
  ]
}
```

### 2.3 分析结果 JSON（最终输出）

```json
{
  "project": "项目名称",
  "controller": {
    "vendor": "控标方厂商全称",
    "confidence": 0.55,
    "scores": {"希沃": 2, "鸿合": 1, "海康威视": 6},
    "hits": [{"seq": 1, "param_name": "摄像头", "hit_vendor": "海康威视"}],
    "anomalies": [{"seq": 9, "param_name": "参数名", "reason": "所有厂商均不满足"}]
  },
  "matching": [
    {
      "seq": 1,
      "category": "参数分类",
      "name": "参数名称",
      "bid_req": "招标要求原文",
      "xunfei_spec": "讯飞对应参数原文",
      "deviation": "positive | negative_wording | negative_real",
      "match_method": "program | ai_semantic",
      "detail": "匹配详情说明",
      "suggestion": "应对建议文本（正偏离时为 null）"
    }
  ],
  "summary": {
    "total": 12,
    "positive": 8,
    "negative_wording": 2,
    "negative_real": 2
  }
}
```

---

## 3. 引擎流水线规格

### 3.1 完整执行流程

```
run_analysis(bid_filename)
    │
    ├── Step 1: 加载数据
    │   load_competitors() → {xiwo, honghe, haikang}
    │   load_xunfei()      → {vendor, params[15]}
    │   load_bid()          → {items[12]}
    │
    ├── Step 2: Layer 2 — 控标识别
    │   identify_controller(bid.items, competitors)
    │   → {vendor, confidence, hits[6], anomalies[1]}
    │
    ├── Step 3: Layer 1 — 逐条程序匹配
    │   for each bid_item:
    │       find_best_match(bid_item, xunfei.params)
    │       → positive → 直接入 matching[]
    │       → negative → 入 matching[] + 标记送 AI 生成建议
    │       → uncertain → 入 uncertain_items[] 待 AI 批量处理
    │
    ├── Step 4: Layer 3 — AI 批量精判
    │   batch_analyze(uncertain_items, xunfei.params)
    │   → 合并 AI 结果到 matching[]
    │
    └── Step 5: 汇总输出
        matching.sort(by seq)
        summary = {total, positive, negative_wording, negative_real}
        return {project, controller, matching, summary}
```

### 3.2 性能指标

| 指标 | 目标值 | 实际值（当前） |
|------|--------|---------------|
| 数据加载 | < 100ms | ~10ms |
| Layer 1 程序匹配（12 条） | < 500ms | ~50ms |
| Layer 2 控标识别（12 条 × 3 家） | < 500ms | ~100ms |
| Layer 3 AI 批量调用 | < 10s | ~5s（DeepSeek v4-flash） |
| **端到端总耗时** | **< 10s** | **~5s** |

---

## 4. 非功能性需求

| 需求 | 标准 |
|------|------|
| 响应速度 | 单次分析（含 AI 调用）≤ 10 秒 |
| 数据安全 | 招标文件处理在本地完成，不上传至第三方 |
| 可用性 | Web 页面（Streamlit），浏览器打开即用 |
| 可扩展性 | 新增竞品厂商只需添加 JSON 文件，无需改代码 |
| 降级能力 | AI API 不可用时自动读取缓存结果，系统不崩溃 |
| 编码兼容 | Windows GBK 环境兼容（避免 emoji 等特殊字符） |

---

## 5. Out of Scope（明确不做）

| 项目 | 原因 |
|------|------|
| 招标评分自动计算 | 超出课题范围，且评分规则各项目不同 |
| 全行业厂商数据库 | 比赛 Demo 只需 3 家，4 天做不完 |
| 用户登录/权限系统 | Demo 场景不需要 |
| 历史记录持久化 / 报告导出 | Demo 以实时展示为主 |
| 移动端适配 | Web 端已满足演示需求 |
| 参数自动抓取/更新（爬虫） | 非 Demo 范围 |
| 文件上传解析（MinerU） | Demo 使用预制 JSON，解析作为后续迭代 |
