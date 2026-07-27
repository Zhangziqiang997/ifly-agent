export const analysisReport = Object.freeze({
  projectName: '智慧教室设备采购项目',
  controller: Object.freeze({
    vendor: '希沃',
    confidence: 0.92,
    summary: '多项关键参数与希沃产品规格高度重合，存在明显控标倾向。',
  }),
  suspiciousItems: Object.freeze([
    '交互平板的专有接口描述与希沃课堂终端配置一致。',
    '软件平台兼容性要求指定希沃既有账号体系。',
  ]),
  analysisItems: Object.freeze([
    Object.freeze({ category: '视频采集', bidRequirement: '摄像头视场角≥145°', xunfeiSpec: '讯飞≥135°，可覆盖常规教室拍摄范围', deviation: 'positive', method: '对照产品公开规格书与招标参数', priority: 'P0', riskExplanation: '超出常规基线的视场角可能缩小可选设备范围。', action: '要求明确视场角测量方法，并接受可验证的等效参数。' }),
    Object.freeze({ category: '视频采集', bidRequirement: '摄像头像素≥1200万', xunfeiSpec: '讯飞采用800万像素广角摄像头', deviation: 'negative_real', method: '比对公开产品规格与招标门槛', priority: 'P1', riskExplanation: '像素门槛高于对标规格，需说明是否为实际教学场景所必需。', action: '补充图像清晰度、帧率和实际拍摄距离的验收指标。' }),
    Object.freeze({ category: '显示交互', bidRequirement: '交互平板亮度≥500nit', xunfeiSpec: '讯飞常规教学平板亮度400nit', deviation: 'positive', method: '对照同类教学终端公开参数', priority: 'P2', riskExplanation: '高亮度有助于强光环境可读性，但应与使用环境匹配。', action: '说明教室照度条件，并允许通过可读性测试验证。' }),
    Object.freeze({ category: '显示交互', bidRequirement: '必须提供专有课堂互动接口', xunfeiSpec: '讯飞提供标准化互动平台接口', deviation: 'negative_wording', method: '审查参数措辞与接口开放性', priority: 'P0', riskExplanation: '“专有”接口表述可能排除采用标准协议的供应商。', action: '改为兼容主流标准协议或提供等效接口证明。' }),
    Object.freeze({ category: '音频采集', bidRequirement: '麦克风拾音距离≥8米', xunfeiSpec: '讯飞阵列麦克风有效拾音距离6米', deviation: 'positive', method: '对照产品规格书及教室声学场景', priority: 'P1', riskExplanation: '较长拾音距离可能提升覆盖范围，也可能带来噪声控制要求。', action: '补充信噪比和实际教室语音识别率验收要求。' }),
    Object.freeze({ category: '音频采集', bidRequirement: '必须采用指定品牌降噪算法', xunfeiSpec: '讯飞提供自研降噪与回声消除能力', deviation: 'negative_wording', method: '审查品牌限定与功能等效性', priority: 'P0', riskExplanation: '指定算法品牌而非性能指标，会限制等效方案参与。', action: '改用噪声抑制率、回声消除等可测试性能指标。' }),
    Object.freeze({ category: '网络与平台', bidRequirement: '终端支持双频Wi-Fi 6', xunfeiSpec: '讯飞终端支持双频Wi-Fi 6', deviation: 'negative_real', method: '核验网络制式和并发能力', priority: 'P2', riskExplanation: '参数本身具备合理性，但未说明并发与漫游要求，验收可能产生争议。', action: '补充并发终端数、吞吐量及漫游测试条件。' }),
    Object.freeze({ category: '网络与平台', bidRequirement: '平台账号须迁移至既有生态', xunfeiSpec: '讯飞支持标准账号迁移与数据导出', deviation: 'negative_real', method: '审查账号体系、数据迁移和兼容条款', priority: 'P0', riskExplanation: '绑定既有生态会提高替换成本，并可能限制其他平台接入。', action: '要求提供开放账号迁移、数据导出及兼容性验证方案。' }),
  ]),
  positiveDeviations: Object.freeze([
    '摄像头视场角≥145°，覆盖范围优于常规方案。',
    '交互平板亮度≥500nit，强光环境可读性更高。',
    '麦克风拾音距离≥8米，适合中大型教室。',
    '终端支持双频 Wi-Fi 6，网络并发能力更强。',
  ]),
  negativeDeviations: Object.freeze([
    '摄像头视场角要求与讯飞≥135°的常规配置相比缺少等效性说明。',
    '平台账号迁移条件偏向既有希沃生态，增加替换成本。',
  ]),
  risks: Object.freeze([
    Object.freeze({
      title: '参数排他风险',
      explanation: '将特定接口、账号体系和品牌规格组合写入需求，可能压缩其他厂商的公平竞争空间。',
      response: '要求采购方拆分功能性指标与品牌生态条件，并接受可验证的等效参数。',
    }),
    Object.freeze({
      title: '验收争议风险',
      explanation: '视场角和兼容性定义不清，可能导致交付后对是否满足招标要求产生争议。',
      response: '在澄清阶段明确摄像头视场角≥145°的测量方法，并以讯飞≥135°作为可比基线说明。',
    }),
  ]),
});

export function getReportMetrics(report) {
  return {
    confidence: report.controller.confidence,
    positiveCount: report.positiveDeviations.length,
    negativeCount: report.negativeDeviations.length,
    riskCount: report.risks.length,
  };
}

export function getDashboardMetrics(report) {
  const items = report.analysisItems ?? [];
  return {
    total: items.length,
    positiveCount: items.filter((item) => item.deviation === 'positive').length,
    wordingCount: items.filter((item) => item.deviation === 'negative_wording').length,
    negativeCount: items.filter((item) => item.deviation === 'negative_real').length,
  };
}

export function getCategoryDistribution(report) {
  return (report.analysisItems ?? []).reduce((distribution, item) => {
    distribution[item.category] = (distribution[item.category] ?? 0) + 1;
    return distribution;
  }, {});
}

export function filterAnalysisItems(report, filter) {
  const items = report.analysisItems ?? [];
  const filters = {
    all: () => true,
    positive: (item) => item.deviation === 'positive',
    wording: (item) => item.deviation === 'negative_wording',
    negative: (item) => item.deviation === 'negative_real',
  };

  return Object.hasOwn(filters, filter) ? items.filter(filters[filter]) : [];
}
