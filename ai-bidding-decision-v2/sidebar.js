(() => {
  const config = window.SidebarConfig;

  if (!config) {
    console.error('SidebarConfig is required before sidebar.js.');
    return;
  }

  function showPendingMessage() {
    let toast = document.querySelector('#sidebar-toast');
    if (!toast) {
      toast = document.createElement('div');
      toast.id = 'sidebar-toast';
      toast.className = 'sidebar-toast';
      toast.setAttribute('role', 'status');
      toast.setAttribute('aria-live', 'polite');
      document.body.append(toast);
    }

    toast.textContent = '功能建设中';
    toast.classList.add('show');
    window.clearTimeout(showPendingMessage.timer);
    showPendingMessage.timer = window.setTimeout(() => toast.classList.remove('show'), 1800);
  }

  function renderItem(item, page) {
    const active = item.page === page;
    const className = active ? 'active' : '';
    const current = active ? ' aria-current="page"' : '';
    const icon = `<span class="nav-ico" aria-hidden="true">${item.icon}</span>`;

    if (item.href) {
      return `<a href="${item.href}" class="${className}"${current}>${icon}${item.label}</a>`;
    }

    return `<a href="#" class="${className}" data-sidebar-pending="true">${icon}${item.label}</a>`;
  }

  function renderSidebar(sidebar) {
    const page = sidebar.dataset.page;
    sidebar.classList.add('sidebar');
    sidebar.innerHTML = `
      <div class="brand"><strong>教育装备投标决策平台</strong><span>讯飞教育业务中心</span></div>
      <div class="business-label">业务选择</div>
      <label class="business-menu"><span class="business-icon" aria-hidden="true">▣</span><select aria-label="业务品类"><option>智慧黑板</option></select></label>
      <nav aria-label="主导航">${config.groups.map((group) => `
        <div class="group-title">${group.title}</div>
        ${group.items.map((item) => renderItem(item, page)).join('')}
      `).join('')}</nav>
      <div class="sidebar-collapse" aria-hidden="true">‹</div>
    `;

    sidebar.addEventListener('click', (event) => {
      if (!event.target.closest('[data-sidebar-pending]')) return;
      event.preventDefault();
      showPendingMessage();
    });
  }

  document.querySelectorAll('[data-sidebar]').forEach(renderSidebar);
})();
