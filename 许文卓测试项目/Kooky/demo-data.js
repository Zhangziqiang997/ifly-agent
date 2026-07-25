// 竞品特征库
const competitorFeatures = {
    "希沃": {
        name: "希沃",
        logo: "🔵",
        features: [
            "希沃白板5.0教学软件",
            "支持希沃云课堂互动",
            "内置希沃品牌摄像头",
            "希沃管家设备管理系统",
            "支持希沃智能语音助手"
        ]
    },
    "鸿合": {
        name: "鸿合",
        logo: "🔴",
        features: [
            "鸿合π交互式教学软件",
            "鸿合云课堂平台",
            "支持鸿合智能笔",
            "鸿合设备管理云平台",
            "内置鸿合AI助教系统"
        ]
    },
    "文香": {
        name: "文香",
        logo: "🟢",
        features: [
            "文香智慧教学平台",
            "支持文香录播系统联动",
            "文香云资源库",
            "内置文香AI课堂分析",
            "文香设备集控平台"
        ]
    }
};

// 演示招标文件数据
const demoTenderData = {
    title: "某市教育局智慧黑板采购项目",
    date: "2026-07-20",
    requirements: [
        {
            id: 1,
            category: "硬件规格",
            requirement: "显示屏尺寸不小于86英寸，分辨率≥3840×2160",
            competitor_hint: null
        },
        {
            id: 2,
            category: "软件平台",
            requirement: "需支持希沃白板5.0教学软件，兼容希沃云课堂互动功能",
            competitor_hint: "希沃"
        },
        {
            id: 3,
            category: "摄像头",
            requirement: "内置4K摄像头，支持AI人脸识别和自动追踪",
            competitor_hint: null
        },
        {
            id: 4,
            category: "语音功能",
            requirement: "支持希沃智能语音助手，可实现语音控制教学设备",
            competitor_hint: "希沃"
        },
        {
            id: 5,
            category: "设备管理",
            requirement: "配备希沃管家设备管理系统，支持远程监控和维护",
            competitor_hint: "希沃"
        },
        {
            id: 6,
            category: "书写体验",
            requirement: "触控响应时间≤6ms，支持20点同时触控",
            competitor_hint: null
        },
        {
            id: 7,
            category: "音频系统",
            requirement: "内置2.1声道音响系统，总功率≥50W",
            competitor_hint: null
        },
        {
            id: 8,
            category: "接口配置",
            requirement: "前置USB接口≥3个，HDMI接口≥2个，支持Type-C全功能接口",
            competitor_hint: null
        }
    ]
};

// 讯飞参数库
const iflytek_params = {
    "显示屏尺寸不小于86英寸，分辨率≥3840×2160": {
        status: "positive",
        iflytek_spec: "86英寸，分辨率4K（3840×2160）",
        deviation: "完全满足",
        solution: null
    },
    "需支持希沃白板5.0教学软件，兼容希沃云课堂互动功能": {
        status: "negative_fixable",
        iflytek_spec: "讯飞AI教学平台v6.0，支持第三方软件兼容",
        deviation: "讯飞有自研教学平台，功能更强大",
        solution: {
            type: "改说辞",
            content: "建议修改为：'支持主流教学软件平台，兼容云课堂互动功能'。讯飞AI教学平台功能完全覆盖希沃白板，且增加了AI智能批改、语音识别等增强功能。"
        }
    },
    "内置4K摄像头，支持AI人脸识别和自动追踪": {
        status: "positive",
        iflytek_spec: "8K超高清摄像头，支持AI人脸识别、自动追踪、手势识别",
        deviation: "讯飞规格更高（8K > 4K）",
        solution: null
    },
    "支持希沃智能语音助手，可实现语音控制教学设备": {
        status: "negative_fixable",
        iflytek_spec: "讯飞智能语音助手（行业领先），支持多轮对话和场景理解",
        deviation: "讯飞语音技术是行业标准",
        solution: {
            type: "改说辞",
            content: "建议修改为：'支持智能语音助手，可实现语音控制教学设备'。讯飞语音识别准确率达98%以上，远超行业平均水平，是科大讯飞的核心技术优势。"
        }
    },
    "配备希沃管家设备管理系统，支持远程监控和维护": {
        status: "negative_hard",
        iflytek_spec: "讯飞智慧教室管理平台，支持设备监控、远程诊断、数据分析",
        deviation: "品牌专属系统要求",
        solution: {
            type: "质疑话术",
            content: [
                "【教学场景角度】指定特定品牌管理系统限制了学校的自主选择权，违背了公平竞争原则。",
                "【功能实现角度】设备管理的核心是'远程监控和维护'功能，而非品牌名称。讯飞智慧教室管理平台同样具备完整的设备监控、故障预警、远程维护能力。",
                "【法律法规角度】根据《政府采购法实施条例》第二十条，采购人不得以特定品牌作为实质性要求，建议修改为功能性描述。",
                "【建议修改】'配备设备管理系统，支持远程监控、故障诊断和维护功能'"
            ]
        }
    },
    "触控响应时间≤6ms，支持20点同时触控": {
        status: "positive",
        iflytek_spec: "触控响应时间≤5ms，支持40点同时触控",
        deviation: "讯飞规格更优",
        solution: null
    },
    "内置2.1声道音响系统，总功率≥50W": {
        status: "negative_hard",
        iflytek_spec: "内置2.0声道音响系统，总功率45W",
        deviation: "功率略低于要求",
        solution: {
            type: "质疑话术",
            content: [
                "【教学场景角度】标准教室面积约60-80平方米，45W功率已完全满足教学音效需求，过高功率反而可能造成噪音干扰。",
                "【音质优先角度】讯飞采用专业DSP音频处理芯片，音质清晰度和还原度优于同类产品，实际教学效果更佳。",
                "【能耗环保角度】适度功率配置既满足使用需求，又符合教育装备节能环保要求。",
                "【渠道兜底】建议销售团队与业主沟通，说明实际音效体验，或提供功率升级方案（外接音响）。"
            ]
        }
    },
    "前置USB接口≥3个，HDMI接口≥2个，支持Type-C全功能接口": {
        status: "positive",
        iflytek_spec: "前置USB 3.0接口×4，HDMI 2.1接口×3，Type-C全功能接口×2",
        deviation: "讯飞接口配置更丰富",
        solution: null
    }
};

// 导出数据
window.demoData = {
    competitorFeatures,
    demoTenderData,
    iflytek_params
};