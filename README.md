# 雀宝 · 日麻牌局分析助手

![小助手模块流程图](./img.png)

一个基于 AI 的日本麻将（立直麻将）实时分析助手，通过 YOLO 视觉识别 + 大语言模型，为玩家提供专业的牌局分析和策略建议。

更多详细说明请参考：
- [📖 日麻Agent架构](docs/日麻Agent架构.md)：核心架构与工作流
- [⚙️ 安装部署运行说明](docs/安装部署运行说明.md)：详细安装与故障排查

## ✨ 核心功能

- **🎯 一键截图分析**：自动截取游戏画面，识别手牌，生成专业分析报告
- **🤖 AI 智能解说**：基于 DeepSeek 大模型，以"雀宝"（可爱女牌友）的角色提供自然口语化的策略建议
- **💬 上下文对话**：支持多轮对话，AI 会记住之前的交流内容
- **📊 专业分析**：包含向听数、听牌分析、打点计算、牌效评估等
- **🎨 美观 GUI**：深色主题界面，支持 Markdown 渲染，流式输出展示

## 🚀 快速开始

### 环境要求

- Python 3.9+
- Windows 10/11（截图功能基于 Windows API，推荐）
- 支持 macOS / Linux（需自行解决截图适配）

### 安装依赖

```bash
pip install -r requirements.txt
```

### 配置 API Key

本项目使用 DeepSeek API 进行流式解说（兼容 OpenAI SDK）。

**Windows PowerShell:**
```powershell
$env:DEEPSEEK_API_KEY = "你的密钥"
```

**macOS / Linux:**
```bash
export DEEPSEEK_API_KEY="你的密钥"
```

### 运行程序

```bash
python main.py
```

程序会自动打开 GUI 界面，你可以：

1. **一键截图 + 分析 + AI解说**：点击底部对应按钮
   - 自动截取当前屏幕并保存到 `Mahjong_YOLO/test.png`
   - YOLO 识别手牌并生成 `output.txt`
   - AI 读取分析报告并流式解说

2. **开始分析（流式输出）**：
   - 仅读取现有的 `output.txt` 进行 AI 解说（适用于已手动生成报告的情况）

3. **聊天对话**：
   - 在底部输入框输入问题，与"雀宝"进行多轮对话

## 📁 项目结构

```
MahjongPaw/
├── main.py                    # 项目入口（启动 GUI）
├── api_gui.py                 # GUI 主界面（流式输出、聊天、Markdown 渲染）
├── analyzer.py                # 牌局分析器（向听数、听牌、打点计算）
├── api.py                     # 大模型 API 调用（DeepSeek）
├── cal_scores.py              # 点数计算模块
├── Mahjong_YOLO/              # YOLO 麻将牌识别模块
│   ├── trained_models_v2/     # 训练好的 YOLO 模型权重
│   │   ├── yolo11m_best.pt    # 默认使用的模型
│   ├── test.py                # 识别逻辑实现
├── world_model/               # 世界模型（麻将对象定义）
│   ├── mahjong_table.py       # 麻将桌类
│   ├── mahjong_player.py      # 玩家类
│   ├── mahjong_tile.py        # 麻将牌类
│   └── mahjong_meld.py        # 副露类
├── requirements.txt           # 项目依赖
├── README.md                  # 项目说明文档
├── 演示文档.md                # 详细功能演示
└── 安装部署运行说明.md        # 安装部署指南
```

## 🔧 核心模块说明

### 1. GUI 界面 (`api_gui.py`)

![GUI 界面](img/structure.png)

**功能**：
- 流式输出展示 AI 回复
- 聊天输入框支持多轮对话
- Markdown 渲染（标题、列表、加粗）
- 深色主题界面

**主要类**：
- `StreamingChatGUI`：主界面类，管理 UI 和流式输出

### 2. 牌局分析器 (`analyzer.py`)

**功能**：
- 手牌识别结果分析
- 向听数计算
- 听牌分析（含打点计算）
- 牌型分布统计

**主要类**：
- `FixedMahjongAnalyzer`：分析器主类
- `run_analysis_to_file()`：一键分析并写入文件

### 3. YOLO 识别 (`Mahjong_YOLO/test.py`)

**功能**：
- 从截图识别麻将牌
- 定位手牌区域
- 转换为标准麻将字符串格式

**主要函数**：
- `perceive()`：识别入口，返回手牌列表和字符串

### 4. 截图服务 (`main.py`)

**功能**：
- 热键截图（Ctrl+Alt+S）
- 截图保存和管理

**主要类**：
- `ScreenshotService`：截图服务类
- `QuickScreenshot`：快速截图类

### 5. 世界模型 (`world_model/`)

**功能**：
- 麻将对象建模
- 游戏状态管理

**主要类**：
- `MahjongTable`：游戏桌
- `MahjongPlayer`：玩家
- `MahjongTile`：麻将牌
- `MahjongMeld`：副露

## 🎮 使用流程

### 方式一：一键截图分析

1. 打开日麻游戏，进入对局
2. 运行 `python main.py` 打开 GUI
3. 点击"一键截图 + 分析 + AI解说"
4. 等待识别和分析完成
5. 查看 AI 的流式解说和建议

### 方式二：手动分析

1. 手动截图保存到 `Mahjong_YOLO/test.png`
2. 运行分析生成 `output.txt`
3. 在 GUI 中点击"开始分析（流式输出）"

### 方式三：聊天对话

1. 在 GUI 底部输入框输入问题
2. 按回车或点击"发送"
3. AI 会基于上下文回复
4. 可以继续追问，AI 会记住之前的对话

## 📊 分析报告内容

分析报告包含以下信息：

- **基础信息**：手牌、牌数、自风、场风、立直状态
- **牌型分布**：万子/筒子/索子/字牌数量，幺九牌比例
- **向听数分析**：当前向听数，是否听牌
- **听牌分析**（如果听牌）：
  - 听牌张列表及点数
  - 高打点听牌张详情
  - 役种和翻数信息
  - 平均点数和最高点数
  - 策略建议

## 🤖 AI 角色设定

"雀宝"是一位：
- 非常会打立直麻将的女玩家
- 性格元气可爱
- 用自然口语交流，像真人牌友聊天
- 专业判断可靠，但语气轻松

## 🔑 依赖说明

主要依赖包：
- `openai`：DeepSeek API 调用
- `ultralytics`：YOLO 模型推理
- `mahjong`：麻将规则和计算
- `tkinter`：GUI 界面（Python 内置）
- `PIL`：图像处理
- `keyboard`：热键监听

完整依赖列表见 `requirements.txt`。

## 📝 注意事项

1. **截图识别率**：YOLO 识别率约 85%，复杂场景可能需要手动修正
2. **API Key**：需要有效的 DeepSeek API Key（代码中有默认值，但建议使用自己的）
3. **截图路径**：默认保存到 `./Mahjong_YOLO/test.png`
4. **分析结果**：会写入 `output.txt`，GUI 会读取并展示

## 🛠️ 开发说明

### 添加新的分析功能

在 `analyzer.py` 的 `FixedMahjongAnalyzer` 类中添加新方法。

### 修改 AI 角色设定

编辑 `api_gui.py` 中的 `system_prompt` 变量。

### 调整 GUI 样式

修改 `api_gui.py` 中的样式配置（颜色、字体等）。

## 📄 许可证

本项目仅供学习和研究使用。

## 🙏 致谢

- YOLO 模型训练基于 Ultralytics
- 麻将规则计算基于 `mahjong` 库
- AI 能力由 DeepSeek 提供

---

**雀宝**：让我们一起征战雀场吧！(≧∇≦)ﾉ
