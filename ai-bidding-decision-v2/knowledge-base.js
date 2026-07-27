const sources = [
  'data/knowledge-base/xunfei/xunfei.json',
  'data/knowledge-base/competitors/希沃.json',
  'data/knowledge-base/competitors/鸿合.json',
  'data/knowledge-base/competitors/海康.json',
  'data/knowledge-base/competitors/文香.json',
];

const state = { products: [], params: [], query: '', vendor: '', category: '' };
const $ = (selector) => document.querySelector(selector);
const esc = (value = '') => String(value).replace(/[&<>"']/g, (char) => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;' })[char]);
const softwareCategories = new Set(['软件', '教学软件', 'AI', 'AI能力', '生态', '集控管理']);

function parameterKind(param) {
  return softwareCategories.has(param.category) ? 0 : 1;
}

function displayOrder(a, b) {
  return a.productIndex - b.productIndex || parameterKind(a) - parameterKind(b) || a.paramIndex - b.paramIndex;
}

async function loadKnowledgeBase() {
  const datasets = await Promise.all(sources.map(async (source) => {
    const response = await fetch(source);
    if (!response.ok) throw new Error(`无法读取 ${source}`);
    const data = await response.json();
    return Array.isArray(data) ? data : [data];
  }));
  state.products = datasets.flat();
  state.params = state.products.flatMap((product, productIndex) => (product.params || []).map((param, paramIndex) => ({
    ...param,
    vendor: product.vendor,
    product: product.product,
    productCategory: product.category,
    updated: product.updated,
    productIndex,
    paramIndex,
  })));
  bindControls();
  render();
}

function bindControls() {
  $('#search').addEventListener('input', (event) => { state.query = event.target.value.trim().toLowerCase(); render(); });
  $('.dialog-close').addEventListener('click', () => $('#detail-dialog').close());
  $('#detail-dialog').addEventListener('click', (event) => { if (event.target === $('#detail-dialog')) $('#detail-dialog').close(); });
}

function filteredParams() {
  return state.params.filter((param) => {
    const haystack = [param.vendor, param.product, param.productCategory, param.category, param.name, param.spec, ...(param.indicators || []).flatMap((indicator) => [indicator.name, indicator.value])].join(' ').toLowerCase();
    return (!state.vendor || param.vendor === state.vendor) && (!state.category || param.category === state.category) && (!state.query || haystack.includes(state.query));
  });
}

function renderChips(container, values, current, label, onChange) {
  container.innerHTML = ['', ...values].map((value) => `<button type="button" class="chip ${current === value ? 'chip-on' : ''}" data-value="${esc(value)}">${esc(value || label)}</button>`).join('');
  container.querySelectorAll('.chip').forEach((button) => button.addEventListener('click', () => onChange(button.dataset.value)));
}

function displayIndicator(indicator) {
  const value = indicator.value === true ? '支持' : indicator.value === false ? '不支持' : indicator.value;
  const unit = ['feature', 'cert', 'spec'].includes(indicator.unit) ? '' : indicator.unit || '';
  return `${indicator.name} ${indicator.comparator || ''} ${value}${unit}`.replace(/\s+/g, ' ').trim();
}

function render() {
  const vendors = [...new Set(state.params.map((param) => param.vendor))];
  const categories = [...new Set(state.params.map((param) => param.category))];
  renderChips($('#vendor-filter'), vendors, state.vendor, '全部厂商', (value) => { state.vendor = value; render(); });
  renderChips($('#category-filter'), categories, state.category, '全部分类', (value) => { state.category = value; render(); });
  const list = filteredParams().sort(displayOrder);
  $('#result-count').innerHTML = `共 <strong>${list.length}</strong> 条参数 · ${vendors.length} 家厂商`;
  const target = $('#kb-list');
  if (!list.length) { target.innerHTML = '<div class="state-empty">无匹配参数，请调整筛选条件。</div>'; return; }
  target.innerHTML = list.map((param) => {
    const indicators = (param.indicators || []).map((indicator) => `<span class="ind">${esc(displayIndicator(indicator))}</span>`).join('');
    const tags = param.star_mark ? '<span class="tag star">★星标</span>' : '';
    return `<article class="kb-item">
      <div class="kb-item-head"><strong>${esc(param.name)}</strong><span class="kb-vendor">${esc(param.vendor)}</span><span class="kb-cat">${esc(param.category || param.productCategory)}</span>${tags}</div>
      <p class="kb-product">${esc(param.product)}</p><p class="kb-spec">${esc(param.spec)}</p>
      ${indicators ? `<div class="kb-inds">${indicators}</div>` : ''}
      <div class="kb-foot"><small class="kb-src">来源：${esc(param.product)} · ${esc(param.id || '')}</small><button type="button" class="detail-btn" data-product="${esc(param.product)}">查看详情</button></div>
    </article>`;
  }).join('');
  target.querySelectorAll('.detail-btn').forEach((button) => button.addEventListener('click', () => showDetails(button.dataset.product)));
}

function showDetails(productName) {
  const product = state.products.find((item) => item.product === productName);
  if (!product) return;
  const dialog = $('#detail-dialog');
  dialog.querySelector('h2').textContent = product.product;
  dialog.querySelector('.dialog-meta').textContent = `${product.vendor} · ${product.category || '教育装备'} · ${product.updated || '已入库'}`;
  dialog.querySelector('.dialog-list').innerHTML = product.params
    .map((param, paramIndex) => ({ ...param, productIndex: state.products.indexOf(product), paramIndex }))
    .sort(displayOrder)
    .map((param) => {
    const tags = (param.indicators || []).map((indicator) => `<span class="ind">${esc(displayIndicator(indicator))}</span>`).join('');
    return `<article class="detail-item"><h3>${esc(param.name)}${param.star_mark ? ' ★' : ''}</h3><p>${esc(param.spec)}</p>${tags ? `<div class="kb-inds">${tags}</div>` : ''}</article>`;
    }).join('');
  dialog.showModal();
}

loadKnowledgeBase().catch((error) => {
  $('#result-count').textContent = '知识库加载失败';
  $('#kb-list').innerHTML = `<div class="state-empty">${esc(error.message)}。请通过本地 HTTP 服务打开页面。</div>`;
});
