from pathlib import Path

from PySide6.QtCore import QObject


class ReceiptsModel(QObject):
    """Модель списка чеков"""
    def __init__(self):
        super().__init__()
        self.__receipts_paths: list[str] = []

    def add_paths(self, paths: list[str]) -> list[tuple[int, str]]:
        """Добавить пути чеков"""
        added = []
        for path in paths:
            if not (path.lower().endswith(".eml") or path.lower().endswith(".html")):
                continue
            normalized = str(Path(path).resolve())
            if normalized in self.__receipts_paths:
                continue
            self.__receipts_paths.append(normalized)
            added.append((len(self.__receipts_paths), normalized))
        return added

    def remove_path(self, path: str) -> bool:
        """Удаление пути до чека"""
        if path not in self.__receipts_paths:
            return False
        self.__receipts_paths.remove(path)
        return True

    def get(self, index: int) -> str:
        return self.__receipts_paths[index]

    def get_receipts_count(self) -> int:
        return len(self.__receipts_paths)

    def is_empty(self) -> bool:
        return len(self.__receipts_paths) == 0

    def get_receipts_paths(self) -> list[str]:
        return self.__receipts_paths

    def reset(self):
        self.__receipts_paths = []
