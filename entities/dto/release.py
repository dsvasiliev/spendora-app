from dataclasses import dataclass

# DTO - Data Transfer Object

@dataclass
class Release:
    version: str
    installer_name: str
    changes: list[str]

    @classmethod
    def from_dict(cls, data: dict):
        return Release(
            data['version'],
            data['installer_name'],
            data['changes']
        )