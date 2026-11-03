from dataclasses import dataclass
from enum import Enum


class DetectionType(Enum):
    FROM_DB = 0
    DETECTED = 1
    UNKNOWN = 2

@dataclass
class Product:
    id: int
    name: str
    price: float
    count: float
    files: list[str]
    category_id: int
    detection_type: DetectionType

    def __eq__(self, other):
        return self.name == other.name and self.price == other.price