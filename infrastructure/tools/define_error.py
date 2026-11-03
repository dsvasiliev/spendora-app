from PySide6.QtWidgets import QWidget

# from dialogs.warning import WarningDialog
# from tools.files import get_icon


def define_error(
        where: str,
        user_message: str = "",
        error: Exception | None = None,
        widget: QWidget | None = None,
        fatal: bool = False,
):
    """Вывод информации об ошибке"""
    if fatal:
        error_type = "Критическая ошибка"
    else:
        error_type = "Ошибка"
    print(f'{error_type} ({where}, {user_message}): {error}')
    # if widget:
    #     notification = WarningDialog(
    #         "Ошибка",
    #         f'{error_type}: {user_message}',
    #         get_icon("Warning.svg"),
    #         widget,
    #         ok_text="Ок",
    #     )
    #     if fatal:
    #         notification.ok.connect(lambda: exit(0))
    #     notification.show_dialog()
    #     if fatal:
    #         exit(0)