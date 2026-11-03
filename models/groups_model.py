from PySide6.QtCore import QObject

from entities.dto.group import Group


class GroupsModel(QObject):
    def __init__(self):
        super().__init__()
        self.__groups: list[Group] = []

    def reset(self):
        self.__groups.clear()

    def set(self, groups: list[Group]):
        self.__groups = groups

    def get_all(self) -> list[Group]:
        return self.__groups