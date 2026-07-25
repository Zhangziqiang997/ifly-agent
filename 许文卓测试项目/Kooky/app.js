// ==================== 配置管理 ====================
const CONFIG = {
    DEEPSEEK_API_URL: 'https://api.deepseek.com/v1/chat/completions',
    DEEPSEEK_MODEL: 'deepseek-v4-flash',
    API_KEY_STORAGE: 'deepseek_api_key',
    USE_AI_MODE: false
};

// 全局状态
let currentCompetitor = null;
let analysisComplete = false;
let apiKey = null;

// ==================== DOM元素 ====================
const uploadArea = document.getElementById('uploadArea');
const fileInput = document.getElementById('fileInput');
const useDemoBtn = document.getElementById('useDemoBtn');
const competitorResult = document.getElementById('competitorResult');
const analyzeBtn = document.getElementById('analyzeBtn');
const reportSection = document.getElementById('reportSection');
const settingsBtn = document.getElementById('settingsBtn');
const settingsModal = document.getElementById('settingsModal');
const closeModal = document.getElementById('closeModal');
const apiKeyInput = document.getElementById('apiKeyInput');
const saveApiKey = document.getElementById('saveApiKey');
const saveSettings = document.getElementById('saveSettings');
const testApi = document.getElementById('testApi');
const apiTestResult = document.getElementById('apiTestResult');
const aiModeText = document.getElementById('aiModeText');
const switchModeBtn = document.getElementById('switchModeBtn');
const aiStatusBar = document.getElementById('aiStatusBar');

// ==================== 初始化 ====================
window.addEventListener('load', () => {
    loadApiKey();
    updateAIStatus();
    console.log('参数智能体AI增强版已就绪');
});

// ==================== API配置相关 ====================
function loadApiKey() {
    const saved = localStorage.getItem(CONFIG.API_KEY_STORAGE);
    if (saved) {
        apiKey = saved;
        apiKeyInput.value = saved;
        saveApiKey.checked = true;
        CONFIG.USE_AI_MODE = true;
    }
}

function updateAIStatus() {
    if (CONFIG.USE_AI_MODE && apiKey) {
        aiModeText.textContent = 'AI模式已启用';
        aiStatusBar.classList.remove('from-purple-50', 'to-blue-50', 'border-purple-200');
        aiStatusBar.classList.add('from-green-50', 'to-blue-50', 'border-green-200');
        aiStatusBar.querySelector('.bg-yellow-400').classList.remove('bg-yellow-400');
        aiStatusBar.querySelector('.animate-pulse').classList.add('bg-green-400');
        switchModeBtn.textContent = 'AI已就绪';
        switchModeBtn.classList.add('cursor-default');
    } else {
        aiModeText.textContent = '演示模式（未配置API）';
        switchModeBtn.textContent = '点击右上角"设置"配置API';
    }
}

// 设置按钮
settingsBtn.addEventListener('click', () => {
    settingsModal.classList.remove('hidden');
});

closeModal.addEventListener('click', () => {
    settingsModal.classList.add('hidden');
});

// 保存设置
saveSettings.addEventListener('click', () => {
    const key = apiKeyInput.value.trim();
    if (!key) {
        showToast('请输入API Key', 'error');
        return;
    }
    
    if (!key.startsWith('sk-')) {
        showToast('API Key格式错误，应以sk-开头', 'error');
        return;
    }
    
    apiKey = key;
    CONFIG.USE_AI_MODE = true;
    
    if (saveApiKey.checked) {
        localStorage.setItem(CONFIG.API_KEY_STORAGE, key);
    } else {
        localStorage.removeItem(CONFIG.API_KEY_STORAGE);
    }
    
    updateAIStatus();
    settingsModal.classList.add('hidden');
    showToast('API配置已保存', 'success');
});

