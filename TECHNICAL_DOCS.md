# 实时语音翻译系统 - 技术文档

## 系统架构

### 整体架构图
```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   用户界面层     │    │   业务逻辑层     │    │   数据服务层     │
│                 │    │                 │    │                 │
│ TransparentSubtitle │◄──►│ AudioProcessor   │◄──►│ 语音识别服务     │
│ SettingsDialog   │    │ TranslationManager│    │ 翻译服务        │
│                 │    │                 │    │ 音频设备        │
└─────────────────┘    └─────────────────┘    └─────────────────┘
```

### 核心模块设计

#### 1. TransparentSubtitle 类
**职责**: 主窗口管理、UI渲染、事件处理

**关键属性**:
```python
class TransparentSubtitle(QWidget):
    # 配置参数
    language_options = ['en', 'zh', 'ja', 'fr', 'de', 'es', 'ru', 'ko']
    recognition_language = 'en'
    translation_language = 'zh'
    font_size = 28
    display_mode = '双语'
    recog_mode = '网络'
    
    # 性能优化
    audio_energy_history = deque([0]*30, maxlen=30)
    text_queue = queue.Queue(maxsize=10)
    _font_cache = {}
    _last_text = ("", "")
```

**主要方法**:
- `initUI()`: 初始化用户界面
- `recognition_loop()`: 语音识别主循环
- `update_subtitle()`: 字幕更新逻辑
- `paintEvent()`: 自定义绘制事件

#### 2. AudioProcessor 类
**职责**: 音频设备管理、音频数据采集

**关键参数**:
```python
class AudioProcessor:
    def __init__(self, mic_name, samplerate=16000, frames_per_buffer=1024):
        self.samplerate = samplerate          # 采样率
        self.frames_per_buffer = frames_per_buffer  # 缓冲区大小
        self.mic_index = self._get_mic_index()      # 麦克风索引
```

**音频处理流程**:
1. 获取麦克风设备列表
2. 初始化PyAudio流
3. 实时采集音频数据
4. 计算音频能量
5. 返回音频字节和能量值

#### 3. TranslationManager 类
**职责**: 翻译服务管理、语言包缓存

**缓存机制**:
```python
class TranslationManager:
    def __init__(self):
        self._translation_cache = {}      # 翻译结果缓存
        self._installed_languages = None  # 语言包缓存
```

**翻译流程**:
1. 检查翻译缓存
2. 获取语言包
3. 自动下载缺失语言包
4. 执行翻译
5. 缓存结果

## API 接口

### 语音识别接口

#### 网络识别 (Google Speech Recognition)
```python
def _network_recognition_loop(self):
    r = sr.Recognizer()
    lang_map = {
        'zh': 'zh-CN', 'en': 'en-US', 'ja': 'ja-JP', 'fr': 'fr-FR',
        'de': 'de-DE', 'es': 'es-ES', 'ru': 'ru-RU', 'ko': 'ko-KR'
    }
    
    # 识别流程
    audio_data = sr.AudioData(audio_bytes, 16000, 2)
    text = r.recognize_google(audio_data, language=google_lang)
```

#### 本地识别 (Vosk)
```python
def _local_recognition_loop(self):
    model = Model(model_path)  # model-cn 或 model-en
    recognizer = KaldiRecognizer(model, 16000)
    
    # 识别流程
    if recognizer.AcceptWaveform(audio_bytes):
        result = recognizer.Result()
        text = json.loads(result).get('text', '').strip()
```

### 翻译接口

#### Argos Translate
```python
def translate_text(self, text, from_code, to_code):
    translation = self.get_translation(from_code, to_code)
    if translation and text:
        return translation.translate(text)
    return ""
```

## 配置参数

### 音频配置
```python
# 音频采集参数
samplerate = 16000              # 采样率 (Hz)
frames_per_buffer = 1024        # 缓冲区大小
channels = 1                    # 单声道
format = pyaudio.paInt16        # 16位整数格式
```

### UI配置
```python
# 窗口配置
window_flags = Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint | Qt.Tool
background_alpha = 180          # 背景透明度
border_width = 8               # 边框宽度
border_radius = 30             # 圆角半径

# 字体配置
font_family = '微软雅黑'
font_size_range = (16, 48)     # 字体大小范围
font_weight = QFont.Bold       # 字体粗细
```

### 性能配置
```python
# 队列配置
text_queue_size = 10           # 文本队列大小
audio_energy_history_size = 30 # 音频能量历史长度

# 定时器配置
update_timer_interval = 200    # 字幕更新间隔 (ms)
waveform_timer_interval = 30   # 波形更新间隔 (ms)

# 音频采集配置
audio_duration = 3             # 音频采集时长 (秒)
sleep_interval = 0.05          # 线程休眠间隔 (秒)
```

