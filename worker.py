import requests
from PyQt6.QtCore import QThread, pyqtSignal


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