// 测试API连接
testApi.addEventListener('click', async () => {
    const key = apiKeyInput.value.trim();
    if (!key) {
        showToast('请先输入API Key', 'error');
        return;
    }
    
    apiTestResult.innerHTML = '<div class="text-center text-gray-600"><i class="fas fa-spinner fa-spin mr-2"></i>测试中...</div>';
    apiTestResult.classList.remove('hidden');
    
    try {
        const result = await callDeepSeekAPI('测试连接', key);
        if (result.success) {
            apiTestResult.innerHTML = '<div class="bg-green-100 text-green-700 p-3 rounded-lg"><i class="fas fa-check-circle mr-2"></i>连接成功！API可用</div>';
        } else {
            apiTestResult.innerHTML = `<div class="bg-red-100 text-red-700 p-3 rounded-lg"><i class="fas fa-times-circle mr-2"></i>连接失败：${result.error}</div>`;
        }
    } catch (error) {
        apiTestResult.innerHTML = `<div class="bg-red-100 text-red-700 p-3 rounded-lg"><i class="fas fa-times-circle mr-2"></i>连接失败：${error.message}</div>`;
    }
});

// ==================== DeepSeek API调用 ====================
async function callDeepSeekAPI(prompt, customKey = null) {
    const key = customKey || apiKey;
    
    try {
        const response = await fetch(CONFIG.DEEPSEEK_API_URL, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'Authorization': `Bearer ${key}`
            },
            body: JSON.stringify({
                model: CONFIG.DEEPSEEK_MODEL,
                messages: [{
                    role: 'user',
                    content: prompt
                }],
                temperature: 0.7,
                max_tokens: 2000
            })
        });
        
        const data = await response.json();
        
        if (data.error) {
            return {
                success: false,
                error: data.error.message || '未知错误'
            };
        }
        
        return {
            success: true,
            content: data.choices[0].message.content
        };
    } catch (error) {
        return {
            success: false,
            error: error.message
        };
    }
}

// ==================== AI竞品识别 ====================
async function aiIdentifyCompetitor(tenderData) {
    const prompt = `你是一个招投标专家，请分析以下招标参数，识别这是哪家厂商控的标。

招标项目：${tenderData.title}

招标参数：
${tenderData.requirements.map((r, i) => `${i + 1}. ${r.category}：${r.requirement}`).join('\n')}

候选厂商：
1. 希沃（特征：希沃白板、希沃云课堂、希沃管家、希沃语音助手）
2. 鸿合（特征：鸿合π软件、鸿合智能笔、鸿合云平台）
3. 文香（特征：文香录播系统、文香云资源库、文香AI课堂分析）

请按以下JSON格式输出（只输出JSON，不要其他文字）：
{
    "competitor": "厂商名称",
    "confidence": "高/中/低",
    "matched_features": ["特征1", "特征2", "特征3"],
    "reason": "识别理由"
}`;

    const result = await callDeepSeekAPI(prompt);
    
    if (result.success) {
        try {
            // 提取JSON内容
            let content = result.content.trim();
            const jsonMatch = content.match(/\{[\s\S]*\}/);
            if (jsonMatch) {
                content = jsonMatch[0];
            }
            const parsed = JSON.parse(content);
            return {
                success: true,
                data: parsed
            };
        } catch (e) {
            console.error('JSON解析失败:', e, result.content);
            return {
                success: false,
                error: 'AI返回格式错误'
            };
        }
    } else {
        return result;
    }
}

// ==================== AI参数分析 ====================
async function aiAnalyzeParameter(requirement, iflytekSpec) {
    const prompt = `你是招投标技术专家，请分析讯飞产品与招标要求的匹配度。

招标要求：${requirement}
讯飞参数：${iflytekSpec}

请按以下JSON格式输出（只输出JSON）：
{
    "status": "positive/negative_fixable/negative_hard",
    "deviation": "差距分析（一句话）",
    "solution": {
        "type": "改说辞/质疑话术/null",
        "content": "具体建议"
    }
}

判断标准：
- positive: 讯飞规格优于要求
- negative_fixable: 有能力但描述不同，可改说辞
- negative_hard: 确实不满足，需质疑话术`;

    const result = await callDeepSeekAPI(prompt);
    
    if (result.success) {
        try {
            let content = result.content.trim();
            const jsonMatch = content.match(/\{[\s\S]*\}/);
            if (jsonMatch) {
                content = jsonMatch[0];
            }
            const parsed = JSON.parse(content);
            return {
                success: true,
                data: parsed
            };
        } catch (e) {
            console.error('JSON解析失败:', e);
            return {
                success: false,
                error: 'AI返回格式错误'
            };
        }
    } else {
        return result;
    }
}

