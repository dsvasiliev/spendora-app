from infrastructure.parsers.abstract_parser import Parser

from bs4 import BeautifulSoup

from entities.dto.product import Product, DetectionType


class TanderParser(Parser):
    def check(self, soup: BeautifulSoup) -> bool:
        tds = soup.find_all('td')
        return len(tds) >= 10 and tds[9].get_text() == 'КАССОВЫЙ ЧЕК'

    def parse(self, soup: BeautifulSoup, file_path: str) -> list[Product]:
        products = []
        # Ищем таблицу с товарами (как в оригинале: tbody[4])
        table = soup.find_all('tbody')[4]
        rows = table.find_all('tr')
        # Пропускаем заголовки и итоги
        for row in rows[2:-4]:
            cells = row.find_all('td')
            # У строк с продуктами всегда 4 столбца
            if len(cells) == 4:
                name = cells[0].get_text(strip=True)
                count_str = cells[1].get_text(strip=True).replace(',', '.')
                price_str = cells[2].get_text(strip=True).replace('₽', '').replace(',', '.')
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