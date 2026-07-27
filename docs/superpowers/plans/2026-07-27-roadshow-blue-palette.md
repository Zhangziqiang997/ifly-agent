# 路演 PPT 品牌蓝配色 Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:executing-plans (or inline execution with the same checkpoints) to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** 将路演 PPT 从紫粉渐变统一为品牌蓝主导、白灰中性底、青绿/橙色承担语义提示的配色，同时保留现有页面结构和内容。

**Architecture:** 只修改 `presentations/路演PPT.html` 的内嵌 CSS，不调整页面 DOM、文案、脚本或 SVG 架构图。先增加颜色 token，再按封面、Demo/结尾、卡片、数据/风险、占位页五类组件映射颜色，最后通过静态断言和浏览器截图检查视觉结果。

**Tech Stack:** HTML/CSS、PowerShell 静态检查、Codex in-app Browser 本地渲染检查。

## Global Constraints

- 保留其他人的页面内容改动，配色分支不得修改新增页面结构或文案。
- 品牌蓝估值使用 `#168BEA`、`#39B7E8`、`#0B315B`；页面背景保持白色/浅灰蓝。
- 紫色和粉色不再作为主色；蓝色只用于品牌和重点信息，橙色/青绿色保留语义区分。
- 所有变更必须先在独立分支 `codex-roadshow-blue-palette` 中完成并提交，再尝试合并回用户当前分支。

---

### Task 1: 建立品牌色 token 并替换全局基础色

**Files:**
- Modify: `presentations/路演PPT.html:10-110`

- [ ] 增加 `:root` 颜色变量，覆盖品牌蓝、深蓝、文字、背景、边框、成功和警告色。
- [ ] 将 `body`、`.slide`、`.page-tag`、`.doc-badge`、`.grad-text`、封面标题/来源框/痛点图标映射到新 token。
- [ ] 保留白色卡片、深灰正文和低透明度阴影，避免蓝色铺满页面。
- [ ] 静态检查目标文件不存在旧主色 `#7c3aed`、`#a855f7`、`#ec4899`、`#f472b6` 的 CSS 使用。

### Task 2: 调整深色演示页、数据组件和语义色

**Files:**
- Modify: `presentations/路演PPT.html:113-233,517`

- [ ] 将 `.slide-demo` 和 `.slide-end` 改为深蓝到品牌蓝渐变，保留白色标题和浅蓝提示文字。
- [ ] 将文档列表、团队角色、甘特图、PRD 对比、架构原则、人机协作等组件按“蓝色主信息、青绿色成功/协作、橙色风险/人工判断”映射。
- [ ] 将浅紫背景改为浅灰蓝/淡蓝；将现有粉色强调改为橙色或青绿色，不改变风险颜色本身的语义。
- [ ] 将技术页的内联背景同步为白色到浅灰蓝渐变；不修改 `output/arch-three-layer.svg`。

### Task 3: 静态检查、浏览器渲染和提交

**Files:**
- Modify: `presentations/路演PPT.html`

- [ ] 用 PowerShell 检查 HTML 仍包含全部 `.slide`、脚本关键字和架构图引用，确认没有误改结构。
- [ ] 在浏览器中打开独立 worktree 的 HTML，检查封面、Demo、技术页、人机协作页和结尾页的配色与可读性。
- [ ] 查看 `git diff --check` 和完整 diff，确认只修改配色相关内容。
- [ ] 提交分支，提交信息为 `style: align roadshow deck with brand blue palette`。

### Task 4: 合并回用户当前分支

**Files:**
- Merge: `codex-roadshow-blue-palette` into the branch active in the original worktree

- [ ] 合并前重新检查原工作区的未提交 diff；如果对方在目标 HTML 继续产生修改，优先停在合并前报告冲突风险。
- [ ] 若工作区状态允许，合并分支并解决仅由颜色行造成的冲突，保留对方新增的页面内容。
- [ ] 合并后再次执行 `git diff --check`、静态结构检查和最终 diff 审核。
