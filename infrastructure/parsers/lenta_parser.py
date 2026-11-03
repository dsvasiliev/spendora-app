from infrastructure.parsers.abstract_parser import Parser

from bs4 import BeautifulSoup

from entities.dto.product import Product, DetectionType


class LentaParser(Parser):
    def check(self, soup: BeautifulSoup) -> bool:
        items = soup.select('.items_item')
        return len(items) > 0

    def parse(self, soup: BeautifulSoup, file_path: str) -> list[Product]:

        products = []
        items = soup.select('.items_item')
        # Пропускаем заголовки и итоги
        for item in items:
            divs = item.find_all('div')
            # У строк с продуктами всегда 4 столбца
            name = divs[3].get_text(strip=True)
            count_str = divs[8].get_text(strip=True).replace(',', '.')
            price_str = divs[7].get_text(strip=True).replace('₽', '').replace(',', '.')
            products.append(Product(
                -1,
                name,
                float(price_str),
                float(count_str),
                [file_path],
                -1,
                DetectionType.UNKNOWN
            ))

        return products