// ==================== 文件上传相关 ====================
uploadArea.addEventListener('click', () => {
    fileInput.click();
});

fileInput.addEventListener('change', (e) => {
    const file = e.target.files[0];
    if (file) {
        handleFileUpload(file);
    }
});

uploadArea.addEventListener('dragover', (e) => {
    e.preventDefault();
    uploadArea.classList.add('border-blue-500', 'bg-blue-50');
});

uploadArea.addEventListener('dragleave', () => {
    uploadArea.classList.remove('border-blue-500', 'bg-blue-50');
});

uploadArea.addEventListener('drop', (e) => {
    e.preventDefault();
    uploadArea.classList.remove('border-blue-500', 'bg-blue-50');
    const file = e.dataTransfer.files[0];
    if (file) {
        handleFileUpload(file);
    }
});

// 使用演示数据
useDemoBtn.addEventListener('click', () => {
    showLoading();
    setTimeout(() => {
        identifyCompetitor(window.demoData.demoTenderData);
    }, 1500);
});

function handleFileUpload(file) {
    showLoading();
    setTimeout(() => {
        identifyCompetitor(window.demoData.demoTenderData);
    }, 2000);
}

function showLoading() {
    competitorResult.innerHTML = `
        <div class="flex flex-col items-center">
            <div class="animate-spin rounded-full h-12 w-12 border-b-2 border-purple-600 mb-4"></div>
            <p class="text-gray-600">正在识别竞品...</p>
            ${CONFIG.USE_AI_MODE ? '<p class="text-xs text-purple-600 mt-2"><i class="fas fa-robot mr-1"></i>AI分析中</p>' : ''}
        </div>
    `;
}

// ==================== 竞品识别 ====================
async function identifyCompetitor(tenderData) {
    if (CONFIG.USE_AI_MODE && apiKey) {
        // AI模式
        const result = await aiIdentifyCompetitor(tenderData);
        
        if (result.success) {
            currentCompetitor = result.data.competitor;
            displayAICompetitorResult(result.data);
        } else {
            showToast(`AI识别失败：${result.error}，切换到演示模式`, 'warning');
            fallbackIdentifyCompetitor(tenderData);
        }
    } else {
        // 演示模式
        fallbackIdentifyCompetitor(tenderData);
    }
}

// 降级方案：规则识别
function fallbackIdentifyCompetitor(tenderData) {
    const competitors = window.demoData.competitorFeatures;
    const matchCounts = {};
    
    Object.keys(competitors).forEach(brand => {
        matchCounts[brand] = 0;
        competitors[brand].features.forEach(feature => {
            tenderData.requirements.forEach(req => {
                if (req.requirement.includes(feature) || 
                    (req.competitor_hint && req.competitor_hint === brand)) {
                    matchCounts[brand]++;
                }
            });
        });
    });
    
    let maxBrand = null;
    let maxCount = 0;
    Object.keys(matchCounts).forEach(brand => {
        if (matchCounts[brand] > maxCount) {
            maxCount = matchCounts[brand];
            maxBrand = brand;
        }
    });
    
    currentCompetitor = maxBrand;
    displayCompetitorResult(maxBrand, matchCounts);
}

