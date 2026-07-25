# 源代码

> 开发工具：Kooky（Claude Code）  
> 原则：让 AI 写代码，人做 code review 和测试

## 计划文件

```
src/
├── app.py                 # Streamlit 主入口
├── engine/
│   ├── parser.py          # 参数提取 & 归一化
│   ├── quick_match.py     # 第一关：程序粗筛
│   ├── controller_id.py   # 第二关：控标方识别（横向对比）
│   └── ai_match.py        # 第三关：AI 语义精判（纵向对比）
├── utils/
│   ├── data_loader.py     # JSON 数据读取
│   └── unit_normalizer.py # 单位归一化映射表
└── tests/
    └── test_quick_match.py
```

## 开发流程

1. 告诉 Kooky 你要实现哪个模块，贴对应的技术方案
2. 让 AI 先给伪代码 / 方案，你确认后再让它写
3. 把生成的代码保存到对应文件
4. 本地跑 `python filename.py` 测试
5. 跑通了 → 截图保存到 `outputs/`
6. 有 bug → 贴报错给 Kooky → 修复 → 回到步骤4

## 切记

- **先跑起来再优化**：不纠结代码风格、性能，能跑就行
- **每个函数写 docstring**：让 AI 帮你写，方便后面调试
- **不要自己手写代码**：全程让 AI 生成，你的角色是"产品经理给开发提需求"
