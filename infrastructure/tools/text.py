def slice_text(text: str, max_len: int) -> str:
    """Обрезка лишнего текста"""
    if len(text) > max_len:
        return text[: max_len - 3] + "..."
    return text


def format_number(number: float, separator=' ') -> str:
    """Приведение числа к красивому виду"""
    return f"{number:,}".replace(',', separator)