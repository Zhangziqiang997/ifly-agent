const mockData = {
  report: [
    ['▧','48','条参数','结构化提取的关键参数','#1670ef'],
    ['▤','12','项语义复核','AI对关键条款的语义复核','#7548e8'],
    ['▤','6','条应对建议','基于风险识别的应对建议','#08a54d']
  ]
};

document.querySelector('#report-items').innerHTML = mockData.report.map(([icon, number, label, note, color]) => `<div class="report-item"><span class="metric-icon" style="background:${color}">${icon}</span><div class="metric-copy"><strong>${number}</strong><span>${label}</span><small>${note}</small></div></div>`).join('');

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

const uploadInput = document.querySelector('#upload-input');
const uploadButton = document.querySelector('#upload-button');
const uploadDrop = document.querySelector('#upload-drop');
const uploadResult = document.querySelector('#upload-result');
const fileName = document.querySelector('#file-name');
const fileType = document.querySelector('#file-type');
const uploadStatus = document.querySelector('#upload-status');
const uploadProgressBar = document.querySelector('#upload-progress-bar');
const uploadRemove = document.querySelector('#upload-remove');
const knowledgeTotal = document.querySelector('#knowledge-total');
const analysisButton = document.querySelector('#analysis-button');
const analysisStatus = document.querySelector('#analysis-status');
const reportButton = document.querySelector('#report-button');
const reportState = document.querySelector('#report-state');
let uploadTimer;
let uploadProgressTimer;
const allowedFileExtensions = ['pdf', 'doc', 'docx', 'xlsx', 'xls'];

uploadButton.addEventListener('click', (event) => {
  event.stopPropagation();
  uploadInput.click();
});

uploadDrop.addEventListener('click', () => uploadInput.click());
uploadDrop.addEventListener('keydown', (event) => {
  if (event.key === 'Enter' || event.key === ' ') {
    event.preventDefault();
    uploadInput.click();
  }
});

['dragenter', 'dragover'].forEach((eventName) => {
  uploadDrop.addEventListener(eventName, (event) => {
    event.preventDefault();
    uploadDrop.classList.add('dragover');
  });
});

['dragleave', 'drop'].forEach((eventName) => {
  uploadDrop.addEventListener(eventName, (event) => {
    event.preventDefault();
    uploadDrop.classList.remove('dragover');
  });
});

uploadDrop.addEventListener('drop', (event) => handleUploadFile(event.dataTransfer.files[0]));
uploadInput.addEventListener('change', () => handleUploadFile(uploadInput.files[0]));
uploadRemove.addEventListener('click', resetUploadUi);

function handleUploadFile(file) {
  clearTimeout(uploadTimer);
  clearInterval(uploadProgressTimer);
  if (!file) {
    resetUploadUi();
    return;
  }

  const extension = file.name.split('.').pop().toLowerCase();
  if (!allowedFileExtensions.includes(extension)) {
    resetUploadUi();
    showToast('请上传 PDF / DOC / DOCX / XLSX 文件');
    return;
  }
  if (file.size > 50 * 1024 * 1024) {
    resetUploadUi();
    showToast('单个文件不能超过 50MB');
    return;
  }

  fileName.textContent = file.name;
  fileType.textContent = extension.toUpperCase().slice(0, 4);
  uploadStatus.textContent = `解析中 · ${formatFileSize(file.size)}`;
  uploadStatus.classList.add('parsing');
  uploadResult.hidden = false;
  uploadProgressBar.style.width = '0%';
  window.requestAnimationFrame(() => { uploadProgressBar.style.width = '72%'; });
  uploadTimer = window.setTimeout(() => {
    uploadProgressBar.style.width = '100%';
    uploadStatus.classList.remove('parsing');
    uploadStatus.textContent = '解析完成 · 已写入参数知识库';
    knowledgeTotal.textContent = '100';
  }, 3000);
}

analysisButton.addEventListener('click', () => {
  analysisButton.disabled = true;
  analysisButton.textContent = 'AI正在分析';
  analysisStatus.textContent = 'AI正在分析';
  setAnalysisState('loading');
  reportButton.disabled = true;
  reportState.hidden = true;
  window.setTimeout(() => {
    analysisButton.disabled = false;
    analysisButton.textContent = '分析完成';
    analysisStatus.textContent = '分析完成';
    setAnalysisState('done');
    reportState.hidden = false;
    reportButton.disabled = false;
  }, 10000);
});

function resetUploadUi() {
  clearTimeout(uploadTimer);
  uploadInput.value = '';
  uploadResult.hidden = true;
  fileName.textContent = '';
  uploadStatus.textContent = '';
  uploadStatus.classList.remove('parsing');
  uploadProgressBar.style.width = '0%';
  knowledgeTotal.textContent = '99';
}

function setAnalysisState(state) {
  document.querySelectorAll('[data-analysis-state]').forEach((element) => {
    element.hidden = element.dataset.analysisState !== state;
  });
}

function formatFileSize(bytes) {
  if (bytes < 1024 * 1024) return `${Math.max(1, Math.round(bytes / 1024))} KB`;
  return `${(bytes / (1024 * 1024)).toFixed(1)} MB`;
}

reportButton.addEventListener('click', () => {
  if (!reportButton.disabled) window.location.href = 'report.html';
});

document.querySelector('.button-row .demo-action').addEventListener('click', (event) => {
  event.preventDefault();
  window.location.href = 'knowledge-base.html';
});

function showToast(message) {
  toast.textContent = message;
  toast.classList.add('show');
  clearTimeout(toastTimer);
  toastTimer = setTimeout(() => toast.classList.remove('show'), 1800);
}
