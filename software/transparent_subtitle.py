import sys
from PyQt5.QtWidgets import QApplication, QWidget, QLabel, QMenu, QAction, QDialog, QVBoxLayout, QHBoxLayout, QComboBox, QPushButton, QSlider, QFormLayout
import PyQt5.QtCore as QtCore
from PyQt5.QtGui import QPainter, QLinearGradient, QColor, QFont, QBrush, QPen, QFontMetrics
import threading
import queue
import time
import pyaudio
import speech_recognition as sr

# Argos-translate相关导入
import numpy as np
from argostranslate import package, translate
import json

class SettingsDialog(QDialog):
    def __init__(self, parent, language_options, current_rec_lang, current_trans_lang, font_size, mic_list, current_mic, display_mode, recog_mode):
        super().__init__(parent)
        self.setWindowTitle('设置')
        self.setFixedSize(350, 400)
        self.setStyleSheet('background: qlineargradient(x1:0, y1:0, x2:1, y2:1, stop:0 #232526, stop:1 #414345); color: white; border-radius: 12px;')
        layout = QVBoxLayout()
        form = QFormLayout()
        # 识别语言
        self.rec_lang_combo = QComboBox()
        self.rec_lang_combo.addItems(language_options)
        self.rec_lang_combo.setCurrentText(current_rec_lang)
        form.addRow('识别语言:', self.rec_lang_combo)
        # 翻译目标语言
        self.trans_lang_combo = QComboBox()
        self.trans_lang_combo.addItems(language_options)
        self.trans_lang_combo.setCurrentText(current_trans_lang)
        form.addRow('翻译目标:', self.trans_lang_combo)
        # 麦克风选择
        self.mic_combo = QComboBox()
        self.mic_combo.addItems(mic_list)
        if current_mic in mic_list:
            self.mic_combo.setCurrentText(current_mic)
        form.addRow('麦克风:', self.mic_combo)
        # 字体大小
        self.font_slider = QSlider(QtCore.Qt.Horizontal)
        self.font_slider.setMinimum(16)
        self.font_slider.setMaximum(48)
        self.font_slider.setValue(font_size)
        self.font_slider.setTickInterval(2)
        self.font_slider.setTickPosition(QSlider.TicksBelow)
        form.addRow('字体大小:', self.font_slider)
        # 字幕展示模式
        self.display_mode_combo = QComboBox()
        self.display_mode_combo.addItems(['双语', '仅原文', '仅译文'])
        self.display_mode_combo.setCurrentText(display_mode)
        form.addRow('字幕展示:', self.display_mode_combo)
        # 识别方式
        self.recog_mode_combo = QComboBox()
        self.recog_mode_combo.addItems(['网络', '本地'])
        self.recog_mode_combo.setCurrentText(recog_mode)
        form.addRow('识别方式:', self.recog_mode_combo)
        layout.addLayout(form)
        # 按钮
        btn_layout = QHBoxLayout()
        self.ok_btn = QPushButton('确定')
        self.ok_btn.setStyleSheet('background-color: #00c6ff; color: white; border-radius: 8px; padding: 6px 18px;')
        self.cancel_btn = QPushButton('取消')
        self.cancel_btn.setStyleSheet('background-color: #888; color: white; border-radius: 8px; padding: 6px 18px;')
        btn_layout.addWidget(self.ok_btn)
        btn_layout.addWidget(self.cancel_btn)
        layout.addLayout(btn_layout)
        self.setLayout(layout)
        self.ok_btn.clicked.connect(self.accept)
        self.cancel_btn.clicked.connect(self.reject)

    def get_settings(self):
        return (self.rec_lang_combo.currentText(), self.trans_lang_combo.currentText(), self.font_slider.value(), self.mic_combo.currentText(), self.display_mode_combo.currentText(), self.recog_mode_combo.currentText())

