// 演示模式：现场网络不稳定，话术改为本地固定文案 + 固定生成时长，
// 不依赖后端与网络，保证任何环境下都能稳定演示。
// 如需恢复真实 AI 调用，将 DEMO_MODE 改为 false 即可。
const DEMO_MODE = true;
const DEMO_DELAY_MS = 2000; // 模拟“AI 生成”的转圈时长（毫秒），按需调整

// 后端联调适配器：可用 window.BIDDING_REPORT_API 覆盖默认服务。
const DEFAULT_API = 'http://127.0.0.1:5001';
const ANALYSIS = { project: '智慧教室设备采购项目' };

const wait = (ms) => new Promise((resolve) => setTimeout(resolve, ms));

export async function generateQuestionScript(item) {
  if (DEMO_MODE) {
    await wait(DEMO_DELAY_MS);
    return { script: item.questionScript, source: 'llm' };
  }

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
