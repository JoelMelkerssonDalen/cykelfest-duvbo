from couple import Course, Couple
from dummy_data import load_dummy_data
import random

def add_couple(couples: dict[int, Couple], new_couple: Couple) -> dict[int,Couple]:
    couples[new_couple.couple_id] = new_couple
    return couples

def assign_hosting(couples: dict[int, Couple]) -> dict[int, Couple]: 
    
    remaining: dict[Course, int] = {Course.STARTER: 6, Course.MAIN: 6, Course.DESSERT: 6}

    shuffled = list(couples.values())
    random.shuffle(shuffled)
    
    for couple in shuffled:
        for course in Course:
            if course != couple.hosted_last_year and remaining[course] > 0 and couple.hosting is None:
                couple.hosting = course
                remaining[course] -= 1
                break
        if couple.hosting is None:
            for course in Course:
                if remaining[course] > 0:
                    couple.hosting = course
                    remaining[course] -= 1
                    break
    
    return couples             
    

def main():
    all_couples: dict[int, Couple] = {}
    
    all_couples = load_dummy_data()
    
    all_couples = assign_hosting(all_couples)
    
    count: dict[Course, int] = {Course.STARTER: 0, Course.MAIN: 0, Course.DESSERT: 0}
    for couple in list(all_couples.values()):
        count[couple.hosting] += 1
    
    print(count)


if __name__ == "__main__":
    main()
