from dataclasses import dataclass

@dataclass
class Person:
    id: int | None
    name: str
    phone: str

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "name": self.name,
            "phone": self.phone,
        }

    @staticmethod
    def from_row(row: tuple) -> "Person":
        return Person(
            id=row[0],
            name=row[1],
            phone=row[2],
        )