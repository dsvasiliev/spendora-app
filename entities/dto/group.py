from dataclasses import dataclass


@dataclass
class Group:
    name: str
    categories_id: list[int]