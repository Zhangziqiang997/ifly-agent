import {
  analysisReport,
  filterAnalysisItems,
  getCategoryDistribution,
  getDashboardMetrics,
} from './report-data.mjs';

const deviationMeta = Object.freeze({
  positive: Object.freeze({ label: '正偏离', tone: 'positive' }),
  negative_wording: Object.freeze({ label: '说辞可改', tone: 'wording' }),
  negative_real: Object.freeze({ label: '真负偏离', tone: 'negative' }),
});

function node(tag, className, text) {
  const element = document.createElement(tag);
  if (className) element.className = className;
  if (text !== undefined) element.textContent = text;
  return element;
}

function setText(id, text) {
  document.getElementById(id).textContent = text;
}

function renderHeader(report) {
  const confidence = Math.round(report.controller.confidence * 100);
  setText('report-title', `${report.projectName} · 分析报告`);
  setText('controller-summary', report.controller.summary);
  setText('controller-vendor', report.controller.vendor);
  setText('controller-confidence', `${confidence}%`);
  setText('confidence-ring-text', `${confidence}%`);
  setText('controller-hit-count', `${report.suspiciousItems.length} 项`);
  const circle = document.getElementById('confidence-progress');
  const circumference = 2 * Math.PI * 38;
  circle.style.strokeDasharray = String(circumference);
  circle.style.strokeDashoffset = String(circumference * (1 - report.controller.confidence));
}

function renderKpis(metrics) {
  const kpis = [
    { label: '有效参数总计', value: metrics.total, tone: 'cyan' },
    { label: '🟢 正偏离', value: metrics.positiveCount, tone: 'green' },
    { label: '🟡 说辞可改', value: metrics.wordingCount, tone: 'amber' },
    { label: '🔴 真负偏离', value: metrics.negativeCount, tone: 'red' },
  ];
  const container = document.getElementById('report-kpis');
  container.replaceChildren(...kpis.map((kpi) => {
    const card = node('article', 'stat-card');
    card.append(node('strong', `stat-num c-${kpi.tone}`, String(kpi.value)), node('span', 'stat-label', kpi.label));
    return card;
  }));
}

function renderEvidence(report) {
  const list = document.getElementById('controller-evidence');
  list.replaceChildren(...report.suspiciousItems.map((evidence) => {
    const item = node('li', 'hit-item');
    item.append(node('i', 'hit-dot'), node('span', 'hit-text', evidence));
    return item;
  }));
}

function renderChart(report) {
  const chart = document.getElementById('category-chart');
  const distribution = getCategoryDistribution(report);
  const allCounts = Object.entries(distribution).map(([category, total]) => {
    const items = report.analysisItems.filter((item) => item.category === category);
    return {
      category,
      total,
      positive: items.filter((item) => item.deviation === 'positive').length,
      wording: items.filter((item) => item.deviation === 'negative_wording').length,
      negative: items.filter((item) => item.deviation === 'negative_real').length,
    };
  });
  const max = Math.max(...allCounts.map((item) => item.total), 1);
  chart.replaceChildren(...allCounts.map((item) => {
    const column = node('div', 'bar-column');
    const stack = node('div', 'bar-stack');
    stack.setAttribute('title', `${item.category}：正偏离 ${item.positive}，说辞可改 ${item.wording}，真负偏离 ${item.negative}`);
    ['negative', 'wording', 'positive'].forEach((tone) => {
      if (!item[tone]) return;
      const segment = node('span', `bar-segment bar-${tone}`);
      segment.style.height = `${Math.max((item[tone] / max) * 90, 8)}px`;
      stack.append(segment);
    });
    column.append(stack, node('span', 'bar-label', item.category));
    return column;
  }));
}

function createSuggestionRow(item) {
  const meta = deviationMeta[item.deviation];
  const row = node('tr', 'suggestion-row');
  const cell = node('td');
  cell.colSpan = 6;
  const details = node('details', 'suggestion-panel');
  const summary = node('summary', 'suggestion-header');
  summary.append(node('b', `priority-tag priority-${item.priority.toLowerCase()}`, item.priority), node('span', '', meta.tone === 'wording' ? '改说辞建议' : '风险研判与处置建议'));
  const body = node('div', 'suggestion-body');
  const risk = node('p', 'suggestion-risk', item.riskExplanation);
  const action = node('p', 'suggestion-text', item.action);
  const basis = node('p', 'suggestion-basis', `判定依据：${item.method}`);
  body.append(risk, action, basis);
  details.append(summary, body);
  cell.append(details);
  row.append(cell);
  return row;
}

function createAnalysisRows(items) {
  return items.flatMap((item, index) => {
    const meta = deviationMeta[item.deviation];
    const row = node('tr', `analysis-row analysis-row-${meta.tone}`);
    const seq = node('td', 'seq-num', String(index + 1).padStart(2, '0'));
    const category = node('td', 'analysis-category', item.category);
    const requirement = node('td', 'analysis-requirement', item.bidRequirement);
    const spec = node('td', 'analysis-spec', item.xunfeiSpec);
    const verdict = node('td');
    verdict.append(node('span', `deviation-tag dev-${meta.tone}`, meta.label));
    const method = node('td');
    method.append(node('span', 'method-tag', item.method.includes('审查') ? 'AI 精判' : '程序粗筛'));
    row.append(seq, category, requirement, spec, verdict, method);
    return item.deviation === 'positive' ? [row] : [row, createSuggestionRow(item)];
  });
}

function renderTable(report, filter) {
  const items = filterAnalysisItems(report, filter);
  document.getElementById('report-table-body').replaceChildren(...createAnalysisRows(items));
  setText('table-count', `显示 ${items.length} / ${report.analysisItems.length} 项`);
}

function bindFilters(report) {
  document.querySelectorAll('.report-filter').forEach((button) => {
    button.addEventListener('click', () => {
      document.querySelectorAll('.report-filter').forEach((candidate) => {
        candidate.setAttribute('aria-pressed', String(candidate === button));
      });
      renderTable(report, button.dataset.filter);
    });
  });
}

const metrics = getDashboardMetrics(analysisReport);
renderHeader(analysisReport);
renderKpis(metrics);
renderEvidence(analysisReport);
renderChart(analysisReport);
renderTable(analysisReport, 'all');
bindFilters(analysisReport);
