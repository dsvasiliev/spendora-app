from infrastructure.parsers.abstract_parser import Parser

from bs4 import BeautifulSoup, Tag

from entities.dto.product import Product, DetectionType


class VkusvillDeliveryParser(Parser):
    def check(self, soup: BeautifulSoup) -> bool:
        tables = soup.find_all('table')
        if len(tables) == 0:
            return False
        bs = tables[0].find_all('b')
        return len(bs) > 0 and bs[0].get_text(strip=True) == 'Кассовый чек / Приход'

    def parse(self, soup: BeautifulSoup, file_path: str) -> list[Product]:
        products = []
        # Ищем таблицу с товарами (как в оригинале: tbody[4])
        tbody = soup.find_all('tbody')[12]
        rows = [row for row in tbody.children if isinstance(row, Tag)]

        # Пропускаем заголовки и итоги
        for index in range(37, len(rows) - 27, 12):
            name = rows[index].find_all('b')[0].get_text(strip=True)
            amount_data = rows[index].find_all('span')[1].get_text(strip=True).split("X")
            count_str = amount_data[0].replace(',', '.')
            price_str = amount_data[1].replace('₽', '').replace(',', '.')
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