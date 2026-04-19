from couple import Course, Couple, Person
from dummy_data import load_dummy_data
from dataclasses import dataclass, field
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

def validate(couples: dict[int, Couple], assigned: dict[Course, dict[int, list[Person]]]) -> None:
    errors = []

    for course, tables in assigned.items():
        for host_id, visitors in tables.items():
            host = couples[host_id]

            # Check capacity not exceeded
            if len(visitors) > host.capacity:
                errors.append(f"{course.name} table {host_id}: {len(visitors)} visitors exceeds capacity {host.capacity}")

            # Check partners not at same visiting table
            visitor_ids = {p.person_id for p in visitors}
            for person in visitors:
                couple_id = person.person_id[:-1]  # strip 'a' or 'b'
                partner_id = couple_id + ("b" if person.person_id.endswith("a") else "a")
                if partner_id in visitor_ids:
                    errors.append(f"{course.name} table {host_id}: partners {person.person_id} and {partner_id} at same table")

    # Check no two individuals meet more than once
    for couple in couples.values():
        for person in [couple.person_a, couple.person_b]:
            # met set should have no duplicates by nature of being a set, but check size is reasonable
            all_met = list(person.met)
            if len(all_met) != len(set(all_met)):
                errors.append(f"{person.person_id} has duplicate entries in met set")

    if errors:
        for e in errors:
            print(f"FAIL: {e}")
    else:
        print("All checks passed!")

def assign_attendees(couples: dict[int, Couple]) -> dict[int, Couple]:

    def met_before(table: list[Person], met: set[Person]) -> bool:
        
        for t in table:
            if len(met) == 0:
                return False
            if t in met:
                return True
            
        return False

    assigned: dict[Course, dict[int, list[Person]]] = {course: {} for course in Course} # Course -> host couple_id -> visiting persons 
    
    # for each course
    # 1. Build list of all individuals not hosting that course
    # 2. Shuffle it
    # 3. For each individual, assign to a host table where:
    #     a) Table isn't full (< capacity)
    #     b) Their partner isn't already at that table
    #     c) (courses 2+) No one at that table is in their met set

    for course in Course:        
        # build list of all individuals not hosting that course
        all = list(couples.values())
        not_hosting_person = list() # list of Persons not hosting the course
        hosting_couple = list() # list of Couples hosting that course
        for c in all:
            if c.hosting != course:
                not_hosting_person.append(c.person_a)
                not_hosting_person.append(c.person_b)
            else:
                hosting_couple.append(c)
        # 2. Shuffle it
        random.shuffle(not_hosting_person)
        random.shuffle(hosting_couple)

        # additional step - initilizing inner dicts
        for c in hosting_couple:
            assigned[course][c.couple_id] = []

        # 3. For each individual, assign to a host table where:
        #     a) Table isn't full (< capacity)
        #     b) Their partner isn't already at that table
        #     c) (courses 2+) No one at that table is in their met set
        for i in not_hosting_person:
           for c in hosting_couple:
               if len(assigned[course][c.couple_id]) < c.capacity and i not in assigned[course][c.couple_id] and not met_before(assigned[course][c.couple_id], i.met): 
                    assigned[course][c.couple_id].append(i)
                    i.schedule[course] = c.couple_id
                    print(f"Individual: {i.name} going to couple: {c.couple_id} for course: {c.hosting}")
                    # i.met.add(c.person_a)
                    # i.met.add(c.person_b)
        assigned[Course.STARTER][1] = couples[1].person_a
        print(assigned[Course.STARTER][1])

    # call to validate
    validate(couples, assigned)

    return couples

def print_overall_schedule(couples: dict[int, Couple]) -> None:
    # 1. Overall scehdule (for organizers)
    #
    # For each course print hosting couple, attending persons and address 
    # 
    # FORMAT
    # 
    # ---- COURSE -----
    #      HOSTS          ATTENDING                            ADRESS
    # Person A Person B   Person C Person D Person E Person F  Street 
    print("overall")

def print_hosting_schedules(couples: dict[int, Couple]) -> None:

    # 2. Hosting information (for all hosts)
    #
    # For each couple, print their hosting course, attending people (with any dietary req.)
    #
    # FORMAT
    #
    # 
    # ---- COUPLE -----
    #
    # Course: [Starter, Main, Dessert]
    # Guests: [Person A (any dietary req.), Person B, Person C, Person D] 
    
    # Q. Should output be in ascending couple id order? 
    for couple in couples.values():
        print(f"---- COUPLE {couple.couple_id} ----\n")
        print(f"Course: {couple.hosting}")
        print(f"Guests: {couple.guests}")

def print_individual_schedules(couples: dict[int, Couple]) -> None:

    # 3. Individual schedules (for all particiants)
    # 
    # For every individual particiapant, print their route (where they will be at each meal & when they will host)  
    # 
    # ---- Individual Person ---- 
    # 
    # Starter: Going to [Person A, Person B] at [Adress]
    # Main (HOSTING): "You and [other part of couple] "are hosting the main course this year
    # Dessert: Going to [Person A, Person B] at [Adress]

    for couple in couples.values():
        print(f"---- {couple.person_a.name} ----\n")
        print(f"Schedule: {couple.person_a.schedule}")

def output(couples: dict[int, Couple]) -> None:

    # Calling each different type of output function 
    print_overall_schedule(couples)
    print_hosting_schedules(couples)
    print_individual_schedules(couples)
    
def main():
    all_couples: dict[int, Couple] = {}
    
    all_couples = load_dummy_data()
    
    all_couples = assign_hosting(all_couples)
    all_couples = assign_attendees(all_couples)
    # output(all_couples)

    count: dict[Course, int] = {Course.STARTER: 0, Course.MAIN: 0, Course.DESSERT: 0}
    for couple in list(all_couples.values()):
        count[couple.hosting] += 1
    
    print(count)

    # test = [Person("Anna"), Person("Bengt"), Person("Charlie")]
    # # test_set: set[Person] = {Person("David"),Person("Emma"), Person("Charlie")}
    # new_person = Person("David")
    # test_set: set[str] = {"David"}
    # test_set.add("David")
    
    # for t in test_set:
    #     if t in test:
    #         print("yes")
    #         break
    #     if t.name == "Charlie":
    #         print("no")

if __name__ == "__main__":
    main()
