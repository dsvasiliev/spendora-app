from __future__ import annotations

from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QIcon, QTransform
from PySide6.QtWidgets import QDialog, QFrame, QHBoxLayout, QLineEdit, QScrollArea, QVBoxLayout, QWidget, \
    QLabel

from infrastructure.tools.files import get_svg_widget, get_icon
from infrastructure.tools.styles import set_header_color, load_styles
from models.categories_model import CategoriesModel
from models.groups_model import GroupsModel
# from app_context import MODEL
from ui.patterns.buttons import MinimalButton
from entities.dto.group import Group


class SearchListItem(QFrame):
    """Расширение стандартного функционала QFrame для поддержки выделения жирным при поиске"""
    clicked = Signal()

    def __init__(self, text: str, icon: QIcon | None = None, parent=None):
        super().__init__(parent)
        layout = QHBoxLayout()
        layout.setContentsMargins(5, 5, 5, 5)

        # Используем QLabel для текста
        self._label = QLabel(text)

        # Используем QLabel для иконки (лучше работает с transform)
        self._icon_label = QLabel()
        # self.__icon_label.setFixedSize(16, 16)  # Размер иконки

        if icon:
            # Загружаем SVG и конвертируем в QPixmap
            pixmap = icon.pixmap(24, 24)
            self._icon_label.setPixmap(pixmap)

        # Иконка справа, текст слева
        layout.addWidget(self._icon_label, 0)  # stretch factor 0
        layout.addWidget(self._label, 1)  # stretch factor 1

        self.setLayout(layout)
        # self.setCursor(Qt.PointingHandCursor)

    def mouseReleaseEvent(self, event):
        self.clicked.emit()

    def set_html(self, text: str):
        self._label.setText(text)

    def text(self):
        return self._label.text()


class GroupButton(SearchListItem):
    def down_arrow(self):
        """Вращаем иконку на 180 градусов"""
        transform = QTransform()
        transform.rotate(180)
        current_pixmap = self._icon_label.pixmap()
        if current_pixmap and not current_pixmap.isNull():
            rotated_pixmap = current_pixmap.transformed(transform, Qt.TransformationMode.SmoothTransformation)
            self._icon_label.setPixmap(rotated_pixmap)

    def up_arrow(self):
        """Возвращаем иконку в исходное положение"""
        transform = QTransform()
        transform.rotate(180)
        current_pixmap = self._icon_label.pixmap()
        if current_pixmap and not current_pixmap.isNull():
            # Восстанавливаем исходную иконку
            rotated_pixmap = current_pixmap.transformed(transform, Qt.TransformationMode.SmoothTransformation)
            self._icon_label.setPixmap(rotated_pixmap)


class CategoryButton(SearchListItem):
    """Кнопка категории"""
    clicked = Signal(int)

    def __init__(self, text: str, category_id: int, icon: QIcon | None = None, parent: QWidget | None = None, ):
        super().__init__(text, icon, parent)
        self.setObjectName("categorySubItem")
        self._category_id = category_id

    def mouseReleaseEvent(self, event):
        self.clicked.emit(self._category_id)


def highlight_match(string: str, lowercase_search: str, lowercase_string: str) -> str:
    """Выделить жирным совпадение"""
    pos = lowercase_string.find(lowercase_search)

    search_len = len(lowercase_search)

    return f'{string[:pos]}<span style="font-weight: bold;">{string[pos:pos + search_len]}</span>{string[pos + search_len:]}'


