from infrastructure.parsers.abstract_parser import Parser

from bs4 import BeautifulSoup

from entities.dto.product import Product, DetectionType


class OFDParser(Parser):
    def check(self, soup: BeautifulSoup) -> bool:
        bs = soup.find_all('b')
        return len(bs) > 3 and "КАССОВЫЙ ЧЕК" in bs[2].get_text()


    def parse(self, soup: BeautifulSoup, file_path: str) -> list[Product]:
        products = []

        bs = soup.find_all('b')

        for index in range(3, len(bs) - 3, 2):
            name = bs[index].get_text(strip=True).split(": ")[1]
            # Важно. Тут действительно два пробела
            amount_data = bs[index + 1].get_text(strip=True).split("шт.  x")
            count_str = amount_data[0].replace(',', '.')
            price_str = amount_data[1].replace(',', '.')
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