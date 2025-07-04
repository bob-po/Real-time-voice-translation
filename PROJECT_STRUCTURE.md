# 实时语音翻译系统 - 项目结构说明

## 目录结构概览

```
Real-time-voice-translation/
├── README.md                           # 项目主要说明文档
├── TECHNICAL_DOCS.md                   # 技术文档
├── USER_MANUAL.md                      # 用户使用手册
├── INSTALLATION_GUIDE.md               # 安装指南
├── PROJECT_STRUCTURE.md                # 项目结构说明（本文档）
├── requirements.txt                    # Python依赖包列表
├── software/                          # 源代码目录
│   ├── transparent_subtitle_optimized.py  # 主程序文件
│   └── transparent_subtitle.py           # 原始版本（备份）
├── model-cn/                           # 中文语音识别模型
│   ├── am/                             # 声学模型
│   ├── conf/                           # 配置文件
│   ├── graph/                          # 解码图
│   ├── ivector/                        # i-vector特征
│   └── README                          # 模型说明
├── model-en/                           # 英文语音识别模型
│   ├── am/                             # 声学模型
│   ├── conf/                           # 配置文件
│   ├── graph/                          # 解码图
│   ├── ivector/                        # i-vector特征
│   ├── rescore/                        # 重打分模型
│   ├── rnnlm/                          # RNN语言模型
│   └── README                          # 模型说明
└── docs/                               # 文档目录（可选）
    ├── images/                         # 文档图片
    ├── screenshots/                    # 界面截图
    └── examples/                       # 使用示例
```

## 核心文件详解

### 1. 主程序文件

#### `Real-time-voice-translation/transparent_subtitle_optimized.py`
**作用**: 系统的主程序文件，包含所有核心功能

**主要组件**:
- `TransparentSubtitle`: 主窗口类
- `AudioProcessor`: 音频处理类
- `TranslationManager`: 翻译管理类
- `SettingsDialog`: 设置对话框类

**关键功能**:
- 实时语音识别
- 多语言翻译
- 透明悬浮字幕
- 音频可视化
- 用户设置管理

#### `Real-time-voice-translation/transparent_subtitle.py`
**作用**: 原始版本备份，用于对比和回滚

### 2. 配置文件

#### `requirements.txt`
**作用**: Python依赖包列表

**包含的主要包**:
```
PyQt5>=5.15.0              # GUI框架
speech_recognition>=3.8.1   # 语音识别
pyaudio>=0.2.11            # 音频处理
argostranslate>=1.8.0      # 翻译服务
numpy>=1.21.0              # 数值计算
vosk>=0.3.32               # 本地语音识别
```

### 3. 语音模型目录

#### `model-cn/` - 中文语音模型
**作用**: 本地中文语音识别模型

**子目录说明**:
- `am/`: 声学模型文件
  - `final.mdl`: 最终声学模型
- `conf/`: 配置文件
  - `mfcc.conf`: MFCC特征配置
  - `model.conf`: 模型配置
- `graph/`: 解码图
  - `HCLr.fst`: 解码图文件
  - `phones/`: 音素文件
- `ivector/`: i-vector特征
  - `final.dubm`: DUBM模型
  - `final.ie`: i-vector提取器
  - `final.mat`: 变换矩阵

#### `model-en/` - 英文语音模型
**作用**: 本地英文语音识别模型

**额外组件**:
- `rescore/`: 重打分模型
  - `G.carpa`: 语言模型
  - `G.fst`: 有限状态转换器
- `rnnlm/`: RNN语言模型
  - `final.raw`: RNN模型文件
  - `feat_embedding.final.mat`: 特征嵌入

## 文档文件说明

### 1. `README.md`
**作用**: 项目主要说明文档

**内容包含**:
- 项目简介和功能特性
- 系统要求和安装指南
- 使用方法和配置说明
- 技术架构和性能优化
- 故障排除和开发说明

