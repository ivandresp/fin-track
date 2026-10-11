from dataclasses import dataclass

@dataclass
class Person:
    name: str
    phone: str
    id: int | None = None

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "name": self.name,
            "phone": self.phone,
        }

    @classmethod
    def from_row(cls, row: tuple) -> "Person":
        return cls(
            id=row["id"],
            name=row["name"],
            phone=row["phone"],
        )