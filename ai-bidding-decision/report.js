import { analysisReport, filterAnalysisItems, getCategoryDistribution, getDashboardMetrics } from './report-data.mjs';

const deviationMeta = Object.freeze({
  positive: { label: '正偏离', tone: 'positive' },
  negative_wording: { label: '措辞可改', tone: 'wording' },
  negative_real: { label: '真实负偏离', tone: 'negative' },
});

const element = (tag, className, text) => {
  const node = document.createElement(tag);
  if (className) node.className = className;
  if (text !== undefined) node.textContent = text;
  return node;
};

function renderHeader(report) {
  const confidence = Math.round(report.controller.confidence * 100);
  document.querySelector('#report-title').textContent = `${report.projectName} · AI 分析报告`;
  document.querySelector('#controller-summary').textContent = report.controller.summary;
  document.querySelector('#controller-vendor').textContent = report.controller.vendor;
  document.querySelector('#controller-confidence').textContent = `${confidence}%`;
  document.querySelector('#controller-evidence').replaceChildren(...report.suspiciousItems.map((item) => element('li', '', item)));
}

function renderKpis(metrics) {
  const data = [
    ['有效参数', metrics.total, '结构化提取的关键招标条款', 'blue'],
    ['正偏离', metrics.positiveCount, '讯飞方案可满足或优于要求', 'green'],
    ['措辞可改', metrics.wordingCount, '建议改为功能或性能指标', 'amber'],
    ['真实负偏离', metrics.negativeCount, '需重点澄清或形成应对方案', 'red'],
  ];
  const container = document.querySelector('#report-kpis');
  container.replaceChildren(...data.map(([label, value, note, tone]) => {
    const card = element('article', `summary-card ${tone}`);
    card.append(element('strong', '', String(value)), element('span', '', label), element('small', '', note));
    return card;
  }));
}

function renderChart(report) {
  const distribution = getCategoryDistribution(report);
  const stats = Object.keys(distribution).map((category) => {
    const entries = report.analysisItems.filter((item) => item.category === category);
    return { category, positive: entries.filter((item) => item.deviation === 'positive').length, wording: entries.filter((item) => item.deviation === 'negative_wording').length, negative: entries.filter((item) => item.deviation === 'negative_real').length };
  });
  const maximum = Math.max(...stats.map((item) => item.positive + item.wording + item.negative), 1);
  const chart = document.querySelector('#category-chart');
  chart.replaceChildren(...stats.map((item) => {
    const column = element('div', 'bar-column');
    const stack = element('div', 'bar-stack');
    stack.title = `${item.category}：正偏离 ${item.positive}，措辞可改 ${item.wording}，真实负偏离 ${item.negative}`;
    [['positive', item.positive], ['wording', item.wording], ['negative', item.negative]].forEach(([tone, value]) => {
      if (!value) return;
      const segment = element('i', `bar ${tone}`);
      segment.style.height = `${Math.max(value / maximum * 96, 13)}px`;
      stack.append(segment);
    });
    column.append(stack, element('span', '', item.category));
    return column;
  }));
}

function createSuggestionRow(item) {
  if (item.deviation === 'positive') return null;
  const meta = deviationMeta[item.deviation];
  const row = element('tr', 'suggestion-row');
  const cell = element('td');
  cell.colSpan = 6;
  const detail = element('details', 'suggestion');
  const summary = element('summary');
  summary.append(element('b', `priority ${item.priority.toLowerCase()}`, item.priority), element('span', '', '查看风险依据与应对建议'));
  const content = element('div', 'suggestion-content');
  content.append(element('p', 'risk-text', `风险研判：${item.riskExplanation}`), element('p', '', `建议动作：${item.action}`), element('p', 'basis', `判定依据：${item.method}`));
  detail.append(summary, content);
  cell.append(detail);
  row.append(cell);
  return row;
}

function createRows(items) {
  return items.flatMap((item, index) => {
    const meta = deviationMeta[item.deviation];
    const row = element('tr', `analysis-row ${meta.tone}`);
    const cells = [
      element('td', 'seq', String(index + 1).padStart(2, '0')),
      element('td', '', item.category),
      element('td', 'requirement', item.bidRequirement),
      element('td', '', item.xunfeiSpec),
      element('td'),
      element('td'),
    ];
    cells[4].append(element('span', `deviation ${meta.tone}`, meta.label));
    cells[5].append(element('span', 'method', item.method.includes('审查') ? 'AI 精判' : '程序粗筛'));
    row.append(...cells);
    const suggestion = createSuggestionRow(item);
    return suggestion ? [row, suggestion] : [row];
  });
}

function renderTable(report, filter) {
  const items = filterAnalysisItems(report, filter);
  document.querySelector('#report-table-body').replaceChildren(...createRows(items));
  document.querySelector('#table-count').textContent = `显示 ${items.length} / ${report.analysisItems.length} 项`;
}

function bindFilters(report) {
  document.querySelectorAll('.report-filter').forEach((button) => button.addEventListener('click', () => {
    document.querySelectorAll('.report-filter').forEach((candidate) => candidate.setAttribute('aria-pressed', String(candidate === button)));
    renderTable(report, button.dataset.filter);
  }));
}

renderHeader(analysisReport);
renderKpis(getDashboardMetrics(analysisReport));
renderChart(analysisReport);
renderTable(analysisReport, 'all');
bindFilters(analysisReport);
