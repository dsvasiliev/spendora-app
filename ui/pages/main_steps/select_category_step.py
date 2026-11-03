from PySide6.QtCore import Qt, QSize, Signal
from PySide6.QtGui import QIcon, QTransform
from PySide6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QScrollArea, QFrame

from models.categories_model import CategoriesModel
from models.products_model import ProductsModel
from services.making_result_service import MakingResultService
from services.select_categories_service import SelectCategoriesService
from ui.dialogs.select_category import CategorySelectDialog
from infrastructure.tools.text import slice_text
from infrastructure.tools.files import get_svg_widget, get_icon
from ui.patterns.buttons import PrimaryButton
from ui.patterns.content_block import ContentBlock
from ui.patterns.page_title import PageTitle
from entities.dto.product import Product, DetectionType


def _arrow_pixmap(expanded: bool, size: int = 16) -> QIcon:
    icon = get_icon("Black arrow.svg")
    pixmap = icon.pixmap(size, size)
    if expanded:
        transform = QTransform().rotate(90)
        pixmap = pixmap.transformed(transform, Qt.TransformationMode.SmoothTransformation)
    return QIcon(pixmap)


class ProductsRow(QWidget):
    """Строка продукта в одном из раскрывающихся списков"""

    on_delete = Signal(int)

    def __init__(
            self,
            list_index: int,
            product: Product,
            category_select_dialog: CategorySelectDialog,
            categories_model: CategoriesModel,
            select_categories_service: SelectCategoriesService,
            parent: QWidget | None = None,
    ):
        super().__init__(parent)

        self.categories_model = categories_model
        self.select_categories_service = select_categories_service
        self.category_select_dialog = category_select_dialog

        self.setAttribute(Qt.WidgetAttribute.WA_StyledBackground, True)

        self.products_id = product.id
        self.category_id = product.category_id

        layout = QHBoxLayout()
        layout.setContentsMargins(20, 10, 20, 10)
        layout.setSpacing(12)

        index_label = QLabel(f"{list_index}.")
        index_label.setObjectName("categoryIndex")
        index_label.setFixedWidth(24)

        name_label = QLabel(slice_text(product.name, 35))
        name_label.setObjectName("categoryName")
        name_label.setWordWrap(False)

        price_label = QLabel()
        if product.count % 1 == 0:
            price_label.setText(str(product.price) + "₽, " + str(int(product.count)) + " шт.")
        else:
            price_label.setText(str(product.price) + "₽ x " + str(product.count))
        price_label.setObjectName("categoryPrice")

        category_widget = self._build_category_widget()

        trash_btn = QPushButton()
        trash_btn.setObjectName("categoryTrashBtn")
        trash_btn.setIcon(get_icon("Trash.svg"))
        trash_btn.setIconSize(QSize(20, 20))
        trash_btn.setFixedSize(32, 32)
        trash_btn.clicked.connect(lambda: self.on_delete.emit(self.products_id))

        layout.addWidget(index_label)
        layout.addWidget(name_label, 1)
        layout.addWidget(price_label)
        layout.addWidget(category_widget, 1)
        layout.addWidget(trash_btn)

        self.set_styles(self.categories_model.get_title_by_id(self.category_id), product.detection_type)

        self.setLayout(layout)

    def _show_dialog(self):
        """Открытие диалогового окна выбора категории"""
        new_category_id = self.category_select_dialog.show_dialog(self.category_id)
        if new_category_id > -1:
            # Обновление категории
            self.select_categories_service.set_category(
                self.products_id,
                new_category_id,
                DetectionType.FROM_DB
            )
            self.set_styles(self.categories_model.get_title_by_id(new_category_id), DetectionType.FROM_DB)

    def _build_category_widget(self) -> QWidget:
        """Конструктор кнопки выбора категории"""
        category_button = QPushButton()

        category_button.setObjectName("categorySelector")
        category_button.setCursor(Qt.CursorShape.PointingHandCursor)
        category_button.clicked.connect(self._show_dialog)
        category_button.setFlat(True)

        inner = QHBoxLayout(category_button)
        # inner.setContentsMargins(10, 6, 10, 6)
        inner.setSpacing(9)

        self.ai_icon = QLabel()
        self.ai_icon.setObjectName("categoryAiIcon")
        self.ai_icon.setFixedSize(18, 18)
        inner.addWidget(self.ai_icon)

        self.category_name = QLabel()
        self.category_name.setAlignment(Qt.AlignmentFlag.AlignCenter)
        inner.addWidget(self.category_name, 1)

        self.arrow = QLabel()
        # arrow.setPixmap(QIcon(icon_path("Select_category.svg")).pixmap(18, 18))
        self.arrow.setObjectName("categoryColorArrow")
        self.arrow.setFixedSize(18, 18)
        inner.addWidget(self.arrow)

        return category_button

    def set_styles(self, category_name: str, row_type: DetectionType):
        """Модифицируем стили в соответствии типом записи"""
        if row_type == DetectionType.DETECTED:
            self.setObjectName("categoryItemDetected")
            self.category_name.setStyleSheet("color: #BF6F4D")
            self.ai_icon.setPixmap(get_icon("AI.svg").pixmap(18, 18))
            self.category_name.setVisible(True)
            self.arrow.setPixmap(get_icon("Select_category_active.svg").pixmap(18, 18))
        elif row_type == DetectionType.FROM_DB:
            self.setObjectName("categoryItemFromDB")
            self.category_name.setStyleSheet("color: black")
            self.ai_icon.setVisible(False)
            self.category_name.setVisible(True)
            self.arrow.setPixmap(get_icon("Select_category.svg").pixmap(18, 18))
        else:
            self.setObjectName("categoryItemUnknown")
            self.category_name.setVisible(False)
            self.ai_icon.setVisible(False)
            self.arrow.setPixmap(get_icon("Select_category_active.svg").pixmap(18, 18))

        self.category_name.setText(category_name)