class GroupCard(QFrame):
    """Раскрывающаяся карточка группы"""
    category_selected = Signal(int)

    def __init__(
            self,
            group: Group,
            arrow_icon: QIcon,
            categories_model: CategoriesModel,
            parent: QWidget | None = None,
    ) -> None:
        super().__init__(parent)
        self.setObjectName("categoryGroupCard")

        self._title = group.name
        self.categories_id = group.categories_id
        self._categories_titles = [categories_model.get_title_by_id(category_id) for category_id in
                                   group.categories_id]
        self._case_fold_titles = [
            subcategory.casefold() for subcategory in self._categories_titles
        ]
        self._categories_count = len(group.categories_id)

        self.expanded = False  # Меню было развёрнуто пользователем
        self._old_expanded: bool | None = None  # Развёртывание до начала поиска

        root = QVBoxLayout()
        root.setContentsMargins(0, 0, 0, 0)
        root.setSpacing(0)

        self._header = GroupButton(
            self._title,
            arrow_icon
        )
        self._header.setObjectName("categoryGroupHeader")
        self._header.setCursor(Qt.CursorShape.PointingHandCursor)
        self._header.setLayoutDirection(Qt.LayoutDirection.RightToLeft)
        self._header.clicked.connect(self.toggle)

        self._body = QWidget()
        body_layout = QVBoxLayout(self._body)
        body_layout.setContentsMargins(0, 0, 0, 4)
        body_layout.setSpacing(0)

        self._categories_widgets: list[SearchListItem] = []
        for list_index in range(self._categories_count):
            category_btn = CategoryButton(self._categories_titles[list_index], group.categories_id[list_index])
            category_btn.clicked.connect(self.category_selected)
            category_btn.setCursor(Qt.CursorShape.PointingHandCursor)
            body_layout.addWidget(category_btn)
            self._categories_widgets.append(category_btn)

            # line_widget = QWidget()
            # line_widget.setObjectName("LineBetweenCategories")
            # line_widget.setAttribute(Qt.WidgetAttribute.WA_StyledBackground, True)
            # body_layout.addWidget(line_widget)

        self._body.setVisible(False)
        # self._header.setEnabled(bool(categories_id))

        root.addWidget(self._header)
        root.addWidget(self._body)

        self.setLayout(root)

    def __open_body(self):
        """Развернуть меню"""
        self._header.down_arrow()
        self._body.setVisible(True)

    def __close_body(self):
        """Свернуть меню"""
        self._header.up_arrow()
        self._body.setVisible(False)

    def toggle(self) -> None:
        """Развернуть или свернуть категорию"""
        self.expanded = not self.expanded
        if self.expanded:
            self.__open_body()
        else:
            self.__close_body()

    def set_expanded(self, expanded: bool) -> None:
        if expanded == self.expanded:
            return
        self.toggle()

    def reset_filter(self):
        """Сброс фильтра"""
        self._header.set_html(self._title)
        for i in range(self._categories_count):
            button = self._categories_widgets[i]
            button.set_html(self._categories_titles[i])
            button.setVisible(True)
        self.setVisible(True)
        self.set_expanded(self._old_expanded if not self._old_expanded is None else False)

    def set_filter(self, normalized_search: str):
        """Показывает карточку, если совпадает заголовок или хотя бы один подпункт"""
        if normalized_search == "":
            self.reset_filter()
            return

        if self._old_expanded is None:
            self._old_expanded = self.expanded

        visible_buttons = any(normalized_search in cf_sb for cf_sb in self._case_fold_titles)
        title_match = normalized_search in self._title.casefold()
        if not title_match and not visible_buttons:
            self.setVisible(False)
            return
        self.setVisible(True)

        # Совпадение заголовка
        if title_match:
            self._header.set_html(highlight_match(self._title, normalized_search, self._title.casefold()))

        # Совпадения среди подкатегорий
        if visible_buttons:
            self.set_expanded(True)
            for i in range(self._categories_count):
                if normalized_search in self._case_fold_titles[i]:
                    self._categories_widgets[i].setVisible(True)
                    self._categories_widgets[i].set_html(
                        highlight_match(
                            self._categories_titles[i],
                            normalized_search,
                            self._case_fold_titles[i]
                        )
                    )
                else:
                    self._categories_widgets[i].setVisible(False)
        else:
            self.set_expanded(False)


