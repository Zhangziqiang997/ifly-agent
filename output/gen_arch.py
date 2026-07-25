W, H = 960, 820

lines = []
def L(s):
    lines.append(s)

L('<?xml version="1.0" encoding="UTF-8"?>')
L(f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" width="{W}" height="{H}">')
L('<style>')
L('  text { font-family: "Helvetica Neue", Helvetica, Arial, "PingFang SC", "Microsoft YaHei", "Microsoft JhengHei", "SimHei", sans-serif; }')
L('</style>')
L('<defs>')
L('  <marker id="a-blue" markerWidth="10" markerHeight="7" refX="9" refY="3.5" orient="auto"><polygon points="0 0, 10 3.5, 0 7" fill="#2563eb"/></marker>')
L('  <marker id="a-green" markerWidth="10" markerHeight="7" refX="9" refY="3.5" orient="auto"><polygon points="0 0, 10 3.5, 0 7" fill="#16a34a"/></marker>')
L('  <marker id="a-orange" markerWidth="10" markerHeight="7" refX="9" refY="3.5" orient="auto"><polygon points="0 0, 10 3.5, 0 7" fill="#ea580c"/></marker>')
L('  <marker id="a-purple" markerWidth="10" markerHeight="7" refX="9" refY="3.5" orient="auto"><polygon points="0 0, 10 3.5, 0 7" fill="#7c3aed"/></marker>')
L('  <marker id="a-gray" markerWidth="10" markerHeight="7" refX="9" refY="3.5" orient="auto"><polygon points="0 0, 10 3.5, 0 7" fill="#6b7280"/></marker>')
L('  <marker id="a-teal" markerWidth="10" markerHeight="7" refX="9" refY="3.5" orient="auto"><polygon points="0 0, 10 3.5, 0 7" fill="#0d9488"/></marker>')
L('  <filter id="shadow" x="-5%" y="-5%" width="115%" height="115%"><feDropShadow dx="0" dy="2" stdDeviation="3" flood-opacity="0.08"/></filter>')
L('</defs>')
L(f'<rect width="{W}" height="{H}" fill="#ffffff"/>')

# ══════════ TITLE ══════════
L('<text x="480" y="30" text-anchor="middle" font-size="18" font-weight="600" fill="#111827">参数智能体 — 系统架构图</text>')
L('<text x="480" y="48" text-anchor="middle" font-size="11" fill="#6b7280">AI 驱动的招投标参数智能比对与决策辅助系统 | 文档解析 + 三层对比 + AI 语义精判</text>')

# ══════════ LAYER 0: USER + INPUT ══════════
L('<circle cx="48" cy="88" r="10" fill="none" stroke="#6b7280" stroke-width="1.5"/>')
L('<path d="M 33 109 Q 33 99, 48 99 Q 63 99, 63 109" fill="none" stroke="#6b7280" stroke-width="1.5"/>')
L('<text x="48" y="125" text-anchor="middle" font-size="11" fill="#6b7280">用户</text>')

# Upload input box
L('<rect x="90" y="68" width="140" height="46" rx="8" fill="#f0fdf4" stroke="#86efac" stroke-width="1.5"/>')
L('<text x="160" y="88" text-anchor="middle" font-size="12" font-weight="600" fill="#166534">招标文件上传</text>')
L('<text x="160" y="103" text-anchor="middle" font-size="10" fill="#6b7280">PDF / Word / Excel</text>')
L('<line x1="65" y1="91" x2="82" y2="91" stroke="#6b7280" stroke-width="1.5" marker-end="url(#a-gray)"/>')

# ══════════ LAYER 1: MinerU DOC PARSER ══════════
L('<rect x="250" y="62" width="694" height="58" rx="8" fill="#f0fdfa" stroke="#5eead4" stroke-width="1.5"/>')
L('<text x="266" y="80" font-size="11" font-weight="600" fill="#0f766e">MinerU — 文档解析引擎 (视觉 Pipeline + VLM 双后端)</text>')

# 5 pipeline stages
pw = 118
ps = 8
px_start = 266
py = 92
stages = [
    ("1. 布局检测", "DocLayout-YOLO"),
    ("2. OCR 提取", "PaddleOCR / VLM"),
    ("3. 公式识别", "Unimernet → LaTeX"),
    ("4. 表格识别", "PP-StructureV2"),
    ("5. 排序拼装", "→ Markdown / JSON"),
]
for i, (title, sub) in enumerate(stages):
    x = px_start + i * (pw + ps)
    L(f'<rect x="{x}" y="{py}" width="{pw}" height="20" rx="4" fill="#ccfbf1" stroke="#99f6e4" stroke-width="0.5"/>')
    L(f'<text x="{x+pw/2}" y="{py+8}" text-anchor="middle" font-size="8" fill="#0f766e">{title}</text>')
    L(f'<text x="{x+pw/2}" y="{py+17}" text-anchor="middle" font-size="7" fill="#6b7280">{sub}</text>')

L('<line x1="236" y1="91" x2="242" y2="91" stroke="#0d9488" stroke-width="1.5" marker-end="url(#a-teal)"/>')

# ══════════ LAYER 2: Streamlit UI ══════════
ui_y = 150
L(f'<rect x="90" y="{ui_y}" width="850" height="72" rx="8" fill="#f8fafc" stroke="#e2e8f0" stroke-width="1" stroke-dasharray="6,3"/>')
L(f'<text x="104" y="{ui_y+16}" font-size="11" fill="#94a3b8">Streamlit Web UI (src/app.py)</text>')

L(f'<rect x="120" y="{ui_y+24}" width="395" height="38" rx="6" fill="#ffffff" stroke="#d1d5db" stroke-width="1.5"/>')
L(f'<text x="317" y="{ui_y+42}" text-anchor="middle" font-size="12" fill="#111827">Page 1: 上传 &amp; 控标结果</text>')
L(f'<text x="317" y="{ui_y+56}" text-anchor="middle" font-size="9" fill="#6b7280">文件上传 · 置信度卡片 · 厂商得分图</text>')

L(f'<rect x="535" y="{ui_y+24}" width="380" height="38" rx="6" fill="#ffffff" stroke="#d1d5db" stroke-width="1.5"/>')
L(f'<text x="725" y="{ui_y+42}" text-anchor="middle" font-size="12" fill="#111827">Page 2: 参数对比表 &amp; 应对建议</text>')
L(f'<text x="725" y="{ui_y+56}" text-anchor="middle" font-size="9" fill="#6b7280">逐条对比 · 筛选器 · 偏离标记 · 建议卡片</text>')

L(f'<line x1="480" y1="114" x2="480" y2="120" stroke="#6b7280" stroke-width="1.5" marker-end="url(#a-gray)"/>')
L(f'<line x1="480" y1="{ui_y-6}" x2="480" y2="{ui_y}" stroke="#6b7280" stroke-width="1.5" marker-end="url(#a-gray)"/>')

# ══════════ LAYER 3: ENGINE ══════════
eng_y = 250
L(f'<rect x="320" y="{eng_y}" width="320" height="46" rx="8" fill="#ffffff" stroke="#2563eb" stroke-width="2" filter="url(#shadow)"/>')
L(f'<text x="480" y="{eng_y+20}" text-anchor="middle" font-size="14" font-weight="600" fill="#1d4ed8">engine.py — run_analysis()</text>')
L(f'<text x="480" y="{eng_y+36}" text-anchor="middle" font-size="10" fill="#6b7280">总调度器: 加载数据 → 调度三层引擎 → 汇总 JSON 输出</text>')

L(f'<line x1="480" y1="{ui_y+72}" x2="480" y2="{eng_y}" stroke="#6b7280" stroke-width="1.5" marker-end="url(#a-gray)"/>')

# ══════════ LAYER 4: ANALYSIS ENGINE (3 columns) ══════════
ana_y = 324
ana_h = 156
L(f'<rect x="16" y="{ana_y}" width="928" height="{ana_h}" rx="8" fill="#f8fafc" stroke="#e2e8f0" stroke-width="1.5"/>')
L(f'<text x="56" y="{ana_y+20}" font-size="11" font-weight="600" fill="#64748b">核心分析引擎 (三层对比)</text>')

col_w = 275
col_h = 126
col_y = ana_y + 30
gutter = 24
x1 = 36; x2 = x1 + col_w + gutter; x3 = x2 + col_w + gutter

# L2: Controller ID (orange)
L(f'<rect x="{x1}" y="{col_y}" width="{col_w}" height="{col_h}" rx="8" fill="#fff7ed" stroke="#fdba74" stroke-width="1.5"/>')
L(f'<text x="{x1+col_w/2}" y="{col_y+24}" text-anchor="middle" font-size="13" font-weight="600" fill="#c2410c">Layer 2 · 控标识别</text>')
L(f'<text x="{x1+col_w/2}" y="{col_y+42}" text-anchor="middle" font-size="9" fill="#9a3412">src/matcher.py — 49 行</text>')
L(f'<line x1="{x1+12}" y1="{col_y+50}" x2="{x1+col_w-12}" y2="{col_y+50}" stroke="#fed7aa" stroke-width="1"/>')
for i, n in enumerate([
    'identify_controller()',
    '→ 招标参数 x 3家竞品逐一查表',
    '→ 仅1家满足 = 独有特征命中',
    '→ 统计 → 控标方 + 置信度',
]):
    L(f'<text x="{x1+16}" y="{col_y+64+i*14}" font-size="10" fill="#431407">{n}</text>')

# L1: Program Match (blue)
L(f'<rect x="{x2}" y="{col_y}" width="{col_w}" height="{col_h}" rx="8" fill="#eff6ff" stroke="#93c5fd" stroke-width="1.5"/>')
L(f'<text x="{x2+col_w/2}" y="{col_y+24}" text-anchor="middle" font-size="13" font-weight="600" fill="#1d4ed8">Layer 1 · 程序粗筛</text>')
L(f'<text x="{x2+col_w/2}" y="{col_y+42}" text-anchor="middle" font-size="9" fill="#1e3a5f">src/parser.py — 216 行</text>')
L(f'<line x1="{x2+12}" y1="{col_y+50}" x2="{x2+col_w-12}" y2="{col_y+50}" stroke="#bfdbfe" stroke-width="1"/>')
for i, n in enumerate([
    'find_best_match() 评分排序',
    '→ extract_numeric() 数值提取',
    '→ compare_indicators() 指标匹配',
    '→ keyword_overlap() 相似度兜底',
]):
    L(f'<text x="{x2+16}" y="{col_y+64+i*14}" font-size="10" fill="#1e3a5f">{n}</text>')

# L3: AI Semantic (purple)
L(f'<rect x="{x3}" y="{col_y}" width="{col_w}" height="{col_h}" rx="8" fill="#faf5ff" stroke="#c4b5fd" stroke-width="1.5"/>')
L(f'<text x="{x3+col_w/2}" y="{col_y+24}" text-anchor="middle" font-size="13" font-weight="600" fill="#6d28d9">Layer 3 · AI 语义精判</text>')
L(f'<text x="{x3+col_w/2}" y="{col_y+42}" text-anchor="middle" font-size="9" fill="#4c1d95">src/advisor.py — 127 行</text>')
L(f'<line x1="{x3+12}" y1="{col_y+50}" x2="{x3+col_w-12}" y2="{col_y+50}" stroke="#ddd6fe" stroke-width="1"/>')
for i, n in enumerate([
    'batch_analyze() 批量打包',
    '→ 全量讯飞目录注入 Prompt',
    '→ DeepSeek API (1次请求)',
    '→ 失败降级: 读本地缓存 JSON',
]):
    L(f'<text x="{x3+16}" y="{col_y+64+i*14}" font-size="10" fill="#4c1d95">{n}</text>')

# DeepSeek badge inside L3
L(f'<rect x="{x3+col_w-76}" y="{col_y+6}" width="68" height="16" rx="4" fill="#ede9fe" stroke="#c4b5fd" stroke-width="0.5"/>')
L(f'<text x="{x3+col_w-42}" y="{col_y+17}" text-anchor="middle" font-size="8" fill="#7c3aed">DeepSeek API</text>')

# HORIZONTAL FLOW: L2 → L1 → L3
ay = col_y + 70
L(f'<path d="M {x1+col_w+4} {ay} L {x2-4} {ay}" stroke="#ea580c" stroke-width="2" fill="none" marker-end="url(#a-orange)"/>')
L(f'<text x="{x1+col_w+gutter/2}" y="{ay-6}" text-anchor="middle" font-size="9" fill="#ea580c">筛选后</text>')
L(f'<path d="M {x2+col_w+4} {ay} L {x3-4} {ay}" stroke="#2563eb" stroke-width="2" fill="none" marker-end="url(#a-blue)"/>')
L(f'<text x="{x2+col_w+gutter/2}" y="{ay-6}" text-anchor="middle" font-size="9" fill="#2563eb">uncertain</text>')

# ENGINE → ANALYSIS (3 paths)
L(f'<path d="M 480 {eng_y+46} L 480 {eng_y+56} L {x2+col_w/2} {eng_y+56} L {x2+col_w/2} {col_y-8}" stroke="#2563eb" stroke-width="1.5" fill="none" marker-end="url(#a-blue)"/>')
L(f'<path d="M 420 {eng_y+46} L 420 {eng_y+56} L {x1+col_w/2} {eng_y+56} L {x1+col_w/2} {col_y-8}" stroke="#ea580c" stroke-width="1.5" fill="none" marker-end="url(#a-orange)"/>')
L(f'<path d="M 540 {eng_y+46} L 540 {eng_y+56} L {x3+col_w/2} {eng_y+56} L {x3+col_w/2} {col_y-8}" stroke="#7c3aed" stroke-width="1.5" fill="none" marker-end="url(#a-purple)"/>')

# ══════════ LAYER 5: DATA ══════════
dy = 510
dh = 70
L(f'<rect x="16" y="{dy}" width="928" height="{dh}" rx="8" fill="#f8fafc" stroke="#e2e8f0" stroke-width="1.5"/>')
L(f'<text x="56" y="{dy+16}" font-size="11" font-weight="600" fill="#64748b">数据层 (src/data_loader.py + config.py / .env)</text>')

dw = 210
ddx = 36
ddy = dy + 28
dg = 16
for idx, (title, sub, is_config) in enumerate([
    ("competitors/", "xiwo · honghe · haikang (各15条)", False),
    ("xunfei/", "xunfei.json (15条)", False),
    ("samples/", "sample-bid.json · demo-result.json", False),
    ("config.py + .env", "API_KEY · MODEL · 环境变量", True),
]):
    cx = ddx + idx * (dw + dg)
    color = "#fef2f2" if is_config else "#f0fdf4"
    stroke = "#fca5a5" if is_config else "#86efac"
    tc = "#991b1b" if is_config else "#166534"
    L(f'<rect x="{cx}" y="{ddy}" width="{dw}" height="32" rx="6" fill="{color}" stroke="{stroke}" stroke-width="1"/>')
    L(f'<text x="{cx+dw/2}" y="{ddy+13}" text-anchor="middle" font-size="10" font-weight="600" fill="{tc}">{title}</text>')
    L(f'<text x="{cx+dw/2}" y="{ddy+27}" text-anchor="middle" font-size="8" fill="#6b7280">{sub}</text>')

# DATA ACCESS
L(f'<path d="M 460 {eng_y+46} L 460 {eng_y+56} L 80 {eng_y+56} L 80 {dy-4}" stroke="#16a34a" stroke-width="1" fill="none" marker-end="url(#a-green)" stroke-dasharray="4,2"/>')
L(f'<text x="90" y="{eng_y+50}" font-size="9" fill="#16a34a">读写 JSON</text>')

# ══════════ EXECUTION ORDER ══════════
bar_y = 596
L(f'<rect x="16" y="{bar_y}" width="928" height="24" rx="6" fill="#f0f9ff" stroke="#bae6fd" stroke-width="1"/>')
L(f'<text x="480" y="{bar_y+16}" text-anchor="middle" font-size="10" fill="#0369a1">执行顺序: MinerU解析 → L2(横向查表) → L1(纵向匹配) → L3(AI精判)  |  总计 ~667 行 Python · 14 个函数  |  端到端耗时 ~5s</text>')

# ══════════ MINERU DETAIL BAR ══════════
minfo_y = 632
L(f'<rect x="16" y="{minfo_y}" width="928" height="36" rx="6" fill="#fafafa" stroke="#e5e7eb" stroke-width="1"/>')
L(f'<text x="32" y="{minfo_y+14}" font-size="10" font-weight="600" fill="#0f766e">MinerU 技术路线</text>')
L(f'<text x="32" y="{minfo_y+29}" font-size="10" fill="#6b7280">Pipeline后端(标准文档): DocLayout-YOLO布局检测 → PaddleOCR文本提取 → Unimernet公式→LaTeX → PP-StructureV2表格→HTML → 阅读顺序排序 → Markdown/JSON</text>')
L(f'<text x="740" y="{minfo_y+29}" font-size="10" fill="#6b7280">| VLM后端: InternVL2 端到端解析</text>')

# ══════════ LEGEND ══════════
leg_y = 684
L(f'<rect x="16" y="{leg_y}" width="928" height="120" rx="6" fill="#fafafa" stroke="#e5e7eb" stroke-width="1"/>')
L(f'<text x="32" y="{leg_y+18}" font-size="10" font-weight="600" fill="#374151">图例</text>')

leg_items = [
    ("#0d9488", "a-teal", "文档解析流", "MinerU: 视觉Pipeline + VLM"),
    ("#ea580c", "a-orange", "控标识别流", "L2: 12条x3家=36次查表"),
    ("#2563eb", "a-blue", "程序匹配流", "L1: ~80%参数直接出结论"),
    ("#7c3aed", "a-purple", "AI 语义流", "L3: 批量打包1次请求 + 降级"),
    ("#16a34a", "a-green", "数据读写", "JSON 文件 / 绿色虚线"),
    ("#6b7280", "a-gray", "用户交互", "Streamlit UI 请求/响应"),
]
for i, (color, marker, label, note) in enumerate(leg_items):
    row = i // 3
    col = i % 3
    lx = 80 + col * 290
    ly = leg_y + 32 + row * 40
    L(f'<line x1="{lx}" y1="{ly}" x2="{lx+28}" y2="{ly}" stroke="{color}" stroke-width="1.5" marker-end="url(#{marker})"/>')
    L(f'<text x="{lx+36}" y="{ly-2}" font-size="10" fill="#374151">{label}</text>')
    L(f'<text x="{lx+36}" y="{ly+12}" font-size="9" fill="#6b7280">{note}</text>')

# VLM backend note
L(f'<text x="32" y="{leg_y+110}" font-size="9" fill="#6b7280">MinerU 双后端架构 | Pipeline 后端(快): PaddleOCR + DocLayout-YOLO | VLM 后端(强): InternVL2 端到端 | pip install mineru → magic-pdf 命令行 / Python API</text>')

L('</svg>')

with open('./output/arch-three-layer.svg', 'w', encoding='utf-8') as f:
    f.write('\n'.join(lines))
print("SVG generated: ./output/arch-three-layer.svg")
print(f"Lines: {len(lines)}, ViewBox: {W}x{H}")