class TransparentSubtitle(QWidget):
    def __init__(self):
        super().__init__()
        self.show_border = False
        self.dragging = False
        self.drag_position = None
        self.language_options = ['en', 'zh', 'ja', 'fr', 'de', 'es', 'ru', 'ko']
        self.recognition_language = 'en'
        self.translation_language = 'zh'
        self.font_size = 28
        self.display_mode = '双语'
        self.recog_mode = '网络'
        self.audio_energy_history = [0]*30  # 用于波形动画
        self.mic_list, self.current_mic = self.get_mic_list_and_default()
        self.initUI()
        self.text_queue = queue.Queue()
        self.recognized_text = ''
        self.translated_text = ''
        self.running = True
        self.start_recognition_thread()
        self.update_timer = QtCore.QTimer(self)
        self.update_timer.timeout.connect(self.update_subtitle)
        self.update_timer.start(300)
        self.waveform_timer = QtCore.QTimer(self)
        self.waveform_timer.timeout.connect(self.update_waveform)
        self.waveform_timer.start(50)

    def get_mic_list_and_default(self):
        pa = pyaudio.PyAudio()
        mic_list = []
        default_idx = None
        for i in range(pa.get_device_count()):
            info = pa.get_device_info_by_index(i)
            if info['maxInputChannels'] > 0:
                mic_list.append(f"{info['name']} (ID:{i})")
                if default_idx is None and info.get('defaultSampleRate', 0) > 0:
                    default_idx = i
        current_mic = mic_list[default_idx] if default_idx is not None and default_idx < len(mic_list) else (mic_list[0] if mic_list else '')
        pa.terminate()
        return mic_list, current_mic

    def initUI(self):
        self.setWindowFlags(QtCore.Qt.FramelessWindowHint | QtCore.Qt.WindowStaysOnTopHint | QtCore.Qt.Tool)
        self.setAttribute(QtCore.Qt.WA_TranslucentBackground)
        self.setGeometry(300, 800, 800, 120)
        self.setWindowTitle('实时字幕')

        self.label = QLabel('', self)
        self.label.setAlignment(QtCore.Qt.AlignCenter)
        self.label.setStyleSheet('color: white; background: transparent;')
        font = QFont('微软雅黑', self.font_size, QFont.Bold)
        self.label.setFont(font)
        self.label.setGeometry(0, 0, 800, 120)

    def update_waveform(self):
        # 波形高度渐变消失
        self.audio_energy_history = [v*0.92 for v in self.audio_energy_history]
        self.update()

    def update_subtitle(self):
        updated = False
        while not self.text_queue.empty():
            self.recognized_text, self.translated_text, energy = self.text_queue.get()
            updated = True
            self.audio_energy_history = self.audio_energy_history[1:] + [energy]
        if updated:
            self.label.setFont(QFont('微软雅黑', self.font_size, QFont.Bold))
            fm = QFontMetrics(self.label.font())
            if self.display_mode == '双语':
                text_width = max(fm.width(self.recognized_text), fm.width(self.translated_text))
                self.setFixedHeight(320)
                self.label.setGeometry(0, 0, 800, 320)
                self.label.setText(f'{self.recognized_text}<br><span style="color:#00ffcc;">{self.translated_text}</span>')
            elif self.display_mode == '仅原文':
                text_width = fm.width(self.recognized_text)
                self.setFixedHeight(160)
                self.label.setGeometry(0, 0, 800, 160)
                self.label.setText(f'{self.recognized_text}')
            elif self.display_mode == '仅译文':
                text_width = fm.width(self.translated_text)
                self.setFixedHeight(160)
                self.label.setGeometry(0, 0, 800, 160)
                self.label.setText(f'<span style="color:#00ffcc;">{self.translated_text}</span>')
            # 设置窗口和label宽度（更大范围）
            min_width = 600
            max_width = 1800
            width = min(max(text_width + 80, min_width), max_width)
            self.setFixedWidth(width)
            self.label.setFixedWidth(width)
            self.label.move(0, 0)

    def start_recognition_thread(self):
        self.rec_thread = threading.Thread(target=self.recognition_loop, daemon=True)
        self.rec_thread.start()

    def recognition_loop(self):
        if self.recog_mode == '网络':
            # SpeechRecognition + Google API
            pa = pyaudio.PyAudio()
            mic_index = 0
            for i in range(pa.get_device_count()):
                info = pa.get_device_info_by_index(i)
                if f"{info['name']} (ID:{i})" == self.current_mic:
                    mic_index = i
                    break
            samplerate = 16000
            block_duration = 5
            frames_per_buffer = 1024
            total_frames = int(samplerate * block_duration)
            r = sr.Recognizer()
            installed_languages = translate.get_installed_languages()
            from_lang = to_lang = None
            for lang in installed_languages:
                if lang.code == self.recognition_language:
                    from_lang = lang
                if lang.code == self.translation_language:
                    to_lang = lang
            if not from_lang or not to_lang:
                packages = package.get_available_packages()
                for p in packages:
                    if p.from_code == self.recognition_language and p.to_code == self.translation_language:
                        package.install_from_path(p.download())
                installed_languages = translate.get_installed_languages()
                for lang in installed_languages:
                    if lang.code == self.recognition_language:
                        from_lang = lang
                    if lang.code == self.translation_language:
                        to_lang = lang
            translation = from_lang.get_translation(to_lang)
            lang_map = {
                'zh': 'zh-CN',
                'en': 'en-US',
                'ja': 'ja-JP',
                'fr': 'fr-FR',
                'de': 'de-DE',
                'es': 'es-ES',
                'ru': 'ru-RU',
                'ko': 'ko-KR'
            }
            while self.running:
                stream = pa.open(format=pyaudio.paInt16, channels=1, rate=samplerate, input=True, input_device_index=mic_index, frames_per_buffer=frames_per_buffer)
                audio_frames = []
                for _ in range(0, total_frames, frames_per_buffer):
                    data = stream.read(frames_per_buffer, exception_on_overflow=False)
                    audio_frames.append(data)
                stream.stop_stream()
                stream.close()
                audio_bytes = b''.join(audio_frames)
                audio_np = np.frombuffer(audio_bytes, dtype=np.int16).astype(np.float32) / 32768.0
                energy = float(np.sqrt(np.mean(audio_np**2)))
                audio_data = sr.AudioData(audio_bytes, samplerate, 2)
                google_lang = lang_map.get(self.recognition_language, self.recognition_language)
                try:
                    text = r.recognize_google(audio_data, language=google_lang)
                except Exception:
                    text = ''
                if text:
                    try:
                        translated = translation.translate(text)
                    except Exception:
                        translated = ''
                    self.text_queue.put((text, translated, energy))
                else:
                    self.text_queue.put(("", "", energy))
                time.sleep(0.1)
            pa.terminate()
        else:
            # vosk本地识别
            from vosk import Model, KaldiRecognizer
            import json
            if self.recognition_language == 'zh':
                model_path = 'model-cn'
            else:
                model_path = 'model-en'
            model = Model(model_path)
            recognizer = KaldiRecognizer(model, 16000)
            installed_languages = translate.get_installed_languages()
            from_lang = to_lang = None
            for lang in installed_languages:
                if lang.code == self.recognition_language:
                    from_lang = lang
                if lang.code == self.translation_language:
                    to_lang = lang
            if not from_lang or not to_lang:
                packages = package.get_available_packages()
                for p in packages:
                    if p.from_code == self.recognition_language and p.to_code == self.translation_language:
                        package.install_from_path(p.download())
                installed_languages = translate.get_installed_languages()
                for lang in installed_languages:
                    if lang.code == self.recognition_language:
                        from_lang = lang
                    if lang.code == self.translation_language:
                        to_lang = lang
            translation = from_lang.get_translation(to_lang)
            samplerate = 16000
            block_duration = 5
            pa = pyaudio.PyAudio()
            mic_index = 0
            for i in range(pa.get_device_count()):
                info = pa.get_device_info_by_index(i)
                if f"{info['name']} (ID:{i})" == self.current_mic:
                    mic_index = i
                    break
            frames_per_buffer = 1024
            total_frames = int(samplerate * block_duration)
            while self.running:
                stream = pa.open(format=pyaudio.paInt16, channels=1, rate=samplerate, input=True, input_device_index=mic_index, frames_per_buffer=frames_per_buffer)
                audio_frames = []
                for _ in range(0, total_frames, frames_per_buffer):
                    data = stream.read(frames_per_buffer, exception_on_overflow=False)
                    audio_frames.append(data)
                stream.stop_stream()
                stream.close()
                audio_bytes = b''.join(audio_frames)
                audio_np = np.frombuffer(audio_bytes, dtype=np.int16).astype(np.float32) / 32768.0
                energy = float(np.sqrt(np.mean(audio_np**2)))
                text = ''
                if recognizer.AcceptWaveform(audio_bytes):
                    result = recognizer.Result()
                    try:
                        text = json.loads(result).get('text', '').strip()
                    except Exception:
                        text = ''
                if text:
                    try:
                        translated = translation.translate(text)
                    except Exception:
                        translated = ''
                    self.text_queue.put((text, translated, energy))
                else:
                    self.text_queue.put(("", "", energy))
                time.sleep(0.1)
            pa.terminate()

    def open_settings(self):
        dlg = SettingsDialog(self, self.language_options, self.recognition_language, self.translation_language, self.font_size, self.mic_list, self.current_mic, self.display_mode, self.recog_mode)
        if dlg.exec_():
            rec_lang, trans_lang, font_size, mic_name, display_mode, recog_mode = dlg.get_settings()
            self.recognition_language = rec_lang
            self.translation_language = trans_lang
            self.font_size = font_size
            self.current_mic = mic_name
            self.display_mode = display_mode
            self.recog_mode = recog_mode
            self.label.setFont(QFont('微软雅黑', self.font_size, QFont.Bold))
            # 动态调整高度
            if self.display_mode == '双语':
                self.setFixedHeight(320)
                self.label.setGeometry(0, 0, self.width(), 320)
            else:
                self.setFixedHeight(160)
                self.label.setGeometry(0, 0, self.width(), 160)
            # 正确关闭旧线程再重启                                                                                                          
            self.running = False                                                      
            if hasattr(self, 'rec_thread') and self.rec_thread.is_alive():                             
                self.rec_thread.join(timeout=2)
            self.running = True
            self.start_recognition_thread()

    def enterEvent(self, event):
        self.show_border = True
        self.update()
        super().enterEvent(event)

    def leaveEvent(self, event):
        self.show_border = False
        self.update()
        super().leaveEvent(event)

    def mousePressEvent(self, event):
        if event.button() == QtCore.Qt.LeftButton:
            self.dragging = True
            self.drag_position = event.globalPos() - self.frameGeometry().topLeft()
            event.accept()
        super().mousePressEvent(event)

    def mouseMoveEvent(self, event):
        if self.dragging and event.buttons() & QtCore.Qt.LeftButton:
            self.move(event.globalPos() - self.drag_position)
            event.accept()
        super().mouseMoveEvent(event)

    def mouseReleaseEvent(self, event):
        if event.button() == QtCore.Qt.LeftButton:
            self.dragging = False
            event.accept()
        super().mouseReleaseEvent(event)

    def paintEvent(self, event):
        painter = QPainter(self)
        rect = self.rect()
        border_width = 8
        # 波形参数
        waveform_bar_count = len(self.audio_energy_history)
        bar_width = 8
        max_bar_height = rect.height() * 0.7
        spacing = 2
        # 仅在鼠标在窗口内时绘制渐变边框和波形
        if self.show_border:
            gradient = QLinearGradient(rect.topLeft(), rect.topRight())
            gradient.setColorAt(0, QColor(0, 255, 255, 180))
            gradient.setColorAt(1, QColor(255, 0, 255, 180))
            pen = QPen(QBrush(gradient), border_width)
            painter.setPen(pen)
            painter.setBrush(QBrush(QtCore.Qt.NoBrush))
            painter.drawRoundedRect(rect.adjusted(border_width//2, border_width//2, -border_width//2, -border_width//2), 30, 30)
            # 左右波形
            for i, v in enumerate(self.audio_energy_history):
                # 渐变高度
                bar_height = max_bar_height * min(1.0, v*6)
                fade = 1.0 - abs(i - waveform_bar_count//2)/(waveform_bar_count//2)
                color = QColor(0, 255, 255, int(120*fade+60))
                # 左侧
                x_left = rect.left() + border_width + i*(bar_width+spacing)
                y = rect.center().y() - bar_height/2
                painter.fillRect(x_left, y, bar_width, bar_height, color)
                # 右侧对称
                x_right = rect.right() - border_width - (i+1)*(bar_width+spacing)
                painter.fillRect(x_right, y, bar_width, bar_height, color)
        # 半透明背景
        painter.setPen(QPen(QtCore.Qt.NoPen))
        painter.setBrush(QColor(30, 30, 30, 180))
        painter.drawRoundedRect(rect.adjusted(border_width, border_width, -border_width, -border_width), 30, 30)

    def close_app(self):
        self.running = False
        QtCore.QCoreApplication.quit()

    def contextMenuEvent(self, event):
        menu = QMenu(self)
        action_settings = QAction('设置', self)
        action_exit = QAction('退出', self)
        action_settings.triggered.connect(self.open_settings)
        action_exit.triggered.connect(self.close_app)
        menu.addAction(action_settings)
        menu.addAction(action_exit)
        menu.exec_(event.globalPos())

if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = TransparentSubtitle()
    window.show()
    sys.exit(app.exec_()) 