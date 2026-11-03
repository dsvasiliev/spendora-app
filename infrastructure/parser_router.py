from email.parser import BytesParser
from email import policy

import base64
import quopri
from PySide6.QtCore import QObject
from bs4 import BeautifulSoup

from entities.dto.product import Product
from entities.errors.parsing_error import ParsingError
from infrastructure.parsers.lenta_parser import LentaParser
from infrastructure.parsers.ofd_parser import OFDParser
from infrastructure.parsers.tander_parser import TanderParser
from infrastructure.parsers.vkusvill_delivery_parser import VkusvillDeliveryParser
from infrastructure.parsers.vkusvill_shop_parser import VkusvillShopParser


class ParserRouter(QObject):
    def __init__(self):
        super().__init__()
        self.parsers = {
            TanderParser(),
            OFDParser(),
            VkusvillDeliveryParser(),
            VkusvillShopParser(),
            LentaParser(),
        }
        self.error_list: list[str] = []

    def reset(self):
        self.error_list.clear()

    def parsers_router(self, file_path: str) -> list[Product]:
        """Открытие файла и парсинг с использованием нужного парсера"""
        # Получаем html часть
        html_content: str| None = None
        if file_path.endswith('.eml'):
            html_content = get_html_from_email(file_path)
        elif file_path.endswith('.html'):
            with open(file_path, 'r', encoding='utf-8') as f:
                html_content = f.read()
        if not html_content:
            raise ParsingError()
        # Обрабатываем html часть
        soup = BeautifulSoup(html_content, 'html.parser')
        for parser in self.parsers:
            if parser.check(soup):
                try:
                    return parser.parse(soup, file_path)
                except Exception as e:
                   # define_error(...)
                   continue
        raise ParsingError()

def get_html_from_email(file_path: str) -> str | None:
    """Получаем html-часть письма формата eml"""
    with open(file_path, 'rb') as fp:
        msg = BytesParser(policy=policy.default).parse(fp)
    if msg.is_multipart():
        for part in msg.walk():
            if part.get_content_type() == 'text/html':
                return decode_email_part(part)
    else:
        if msg.get_content_type() == 'text/html':
            return decode_email_part(msg)
    return None


def decode_email_part(part) -> str | None:
    """
    Декодирует часть письма с учетом Content-Transfer-Encoding.
    Поддерживает base64, quoted-printable и 7bit/8bit.
    """
    # Получаем сырые данные (закодированные)
    payload = part.get_payload(decode=False)

    # Если это bytes, а не строка
    if isinstance(payload, bytes):
        payload_bytes = payload
    else:
        payload_bytes = payload.encode('utf-8', errors='ignore')

    # Определяем кодировку передачи
    encoding = part.get('Content-Transfer-Encoding', '').lower()


    if encoding == 'base64':
        try:
            decoded_bytes = base64.b64decode(payload_bytes)
        except Exception as e:
            print(f"Ошибка декодирования Base64: {e}")
            return None
    elif encoding == 'quoted-printable':
        try:
            decoded_bytes = quopri.decodestring(payload_bytes)
        except Exception as e:
            print(f"Ошибка декодирования Quoted-Printable: {e}")
            return None
    elif encoding in ['7bit', '8bit', 'binary']:
        # Обычный текст, не требует декодирования
        decoded_bytes = payload_bytes
    else:
        # Если кодировка не указана или неизвестна, пробуем как есть
        decoded_bytes = payload_bytes
    if decoded_bytes is None:
        return None

    # Определяем кодировку символов из заголовков
    charset = part.get_content_charset() or 'utf-8'

    try:
        return decoded_bytes.decode(charset, errors='replace')
    except (LookupError, UnicodeDecodeError):
        # Если кодировка не поддерживается, пробуем UTF-8 с заменой
        return decoded_bytes.decode('utf-8', errors='replace')


# router = ParserRouter()
# print(router.parsers_router("D:\\Spendora\\Для тестов\\Лента.html"))