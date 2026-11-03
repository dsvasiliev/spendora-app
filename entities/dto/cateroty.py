from dataclasses import dataclass


@dataclass
class Category:
    id: int
    name: str
    row: int
    add_row: int