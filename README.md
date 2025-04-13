```markdown
PalBot/
├── hardware/                         # 封装底层 I/O 设备（硬件驱动）
│   ├── camera.py                     # 摄像头封装：图像采集、情绪识别、物体检测
│   ├── microphone.py                 # 麦克风输入：叹气识别、ASR 录音接口（whisper）
│   └── speaker.py                    # 语音播放：TTS 接口封装（使用 whisper TTS 或其他库）
│
├── pal_agent/                        # Agent 核心逻辑模块
│   ├── env/                          # 环境交互与技能行为
│   │   ├── atomic_skills/            # 原子技能（低层控制动作）
│   │   │   └── [每个.py = 一个基础动作，如 move, grasp, release 等]
│   │   └── composite_skills/         # 组合技能（Snack Delivery, Table Cleanup 等）
│   │       ├── snack_delivery.py     # 包含零食递送任务的完整逻辑流程
│   │       └── table_cleanup.py      # 包含桌面清理任务的组合技能逻辑
│   │
│   ├── memory/                       # 记忆模块
│   │   ├── base_memory.py            # 记忆系统基础接口（抽象类/通用操作）
│   │   ├── long_memory.py            # 长期记忆模块：长期存储、召回经验等
│   │   └── short_memory.py           # 短期记忆模块：当前 session 的上下文、临时状态
│   │
│   └── provider/                     # 能力提供者模块（处理感知与推理）
│       ├── audio_provider.py         # 声音事件处理（如叹气检测、ASR）
│       ├── openai_provider.py        # GPT-4o 接口封装：反思 / 推理 / 规划 / 聊天
│       ├── skill_provider.py         # 技能嵌入 / 向量搜索 / 匹配任务相关技能
│       ├── vision_provider.py        # 图像处理（表情识别、桌面垃圾检测）
│       └── processors.py             # 感知数据预处理与触发条件检测（如姿态变化分析）
│
├── res/                              # 项目资源
│   ├── prompts/                      # GPT 使用的提示词模板（reflection, planning 等）
│   │   └── [*.txt / *.md]            # 每个任务或模块的提示模板
│   └── skills/                       # 技能元数据、分类、能力映射等
│
├── pal_agent.utils/                            # 工具类与常量
│   └── constants.py                  # 全局使用的常量定义（路径、标签、阈值等）
│
├── config.yaml                       # 系统配置文件（如设备参数、模型 key、任务路径）
│
└── main.py                           # 项目启动主程序
                                       # 初始化 Agent → 进入主循环 → 管理任务执行
```

pip install --upgrade torch==2.1.1+cu118 -f https://download.pytorch.org/whl/torch_stable.html

pip install torchvision==0.16.1+cu118 -f https://download.pytorch.org/whl/torch_stable.html

numpy==1.24.3

opencv-python==4.8.1.78

opencv-contrib-python==4.8.1.78

mss==9.0.1

spacy==3.7.2

easyocr==1.7.1

python -m spacy download en_core_web_lg # OCR
