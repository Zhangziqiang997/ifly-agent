#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""参数智能体 — 三层对比架构图 (Style 3 Blueprint)"""

lines = []
def L(s): lines.append(s)

W, H = 1200, 720
L(f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" width="{W}" height="{H}">')
L('  <style>')
L('    text { font-family: "Microsoft YaHei", "PingFang SC", "SimHei", sans-serif; }')
L('    .mono { font-family: "Courier New", "Consolas", monospace; }')
L('  </style>')
L('  <defs>')
L('    <pattern id="grid" width="30" height="30" patternUnits="userSpaceOnUse">')
L('      <path d="M 30 0 L 0 0 0 30" fill="none" stroke="#112240" stroke-width="0.5"/>')
L('    </pattern>')
L('    <marker id="ar" markerWidth="9" markerHeight="7" refX="8" refY="3.5" orient="auto">')
L('      <polygon points="0 0, 9 3.5, 0 7" fill="#00b4d8"/>')
L('    </marker>')
L('    <marker id="ar-g" markerWidth="9" markerHeight="7" refX="8" refY="3.5" orient="auto">')
L('      <polygon points="0 0, 9 3.5, 0 7" fill="#06d6a0"/>')
L('    </marker>')
L('    <marker id="ar-o" markerWidth="9" markerHeight="7" refX="8" refY="3.5" orient="auto">')
L('      <polygon points="0 0, 9 3.5, 0 7" fill="#f77f00"/>')
L('    </marker>')
L('  </defs>')
# background
L(f'  <rect width="{W}" height="{H}" fill="#0a1628"/>')
L(f'  <rect width="{W}" height="{H}" fill="url(#grid)" opacity="0.6"/>')

# ---- Title ----
L('  <text x="40" y="46" fill="#ffffff" font-size="22" font-weight="700">参数智能体 · 三层对比分析架构</text>')
L('  <text x="40" y="70" fill="#48cae4" font-size="13">招投标参数智能比对系统 — 由确定到模糊，能算清的绝不交给大模型</text>')
L('  <line x1="40" y1="84" x2="1160" y2="84" stroke="#00b4d8" stroke-width="1" opacity="0.4"/>')

# ============ INPUT (left) ============
L('  <rect x="40" y="300" width="150" height="120" rx="2" fill="#0d1f3c" stroke="#00b4d8" stroke-width="1.5"/>')
L('  <text x="115" y="330" fill="#00b4d8" font-size="11" text-anchor="middle" letter-spacing="0.05em">输 入</text>')
L('  <text x="115" y="358" fill="#ffffff" font-size="14" text-anchor="middle" font-weight="700">招标文件</text>')
L('  <text x="115" y="380" fill="#caf0f8" font-size="11" text-anchor="middle">多条参数要求</text>')
L('  <text x="115" y="400" fill="#48cae4" font-size="10" text-anchor="middle" class="mono">亮度 &#8805; 500cd/m2</text>')

# ============ CORE (three stacked layers) ============
CX = 250      # core container x
CW = 620      # core container width
L(f'  <rect x="{CX}" y="110" width="{CW}" height="560" rx="2" fill="none" stroke="#00b4d8" stroke-width="1" stroke-dasharray="6,3" opacity="0.5"/>')
L(f'  <text x="{CX+16}" y="132" fill="#48cae4" font-size="11" letter-spacing="0.08em">三 层 对 比 引 擎 · 串 行 流 水 线</text>')

lx = CX + 30
lw = CW - 60

# --- Layer 1: 数值比对 ---
y1 = 150
L(f'  <rect x="{lx}" y="{y1}" width="{lw}" height="150" rx="2" fill="#0d1f3c" stroke="#06d6a0" stroke-width="1.5"/>')
L(f'  <circle cx="{lx+26}" cy="{y1+30}" r="15" fill="#06d6a0" opacity="0.15" stroke="#06d6a0" stroke-width="1"/>')
L(f'  <text x="{lx+26}" y="{y1+35}" fill="#06d6a0" font-size="15" text-anchor="middle" font-weight="700">1</text>')
L(f'  <text x="{lx+52}" y="{y1+28}" fill="#ffffff" font-size="15" font-weight="700">第一层 · 数值比对</text>')
L(f'  <text x="{lx+52}" y="{y1+48}" fill="#48cae4" font-size="11">纯程序计算，不用大模型</text>')
L(f'  <text x="{lx+20}" y="{y1+78}" fill="#caf0f8" font-size="12">· 单位对齐：4K = 3840&#215;2160，13MP = 1300万像素</text>')
L(f'  <text x="{lx+20}" y="{y1+100}" fill="#caf0f8" font-size="12">· 数值大小比较，按招标要求方向判定满足与否</text>')
L(f'  <text x="{lx+20}" y="{y1+122}" fill="#06d6a0" font-size="12" font-weight="700">约 80% 参数在此层直接出结论</text>')

# --- Layer 2: 控标方识别 ---
y2 = 320
L(f'  <rect x="{lx}" y="{y2}" width="{lw}" height="150" rx="2" fill="#0d1f3c" stroke="#00b4d8" stroke-width="1.5"/>')
L(f'  <circle cx="{lx+26}" cy="{y2+30}" r="15" fill="#00b4d8" opacity="0.15" stroke="#00b4d8" stroke-width="1"/>')
L(f'  <text x="{lx+26}" y="{y2+35}" fill="#00b4d8" font-size="15" text-anchor="middle" font-weight="700">2</text>')
L(f'  <text x="{lx+52}" y="{y2+28}" fill="#ffffff" font-size="15" font-weight="700">第二层 · 控标方识别</text>')
L(f'  <text x="{lx+52}" y="{y2+48}" fill="#48cae4" font-size="11">查表统计，不用大模型</text>')
L(f'  <text x="{lx+20}" y="{y2+78}" fill="#caf0f8" font-size="12">· 每条参数比对三家竞品：希沃 / 鸿合 / 海康</text>')
L(f'  <text x="{lx+20}" y="{y2+100}" fill="#caf0f8" font-size="12">· 仅一家满足 = 独有特征，统计各家命中数</text>')
L(f'  <text x="{lx+20}" y="{y2+122}" fill="#00b4d8" font-size="12" font-weight="700">命中最多者 = 控标方 + 置信度</text>')

# --- Layer 3: AI语义精判 ---
y3 = 490
L(f'  <rect x="{lx}" y="{y3}" width="{lw}" height="150" rx="2" fill="#0d1f3c" stroke="#f77f00" stroke-width="1.5"/>')
L(f'  <circle cx="{lx+26}" cy="{y3+30}" r="15" fill="#f77f00" opacity="0.15" stroke="#f77f00" stroke-width="1"/>')
L(f'  <text x="{lx+26}" y="{y3+35}" fill="#f77f00" font-size="15" text-anchor="middle" font-weight="700">3</text>')
L(f'  <text x="{lx+52}" y="{y3+28}" fill="#ffffff" font-size="15" font-weight="700">第三层 · 语义精判</text>')
L(f'  <text x="{lx+52}" y="{y3+48}" fill="#48cae4" font-size="11">大模型理解 · DeepSeek</text>')
L(f'  <text x="{lx+20}" y="{y3+78}" fill="#caf0f8" font-size="12">· 说法不同意思相同 → 说辞可改，给改写建议</text>')
L(f'  <text x="{lx+20}" y="{y3+100}" fill="#caf0f8" font-size="12">· 确实不满足 → 生成质疑话术 / 渠道协调建议</text>')
L(f'  <text x="{lx+20}" y="{y3+122}" fill="#f77f00" font-size="12" font-weight="700">只处理前两层无法确定的疑难项</text>')

# ============ OUTPUT (right) ============
ox = 910
L(f'  <rect x="{ox}" y="150" width="250" height="150" rx="2" fill="#0d1f3c" stroke="#00b4d8" stroke-width="1.5"/>')
L(f'  <text x="{ox+125}" y="180" fill="#00b4d8" font-size="11" text-anchor="middle" letter-spacing="0.05em">输 出 · 分 析 报 告</text>')
L(f'  <line x1="{ox+16}" y1="192" x2="{ox+234}" y2="192" stroke="#00b4d8" stroke-width="0.5" opacity="0.5"/>')
L(f'  <text x="{ox+20}" y="218" fill="#caf0f8" font-size="12">&#9679; 控标方判定 + 置信度</text>')
L(f'  <text x="{ox+20}" y="244" fill="#caf0f8" font-size="12">&#9679; 逐条正 / 负偏离标记</text>')
L(f'  <text x="{ox+20}" y="270" fill="#caf0f8" font-size="12">&#9679; 负偏离应对建议</text>')

# deviation legend chips inside output
L(f'  <rect x="{ox+20}" y="285" width="14" height="8" rx="1" fill="#06d6a0"/>')
L(f'  <rect x="{ox+90}" y="285" width="14" height="8" rx="1" fill="#f77f00"/>')
L(f'  <rect x="{ox+165}" y="285" width="14" height="8" rx="1" fill="#e63946"/>')

# ============ FLOW ARROWS ============
# input -> core (into layer1 area)
L(f'  <polyline points="190,360 220,360 220,225 {lx},225" fill="none" stroke="#00b4d8" stroke-width="1.5" marker-end="url(#ar)"/>')
# layer1 -> layer2 (down)
L(f'  <polyline points="{lx+lw//2},300 {lx+lw//2},320" fill="none" stroke="#48cae4" stroke-width="1.5" marker-end="url(#ar)"/>')
L(f'  <text x="{lx+lw//2+10}" y="314" fill="#48cae4" font-size="10">数值判定</text>')
# layer2 -> layer3 (down)
L(f'  <polyline points="{lx+lw//2},470 {lx+lw//2},490" fill="none" stroke="#48cae4" stroke-width="1.5" marker-end="url(#ar)"/>')
L(f'  <text x="{lx+lw//2+10}" y="484" fill="#48cae4" font-size="10">疑难项下沉</text>')
# core -> output (three merge into output). Use right edge of each layer.
L(f'  <polyline points="{lx+lw},225 890,225 890,200 {ox},200" fill="none" stroke="#06d6a0" stroke-width="1.5" marker-end="url(#ar-g)"/>')
L(f'  <polyline points="{lx+lw},395 890,395 890,235 {ox},235" fill="none" stroke="#00b4d8" stroke-width="1.5" marker-end="url(#ar)"/>')
L(f'  <polyline points="{lx+lw},565 895,565 895,265 {ox},265" fill="none" stroke="#f77f00" stroke-width="1.5" marker-end="url(#ar-o)"/>')

# ============ LEGEND (bottom-left) ============
ly = 690
L(f'  <rect x="40" y="{ly-24}" width="14" height="8" rx="1" fill="#06d6a0"/>')
L(f'  <text x="60" y="{ly-16}" fill="#caf0f8" font-size="11">正偏离(满足)</text>')
L(f'  <rect x="160" y="{ly-24}" width="14" height="8" rx="1" fill="#f77f00"/>')
L(f'  <text x="180" y="{ly-16}" fill="#caf0f8" font-size="11">说辞可改</text>')
L(f'  <rect x="270" y="{ly-24}" width="14" height="8" rx="1" fill="#e63946"/>')
L(f'  <text x="290" y="{ly-16}" fill="#caf0f8" font-size="11">真不满足</text>')

# ============ TITLE BLOCK (bottom-right) ============
L('  <rect x="920" y="660" width="240" height="44" rx="2" fill="#0d1f3c" stroke="#00b4d8" stroke-width="1"/>')
L('  <line x1="920" y1="676" x2="1160" y2="676" stroke="#00b4d8" stroke-width="0.5"/>')
L('  <text x="1040" y="672" text-anchor="middle" fill="#48cae4" font-size="9" letter-spacing="0.08em">SYSTEM ARCHITECTURE</text>')
L('  <text x="1040" y="695" text-anchor="middle" fill="#caf0f8" font-size="12" font-weight="700">三层对比分析引擎 v1.0</text>')

L('</svg>')
with open('output/arch-three-layer.svg', 'w', encoding='utf-8') as f:
    f.write('\n'.join(lines))
print("SVG written:", len(lines), "lines")
