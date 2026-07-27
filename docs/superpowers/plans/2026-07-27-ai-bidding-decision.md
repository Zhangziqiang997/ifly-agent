# AI 投标决策中心静态页 Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** 构建一个能直接在浏览器打开的高保真 AI 投标决策中心演示页面。

**Architecture:** 页面放在独立目录中；HTML 提供语义化模块，CSS 完成固定桌面宽屏布局与图形化视觉元素，JavaScript 保存展示数据并提供最小的演示反馈。页面不依赖后端、框架或外部资源。

**Tech Stack:** HTML5、CSS3、原生 JavaScript。

## Global Constraints

- 创建 `ai-bidding-decision/`，不修改仓库现有原型文件。
- 无构建工具、无外部依赖；`index.html` 可直接打开。
- 目标截图尺寸为 1680×940，优先桌面端视觉一致性。
- 这是一次性静态演示；采用浏览器视觉校验代替自动化单元测试。

---

### Task 1: 页面骨架与内容

**Files:**
- Create: `ai-bidding-decision/index.html`
- Create: `ai-bidding-decision/app.js`

**Interfaces:**
- Consumes: `uiData`，包含导航标签、统计数值与演示提示。
- Produces: 带 `data-section` 标记的 sidebar、topbar、knowledge、risk、report、shortcuts、results 和 capabilities 区块。

- [ ] **Step 1:** 创建语义化页面骨架与完整中文展示文案。
- [ ] **Step 2:** 在 `app.js` 中声明 `uiData` 并为 `.demo-action` 添加点击提示，不请求网络。

### Task 2: 视觉实现

**Files:**
- Create: `ai-bidding-decision/styles.css`

**Interfaces:**
- Consumes: `index.html` 的 class、图标文字和 data 标记。
- Produces: 1680px 设计基准上的双栏布局、卡片、按钮、流程箭头、数据标签与响应式缩放。

- [ ] **Step 1:** 定义颜色、阴影、边框和字体的 CSS 变量。
- [ ] **Step 2:** 实现左侧导航、顶部工具栏、上方三卡和底部两栏面板。
- [ ] **Step 3:** 在较窄窗口保持内容可读，并避免 1680px 基准下横向溢出。

### Task 3: 浏览器验收

**Files:**
- Verify: `ai-bidding-decision/index.html`

**Interfaces:**
- Consumes: 1680×940 Chromium 页面截图。
- Produces: 可视化确认结果。

- [ ] **Step 1:** 在浏览器打开页面，确认中文内容、布局与视觉层级加载正确。
- [ ] **Step 2:** 截图检查左右栏比例、三列卡片、按钮、表格和页面无水平滚动。
- [ ] **Step 3:** 修复任何影响参考图一致性的布局问题后重新检查。
