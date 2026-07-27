# 路演 PPT“规范流程”页字号调整 Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** 放大“规范流程”页 10 个工程文档卡片的文字并填充底部留白，同时保持 5 行两列结构和现有视觉体系。

**Architecture:** 继续使用现有单文件 HTML/CSS。仅调整 `presentations/路演PPT.html` 中文档体系页共用的 `.doc-grid`、`.doc-item`、`.doc-no`、`.doc-cn`、`.doc-en` 和 `.doc-flag` 样式，不改变 DOM 结构或其他页面内容。

**Tech Stack:** HTML、CSS、Git、浏览器回归检查。

## Global Constraints

- 保持“规范流程”页为 5 行两列，共 10 个文档卡片。
- 保持 1920×1200 页面画布内无越界、裁切或意外换行。
- 保持现有页眉、蓝色配色、卡片圆角、阴影与边框体系。
- 仅修改与本页文档卡片排版直接相关的样式和工程记录。

---

### Task 1: 记录并核对目标样式

**Files:**
- Read: `presentations/路演PPT.html:175-185`
- Read: `docs/superpowers/specs/2026-07-27-roadshow-doc-grid-typography-design.md`

**Interfaces:**
- Consumes: 已批准的字号与间距设计。
- Produces: 可直接核对的目标值清单。

- [ ] **Step 1: 核对当前文档体系 CSS**

确认目标选择器当前分别控制网格行间距、卡片上下内边距、编号、中文标题、英文副标题和右侧标记。

- [ ] **Step 2: 核对页面结构**

确认目标页包含 10 个 `.doc-item`，且没有需要单独改写的第三列或额外底部元素。

### Task 2: 修改文档卡片字号和纵向间距

**Files:**
- Modify: `presentations/路演PPT.html:176-184`

**Interfaces:**
- Consumes: Task 1 的选择器与结构核对结果。
- Produces: 10 个卡片使用统一放大后的排版样式。

- [ ] **Step 1: 调整网格和卡片纵向占用**

将 `.doc-grid` 的行间距从 `22px` 改为 `26px`，将 `.doc-item` 的上下内边距从 `22px` 改为 `28px`，保留左右间距 `40px` 和左右内边距 `30px`。

- [ ] **Step 2: 调整四类文字字号**

将 `.doc-no` 改为 `46px`、`.doc-cn` 改为 `32px`、`.doc-en` 改为 `22px`、`.doc-flag` 改为 `24px`，保留现有颜色、字重和行高规则。

- [ ] **Step 3: 检查差异范围**

运行 `git diff -- presentations/路演PPT.html`，确认差异仅涉及目标文档卡片样式，没有修改其他页面结构或内容。

### Task 3: 浏览器回归与边界验证

**Files:**
- Test: `presentations/路演PPT.html`

**Interfaces:**
- Consumes: Task 2 的 HTML/CSS 修改。
- Produces: 1920×1200 下的页面边界与元素字号验证结果。

- [ ] **Step 1: 打开本地路演 HTML**

通过浏览器打开 `presentations/路演PPT.html`，定位“规范流程”页并读取其 `.doc-grid`、`.doc-item` 与文字元素的实际边界。

- [ ] **Step 2: 验证结构和边界**

确认 `.doc-item` 数量为 10、每个卡片的底部不超过 1200px，且 `.doc-cn`、`.doc-en`、`.doc-no` 和 `.doc-flag` 的 computed font-size 分别为 `32px`、`22px`、`46px` 和 `24px`。

- [ ] **Step 3: 验证回归约束**

确认页眉数量仍为 9，“现场演示”页仍没有页眉，且目标页没有水平溢出或文本裁切。

### Task 4: 提交并同步 master

**Files:**
- Modify: `presentations/路演PPT.html`
- Create: `docs/superpowers/specs/2026-07-27-roadshow-doc-grid-typography-design.md`
- Create: `docs/superpowers/plans/2026-07-27-roadshow-doc-grid-typography.md`

**Interfaces:**
- Consumes: Task 3 的验证结果。
- Produces: GitHub `master` 上可追溯的单次提交。

- [ ] **Step 1: 运行静态检查**

运行 `git diff --check` 并确认退出码为 0。

- [ ] **Step 2: 检查 Git 状态和差异**

运行 `git status --short` 与 `git diff --stat`，确认只包含本任务涉及的三个文件。

- [ ] **Step 3: 提交修改**

运行 `git add -- presentations/路演PPT.html docs/superpowers/specs/2026-07-27-roadshow-doc-grid-typography-design.md docs/superpowers/plans/2026-07-27-roadshow-doc-grid-typography.md`，然后提交：

```bash
git commit -m "style: enlarge roadshow document grid typography"
```

- [ ] **Step 4: 推送并确认同步**

运行 `git push origin master`，随后运行 `git status --short --branch` 和 `git rev-parse HEAD origin/master`，确认工作区干净且两者指向同一提交。
