from infrastructure.parsers.abstract_parser import Parser

from bs4 import BeautifulSoup, Tag

from entities.dto.product import Product, DetectionType


class VkusvillShopParser(Parser):
    def check(self, soup: BeautifulSoup) -> bool:
        h3s = soup.find_all('h3')
        return len(h3s) > 0 and 'Кассовый чек' in h3s[0].get_text()

    def parse(self, soup: BeautifulSoup, file_path: str) -> list[Product]:
        products = []
        # Ищем таблицу с товарами (как в оригинале: tbody[4])
        tbody = soup.find_all('tbody')[10]
        rows = [row for row in tbody.children if isinstance(row, Tag)]

        # Пропускаем заголовки и итоги
        for index in range(6, len(rows) - 22, 5):
            tds = rows[index].find_all('td')
            name = tds[1].get_text(strip=True)
            count_str = tds[2].get_text(strip=True).replace(',', '.')
            price_str = tds[3].get_text(strip=True).replace('₽', '').replace(',', '.')
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
