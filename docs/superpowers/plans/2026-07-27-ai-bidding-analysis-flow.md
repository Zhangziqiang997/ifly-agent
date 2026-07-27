# AI 投标决策中心演示分析闭环 Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (\`- [ ]\`) syntax for tracking.

**Goal:** 在静态 AI 投标决策中心中实现 PDF 模拟入库、10 秒 AI 分析和固定分析报告闭环。

**Architecture:** 首页通过状态对象独立管理上传和分析流程；PDF 只用于文件类型和名称展示。报告页从 ES module 读取固定数据，以 DOM API 安全渲染，并复用现有蓝色体系。

**Tech Stack:** HTML5、CSS3、原生 JavaScript ES Modules、Node.js 内置 \`node:test\`。

## Global Constraints

- 只修改 \`ai-bidding-decision/\`，不修改 \`kc_aiHackson\`。
- 仅允许 \`.pdf\`，不读取、不上传、不真实解析文件。
- 上传固定 3 秒、AI 分析固定 10 秒；报告只在分析完成后可打开。
- 报告数据固定；动态文本使用 \`textContent\`；无第三方依赖。

---

### Task 1: 固化报告数据与汇总

**Files:**
- Create: \`ai-bidding-decision/report-data.mjs\`
- Create: \`ai-bidding-decision/tests/report-data.test.mjs\`

**Interfaces:**
- Produces: \`analysisReport\`，字段为 \`project\`、\`controller\`、\`items\`。
- Produces: \`getReportMetrics(report)\`，返回 \`{ positiveCount, negativeCount, wordingCount, riskCount }\`。

- [ ] **Step 1: 写出失败测试**

\`\`\`js
import test from 'node:test';
import assert from 'node:assert/strict';
import { analysisReport, getReportMetrics } from '../report-data.mjs';

test('固定报告汇总与偏离项一致', () => {
  const metrics = getReportMetrics(analysisReport);
  assert.equal(analysisReport.controller.confidence, 0.92);
  assert.equal(metrics.positiveCount, 4);
  assert.equal(metrics.negativeCount, 2);
  assert.equal(metrics.riskCount, 2);
});
\`\`\`

- [ ] **Step 2: 验证测试失败**

Run: \`node --test ai-bidding-decision/tests/report-data.test.mjs\`  
Expected: FAIL，模块不存在。

- [ ] **Step 3: 实现数据模块**

\`\`\`js
export const analysisReport = {
  project: '智慧教室采购需求（演示）',
  controller: { vendor: '希沃', confidence: 0.92 },
  items: [{ deviation: 'positive' }, { deviation: 'negative_real' }]
};

export function getReportMetrics(report) {
  const items = report.items;
  return {
    positiveCount: items.filter((item) => item.deviation === 'positive').length,
    negativeCount: items.filter((item) => item.deviation === 'negative_real').length,
    wordingCount: items.filter((item) => item.deviation === 'negative_wording').length,
    riskCount: items.filter((item) => item.deviation === 'negative_real').length
  };
}
\`\`\`

- [ ] **Step 4: 验证通过并提交**

Run: \`node --test ai-bidding-decision/tests/report-data.test.mjs\`  
Expected: PASS。

\`\`\`bash
git add ai-bidding-decision/report-data.mjs ai-bidding-decision/tests/report-data.test.mjs
git commit -m "feat: add fixed bidding report data"
\`\`\`

### Task 2: 实现首页演示状态机

**Files:**
- Modify: \`ai-bidding-decision/index.html\`
- Modify: \`ai-bidding-decision/app.js\`
- Modify: \`ai-bidding-decision/styles.css\`
- Create: \`ai-bidding-decision/tests/home-contract.test.mjs\`

**Interfaces:**
- Consumes: \`#document-input\`、\`#upload-trigger\`、\`#upload-status\`、\`#analysis-trigger\`、\`#report-trigger\`。
- Produces: \`window.AIBiddingDemo.validatePdfFile(file)\`；上述节点的演示状态。

- [ ] **Step 1: 写出失败的首页契约测试**

\`\`\`js
import test from 'node:test';
import assert from 'node:assert/strict';
import { readFile } from 'node:fs/promises';

test('首页具备上传、分析与禁用报告入口', async () => {
  const html = await readFile(new URL('../index.html', import.meta.url), 'utf8');
  assert.match(html, /id="document-input"[^>]*accept="\\.pdf,application\\/pdf"/);
  assert.match(html, /id="analysis-trigger"/);
  assert.match(html, /id="report-trigger"[^>]*disabled/);
});
\`\`\`

- [ ] **Step 2: 验证测试失败**

Run: \`node --test ai-bidding-decision/tests/home-contract.test.mjs\`  
Expected: FAIL，首页没有这些节点。

- [ ] **Step 3: 写入状态驱动控件和逻辑**

\`\`\`html
<input id="document-input" type="file" accept=".pdf,application/pdf" hidden />
<button id="upload-trigger" type="button">上传 PDF</button>
<p id="upload-status" aria-live="polite">可上传 PDF 补充参数知识库</p>
<button id="analysis-trigger" type="button">开始 AI 分析</button>
<button id="report-trigger" type="button" disabled>查看文档 AI 分析报告</button>
\`\`\`

在 \`app.js\` 建立 \`demoState = { uploadStatus: 'idle', analysisStatus: 'idle' }\`。选择非 PDF 时 Toast 提示且状态不变；合法 PDF 用 3,000 ms 计时更新为“参数已进入知识库”。点击分析用 10,000 ms 计时更新为完成、移除报告按钮 \`disabled\`，报告按钮跳转 \`report.html\`。

- [ ] **Step 4: 写入状态样式并验证**

\`\`\`css
.flow-status.is-running { color: #1670ef; }
.flow-status.is-complete { color: #15945d; }
.report-btn:disabled { color: #9aa9bb; background: #edf1f5; border-color: #edf1f5; cursor: not-allowed; }
\`\`\`

Run: \`node --test ai-bidding-decision/tests/home-contract.test.mjs; node --check ai-bidding-decision/app.js\`  
Expected: PASS 且无语法错误。

### Task 3: 新建蓝色报告页

**Files:**
- Create: \`ai-bidding-decision/report.html\`
- Create: \`ai-bidding-decision/report.js\`
- Modify: \`ai-bidding-decision/styles.css\`
- Create: \`ai-bidding-decision/tests/report-contract.test.mjs\`

**Interfaces:**
- Consumes: \`analysisReport\` 与 \`getReportMetrics\`（来自 \`report-data.mjs\`）。
- Produces: \`#report-summary\`、\`#risk-list\`、\`#report-table-body\`。

- [ ] **Step 1: 写出失败的报告契约测试**

\`\`\`js
import test from 'node:test';
import assert from 'node:assert/strict';
import { readFile } from 'node:fs/promises';

test('报告页加载模块化数据并具有关键容器', async () => {
  const html = await readFile(new URL('../report.html', import.meta.url), 'utf8');
  assert.match(html, /id="report-summary"/);
  assert.match(html, /id="report-table-body"/);
  assert.match(html, /src="report\\.js" type="module"/);
});
\`\`\`

- [ ] **Step 2: 验证测试失败**

Run: \`node --test ai-bidding-decision/tests/report-contract.test.mjs\`  
Expected: FAIL，报告页不存在。

- [ ] **Step 3: 编写安全报告渲染和样式**

\`\`\`js
import { analysisReport, getReportMetrics } from './report-data.mjs';

function appendTextCell(row, value) {
  const cell = document.createElement('td');
  cell.textContent = value;
  row.append(cell);
}
\`\`\`

渲染 92% 置信度、可疑项说明、正/负偏离指标卡、风险清单、参数对比表与应对建议；返回按钮指向 \`index.html\`。CSS 追加 \`.report-layout\`、\`.summary-card\`、\`.deviation-negative\`、\`.deviation-positive\`，延续首页蓝白卡片风格。

- [ ] **Step 4: 验证并提交**

Run: \`node --test ai-bidding-decision/tests/report-contract.test.mjs ai-bidding-decision/tests/report-data.test.mjs; node --check ai-bidding-decision/report.js\`  
Expected: PASS 且无语法错误。

\`\`\`bash
git add ai-bidding-decision/report.html ai-bidding-decision/report.js ai-bidding-decision/report-data.mjs ai-bidding-decision/tests ai-bidding-decision/styles.css
git commit -m "feat: add bidding analysis report flow"
\`\`\`

### Task 4: 更新交接说明与端到端验收

**Files:**
- Modify: \`ai-bidding-decision/README.md\`

**Interfaces:**
- Consumes: 首页和报告页最终交互。
- Produces: 后续前端可替换的模拟边界和验收步骤。

- [ ] **Step 1: 更新 README**

加入以下闭环说明：\`PDF 上传（3 秒模拟解析） → 参数进入知识库提示 → 开始 AI 分析（10 秒） → 查看固定 AI 分析报告\`。明确 PDF 未真实读取/上传，报告为固定 mock；联调时将定时器替换为上传与任务轮询接口。

- [ ] **Step 2: 完整验证和手工验收**

Run: \`node --test ai-bidding-decision/tests/*.test.mjs; node --check ai-bidding-decision/app.js; node --check ai-bidding-decision/report.js\`  
Expected: 全部 PASS。

手工检查：PDF 3 秒后入库提示；非 PDF 不解析；10 秒前报告按钮禁用、之后可进入报告页；报告有 92% 置信度、145° 风险、正/负偏离和建议，且为蓝色体系。

- [ ] **Step 3: 提交文档**

\`\`\`bash
git add ai-bidding-decision/README.md
git commit -m "docs: describe analysis demo flow"
\`\`\`

