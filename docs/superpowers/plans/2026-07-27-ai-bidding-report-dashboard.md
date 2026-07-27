# AI 投标分析报告驾驶舱 Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development or superpowers:executing-plans. Steps use checkbox (\`- [ ]\`) syntax.

**Goal:** 把固定报告升级为带 KPI、证据、分类图、筛选和行级行动建议的蓝白驾驶舱。

**Architecture:** \`report-data.mjs\` 提供固定逐项数据与纯聚合/筛选函数；\`report.js\` 以安全 DOM API 渲染并维护当前筛选状态；HTML/CSS 只承担结构与蓝白视觉。

**Tech Stack:** 原生 HTML/CSS/JavaScript ES Modules、Node.js \`node:test\`。

## Global Constraints

- 仅修改 \`ai-bidding-decision/\`；保留蓝白主风格和固定 mock。
- 不使用第三方依赖或后端；不得将数据插入 \`innerHTML\`。
- 保留“145°/135°”风险证据，四个筛选必须即时生效。

---

### Task 1: 扩展可测试的报告模型

**Files:** Modify \`report-data.mjs\`; Modify/Create \`tests/report-data.test.mjs\`.

- [ ] 先添加失败测试，断言总参数、正偏离、可改说辞、真负偏离，类别分布和按 \`all|positive|wording|negative\` 筛选结果。
- [ ] 实现 \`getDashboardMetrics(report)\`、\`getCategoryDistribution(report)\`、\`filterAnalysisItems(report, filter)\`，并为每项提供类别、招标要求、讯飞规格、偏离、来源、优先级、风险解释和行动建议。
- [ ] 运行 \`node --test ai-bidding-decision/tests/report-data.test.mjs\`。

### Task 2: 渲染驾驶舱和行级闭环

**Files:** Modify \`report.html\`; Modify \`report.js\`; Modify \`styles.css\`; Modify/Create \`tests/report-contract.test.mjs\`.

- [ ] 先添加失败契约测试，断言四 KPI、控标证据、分类图、筛选区和详情行容器存在。
- [ ] 将 Hero 下方改为四 KPI；增加控标证据清单与 SVG/CSS 分类分布图。
- [ ] 渲染四个可访问筛选按钮；点击后重绘表格和计数。
- [ ] 将表格升级为类别、招标要求、讯飞规格、判定、来源/优先级和行动；负偏离行有可展开详情。
- [ ] 使用 \`createElement/textContent\` 渲染全部动态内容，运行报告测试和语法检查。

### Task 3: 审查与验证

**Files:** Modify \`README.md\` only if the report interaction description becomes inaccurate.

- [ ] 运行 \`node --test ai-bidding-decision/tests/*.test.mjs\`、\`node --check ai-bidding-decision/report.js\`、\`node --check ai-bidding-decision/report-data.mjs\`。
- [ ] 审查蓝白色彩、筛选、展开状态和证据闭环；修复 Important 级问题。

