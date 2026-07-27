window.SidebarConfig = Object.freeze({
  groups: [
    {
      title: '业务中心',
      items: [
        { label: '项目总览', icon: '▣', href: 'index.html', page: 'home' },
        { label: '投标项目', icon: '▣' },
        { label: '文档中心', icon: '▥' },
      ],
    },
    {
      title: '智能分析',
      items: [
        { label: '招标参数对比', icon: '♧' },
        { label: 'AI分析报告', icon: '▧', href: 'report.html', page: 'report' },
        { label: 'AI风险识别', icon: '♧' },
        { label: '话术与方案', icon: '▣' },
      ],
    },
    {
      title: '产品与知识',
      items: [
        { label: '产品与参数中心', icon: '♧' },
        { label: '参数知识库', icon: '▣', href: 'knowledge-base.html', page: 'knowledge' },
        { label: '产品与竞品', icon: '▤' },
        { label: '规则与标准', icon: '▤' },
      ],
    },
  ],
});
