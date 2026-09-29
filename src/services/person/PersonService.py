from repositories.person.PersonRepository import PersonRepository
from models.person.Person import Person

class PersonService:
    def __init__(self, repo: PersonRepository):
        self.repo = repo

    def save(self, name:str, phone:str) -> int:
        if not name or not name.strip():
            raise ValueError("El nombre de la persona no puede estar vacio.")

        if not phone or not phone.isnumeric():
            raise ValueError("El telefono no puede ser vacio, y debe contener 10 digitos")

        person = Person(name=name.strip(), phone=phone.strip())
        return self.repo.save(person)

    def find_all(self):
        return [Person.from_row(p) for p in self.repo.get_all()]