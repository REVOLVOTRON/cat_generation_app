import sys
import random
import time
from PyQt6 import QtWidgets, QtGui, QtCore
from PyQt6.QtCore import Qt, QThread, pyqtSignal
import requests


class ImageGeneratorWorker(QThread):
    finished = pyqtSignal(bytes)
    error = pyqtSignal(str)

    def __init__(self, url):
        super().__init__()
        self.url = url

    def run(self):
        try:
            response = requests.get(self.url, timeout=30)
            response.raise_for_status()
            self.finished.emit(response.content)
        except Exception as e:
            self.error.emit(str(e))


class CatGeneratorApp(QtWidgets.QMainWindow):
    def __init__(self):
        super().__init__()
        self.init_ui()

    def init_ui(self):
        self.setWindowTitle("Котопроизводитель")
        self.setFixedSize(620, 600)
        self.central_widget = QtWidgets.QWidget()
        self.setCentralWidget(self.central_widget)
        self.layout = QtWidgets.QVBoxLayout(self.central_widget)

        # Поле для ввода промпта
        self.prompt_field = QtWidgets.QLineEdit()
        self.prompt_field.setPlaceholderText("Введите описание...")
        self.prompt_field.setFixedWidth(600)
        self.prompt_field.setClearButtonEnabled(True)
        self.layout.addWidget(self.prompt_field)

        # Кнопка генерации
        self.generate_button = QtWidgets.QPushButton("Сгенерировать изображение")
        self.generate_button.setFixedWidth(600)
        self.generate_button.setStyleSheet("""
            QPushButton {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0, 
                    stop:0 #A8DADC, stop:1 #008394);
                border-radius: 15px;
                padding: 10px;
                color: white;
                min-height: 40px;
            }
            QPushButton:hover {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0, 
                    stop:0 #008394, stop:1 #A8DADC);
            }
        """)
        self.layout.addWidget(self.generate_button)

        # Область для отображения изображения
        self.image_label = QtWidgets.QLabel()
        self.image_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.image_label.setStyleSheet("""
            border: 2px dashed #CCCCCC;
            border-radius: 10px;
            background: qradialgradient(cx:0.5, cy:0.5, 
                radius: 0.5, fx:0.5, fy:0.5, 
                stop:0 #F0F0F0, stop:1 #E0E0E0);
        """)
        self.image_label.setFixedSize(600, 400)
        self.layout.addWidget(self.image_label, alignment=Qt.AlignmentFlag.AlignCenter)

        # Кнопка сохранения изображения
        self.save_button = QtWidgets.QPushButton("Сохранить изображение")
        self.save_button.setEnabled(False)
        self.save_button.setFixedWidth(600)
        self.save_button.setStyleSheet("""
            QPushButton {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0, 
                    stop:0 #F5EAEA, stop:1 #C54B4B);
                border-radius: 15px;
                padding: 10px;
                color: white;
                min-height: 40px;
            }
            QPushButton:hover {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0, 
                    stop:0 #C54B4B, stop:1 #F5EAEA);
            }
        """)
        self.layout.addWidget(self.save_button)

        # Подключение сигналов
        self.generate_button.clicked.connect(self.start_generation)
        self.save_button.clicked.connect(self.save_image)

    def start_generation(self):
        self.generate_button.setEnabled(False)
        prompt = self.prompt_field.text() or "Крутой кот"
        seed = random.randint(0, 1_000_000)
        model = "flux"  # Фиксированная модель

        url = (
            f"https://pollinations.ai/p/{prompt}"
            f"?width=1024"
            f"&height=1024"
            f"&seed={seed}"
            f"&model={model}"
        )

        self.worker = ImageGeneratorWorker(url)
        self.worker.finished.connect(self.handle_image)
        self.worker.error.connect(self.show_error)
        self.worker.start()

    def handle_image(self, image_data):
        pixmap = QtGui.QPixmap()
        pixmap.loadFromData(image_data)
        scaled_pixmap = pixmap.scaled(
            self.image_label.size(),
            Qt.AspectRatioMode.KeepAspectRatio,
            Qt.TransformationMode.SmoothTransformation
        )
        self.image_label.setPixmap(scaled_pixmap)

        self.generated_image_data = image_data  # Сохраняем данные изображения для последующего сохранения
        self.save_button.setEnabled(True)
        self.generate_button.setEnabled(True)

    def show_error(self, message):
        QtWidgets.QMessageBox.critical(
            self,
            "Ошибка",
            f"Не удалось сгенерировать изображение:\n{message}",
            QtWidgets.QMessageBox.StandardButton.Ok
        )
        self.generate_button.setEnabled(True)

    def save_image(self):
        if hasattr(self, 'generated_image_data'):
            timestamp = int(time.time())
            filename = f"Изображение{timestamp}.jpg"
            with open(filename, 'wb') as f:
                f.write(self.generated_image_data)
            QtWidgets.QMessageBox.information(
                self,
                "Успех",
                f"Изображение сохранено в файл: {filename}",
                QtWidgets.QMessageBox.StandardButton.Ok
            )


if __name__ == '__main__':
    app = QtWidgets.QApplication(sys.argv)
    window = CatGeneratorApp()
    window.show()
    sys.exit(app.exec())