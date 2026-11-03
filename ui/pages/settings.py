from PySide6.QtCore import Qt
from PySide6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLabel

from config import VERSION, PRIVACY_POLICY_URL, TERMS_OF_USE_URL, ACTUAL_INFO_URL, IMPORTANT_INFO_URL
from ui.dialogs.updating import Updating
from infrastructure.network.load_update_info import LoadUpdateInfo
from entities.dto.release import Release
from infrastructure.tools.files import get_svg_widget
from ui.patterns.buttons import MinimalButton
from ui.patterns.content_block import ContentBlock
from ui.patterns.link_card import LinkCard
from ui.patterns.page_title import PageTitle
from infrastructure.tools.is_new_version import is_new_version
from infrastructure.tools.open_url import open_url


class CheckUpdatesBlock(ContentBlock):
    """Блок проверки обновлений"""
    def __init__(self):
        super().__init__()

        self.update_checker = LoadUpdateInfo(ACTUAL_INFO_URL, IMPORTANT_INFO_URL, self)
        self.update_checker.finished.connect(self.show_info)

        update_layout = QHBoxLayout()
        update_layout.setSpacing(20)
        refresh_icon = get_svg_widget("refresh.svg")
        refresh_icon.setObjectName("ContentBlockIcon")
        self.text = QLabel("Проверить обновления?")
        self.button = MinimalButton("Проверить", active=True)
        self.button.clicked.connect(self.button_click)
        update_layout.addWidget(refresh_icon)
        update_layout.addWidget(self.text)
        update_layout.addWidget(self.button)
        self.setLayout(update_layout)

        self.release_info: Release | None = None

    def button_click(self):
        if self.release_info:
            dialog = Updating(self)
            dialog.show_dialog(self.release_info)
        else:
            self.update_checker.start()

    def show_info(self, version_info: Release, important_info: Release):
        if is_new_version(version_info.version, VERSION):
            self.release_info = version_info
            self.text.setText(f"Доступна новая версия: {version_info.version}")
            self.button.setText("Обновить")
        else:
            self.text.setText("Обновления не нужны")



class SettingsPage(QWidget):
    def __init__(self):
        super().__init__()

        page_layout = QVBoxLayout()
        title = PageTitle("Настройки")
        version = QLabel(f"v. {VERSION}")
        version.setObjectName("version")
        version.setAlignment(Qt.AlignmentFlag.AlignCenter)

        setting_list_block = QWidget()
        setting_list_block.setObjectName("SettingListBlock")
        settings_layout = QVBoxLayout()

        update_block = CheckUpdatesBlock()

        privacy_policy_link = LinkCard("Политика конфиденциальности")
        privacy_policy_link.clicked.connect(lambda: open_url(PRIVACY_POLICY_URL))

        terms_of_use_link = LinkCard("Условия использования")
        terms_of_use_link.clicked.connect(lambda: open_url(TERMS_OF_USE_URL))

        white_space = QWidget()

        settings_layout.addWidget(update_block)
        settings_layout.addWidget(privacy_policy_link)
        settings_layout.addWidget(terms_of_use_link)
        settings_layout.addWidget(white_space, 1)

        setting_list_block.setLayout(settings_layout)

        page_layout.addWidget(title)
        page_layout.addWidget(setting_list_block, 1)
        page_layout.addWidget(version)

        self.setLayout(page_layout)