## 数据流详解

### 1. 音频数据流
```
麦克风 → PyAudio → AudioProcessor.read_audio() → 音频字节 + 能量值
```

**音频处理步骤**:
1. 从麦克风读取原始音频数据
2. 转换为numpy数组
3. 归一化到[-1, 1]范围
4. 计算RMS能量值
5. 返回音频字节和能量

### 2. 识别数据流
```
音频字节 → 语音识别 → 识别文本 → 翻译 → 翻译文本 → 队列 → UI更新
```

**识别流程**:
1. 音频数据转换为AudioData对象
2. 调用识别API获取文本
3. 文本翻译处理
4. 结果放入队列
5. UI定时器读取队列更新显示

### 3. UI更新流
```
队列 → update_subtitle() → _update_label_text() → 重绘界面
```

**更新流程**:
1. 定时器触发更新
2. 批量处理队列数据
3. 检查文本变化
4. 更新标签内容
5. 触发重绘事件

## 性能优化策略

### 1. 内存优化
- **对象池**: 重用音频和UI对象
- **缓存机制**: 翻译结果、字体、语言包缓存
- **队列限制**: 防止内存溢出

### 2. CPU优化
- **线程分离**: UI和识别分离处理
- **批量处理**: 减少UI更新频率
- **条件更新**: 只在文本变化时更新

### 3. 延迟优化
- **非阻塞操作**: 使用put_nowait()避免阻塞
- **定时器优化**: 减少不必要的更新
- **音频参数调优**: 平衡延迟和准确性

## 错误处理

### 异常类型
1. **音频设备异常**: 麦克风不可用
2. **网络异常**: 识别或翻译服务不可用
3. **内存异常**: 队列溢出或缓存过大
4. **线程异常**: 线程意外终止

### 处理策略
```python
# 音频异常处理
try:
    audio_bytes, energy = self.audio_processor.read_audio(3)
except Exception as e:
    print(f"音频处理错误: {e}")
    time.sleep(0.1)
    continue

# 网络异常处理
try:
    text = r.recognize_google(audio_data, language=google_lang)
except Exception:
    text = ''  # 静默失败，继续处理

# 队列异常处理
try:
    self.text_queue.put_nowait((text, translated, energy))
except queue.Full:
    # 丢弃最旧的数据
    try:
        self.text_queue.get_nowait()
        self.text_queue.put_nowait((text, translated, energy))
    except queue.Empty:
        pass
```

## 扩展开发指南

### 添加新语言支持
1. 在`language_options`中添加语言代码
2. 在`lang_map`中添加Google Speech Recognition映射
3. 下载对应的Vosk模型（本地识别）
4. 安装Argos Translate语言包

### 集成新的翻译服务
1. 创建新的翻译管理器类
2. 实现`translate_text()`方法
3. 在`TranslationManager`中添加服务选择逻辑

### 自定义UI主题
1. 修改`paintEvent()`方法
2. 调整颜色、渐变、动画参数
3. 添加新的视觉效果

### 添加新功能
1. 录音功能: 保存音频文件
2. 字幕导出: 保存识别结果
3. 快捷键支持: 全局热键控制
4. 插件系统: 支持第三方扩展

## 调试和监控

### 日志记录
```python
import logging

logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    filename='subtitle_system.log'
)

logger = logging.getLogger(__name__)
```

### 性能监控
```python
import time
import psutil

def monitor_performance():
    cpu_percent = psutil.cpu_percent()
    memory_percent = psutil.virtual_memory().percent
    logger.info(f"CPU: {cpu_percent}%, Memory: {memory_percent}%")
```

### 调试模式
```python
DEBUG_MODE = True

def debug_print(message):
    if DEBUG_MODE:
        print(f"[DEBUG] {message}")
```

## 部署说明

### 打包为可执行文件
```bash
# 使用PyInstaller
pip install pyinstaller
pyinstaller --onefile --windowed transparent_subtitle_optimized.py

# 使用cx_Freeze
pip install cx_Freeze
python setup.py build
```

### 环境配置
```bash
# 创建虚拟环境
python -m venv subtitle_env
source subtitle_env/bin/activate  # Linux/Mac
subtitle_env\Scripts\activate     # Windows

# 安装依赖
pip install -r requirements.txt
```

### 系统服务
```bash
# 创建系统服务 (Linux)
sudo cp subtitle.service /etc/systemd/system/
sudo systemctl enable subtitle.service
sudo systemctl start subtitle.service
```

---

**注意**: 本技术文档适用于系统版本 v1.0.0，后续版本可能有API变化。 