window.SidebarConfig = Object.freeze({
  groups: [
    {
      title: '业务中心',
      items: [
        { label: '投标分析', icon: '▣', href: 'index.html', page: 'home' },
        { label: '投标项目', icon: '▣' },
      ],
    },
    {
      title: '智能分析',
      items: [
        { label: 'AI分析报告', icon: '▧', href: 'report.html', page: 'report' },
        { label: 'AI风险识别', icon: '♧' },
        { label: '话术与方案', icon: '▣' },
      ],
    },
    {
      title: '产品与知识',
      items: [
        { label: '参数知识库', icon: '▣', href: 'knowledge-base.html', page: 'knowledge' },
      ],
    },
  ],
});
