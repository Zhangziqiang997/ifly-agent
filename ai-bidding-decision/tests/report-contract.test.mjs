import assert from 'node:assert/strict';
import { readFile } from 'node:fs/promises';
import test from 'node:test';

const root = new URL('../', import.meta.url);

async function readProjectFile(name) {
  try {
    return await readFile(new URL(name, root), 'utf8');
  } catch (error) {
    if (error.code === 'ENOENT') return '';
    throw error;
  }
}

const reportHtml = await readProjectFile('report.html');
const reportJs = await readProjectFile('report.js');
const stylesCss = await readProjectFile('styles.css');

test('report page exposes the blue-and-white cockpit rendering targets', () => {
  assert.match(reportHtml, /href=["']index\.html["']/i);
  assert.match(reportHtml, /id=["']report-kpis["']/i);
  assert.match(reportHtml, /id=["']controller-evidence["']/i);
  assert.match(reportHtml, /id=["']category-chart["']/i);
  assert.match(reportHtml, /id=["']table-count["']/i);
  assert.match(reportHtml, /id=["']report-table-body["']/i);
  assert.match(
    reportHtml,
    /<script(?=[^>]*\bsrc=["']report\.js["'])(?=[^>]*\btype=["']module["'])[^>]*>/i,
  );
});

test('report page provides four accessible filters and the six analysis columns', () => {
  for (const filter of ['all', 'positive', 'wording', 'negative']) {
    assert.match(
      reportHtml,
      new RegExp(`<button(?=[^>]*data-filter=["']${filter}["'])(?=[^>]*aria-pressed=["'](?:true|false)["'])`, 'i'),
    );
  }

  for (const heading of ['类别', '招标要求', '讯飞规格', '判定', '来源 / 优先级', '行动建议']) {
    assert.match(reportHtml, new RegExp(`<th[^>]*>${heading.replace(' / ', '\\s*/\\s*')}<\\/th>`));
  }
});

test('report renderer imports report data and uses safe DOM APIs for dynamic content', () => {
  assert.match(reportJs, /from\s+['"]\.\/report-data\.mjs['"]/);
  assert.match(reportJs, /document\.createElement\(/);
  assert.match(reportJs, /\.textContent\s*=/);
  assert.doesNotMatch(reportJs, /\binnerHTML\b/);
});

test('report renderer covers KPI, controller evidence, distribution, and filtering', () => {
  assert.match(reportJs, /projectName/);
  assert.match(reportJs, /controller/);
  assert.match(reportJs, /getDashboardMetrics/);
  assert.match(reportJs, /getCategoryDistribution/);
  assert.match(reportJs, /filterAnalysisItems/);
  assert.match(reportJs, /suspiciousItems/);
  assert.match(reportJs, /aria-pressed/);
  assert.match(reportJs, /addEventListener\(['"]click['"]/);
  assert.match(reportJs, /positiveCount/);
  assert.match(reportJs, /wordingCount/);
  assert.match(reportJs, /negativeCount/);
});

test('report renderer builds safe expandable real-negative details and action closure', () => {
  assert.match(reportJs, /createNode\(['"]details['"]/);
  assert.match(reportJs, /createNode\(['"]summary['"]/);
  assert.match(reportJs, /riskExplanation/);
  assert.match(reportJs, /\.method/);
  assert.match(reportJs, /\.priority/);
  assert.match(reportJs, /\.action/);
  assert.match(reportJs, /negative_real/);
});

test('report stylesheet defines a responsive blue-and-white report layout', () => {
  assert.match(stylesCss, /\.report-page\b/);
  assert.match(stylesCss, /\.report-kpi-grid\b/);
  assert.match(stylesCss, /\.category-chart\b/);
  assert.match(stylesCss, /\.report-filter\[aria-pressed=["']true["']\]/);
  assert.match(stylesCss, /\.deviation-segment-positive\b/);
  assert.match(stylesCss, /\.deviation-segment-wording\b/);
  assert.match(stylesCss, /\.deviation-segment-negative\b/);
  assert.match(stylesCss, /\.analysis-details\b/);
  assert.match(stylesCss, /\.report-table-wrap\b/);
  assert.match(stylesCss, /@media\s*\(max-width:\s*760px\)/);
});
