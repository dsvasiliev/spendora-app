import requests
from PySide6.QtCore import QThread, Signal
import tempfile


class DownloadUpdate(QThread):
    """Процесс скачивания обновления"""
    set_total = Signal(int)
    progress = Signal(int)
    finished = Signal(str)
    error = Signal(str)

    def __init__(self):
        super().__init__()
        self.url = ""

    def set_url(self, url):
        """Установить URL для загрузки"""
        self.url = url

    def run(self):
        try:
            pass
            response = requests.get(self.url, stream=True, timeout=30)
            total = int(response.headers.get("content-length", 0))
            self.set_total.emit(total)

            tmp = tempfile.NamedTemporaryFile(delete=False, suffix=".exe", prefix="spendora_installer_")
            downloaded = 0

            for chunk in response.iter_content(chunk_size=8192):
                tmp.write(chunk)
                downloaded += len(chunk)
                if total:
                    self.progress.emit(downloaded)
            tmp.close()
            self.finished.emit(tmp.name)
        except Exception as e:
            self.error.emit(str(e))