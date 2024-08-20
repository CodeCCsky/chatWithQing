import sys
from PyQt5.QtWidgets import QApplication, QTextEdit, QVBoxLayout, QWidget, QPushButton, QLineEdit
from PyQt5.QtCore import QThread, pyqtSignal, QTimer
from deepseek_api import deepseek_model

class PyQtDeepSeekThread(QThread):
    text_update = pyqtSignal(str)
    finish_signal = pyqtSignal(str)

    def __init__(self, model: deepseek_model):
        super().__init__()
        self.model = model
        self.message = ""
        self.response_stream = None
        self.last_chunk_time = 0
        self.chunk_interval = 100  # 定时返回的时间间隔，单位为毫秒

    def run(self):
        self.model.add_msg(self.message)
        self.response_stream = self.model.send_message()
        self.last_chunk_time = self.current_time()
        self.timer = QTimer()
        self.timer.timeout.connect(self.check_response)
        self.timer.start(self.chunk_interval)
        self.wait_for_completion()

    def check_response(self):
        if self.response_stream and self.current_time() - self.last_chunk_time >= self.chunk_interval:
            new_text = self.get_new_text()
            if new_text:
                self.text_update.emit(new_text)
                self.last_chunk_time = self.current_time()

    def get_new_text(self):
        new_text = ""
        while True:
            try:
                chunk = next(self.response_stream)
                if chunk.choices[0].delta.content:
                    new_text += chunk.choices[0].delta.content
                if chunk.choices[0].finish_reason:
                    self.finish_signal.emit(chunk.choices[0].finish_reason)
                    self.timer.stop()
                    break
            except StopIteration:
                break
        return new_text

    def current_time(self):
        return self.timer.remainingTime()

    def wait_for_completion(self):
        self.exec_()

    def set_message(self, message):
        self.message = message

class MainWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.initUI()

    def initUI(self):
        self.text_area = QTextEdit(self)
        self.text_area.setReadOnly(True)

        self.input_field = QLineEdit(self)
        self.input_field.setPlaceholderText("Enter your message here")

        self.send_button = QPushButton("Send", self)
        self.send_button.clicked.connect(self.send_message)

        layout = QVBoxLayout()
        layout.addWidget(self.text_area)
        layout.addWidget(self.input_field)
        layout.addWidget(self.send_button)
        self.setLayout(layout)

        self.setWindowTitle('DeepSeek Chat Example')
        self.setGeometry(300, 300, 600, 400)

        self.api_key = "YOUR_API_KEY"  # 替换为你的API密钥
        self.system_prompt = "You are a helpful assistant."
        self.model = deepseek_model(api_key=self.api_key, system_prompt=self.system_prompt)
        self.deepseek_thread = PyQtDeepSeekThread(self.model)
        self.deepseek_thread.text_update.connect(self.update_text)
        self.deepseek_thread.finish_signal.connect(self.finish_message)

    def send_message(self):
        message = self.input_field.text()
        if message:
            self.text_area.append(f"User: {message}")
            self.input_field.clear()
            self.deepseek_thread.set_message(message)
            self.deepseek_thread.start()

    def update_text(self, new_str):
        self.text_area.insertPlainText(new_str)

    def finish_message(self, finish_reason):
        self.text_area.append(f"Finish Reason: {finish_reason}\n")

if __name__ == '__main__':
    app = QApplication(sys.argv)
    main_window = MainWindow()
    main_window.show()
    sys.exit(app.exec_())