// AI识别结果展示
function displayAICompetitorResult(aiResult) {
    const competitor = window.demoData.competitorFeatures[aiResult.competitor];
    
    competitorResult.innerHTML = `
        <div class="text-center">
            <div class="text-6xl mb-3">${competitor.logo}</div>
            <div class="text-2xl font-bold text-gray-800 mb-2">${aiResult.competitor}</div>
            <div class="inline-block bg-red-100 text-red-700 px-4 py-1 rounded-full text-sm font-semibold mb-2">
                疑似控标方
            </div>
            <div class="inline-block ai-badge text-xs px-2 py-1 rounded ml-2">
                <i class="fas fa-robot mr-1"></i>AI识别
            </div>
            <div class="text-sm text-gray-600 mb-4 mt-3">
                置信度：<span class="font-bold">${aiResult.confidence}</span>
            </div>
            <div class="border-t pt-4 mt-4">
                <p class="text-xs text-gray-500 mb-2">AI识别理由：</p>
                <p class="text-sm text-gray-700 mb-3">${aiResult.reason}</p>
                <p class="text-xs text-gray-500 mb-2">匹配的关键特征：</p>
                ${aiResult.matched_features.map(f => 
                    `<span class="inline-block bg-purple-100 text-purple-700 px-2 py-1 rounded text-xs m-1">${f}</span>`
                ).join('')}
            </div>
        </div>
    `;
    
    enableAnalyzeButton();
}

// 规则识别结果展示
function displayCompetitorResult(winner, matchCounts) {
    const competitor = window.demoData.competitorFeatures[winner];
    
    competitorResult.innerHTML = `
        <div class="text-center">
            <div class="text-6xl mb-3">${competitor.logo}</div>
            <div class="text-2xl font-bold text-gray-800 mb-2">${competitor.name}</div>
            <div class="inline-block bg-red-100 text-red-700 px-4 py-1 rounded-full text-sm font-semibold mb-4">
                疑似控标方
            </div>
            <div class="text-sm text-gray-600 mb-4">
                匹配特征数：${matchCounts[winner]} 项
            </div>
            <div class="border-t pt-4 mt-4">
                <p class="text-xs text-gray-500 mb-2">匹配的关键特征：</p>
                ${competitor.features.slice(0, 3).map(f => 
                    `<span class="inline-block bg-purple-100 text-purple-700 px-2 py-1 rounded text-xs m-1">${f}</span>`
                ).join('')}
            </div>
        </div>
    `;
    
    enableAnalyzeButton();
}

function enableAnalyzeButton() {
    analyzeBtn.disabled = false;
    analyzeBtn.classList.remove('bg-gray-300', 'text-gray-500', 'cursor-not-allowed');
    analyzeBtn.classList.add('bg-gradient-to-r', 'from-green-500', 'to-green-600', 'text-white', 'hover:from-green-600', 'hover:to-green-700', 'cursor-pointer');
}

// ==================== 参数分析 ====================
analyzeBtn.addEventListener('click', async () => {
    if (!currentCompetitor) return;
    
    analyzeBtn.innerHTML = '<i class="fas fa-spinner fa-spin mr-2"></i>AI分析中...';
    analyzeBtn.disabled = true;
    
    await generateReport();
    
    analyzeBtn.innerHTML = '<i class="fas fa-check mr-2"></i>分析完成';
});

async function generateReport() {
    const tenderData = window.demoData.demoTenderData;
    const params = window.demoData.iflytek_params;
    
    let positiveCount = 0;
    let fixableCount = 0;
    let hardCount = 0;
    let html = '';
    
    for (let i = 0; i < tenderData.requirements.length; i++) {
        const req = tenderData.requirements[i];
        let analysis = params[req.requirement];
        
        // AI模式：实时分析
        if (CONFIG.USE_AI_MODE && apiKey) {
            const aiResult = await aiAnalyzeParameter(req.requirement, analysis.iflytek_spec);
            if (aiResult.success) {
                analysis = {
                    ...analysis,
                    ...aiResult.data,
                    ai_generated: true
                };
            }
        }
        
        if (analysis.status === 'positive') positiveCount++;
        else if (analysis.status === 'negative_fixable') fixableCount++;
        else if (analysis.status === 'negative_hard') hardCount++;
        
        html += generateParameterCard(req, analysis, i + 1);
    }
    
    document.getElementById('positiveCount').textContent = positiveCount;
    document.getElementById('fixableCount').textContent = fixableCount;
    document.getElementById('hardCount').textContent = hardCount;
    document.getElementById('parameterList').innerHTML = html;
    
    reportSection.classList.remove('hidden');
    reportSection.scrollIntoView({ behavior: 'smooth', block: 'start' });
}

