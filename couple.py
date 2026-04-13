from enum import Enum
from dataclasses import dataclass, field

class Course(Enum):
    STARTER = 0
    MAIN = 1
    DESSERT = 2

@dataclass
class Person:
    name: str
    dietary_requirements: str | None = None
    schedule: dict[Course, int] = field(default_factory=dict) # Course -> couple_id
    

@dataclass
class Couple:
    couple_id: int # unique identifier for the couple  
    person_a: Person
    person_b: Person
    address: str
    hosting: Course | None = None
    capacity: int = 4
