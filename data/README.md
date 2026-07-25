# 数据层 — JSON Schema 规范（v3.0）

> ⚠️ **本文档是产品组和开发组的共同契约。**  
> 产品组从知识库3提取真实参数时，严格按此格式输出 JSON。  
> 开发组写 Parser/Matcher 时，严格按此格式读取 JSON。  
> **两组格式不统一 = 引擎读不到数据 = Demo 跑不起来。**

---

## 目录结构

```
data/
├── competitors/            # 竞品参数库（每个 JSON 一个厂商）
│   ├── xiwo.json           # 希沃 — Mock 数据，待替换为真实参数
│   ├── honghe.json         # 鸿合 — Mock 数据，待替换为真实参数
│   ├── wenxiang.json       # 文香 — Mock 数据（真实竞品为海康威视，此文件仅供开发测试）
│   └── haikang.json        # 海康 — ⬜ 待产品组创建（从知识库3/海康/ 提取）
├── xunfei/
│   └── xunfei.json         # 讯飞 — Mock 数据，待替换为真实参数
├── samples/
│   └── sample-bid.json     # 样例招标文件 — ⬜ 待产品组创建
└── README.md               # ← 本文件，Schema 规范
```

---

## 竞品/讯飞参数 JSON Schema

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
      "name": "参数名称（人可读，如：屏幕分辨率）",
      "spec": "原始描述文本（从源文档直接复制）",
      "indicators": [
        {
          "name": "子指标名称（如：水平分辨率）",
          "value": "数值或布尔值（如：3840 或 true）",
          "unit": "单位（px/inch/cd_m2/watt/mp/mm/gb/count/touch_points/pressure_level/degree/pct/hour/platform_count/feature/cert/spec/type/second）",
          "comparator": "比较方式：eq（等于）/ gte（大于等于）/ lte（小于等于）/ gt（大于）/ lt（小于）"
        }
      ],
      "star_mark": "是否为★废标项：true/false",
      "cert_required": "是否需要提供检测报告/证明材料：true/false"
    }
  ]
}
```

### 关键规则

1. **每个参数必须有 `indicators` 数组**——即使是简单参数（单个数值），也用数组包一层
2. **`indicators[].value` 可以是数字或布尔值**——数值型填数字，特征型填 `true`/`false`
3. **`comparator` 决定匹配方向**——`gte` = 讯飞值 ≥ 招标值才算满足，`lte` = 讯飞值 ≤ 招标值
4. **`spec` 必须保留原始文本**——供 AI 语义匹配时参考，不能丢掉

### 示例：简单参数 vs 复合参数

```json
// 简单参数（单个指标）
{
  "id": "XX-001",
  "category": "显示",
  "name": "屏幕亮度",
  "spec": "500cd/m²",
  "indicators": [
    {"name": "亮度", "value": 500, "unit": "cd_m2", "comparator": "gte"}
  ]
}

// 复合参数（多个指标）
{
  "id": "XX-006",
  "category": "摄像",
  "name": "内置摄像头",
  "spec": "1300万像素（1080P），120°广角",
  "indicators": [
    {"name": "摄像头像素", "value": 1300, "unit": "mp", "comparator": "gte"},
    {"name": "视频分辨率", "value": 1920, "unit": "px", "comparator": "gte"},
    {"name": "视场角", "value": 120, "unit": "degree", "comparator": "gte"}
  ]
}
```

---

## 样例招标文件 JSON Schema

```json
{
  "project": "项目名称（如：XX市教育局智慧教室建设项目）",
  "date": "招标日期（如：2026-07）",
  "items": [
    {
      "seq": 1,
      "category": "参数分类",
      "name": "参数名称",
      "requirement": "招标要求原始文本",
      "star_mark": false,
      "triangle_mark": true
    }
  ]
}
```

---

## 开发组的读取方式

```python
import json

# 加载所有竞品
competitors = {}
for vendor in ["xiwo", "honghe", "wenxiang", "haikang"]:
    try:
        with open(f"data/competitors/{vendor}.json", "r", encoding="utf-8") as f:
            competitors[vendor] = json.load(f)
    except FileNotFoundError:
        pass  # 文件不存在就跳过（海康还没建好时不会崩）

# 加载讯飞
with open("data/xunfei/xunfei.json", "r", encoding="utf-8") as f:
    xunfei = json.load(f)

# 加载招标文件
with open("data/samples/sample-bid.json", "r", encoding="utf-8") as f:
    bid = json.load(f)

# 遍历方式
for param in competitors["xiwo"]["params"]:
    for indicator in param["indicators"]:
        print(f"{param['name']} / {indicator['name']}: {indicator['comparator']} {indicator['value']} {indicator['unit']}")
```