function generateParameterCard(requirement, analysis, index) {
    let statusBadge, statusIcon, bgColor;
    
    if (analysis.status === 'positive') {
        statusBadge = '<span class="badge-positive px-3 py-1 rounded-full text-sm font-semibold">✅ 正偏离</span>';
        statusIcon = '✅';
        bgColor = 'bg-green-50 border-green-200';
    } else if (analysis.status === 'negative_fixable') {
        statusBadge = '<span class="badge-negative-fixable px-3 py-1 rounded-full text-sm font-semibold">⚠️ 负偏离（可改说辞）</span>';
        statusIcon = '⚠️';
        bgColor = 'bg-yellow-50 border-yellow-200';
    } else {
        statusBadge = '<span class="badge-negative-hard px-3 py-1 rounded-full text-sm font-semibold">❌ 负偏离（确实不满足）</span>';
        statusIcon = '❌';
        bgColor = 'bg-red-50 border-red-200';
    }
    
    let solutionHtml = '';
    if (analysis.solution && analysis.solution.type !== 'null' && analysis.solution.type !== null) {
        const content = typeof analysis.solution.content === 'string' 
            ? analysis.solution.content 
            : analysis.solution.content.join('<br><br>');
        
        solutionHtml = `
            <div class="mt-4 p-4 bg-blue-50 border border-blue-200 rounded-lg">
                <div class="flex items-start">
                    <i class="fas fa-lightbulb text-blue-500 text-xl mr-3 mt-1"></i>
                    <div>
                        <h5 class="font-bold text-blue-800 mb-2">
                            应对方案：${analysis.solution.type}
                            ${analysis.ai_generated ? '<span class="ai-badge text-xs px-2 py-1 rounded ml-2"><i class="fas fa-robot mr-1"></i>AI生成</span>' : ''}
                        </h5>
                        <p class="text-sm text-gray-700">${content}</p>
                    </div>
                </div>
            </div>
        `;
    }
    
    return `
        <div class="border ${bgColor} rounded-lg p-5 mb-4">
            <div class="flex items-start justify-between mb-3">
                <div class="flex-1">
                    <div class="flex items-center mb-2">
                        <span class="text-2xl mr-3">${statusIcon}</span>
                        <span class="text-xs text-gray-500 bg-white px-2 py-1 rounded">参数 #${index}</span>
                        <span class="ml-2 text-xs text-gray-500 bg-white px-2 py-1 rounded">${requirement.category}</span>
                    </div>
                    <h4 class="font-bold text-gray-800 text-lg mb-2">招标要求</h4>
                    <p class="text-gray-700 mb-3">${requirement.requirement}</p>
                </div>
                <div class="ml-4">
                    ${statusBadge}
                </div>
            </div>
            
            <div class="grid md:grid-cols-2 gap-4 mt-4">
                <div class="bg-white p-3 rounded border">
                    <h5 class="font-semibold text-sm text-gray-600 mb-2">
                        <i class="fas fa-building mr-1"></i>讯飞实际参数
                    </h5>
                    <p class="text-sm text-gray-800">${analysis.iflytek_spec}</p>
                </div>
                <div class="bg-white p-3 rounded border">
                    <h5 class="font-semibold text-sm text-gray-600 mb-2">
                        <i class="fas fa-chart-line mr-1"></i>差距分析
                    </h5>
                    <p class="text-sm text-gray-800">${analysis.deviation}</p>
                </div>
            </div>
            
            ${solutionHtml}
        </div>
    `;
}

// ==================== 工具函数 ====================
function showToast(message, type = 'info') {
    const colors = {
        success: 'bg-green-500',
        error: 'bg-red-500',
        warning: 'bg-yellow-500',
        info: 'bg-blue-500'
    };
    
    const toast = document.createElement('div');
    toast.className = `fixed top-4 right-4 ${colors[type]} text-white px-6 py-3 rounded-lg shadow-lg z-50 animate-fade-in`;
    toast.textContent = message;
    document.body.appendChild(toast);
    
    setTimeout(() => {
        toast.remove();
    }, 3000);
}