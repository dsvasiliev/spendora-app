import sys
from PySide6.QtWidgets import QApplication

from app_context import AppContext
from ui.main_window import MainWindow
from models.settings_model import SettingsModel
from infrastructure.tools.fonts import load_fonts

app = QApplication([])
load_fonts(app, "ui/src/fonts/Commissioner-VariableFont_FLAR,VOLM,slnt,wght.ttf")
# try:
app_context = AppContext()
window = MainWindow(app_context)
window.show()
os_memory = SettingsModel()
os_memory.check_if_back()
sys.exit(app.exec())
# except Exception as e:
#     window = QMainWindow()
#     QMessageBox.critical(
#         window,
#         "Критическая ошибка",
#         f"В приложении произошла критическая ошибка: {e}. Пожалуйста, сообщите нам об этом по почте {EMAIL}"
#     )
#     sys.exit(app.exec())

# TODO: сделать вывод и логирование ошибок
# TODO: почистить комментарии и выводы типа print()
# TODO: разобраться с тестированием и убрать тестовые компоненты
