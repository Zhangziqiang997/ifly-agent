// 后端联调适配器：可用 window.BIDDING_REPORT_API 覆盖默认服务。
const DEFAULT_API = 'http://127.0.0.1:5001';
const ANALYSIS = { project: '智慧教室设备采购项目' };

export async function generateQuestionScript(item) {
  const adapter = globalThis.BIDDING_REPORT_API?.generateQuestionScript;
  if (typeof adapter === 'function') {
    try {
      const result = await adapter({ seq: item.seq, item });
      if (result?.script) return { script: result.script, source: result.source || 'llm' };
    } catch (error) {
      console.warn('自定义 AI 话术接口调用失败，已使用固定话术。', error);
      return { script: item.questionScript, source: 'template' };
    }
  }

  try {
    const response = await fetch(
      `${DEFAULT_API}/api/analyses/demo/items/${encodeURIComponent(item.seq)}/script`,
      {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ item, analysis: ANALYSIS }),
      },
    );
    if (!response.ok) throw new Error(`HTTP ${response.status}`);

    const result = await response.json();
    if (result?.script) {
      return { script: result.script, source: result.source || 'llm' };
    }
    throw new Error('响应中缺少 script');
  } catch (error) {
    console.warn('AI 话术服务不可用，已使用固定话术。', error);
  }

  return { script: item.questionScript, source: 'template' };
}
