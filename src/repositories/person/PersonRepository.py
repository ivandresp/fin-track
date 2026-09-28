import sqlite3 as sql
from repositories.utils.DB import DB
from repositories.utils.querys import SELECT_ALL_PEOPLE, INSERT_PERSON
from models.person.Person import Person

class PersonRepository:
    def __init__(self, db: DB):
        self.db = db

    def get_all(self) -> list[sql.Row]:
        with self.db.connect() as conn:
            return conn.execute(SELECT_ALL_PEOPLE).fetchall()

    def save(self, person: Person) -> int:
        with self.db.connect() as conn:
            cursor = conn.execute(INSERT_PERSON, (person.name, person.phone))
            return cursor.lastrowid
        
        