class CollapsibleSection(QWidget):
    """Раскрывающийся блок со списком позиций"""

    # change_category = Signal(int, int)

    def __init__(self,
                 categories_model: CategoriesModel,
                 products_model: ProductsModel,
                 category_select_dialog: CategorySelectDialog,
                 select_categories_service: SelectCategoriesService,
                 title: str | None = None,
                 parent: QWidget | None = None
                 ):
        super().__init__(parent)
        self._expanded = False

        self.categories_model = categories_model
        self.products_model = products_model
        self.select_categories_service = select_categories_service
        self.category_select_dialog = category_select_dialog

        root = QVBoxLayout(self)
        root.setContentsMargins(0, 0, 0, 0)
        root.setSpacing(0)

        self._header_btn = QPushButton(title if title else "")
        self._header_btn.setObjectName("collapsibleHeader")

        icon = _arrow_pixmap(False)
        self._header_btn.setIcon(icon)
        # self._header_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self._header_btn.clicked.connect(self._toggle)

        # self._title_label = QLabel()
        # self._title_label.setObjectName("collapsibleTitle")

        self._content = QWidget()
        self._content.setObjectName("collapsibleContent")
        self._items_layout = QVBoxLayout(self._content)
        self._items_layout.setContentsMargins(0, 4, 0, 8)
        self._items_layout.setSpacing(8)

        self._content.setVisible(False)

        root.addWidget(self._header_btn)
        root.addWidget(self._content)

    def set_title(self, title: str):
        """Установить заголовок"""
        self._header_btn.setText(title)

    def delete_item(self, product_id: int):
        """Удаление конкретного продукта"""
        self.products_model.delete_product(product_id)
        for index in range(self._items_layout.count()):
            item = self._items_layout.itemAt(index)
            widget = item.widget() if item else None
            if isinstance(widget, ProductsRow) and widget.products_id == product_id:
                widget.deleteLater()
                break

    def reset(self):
        """Сбросить список"""
        for index in range(self._items_layout.count()):
            item = self._items_layout.itemAt(index)
            widget = item.widget() if item else None
            if isinstance(widget, ProductsRow):
                widget.deleteLater()

    def put_items(self, items: list[Product]):
        """Задать список продуктов"""
        for list_index in range(len(items)):
            new_item = ProductsRow(
                list_index=list_index + 1,
                product=items[list_index],
                category_select_dialog=self.category_select_dialog,
                categories_model=self.categories_model,
                select_categories_service=self.select_categories_service,
                parent=self
            )
            new_item.on_delete.connect(self.delete_item)
            self._items_layout.addWidget(new_item)

    def _update_arrow_icon(self) -> None:
        self._header_btn.setIcon(_arrow_pixmap(self._expanded, 16).pixmap(16, 16))

    def set_expanded(self, expanded: bool) -> None:
        """Раскрыть или скрыть список"""
        if expanded != self._expanded:
            self._toggle()

    def _toggle(self) -> None:
        self._expanded = not self._expanded
        self._content.setVisible(self._expanded)
        self._header_btn.setProperty("expanded", self._expanded)
        self._header_btn.style().unpolish(self._header_btn)
        self._header_btn.style().polish(self._header_btn)
        self._update_arrow_icon()


