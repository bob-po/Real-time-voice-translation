# 实时语音翻译系统 - 安装指南

## 系统要求

### 最低配置
- **操作系统**: Windows 10 (64位)
- **Python**: 3.7 或更高版本
- **内存**: 2GB RAM
- **存储**: 500MB 可用空间
- **网络**: 网络识别模式需要稳定的互联网连接

### 推荐配置
- **操作系统**: Windows 11 (64位)
- **Python**: 3.9 或更高版本
- **内存**: 4GB RAM 或更多
- **存储**: 1GB 可用空间
- **网络**: 高速稳定的互联网连接
- **音频设备**: 高质量麦克风

### 硬件要求
- **麦克风**: 内置或外接麦克风
- **声卡**: 支持音频输入
- **显卡**: 支持OpenGL 2.0或更高版本
- **处理器**: 双核处理器或更高

## 环境准备

### 1. 安装Python

#### Windows用户
1. 访问 [Python官网](https://www.python.org/downloads/)
2. 下载Python 3.7+版本
3. 运行安装程序，**重要**: 勾选"Add Python to PATH"
4. 验证安装：
   ```bash
   python --version
   pip --version
   ```

#### 验证Python安装
```bash
# 检查Python版本
python --version

# 检查pip版本
pip --version

# 检查Python路径
where python
```

### 2. 安装Git (可选)
```bash
# 下载Git for Windows
# https://git-scm.com/download/win

# 验证安装
git --version
```

## 项目安装

### 方法一：从GitHub克隆
```bash
# 克隆项目
git clone https://github.com/bob-po/Real-time-voice-translation.git
cd Real-time-voice-translation

# 或下载ZIP文件并解压
```

### 方法二：直接下载
1. 下载项目ZIP文件
2. 解压到本地目录
3. 进入项目文件夹

## 依赖安装

### 1. 创建虚拟环境（推荐）
```bash
# 创建虚拟环境
python -m venv subtitle_env

# 激活虚拟环境
# Windows
subtitle_env\Scripts\activate

# Linux/Mac
source subtitle_env/bin/activate
```

### 2. 安装依赖包
```bash
# 升级pip
python -m pip install --upgrade pip

# 安装依赖
pip install -r requirements.txt
```

### 3. 验证安装
```bash
# 检查关键包
python -c "import PyQt5; print('PyQt5 installed')"
python -c "import speech_recognition; print('SpeechRecognition installed')"
python -c "import pyaudio; print('PyAudio installed')"
python -c "import argostranslate; print('ArgosTranslate installed')"
```

## 语音模型安装

### 网络识别模式
网络识别模式使用Google Speech Recognition，无需额外安装模型。

### 本地识别模式
本地识别需要下载Vosk语音模型：

#### 1. 下载模型
```bash
# 创建模型目录
mkdir model-cn model-en

# 下载中文模型 (约1GB)
# 访问: https://alphacephei.com/vosk/models
# 下载: vosk-model-small-cn-0.22.zip
# 解压到 model-cn/ 目录

# 下载英文模型 (约1GB)
# 下载: vosk-model-small-en-us-0.15.zip
# 解压到 model-en/ 目录
```

#### 2. 模型目录结构
```
Real-time-voice-translation/
├── model-cn/
│   ├── am/
│   ├── conf/
│   ├── graph/
│   ├── ivector/
│   └── README
├── model-en/
│   ├── am/
│   ├── conf/
│   ├── graph/
│   ├── ivector/
│   └── README
```

#### 3. 安装Vosk
```bash
pip install vosk
```

## 语言包安装

### 自动安装
系统会自动下载所需的翻译语言包，首次使用新语言时可能需要等待下载完成。

### 手动安装
```bash
# 安装特定语言包
argospm install translate-en_zh
argospm install translate-zh_en
argospm install translate-en_ja
# ... 其他语言包
```

### 查看已安装语言包
```bash
python -c "from argostranslate import translate; print(translate.get_installed_languages())"
```

## 配置说明

### 1. 音频设备配置
```python
# 检查可用麦克风
import pyaudio
pa = pyaudio.PyAudio()
for i in range(pa.get_device_count()):
    info = pa.get_device_info_by_index(i)
    if info['maxInputChannels'] > 0:
        print(f"麦克风 {i}: {info['name']}")
pa.terminate()
```

### 2. 网络配置
确保以下端口可访问：
- **HTTPS (443)**: Google Speech Recognition
- **HTTP (80)**: Argos Translate语言包下载

### 3. 防火墙设置
如果遇到网络问题，请检查防火墙设置：
1. 打开Windows防火墙设置
2. 允许Python.exe通过防火墙
3. 允许应用访问网络

## 测试安装

### 1. 基础功能测试
```bash
# 运行测试脚本
python test_installation.py
```

### 2. 启动应用
```bash
# 启动字幕系统
python Real-time-voice-translation/transparent_subtitle_optimized.py
```

### 3. 功能验证
1. 检查麦克风是否正常工作
2. 测试语音识别功能
3. 验证翻译功能
4. 确认UI显示正常

## 常见安装问题

### 问题1: PyAudio安装失败
**错误信息**: `Microsoft Visual C++ 14.0 is required`

**解决方法**:
```bash
# 方法1: 安装预编译包
pip install pipwin
pipwin install pyaudio

# 方法2: 使用conda
conda install pyaudio

# 方法3: 下载wheel文件
# 访问: https://www.lfd.uci.edu/~gohlke/pythonlibs/#pyaudio
# 下载对应版本的.whl文件
pip install PyAudio-0.2.11-cp39-cp39-win_amd64.whl
```

### 问题2: PyQt5安装失败
**解决方法**:
```bash
# 升级pip
python -m pip install --upgrade pip

# 安装PyQt5
pip install PyQt5

# 如果失败，尝试
pip install PyQt5-tools
```

### 问题3: 麦克风权限问题
**解决方法**:
1. 打开Windows设置 → 隐私 → 麦克风
2. 允许应用访问麦克风
3. 重启应用

### 问题4: 网络连接问题
**解决方法**:
1. 检查网络连接
2. 配置代理设置（如果需要）
3. 检查防火墙设置
4. 尝试使用本地识别模式

### 问题5: 内存不足
**解决方法**:
1. 关闭其他应用
2. 增加虚拟内存
3. 使用本地识别模式
4. 减少音频缓冲区大小

## 性能优化

### 1. 系统优化
```bash
# 清理临时文件
python -m pip cache purge

# 更新包
pip list --outdated
pip install --upgrade package_name
```

### 2. 音频优化
- 使用高质量麦克风
- 调整音频采样率
- 优化缓冲区大小
- 减少环境噪音

### 3. 网络优化
- 使用有线网络连接
- 配置DNS服务器
- 启用网络加速
- 使用代理服务器（如果需要）

## 卸载说明

### 1. 卸载应用
```bash
# 删除项目文件
rm -rf Real-time-voice-translation/

# 删除虚拟环境
rm -rf subtitle_env/
```

### 2. 清理依赖
```bash
# 卸载包
pip uninstall PyQt5 speech_recognition pyaudio argostranslate vosk numpy

# 清理缓存
pip cache purge
```

### 3. 删除模型文件
```bash
# 删除语音模型
rm -rf model-cn/ model-en/
```

## 更新指南

### 1. 检查更新
```bash
# 拉取最新代码
git pull origin main

# 更新依赖
pip install -r requirements.txt --upgrade
```

### 2. 备份配置
```bash
# 备份用户配置
cp config.json config_backup.json
```

### 3. 测试更新
```bash
# 测试新版本
python Real-time-voice-translation/transparent_subtitle_optimized.py
```

## 技术支持

### 获取帮助
- **文档**: 查看README.md和用户手册
- **问题反馈**: 提交GitHub Issue
- **社区支持**: 参与项目讨论

### 日志文件
```bash
# 查看应用日志
tail -f subtitle_system.log

# 查看错误日志
grep ERROR subtitle_system.log
```

---

**注意**: 安装过程中如遇到问题，请先查看常见问题解答，或提交Issue获取技术支持。 