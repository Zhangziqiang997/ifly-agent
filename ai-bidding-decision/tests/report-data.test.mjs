import test from 'node:test';
import assert from 'node:assert/strict';

import {
  analysisReport,
  filterAnalysisItems,
  getCategoryDistribution,
  getDashboardMetrics,
  getReportMetrics,
} from '../report-data.mjs';

test('stores the fixed AI bidding-analysis report with the required evidence', () => {
  assert.equal(analysisReport.projectName, '智慧教室设备采购项目');
  assert.equal(analysisReport.controller.vendor, '希沃');
  assert.equal(analysisReport.controller.confidence, 0.92);
  assert.match(analysisReport.controller.summary, /控标倾向/);

  assert.equal(analysisReport.suspiciousItems.length, 2);
  assert.equal(analysisReport.positiveDeviations.length, 4);
  assert.equal(analysisReport.negativeDeviations.length, 2);
  assert.equal(analysisReport.risks.length, 2);

  assert.match(analysisReport.positiveDeviations.join(' '), /摄像头视场角≥145°/);
  assert.match(analysisReport.negativeDeviations.join(' '), /讯飞≥135°/);
  assert.ok(analysisReport.risks.every((risk) => risk.explanation && risk.response));
});

test('derives the dashboard metrics without a backend request', () => {
  assert.deepEqual(getReportMetrics(analysisReport), {
    confidence: 0.92,
    positiveCount: 4,
    negativeCount: 2,
    riskCount: 2,
  });
});

test('stores at least eight complete item-by-item parameter analyses', () => {
  assert.ok(analysisReport.analysisItems.length >= 8);
  assert.ok(analysisReport.analysisItems.every((item) => (
    item.category
    && item.bidRequirement
    && item.xunfeiSpec
    && ['positive', 'negative_wording', 'negative_real'].includes(item.deviation)
    && item.method
    && ['P0', 'P1', 'P2'].includes(item.priority)
    && item.riskExplanation
    && item.action
  )));

  const evidence = analysisReport.analysisItems.map((item) => item.bidRequirement).join(' ');
  assert.match(evidence, /摄像头视场角≥145°/);
  assert.match(analysisReport.analysisItems.map((item) => item.xunfeiSpec).join(' '), /讯飞≥135°/);
});

test('derives dashboard metrics and category distribution from analysis items', () => {
  assert.deepEqual(getDashboardMetrics(analysisReport), {
    total: 8,
    positiveCount: 3,
    wordingCount: 2,
    negativeCount: 3,
  });
  assert.deepEqual(getCategoryDistribution(analysisReport), {
    '视频采集': 2,
    '显示交互': 2,
    '音频采集': 2,
    '网络与平台': 2,
  });
});

test('filters analysis items by the supported dashboard status', () => {
  assert.equal(filterAnalysisItems(analysisReport, 'all').length, 8);
  assert.equal(filterAnalysisItems(analysisReport, 'positive').length, 3);
  assert.equal(filterAnalysisItems(analysisReport, 'wording').length, 2);
  assert.equal(filterAnalysisItems(analysisReport, 'negative').length, 3);
  assert.deepEqual(filterAnalysisItems(analysisReport, 'unsupported'), []);
});
