const positiveRows = [
  ['视频采集','摄像头视场角≥145°','讯飞双目摄像头视场角150°','视场角','中'],['视频采集','摄像头像素≥800万','讯飞800万像素广角摄像头','像素','低'],['显示交互','交互平板亮度≥400nit','讯飞86英寸交互平板亮度450nit','亮度','低'],['显示交互','触控响应≤20ms','讯飞红外触控响应≤15ms','触控响应','低'],['显示交互','支持20点触控','讯飞支持40点触控','多点触控','低'],['音频采集','麦克风拾音距离≥8米','讯飞阵列麦克风有效拾音9米','拾音距离','中'],['音频采集','支持回声消除与降噪','讯飞支持全双工回声消除及AI降噪','降噪能力','低'],['网络与平台','终端支持双频Wi‑Fi 6','讯飞终端支持双频Wi‑Fi 6','网络协议','低'],['网络与平台','支持千兆有线网络','讯飞支持千兆RJ45有线网络','有线网络','低'],['教学软件','支持课件批注与保存','讯飞教学软件支持批注、保存和回放','课件批注','低'],['教学软件','支持课堂互动答题','讯飞支持随堂答题和统计','互动答题','低'],['教学软件','支持学情数据统计','讯飞提供班级、学生维度学情报表','学情统计','低'],['设备管理','支持远程开关机','讯飞设备管理平台支持远程开关机','远程控制','低'],['设备管理','支持设备状态巡检','讯飞平台支持在线状态和故障告警','状态巡检','低'],['安全与服务','支持账号分级管理','讯飞支持管理员、教师等角色分级','权限管理','低'],['安全与服务','提供三年原厂质保','讯飞提供三年原厂质保服务','质保服务','低'],['扩展接口','配置HDMI输入接口','讯飞设备提供HDMI IN接口','HDMI接口','低'],['扩展接口','配置USB 3.0接口','讯飞设备配置前置USB 3.0接口','USB接口','低'],
];

const wordingRows = [
  ['显示交互','必须提供专有课堂互动接口','讯飞提供标准化开放互动平台接口','课堂互动接口','高'],['音频采集','必须采用指定品牌降噪算法','讯飞提供自研降噪与回声消除能力','降噪算法','高'],['网络与平台','平台账号须迁移至既有生态','讯飞支持标准账号迁移及数据导出','账号迁移','高'],['教学软件','须兼容某品牌云课件格式','讯飞支持通用课件格式与开放导入','课件格式','中'],['教学软件','必须使用指定课堂评价模型','讯飞提供可配置评价指标体系','课堂评价','高'],['设备管理','须接入指定厂商管理后台','讯飞提供标准API及平台对接能力','管理后台','中'],['安全与服务','须提供指定认证品牌证书','讯飞可提供符合等保要求的材料','认证材料','中'],['扩展接口','接口协议须为厂商私有协议','讯飞支持主流标准协议与开放接口','接口协议','高'],['视频采集','须配套指定录播软件客户端','讯飞支持标准录播协议及第三方接入','录播客户端','中'],['音频采集','音频处理须使用指定引擎','讯飞提供同等性能的音频处理引擎','音频引擎','中'],['网络与平台','须使用既有统一身份认证组件','讯飞支持SAML、OAuth等标准认证','身份认证','高'],['安全与服务','须提供指定厂商驻场团队','讯飞可提供同等级本地化服务方案','驻场服务','中'],
];

const negativeRows = [
  ['视频采集','摄像头像素≥1200万','讯飞采用800万像素广角摄像头','摄像头像素','高'],['显示交互','整机屏幕尺寸≥98英寸','讯飞主推86英寸交互平板','屏幕尺寸','高'],['显示交互','整机亮度≥600nit','讯飞常规配置亮度450nit','屏幕亮度','中'],['音频采集','麦克风拾音距离≥12米','讯飞阵列麦克风有效拾音9米','拾音距离','高'],['音频采集','支持64路独立音频采集','讯飞常规方案支持16路采集','音频通道','高'],['网络与平台','同时在线终端数≥2000','讯飞单校区推荐并发1000终端','并发终端','中'],['网络与平台','平台需提供99.99%可用性','讯飞标准服务可用性99.9%','平台可用性','中'],['教学软件','题库资源不少于100万道','讯飞现有可用题库约80万道','题库数量','中'],['教学软件','支持离线连续教学72小时','讯飞离线缓存可支持24小时','离线时长','高'],['设备管理','设备批量升级完成时间≤10分钟','讯飞常规批量升级约20分钟','升级效率','中'],['设备管理','支持5000台设备统一纳管','讯飞当前单实例建议3000台','纳管规模','中'],['安全与服务','故障响应时间≤30分钟','讯飞标准SLA响应时间为1小时','故障响应','中'],['安全与服务','提供7×24小时现场保障','讯飞提供7×24小时远程及工作日现场服务','现场保障','高'],['扩展接口','提供不少于12路USB接口','讯飞整机提供6路USB接口','USB数量','中'],['扩展接口','支持4路HDMI输入','讯飞整机支持2路HDMI输入','HDMI输入','中'],['视频采集','视频输出支持8K编码','讯飞常规视频输出支持4K编码','视频编码','中'],['显示交互','触控精度≤0.5mm','讯飞常规触控精度约1mm','触控精度','低'],['网络与平台','支持IPv6双栈全链路部署','讯飞当前项目配置支持IPv4，IPv6需定制','IPv6能力','中'],
];