class InfoCard(QFrame):
    """Верхний информационный блок со статистикой"""

    def __init__(self, parent: QWidget | None = None):
        super().__init__(parent)
        self.setObjectName("categoryInfoCard")

        layout = QHBoxLayout(self)
        layout.setContentsMargins(18, 16, 18, 16)
        layout.setSpacing(14)

        ai_icon = get_svg_widget("AI.svg")
        ai_icon.setObjectName("categoryInfoIcon")
        ai_icon.setFixedSize(28, 28)

        text_layout = QVBoxLayout()
        text_layout.setSpacing(4)

        self.line1 = QLabel()
        self.line1.setWordWrap(True)
        self.line2 = QLabel("Проверьте оставшиеся категории")
        self.line3 = QLabel()
        self.line3.setTextFormat(Qt.TextFormat.RichText)
        self.line4 = QLabel()
        self.line4.setTextFormat(Qt.TextFormat.RichText)

        text_layout.addWidget(self.line1)
        text_layout.addWidget(self.line2)
        text_layout.addWidget(self.line3)
        text_layout.addWidget(self.line4)

        layout.addWidget(ai_icon, 0, Qt.AlignmentFlag.AlignTop)
        layout.addLayout(text_layout, 1)

    def update_data(self, recognized_count: int, all_count: int):
        """Обновление данных"""
        if all_count == 0:
            self.line1.setText("К сожалению, обработка чеков не дала результатов")
            self.line2.setVisible(False)
            self.line3.setVisible(False)
            self.line4.setVisible(False)
        else:
            self.line1.setText("Мы распознали большую часть покупок"
                               if recognized_count > all_count / 2 else "Распознали не всё. Не волшебники, пока только учимся")
            self.line2.setVisible(recognized_count != all_count)
            self.line3.setVisible(True)
            self.line4.setVisible(True)
            self.line3.setText(
                f'Распознано: <span style="font-weight:600;">{round(recognized_count * 100 / all_count)}%</span>')
            self.line4.setText(f'Всего позиций: <span style="font-weight:600;">{all_count}</span>')


class SelectCategoryStep(QWidget):
    def __init__(
            self,
            categories_model: CategoriesModel,
            products_model: ProductsModel,
            category_select_dialog: CategorySelectDialog,
            making_result_service: MakingResultService,
            select_categories_service: SelectCategoriesService,
            parent: QWidget | None = None
    ):
        super().__init__(parent)

        self.products_model = products_model
        self.categories_model = categories_model
        self.select_categories_service = select_categories_service

        # Продукты с неопределённой категорией, без изменения которых невозможен переход дальше

        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(16)

        header_layout = QHBoxLayout()
        header_layout.addWidget(PageTitle("Почти готово..."), 1)
        self._next_button = PrimaryButton("Продолжить", active=True)
        self._next_button.clicked.connect(making_result_service.start)
        header_layout.addWidget(self._next_button)

        layout.addLayout(header_layout)

        container_block = ContentBlock()
        container_block.setObjectName("selectCategoryBlock")
        container_layout = QVBoxLayout()
        container_block.setLayout(container_layout)
        self.category_info_card = InfoCard()
        container_layout.addWidget(self.category_info_card)

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        scroll.setFrameShape(QFrame.Shape.NoFrame)

        sections_widget = QWidget()
        sections_widget.setObjectName("categorySections")
        sections_layout = QVBoxLayout(sections_widget)
        sections_layout.setContentsMargins(0, 0, 4, 0)
        sections_layout.setSpacing(4)

        self.attention_section = CollapsibleSection(
            categories_model,
            products_model,
            category_select_dialog,
            self.select_categories_service
        )
        sections_layout.addWidget(self.attention_section)

        self.other_products_section = CollapsibleSection(
            categories_model,
            products_model,
            category_select_dialog,
            self.select_categories_service,
            "Распределено автоматически"
        )
        sections_layout.addWidget(self.other_products_section)

        sections_layout.addStretch(1)

        scroll.setWidget(sections_widget)
        container_layout.addWidget(scroll, 1)
        layout.addWidget(container_block)

        self.products_model.attention_count_change.connect(self._update_button)

    def _update_button(self):
        """Изменение состояния кнопки Продолжить"""
        self._next_button.setEnabled(self.products_model.get_attention_count() == 0)

    def update_data(self):
        """Обновление всех списков продуктов"""
        self.attention_section.reset()
        self.other_products_section.reset()

        attention_products = self.products_model.get_attention_products()
        self.attention_section.set_title("Требуют внимания: " + str(len(attention_products)) + " шт.")
        self.attention_section.put_items(attention_products)

        self.other_products_section.put_items(self.products_model.get_recognized_products())

        self.category_info_card.update_data(
            self.products_model.count() - self.products_model.get_attention_count(),
            self.products_model.count()
        )

        if len(attention_products) == 0:
            self.attention_section.set_expanded(False)
            self.other_products_section.set_expanded(True)
        else:
            self.attention_section.set_expanded(True)
            self.other_products_section.set_expanded(False)

        self._update_button()
