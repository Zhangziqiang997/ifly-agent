const sources = [
  'data/knowledge-base/xunfei/xunfei.json',
  'data/knowledge-base/competitors/希沃.json',
  'data/knowledge-base/competitors/鸿合.json',
  'data/knowledge-base/competitors/海康.json',
  'data/knowledge-base/competitors/文香.json',
];

const state = { entries: [], query: '', vendor: '', category: '' };
const $ = (selector) => document.querySelector(selector);
const esc = (value = '') => String(value).replace(/[&<>"']/g, (char) => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;' })[char]);

async function loadKnowledgeBase() {
  const datasets = await Promise.all(sources.map(async (source) => {
    const response = await fetch(source);
    if (!response.ok) throw new Error(`无法读取 ${source}`);
    const data = await response.json();
    return Array.isArray(data) ? data : [data];
  }));
  state.entries = datasets.flat();
  setupFilters();
  render();
}

function setupFilters() {
  const vendors = [...new Set(state.entries.map((entry) => entry.vendor))];
  const categories = [...new Set(state.entries.map((entry) => entry.category))];
  $('#vendor-filter').insertAdjacentHTML('beforeend', vendors.map((vendor) => `<option value="${esc(vendor)}">${esc(vendor)}</option>`).join(''));
  $('#category-filter').insertAdjacentHTML('beforeend', categories.map((category) => `<option value="${esc(category)}">${esc(category)}</option>`).join(''));
  $('#vendor-count').textContent = vendors.length;
  $('#search').addEventListener('input', (event) => { state.query = event.target.value.trim().toLowerCase(); render(); });
  $('#vendor-filter').addEventListener('change', (event) => { state.vendor = event.target.value; render(); });
  $('#category-filter').addEventListener('change', (event) => { state.category = event.target.value; render(); });
}

function getVisibleEntries() {
  return state.entries.filter((entry) => {
    const haystack = [entry.vendor, entry.product, entry.category, ...(entry.params || []).flatMap((param) => [param.name, param.spec])].join(' ').toLowerCase();
    return (!state.vendor || entry.vendor === state.vendor) && (!state.category || entry.category === state.category) && (!state.query || haystack.includes(state.query));
  });
}

function vendorClass(vendor) {
  if (vendor.includes('讯飞')) return 'vendor-xunfei';
  return `vendor-${vendor}`;
}

function indicatorText(param) {
  const first = param.indicators?.[0];
  return first ? `${first.value}${first.unit === 'feature' || first.unit === 'cert' ? '' : first.unit}` : '查看规格';
}

function render() {
  const entries = getVisibleEntries();
  $('#result-count').textContent = `共 ${entries.length} 个产品条目 · ${entries.reduce((sum, entry) => sum + entry.params.length, 0)} 条参数`;
  const grid = $('#kb-grid');
  grid.innerHTML = '';
  if (!entries.length) { grid.innerHTML = '<div class="kb-card">没有找到匹配的参数条目，请调整筛选条件。</div>'; return; }
  const template = $('#card-template');
  entries.forEach((entry, index) => {
    const card = template.content.cloneNode(true);
    card.querySelector('.vendor-badge').classList.add(vendorClass(entry.vendor));
    card.querySelector('.vendor-badge').textContent = entry.vendor;
    card.querySelector('.updated').textContent = entry.updated || '已入库';
    card.querySelector('h2').textContent = entry.product;
    card.querySelector('.product-category').textContent = entry.category || '教育装备';
    card.querySelector('.parameter-list').innerHTML = entry.params.slice(0, 5).map((param) => `<div class="param-row"><span>${esc(param.name)}</span><strong>${esc(indicatorText(param))}</strong></div>`).join('');
    card.querySelector('.show-all').addEventListener('click', () => showDetails(entry));
    grid.append(card);
  });
}

function showDetails(entry) {
  const dialog = $('#detail-dialog');
  dialog.querySelector('h2').textContent = entry.product;
  dialog.querySelector('.dialog-head p:last-child').textContent = `${entry.vendor} · ${entry.category || '教育装备'} · ${entry.updated || '已入库'}`;
  dialog.querySelector('.dialog-list').innerHTML = entry.params.map((param) => {
    const tags = (param.indicators || []).map((item) => `<span class="tag">${esc(item.name)}：${esc(item.value)}${item.unit === 'feature' || item.unit === 'cert' ? '' : esc(item.unit)}</span>`).join('');
    return `<article class="detail-item"><h3>${esc(param.name)}${param.star_mark ? ' ★' : ''}</h3><p>${esc(param.spec)}</p>${tags ? `<div class="tags">${tags}</div>` : ''}</article>`;
  }).join('');
  dialog.showModal();
}

$('.dialog-close').addEventListener('click', () => $('#detail-dialog').close());
$('#detail-dialog').addEventListener('click', (event) => { if (event.target === $('#detail-dialog')) $('#detail-dialog').close(); });
loadKnowledgeBase().catch((error) => { $('#result-count').textContent = '知识库加载失败'; $('#kb-grid').innerHTML = `<div class="kb-card">${esc(error.message)}。请通过本地 HTTP 服务打开页面。</div>`; });