### 2. `TECHNICAL_DOCS.md`
**作用**: 详细技术文档

**内容包含**:
- 系统架构设计
- API接口说明
- 配置参数详解
- 数据流分析
- 性能优化策略
- 扩展开发指南

### 3. `USER_MANUAL.md`
**作用**: 用户使用手册

**内容包含**:
- 快速开始指南
- 界面操作说明
- 详细功能使用
- 常见问题解答
- 使用技巧和优化

### 4. `INSTALLATION_GUIDE.md`
**作用**: 详细安装指南

**内容包含**:
- 系统要求说明
- 环境准备步骤
- 依赖安装方法
- 模型下载配置
- 常见问题解决

### 5. `PROJECT_STRUCTURE.md`
**作用**: 项目结构说明（本文档）

## 代码结构分析

### 主程序架构
```python
# 核心类结构
class TransparentSubtitle(QWidget):
    """主窗口类 - 负责UI和整体协调"""
    
class AudioProcessor:
    """音频处理类 - 负责音频采集和处理"""
    
class TranslationManager:
    """翻译管理类 - 负责翻译服务"""
    
class SettingsDialog(QDialog):
    """设置对话框类 - 负责用户配置"""
```

### 模块依赖关系
```
TransparentSubtitle
├── AudioProcessor (音频处理)
├── TranslationManager (翻译管理)
├── SettingsDialog (设置界面)
└── 线程管理 (识别线程、UI更新)
```

### 数据流向
```
麦克风 → AudioProcessor → 识别线程 → TranslationManager → UI更新
```

## 开发环境配置

### 推荐的开发工具
- **IDE**: PyCharm, VS Code
- **版本控制**: Git
- **虚拟环境**: venv, conda
- **调试工具**: pdb, logging

### 开发目录结构
```
Real-time-voice-translation/
├── src/                    # 源代码
├── tests/                  # 测试文件
├── docs/                   # 文档
├── scripts/                # 脚本工具
├── config/                 # 配置文件
└── data/                   # 数据文件
```

## 部署结构

### 生产环境
```
deploy/
├── executable/             # 可执行文件
├── models/                 # 语音模型
├── config/                 # 配置文件
├── logs/                   # 日志文件
└── resources/              # 资源文件
```

### 打包配置
```python
# setup.py 或 pyproject.toml
# 用于打包为可执行文件
```

## 版本管理

### 文件版本控制
- **源代码**: 使用Git进行版本控制
- **模型文件**: 大文件使用Git LFS
- **文档**: 随代码一起版本控制
- **配置**: 模板文件版本控制，用户配置忽略

### 发布版本
```
v1.0.0/
├── Real-time-voice-translation/
├── models/
├── docs/
└── requirements.txt
```

## 扩展开发

### 插件系统结构
```
plugins/
├── recognition/            # 识别插件
├── translation/            # 翻译插件
├── ui/                     # UI插件
└── utils/                  # 工具插件
```

### 配置文件结构
```
config/
├── app.json               # 应用配置
├── audio.json             # 音频配置
├── ui.json                # UI配置
└── translation.json       # 翻译配置
```

## 测试结构

### 测试文件组织
```
tests/
├── unit/                  # 单元测试
├── integration/           # 集成测试
├── performance/           # 性能测试
└── ui/                    # UI测试
```

### 测试数据
```
test_data/
├── audio/                 # 测试音频
├── text/                  # 测试文本
└── models/                # 测试模型
```

## 文档维护

### 文档更新流程
1. 代码变更时同步更新相关文档
2. 定期检查和更新文档
3. 用户反馈时及时修正文档
4. 版本发布时更新文档版本

### 文档质量标准
- 内容准确性和完整性
- 格式规范和一致性
- 示例代码的可执行性
- 用户友好的表达方式

---

**注意**: 项目结构可能会随着开发进展而调整，请关注最新版本的文档更新。 