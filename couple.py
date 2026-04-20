from enum import Enum
from dataclasses import dataclass, field

class Course(Enum):
    STARTER = 0
    MAIN = 1
    DESSERT = 2

@dataclass
class Person:
    person_id: str = field(init=False, default="") # unique identifer for the person, set in couple
    couple_id: int = field(init=False, default=-1) # unique identifer for the couple the person is part of, set in couple
    name: str
    dietary_requirements: str | None = None
    schedule: dict[Course, int] = field(default_factory=dict) # Course -> couple_id
    met: set[str] = field(default_factory=set) 

@dataclass
class Couple:
    couple_id: int # unique identifier for the couple  
    person_a: Person
    person_b: Person
    address: str
    hosting: Course | None = None
    hosted_last_year: Course | None = None
    capacity: int = 4
    guests: list[Person] = field(default_factory=list) 
    
    def __post_init__(self):
        self.person_a.person_id = f"{self.couple_id}a"
        self.person_b.person_id = f"{self.couple_id}b"
        self.person_a.couple_id = self.couple_id
        self.person_b.couple_id = self.couple_id
