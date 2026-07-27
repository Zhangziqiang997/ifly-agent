const mockData = {
  nav: [
    ['业务中心', [['▣','项目总览',true],['▣','投标项目'],['▥','文档中心']]],
    ['智能分析', [['♧','招标参数对比'],['▧','AI分析报告'],['♧','AI风险识别'],['▣','话术与方案']]],
    ['产品与知识', [['♧','产品与参数中心'],['▣','参数知识库'],['▤','产品与竞品'],['▤','规则与标准']]]
  ],
  report: [
    ['▧','48','条参数','结构化提取的关键参数','#1670ef'],
    ['▤','12','项语义复核','AI对关键条款的语义复核','#7548e8'],
    ['▤','6','条应对建议','基于风险识别的应对建议','#08a54d']
  ],
  work: [
    ['⚖','招标参数对比','快速对比招标参数与产品差异',true],
    ['▧','AI文档分析报告','查看本次文档的 AI分析结果'],
    ['▰','生成质疑话术','AI生成质疑话术与问询内容'],
    ['●','查看参数知识库','浏览已沉淀的参数知识库']
  ],
  assessment: [['投标方识别','疑似承诺','高','查看依据'],['摄像头视场角','竞品独有特征','高','生成质疑话术'],['语音转写能力','讯飞具备优势','中','加入方案']],
  capabilities: [['♩','AI语音转写','高准确率语音转写\n支持多语种与行业词库'],['◉','远场语音交互','远距离拾音与降噪\n自然语音交互'],['♟','课堂互动评测','多维度课堂互动评测\n实时反馈学习效果'],['▥','学情数据分析','学情数据采集与分析\n精准教学决策支持']]
};

const nav = document.querySelector('#side-nav');
nav.innerHTML = mockData.nav.map(([title, items]) => `<div class="group-title">${title}</div>${items.map(([icon, label, active]) => `<a href="#" class="${active ? 'active' : ''}"><span class="nav-ico">${icon}</span>${label}</a>`).join('')}`).join('');

document.querySelector('#report-items').innerHTML = mockData.report.map(([icon, number, label, note, color]) => `<div class="report-item"><span class="metric-icon" style="background:${color}">${icon}</span><div class="metric-copy"><strong>${number}</strong><span>${label}</span><small>${note}</small></div></div>`).join('');
document.querySelector('#work-list').innerHTML = mockData.work.map(([icon, title, note, active]) => `<button class="work-item demo-action ${active ? 'active' : ''}"><span class="work-icon">${icon}</span><span class="work-copy"><strong>${title}</strong><small>${note}</small></span><span class="work-arrow">›</span></button>`).join('');
document.querySelector('#assessment-body').innerHTML = mockData.assessment.map(([object, verdict, risk, action]) => `<tr><td>${object}</td><td>${verdict}</td><td><span class="badge ${risk === '中' ? 'mid' : ''}">${risk}</span></td><td>${action}</td></tr>`).join('');
document.querySelector('#capability-list').innerHTML = mockData.capabilities.map(([icon, title, note]) => `<div class="capability"><span class="cap-ico">${icon}</span><strong>${title}</strong><small>${note.replace('\n','<br>')}</small></div>`).join('');

const toast = document.querySelector('#toast');
let toastTimer;
document.addEventListener('click', (event) => {
  const action = event.target.closest('.demo-action');
  if (!action) return;
  event.preventDefault();
  toast.textContent = `功能演示：${action.textContent.trim().replace(/\s+/g, ' ')} 已触发`;
  toast.classList.add('show');
  clearTimeout(toastTimer);
  toastTimer = setTimeout(() => toast.classList.remove('show'), 1800);
});
