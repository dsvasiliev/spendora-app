class ParsingError(Exception):
    def __init__(self):
        super().__init__("Не удалось найти подходящий парсер")