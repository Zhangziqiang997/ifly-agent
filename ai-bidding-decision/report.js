import {
  analysisReport,
  filterAnalysisItems,
  getCategoryDistribution,
  getDashboardMetrics,
} from './report-data.mjs';

const deviationMeta = Object.freeze({
  positive: Object.freeze({ label: '正偏离', tone: 'positive' }),
  negative_wording: Object.freeze({ label: '可改说辞', tone: 'wording' }),
  negative_real: Object.freeze({ label: '真负偏离', tone: 'negative' }),
});

function createNode(tagName, className, text) {
  const node = document.createElement(tagName);
  if (className) node.className = className;
  if (text !== undefined) node.textContent = text;
  return node;
}

function setText(id, text) {
  document.getElementById(id).textContent = text;
}

function renderHeader(report) {
  setText('report-title', report.projectName);
  setText('controller-summary', report.controller.summary);
  setText('controller-vendor', report.controller.vendor);
  setText('controller-confidence', `${Math.round(report.controller.confidence * 100)}%`);
  setText('controller-hit-count', `${report.suspiciousItems.length} 项`);
}

function renderKpis(metrics) {
  const container = document.getElementById('report-kpis');
  const kpis = [
    { label: '总参数', value: metrics.total, note: '纳入逐项研判', tone: 'total' },
    { label: '正偏离', value: metrics.positiveCount, note: '优于对标规格', tone: 'positive' },
    { label: '可改说辞', value: metrics.wordingCount, note: '可通过措辞修订', tone: 'wording' },
    { label: '真负偏离', value: metrics.negativeCount, note: '需形成处置闭环', tone: 'negative' },
  ];

  kpis.forEach((kpi) => {
    const card = createNode('article', `report-kpi report-kpi-${kpi.tone}`);
    const marker = createNode('span', 'report-kpi-marker');
    marker.setAttribute('aria-hidden', 'true');
    const copy = createNode('div', 'report-kpi-copy');
    const label = createNode('span', 'report-kpi-label', kpi.label);
    const value = createNode('strong', 'report-kpi-value', String(kpi.value));
    const note = createNode('p', 'report-kpi-note', kpi.note);

    copy.append(label, value, note);
    card.append(marker, copy);
    container.append(card);
  });
}

function renderControllerEvidence(report) {
  const list = document.getElementById('controller-evidence');

  report.suspiciousItems.forEach((evidence) => {
    const item = createNode('li', 'controller-evidence-item');
    const marker = createNode('span', 'controller-evidence-marker', '✓');
    marker.setAttribute('aria-hidden', 'true');
    const text = createNode('p', '', evidence);
    item.append(marker, text);
    list.append(item);
  });
}

function renderCategoryChart(report) {
  const chart = document.getElementById('category-chart');
  const distribution = getCategoryDistribution(report);

  Object.entries(distribution).forEach(([category, total]) => {
    const categoryItems = report.analysisItems.filter((item) => item.category === category);
    const counts = {
      positive: categoryItems.filter((item) => item.deviation === 'positive').length,
      wording: categoryItems.filter((item) => item.deviation === 'negative_wording').length,
      negative: categoryItems.filter((item) => item.deviation === 'negative_real').length,
    };
    const row = createNode('div', 'category-chart-row');
    const heading = createNode('div', 'category-chart-heading');
    const label = createNode('strong', '', category);
    const count = createNode('span', '', `${total} 项`);
    const bar = createNode('div', 'category-chart-bar');
    bar.setAttribute(
      'aria-label',
      `${category}：正偏离 ${counts.positive}，可改说辞 ${counts.wording}，真负偏离 ${counts.negative}`,
    );

    ['positive', 'wording', 'negative'].forEach((tone) => {
      if (counts[tone] === 0) return;
      const segment = createNode(
        'span',
        `deviation-segment deviation-segment-${tone}`,
        String(counts[tone]),
      );
      segment.style.width = `${(counts[tone] / total) * 100}%`;
      segment.title = `${deviationMeta[tone === 'negative' ? 'negative_real' : tone === 'wording' ? 'negative_wording' : 'positive'].label} ${counts[tone]} 项`;
      bar.append(segment);
    });

    heading.append(label, count);
    row.append(heading, bar);
    chart.append(row);
  });
}

function createDetails(item) {
  const details = createNode('details', 'analysis-details');
  const summary = createNode('summary', '', '展开风险与处置闭环');
  const body = createNode('div', 'analysis-details-body');
  const explanation = createNode('div', 'analysis-detail-block');
  const explanationLabel = createNode('strong', '', '风险解释');
  const explanationText = createNode('p', '', item.riskExplanation);
  const basis = createNode('div', 'analysis-detail-block');
  const basisLabel = createNode('strong', '', '判定依据');
  const basisText = createNode('p', '', item.method);
  const closure = createNode('div', 'analysis-detail-block analysis-detail-closure');
  const closureLabel = createNode('strong', '', '行动闭环');
  const closureText = createNode('p', '', item.action);

  explanation.append(explanationLabel, explanationText);
  basis.append(basisLabel, basisText);
  closure.append(closureLabel, closureText);
  body.append(explanation, basis, closure);
  details.append(summary, body);
  return details;
}

function createAnalysisRow(item) {
  const meta = deviationMeta[item.deviation];
  const row = createNode('tr', `analysis-row analysis-row-${meta.tone}`);
  const categoryCell = createNode('td', 'analysis-category', item.category);
  const requirementCell = createNode('td', 'analysis-requirement', item.bidRequirement);
  const specCell = createNode('td', 'analysis-spec', item.xunfeiSpec);
  const resultCell = createNode('td', '');
  const status = createNode('span', `report-status report-status-${meta.tone}`, meta.label);
  const sourceCell = createNode('td', 'analysis-source');
  const method = createNode('span', '', item.method);
  const priority = createNode('strong', `priority-tag priority-${item.priority.toLowerCase()}`, item.priority);
  const actionCell = createNode('td', 'analysis-action');
  const action = createNode('p', '', item.action);

  resultCell.append(status);
  sourceCell.append(method, priority);
  actionCell.append(action);
  if (item.deviation === 'negative_real') actionCell.append(createDetails(item));
  row.append(categoryCell, requirementCell, specCell, resultCell, sourceCell, actionCell);
  return row;
}

function renderTable(report, filter) {
  const body = document.getElementById('report-table-body');
  const items = filterAnalysisItems(report, filter);
  body.replaceChildren(...items.map(createAnalysisRow));
  setText('table-count', `显示 ${items.length} / ${report.analysisItems.length} 项`);
}

function activateFilter(report, activeButton) {
  document.querySelectorAll('.report-filter').forEach((button) => {
    button.setAttribute('aria-pressed', String(button === activeButton));
  });
  renderTable(report, activeButton.dataset.filter);
}

function bindFilters(report) {
  document.querySelectorAll('.report-filter').forEach((button) => {
    button.addEventListener('click', () => activateFilter(report, button));
  });
}

const metrics = getDashboardMetrics(analysisReport);
renderHeader(analysisReport);
renderKpis(metrics);
renderControllerEvidence(analysisReport);
renderCategoryChart(analysisReport);
renderTable(analysisReport, 'all');
bindFilters(analysisReport);
