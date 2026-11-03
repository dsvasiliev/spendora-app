from bs4 import BeautifulSoup

from entities.dto.product import Product


class Parser:
    def check(self, soup: BeautifulSoup) -> bool:
        raise NotImplementedError


    def parse(self,
              soup: BeautifulSoup,
              file_path: str
              ) -> list[Product]:
        raise NotImplementedError