class CategorySelectDialog(QDialog):
    """Диалоговое окно выбора категории"""

    def __init__(
            self,
            categories_model: CategoriesModel,
            groups_model: GroupsModel,
            parent: QWidget
    ) -> None:
        super().__init__(parent)

        self.categories_model = categories_model
        self.groups_model = groups_model

        self.setWindowTitle("Выбор категории")

        self.setMinimumHeight(420)
        self.setMaximumHeight(580)
        self.setMinimumWidth(420)
        self.setMaximumWidth(580)

        self.setAttribute(Qt.WidgetAttribute.WA_StyledBackground, True)

        self._selected_category: int = -1
        self._group_widgets: list[GroupCard] = []

        root = QVBoxLayout(self)
        root.setContentsMargins(14, 14, 10, 14)
        root.setSpacing(12)

        search_row = QHBoxLayout()
        search_row.setSpacing(8)

        self._search_field = QLineEdit()
        self._search_field.setObjectName("categorySearchField")
        self._search_field.setPlaceholderText("Найти категорию....")
        self._search_field.textChanged.connect(self._search_text_changed)

        self._reset_search_btn = MinimalButton(
            None,
            False,
            get_svg_widget("X.svg"),
            width=44
        )
        self._reset_search_btn.setObjectName("resetSearchButton")
        self._reset_search_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self._reset_search_btn.clicked.connect(self._reset_search)

        search_row.addWidget(self._search_field, 1)
        search_row.addWidget(self._reset_search_btn)
        root.addLayout(search_row)

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setHorizontalScrollBarPolicy(
            Qt.ScrollBarPolicy.ScrollBarAlwaysOff
        )
        scroll.setFrameShape(QFrame.Shape.NoFrame)

        list_host = QWidget()
        self._list_layout = QVBoxLayout(list_host)
        self._list_layout.setContentsMargins(0, 10, 0, 0)
        self._list_layout.setSpacing(10)
        self._list_layout.addStretch(1)
        scroll.setWidget(list_host)
        root.addWidget(scroll, 1)

        load_styles(self, "select_category_menu.qss")

    # def _on_subcategory_chosen(self, group: str, name: str) -> None:
    #     self.category_chosen.emit(group, name)
    #     self.accept()

    def _search_text_changed(self, text: str) -> None:
        """Изменение текста в поле ввода вызывает поиск или сброс фильтров"""
        normalized_search = text.strip().casefold()
        if normalized_search == "":
            self._reset_search_btn.setEnabled(False)
            for card in self._group_widgets:
                card.reset_filter()
        else:
            self._reset_search_btn.setEnabled(True)
            for card in self._group_widgets:
                card.set_filter(normalized_search)

    def _reset_search(self):
        """Сброс поиска"""
        self._search_field.setText("")

    def reset(self):
        """Глубокая очистка с рекурсивным удалением."""
        widgets_to_delete = []

        # Собираем все GroupCard
        for i in range(self._list_layout.count()):
            item = self._list_layout.itemAt(i)
            if item and item.widget() and isinstance(item.widget(), GroupCard):
                widgets_to_delete.append(item.widget())

        # Рекурсивно удаляем все вложенные виджеты
        for group_card in widgets_to_delete:
            group_card.setParent(None)
            group_card.deleteLater()

        self._group_widgets.clear()

        # Принудительная обработка событий
        self._list_layout.invalidate()
        self._list_layout.activate()

    def update_data(self):
        """Обновить категории и группы"""
        self.reset()
        expand_arrow_icon = get_icon("Expand_arrow.svg")
        for group in self.groups_model.get_all():
            group_card = GroupCard(
                group,
                expand_arrow_icon,
                self.categories_model
            )
            group_card.category_selected.connect(self.set_selected)
            insert_at = self._list_layout.count() - 1
            self._list_layout.insertWidget(insert_at, group_card)
            self._group_widgets.append(group_card)

    def set_selected(self, category_id: int):
        """Запоминаем значение выбранной категории и закрываем меню"""
        self._selected_category = category_id
        self.close()

    def show_dialog(self, now_id: int) -> int:
        """Показать меню"""
        self._reset_search()
        if now_id > -1:
            for group in self._group_widgets:
                group.set_expanded(now_id in group.categories_id)
        set_header_color(self)
        self.exec()
        selected_category = self._selected_category
        self._selected_category = -1
        return selected_category