function toItem(row, deviation, offset) {
  const [category, bidRequirement, xunfeiSpec, name, riskLevel] = row;
  const isWording = deviation === 'negative_wording';
  const isPositive = deviation === 'positive';
  const riskExplanation = isPositive
    ? `讯飞规格满足或优于“${name}”要求，可作为可验证的正向匹配项。`
    : isWording
      ? `条款以“必须、指定、专有”等限定性措辞描述${name}，可能排除具备等效能力的供应商。`
      : `招标要求与讯飞现有规格在“${name}”上存在可量化差距，需核实该阈值是否为项目必要条件。`;
  const action = isPositive
    ? '保留该条款，并在应答文件中附上产品规格书和验收证明。'
    : isWording
      ? '建议改为可验证的功能或性能指标，并接受标准协议或等效能力证明。'
      : '建议在澄清阶段说明业务必要性，或调整为满足教学场景的可验收指标。';
  const questionScript = `关于第 ${offset} 项“${name}”，请采购方说明该项要求与本项目实际教学场景的直接对应关系、验收口径及设置依据。建议以可公开验证的性能指标或标准协议表述，并允许满足同等功能与质量水平的产品参与。`;
  return Object.freeze({ seq: offset, name, category, bidRequirement, xunfeiSpec, deviation, riskLevel, matchMethod: isPositive ? '程序粗筛' : 'AI 精判', method: isPositive ? '程序粗筛' : 'AI 精判', priority: riskLevel === '高' ? 'P0' : riskLevel === '中' ? 'P1' : 'P2', riskExplanation, action, questionScript });
}

const analysisItems = Object.freeze([
  ...positiveRows.map((row, index) => toItem(row, 'positive', index + 1)),
  ...wordingRows.map((row, index) => toItem(row, 'negative_wording', index + 19)),
  ...negativeRows.map((row, index) => toItem(row, 'negative_real', index + 31)),
]);

export const analysisReport = Object.freeze({
  projectName: '智慧教室设备采购项目',
  controller: Object.freeze({ vendor: '希沃', confidence: 0.92, summary: '多项关键参数与希沃产品规格高度重合，存在明显控标倾向。' }),
  suspiciousItems: Object.freeze(['专有接口与既有账号生态存在较强排他性。', '多项超出常规教学场景的硬件门槛需要补充设置依据。']),
  analysisItems,
  positiveDeviations: Object.freeze(analysisItems.filter((item) => item.deviation === 'positive').map((item) => item.name)),
  negativeDeviations: Object.freeze(analysisItems.filter((item) => item.deviation !== 'positive').map((item) => item.name)),
  risks: Object.freeze([{ title: '参数排他风险', explanation: '专有接口、生态与品牌化描述可能压缩公平竞争空间。', response: '采用可验证功能指标与等效性证明。' }]),
});

export function getDashboardMetrics(report) { const items = report.analysisItems ?? []; return { total: items.length, positiveCount: items.filter((item) => item.deviation === 'positive').length, wordingCount: items.filter((item) => item.deviation === 'negative_wording').length, negativeCount: items.filter((item) => item.deviation === 'negative_real').length }; }
export function getCategoryDistribution(report) { return (report.analysisItems ?? []).reduce((distribution, item) => { distribution[item.category] = (distribution[item.category] ?? 0) + 1; return distribution; }, {}); }
export function filterAnalysisItems(report, filter) { const filters = { all: () => true, positive: (item) => item.deviation === 'positive', wording: (item) => item.deviation === 'negative_wording', negative: (item) => item.deviation === 'negative_real' }; return Object.hasOwn(filters, filter) ? report.analysisItems.filter(filters[filter]) : []; }
