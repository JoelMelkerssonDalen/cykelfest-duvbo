from couple import Course, Couple, Person
from dummy_data import load_dummy_data
from dataclasses import dataclass, field
import random

def get_partner(person: Person, couples: dict[int, Couple]) -> Person:
    
    if couples[person.couple_id].person_a == person:
        return couples[person.couple_id].person_b   
    
    return couples[person.couple_id].person_a

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

            # Check that everyone at a table have everyone else in their met set
            at_table = visitors + [host.person_a, host.person_b]
            for person in at_table:
                for other_person in [p for p in at_table if p != person]:
                    if person.person_id not in other_person.met:
                        errors.append(f"{course.name} table {host_id}: {person.person_id} not in {other_person.person_id} met set")
           
           
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

def met_updates(person: Person, table: list[Person], couples: dict[int, Couple], host_id: int) -> None:
    
    # For each person already on the table: add person.person_id to their met set
    # Add every table member's person_id to person.met
    # Add both hosts' person_ids to person.met
    # Add person.person_id to both hosts' met sets
    
    for p in table:
        p.met.add(person.person_id)
        person.met.add(p.person_id)
        
    person.met.add(couples[host_id].person_a.person_id)
    person.met.add(couples[host_id].person_b.person_id)
    couples[host_id].person_a.met.add(person.person_id)
    couples[host_id].person_b.met.add(person.person_id)
    
def met_undo(person: Person, table: list[Person], couples: dict[int, Couple], host_id: int) -> None:
    
    for p in table:
        p.met.remove(person.person_id)
        person.met.remove(p.person_id)
    
    person.met.remove(couples[host_id].person_a.person_id)
    person.met.remove(couples[host_id].person_b.person_id)
    couples[host_id].person_a.met.remove(person.person_id)
    couples[host_id].person_b.met.remove(person.person_id)

def assign_attendees(couples: dict[int, Couple]) -> dict[int, Couple]:
    
    def met_before(table: list[Person], met: set[str]) -> bool:
    
        return any([p.person_id in met for p in table])
    
    def minimum_available_values_sort(persons: list[Person], hosts: list[Couple]) -> None:
        # For each person, count the number of avilable tables 
        available_tables_per_person: list[tuple[Person, int]] = [] # list of each persons number of available tables
        for p in persons:
            available_tables_per_person.append((p, len([h for h in hosts if h.person_a.person_id not in p.met and h.person_b.person_id not in p.met])))
        
        # Sort persons based on numbered order in available tables per person 
        available_tables_per_person.sort(key=lambda x: x[1])
        persons[:] = [t[0] for t in available_tables_per_person]
    
    def backtrack(persons: list[Person], index: int, tables: dict[int, list[Person]], hosting_couples: list[Couple], couples: dict[int, Couple], course: Course) -> bool:
        if index == len(persons):
            return True
        
        for couple in hosting_couples:
            table = tables[couple.couple_id]
            not_full = len(table) < couple.capacity
            partner_not_there = get_partner(persons[index], couples).person_id not in [p.person_id for p in table]
            no_prior_meetings = not met_before(table, persons[index].met)
            if not_full and partner_not_there and no_prior_meetings:
                met_updates(persons[index], table, couples, couple.couple_id)
                table.append(persons[index])
                persons[index].schedule[course] = couple.couple_id
                if backtrack(persons, index+1, tables, hosting_couples, couples, course):
                    return True
                else:
                    table.remove(persons[index])
                    met_undo(persons[index], table, couples, couple.couple_id)
                    del persons[index].schedule[course]
                    
        return False
        
    assigned: dict[Course, dict[int, list[Person]]] = {course: {} for course in Course} # Course -> host couple_id -> visiting persons 

    for course in Course:
        # 1. build list of all individuals not hosting that course
        not_hosting_persons = list() # list of Persons not hosting the course
        hosting_couples = list() # list of Couples hosting that course
        for c in couples.values():
            if c.hosting != course:
                not_hosting_persons.append(c.person_a)
                not_hosting_persons.append(c.person_b)
            else:
                hosting_couples.append(c)
                
        # 2. Shuffle it
        random.shuffle(not_hosting_persons)
        random.shuffle(hosting_couples)
        
        # 3. Sort pesons by fewest valid tables available (MRW), order: fewest -> most  
        minimum_available_values_sort(not_hosting_persons, hosting_couples)
        
        # 4. Initilizing inner dicts
        for couple in hosting_couples:
            assigned[course][couple.couple_id] = []
            couple.person_a.met.add(couple.person_b.person_id)
            couple.person_b.met.add(couple.person_a.person_id)
        
        # 5. call backtrack to assign all persons to a table
        if not backtrack(not_hosting_persons, 0, assigned[course], hosting_couples, couples, course):
            print(f"FAIL: could not assign all persons for {course.name}")

        # 6. populate guests on each hosting couple
        for couple in hosting_couples:
            couple.guests = assigned[course][couple.couple_id]

    validate(couples, assigned)
    return couples

# def assign_attendees(couples: dict[int, Couple]) -> dict[int, Couple]:

#     def met_before(table: list[Person], met: set[str]) -> bool:
        
#         return any([p.person_id in met for p in table])

#     assigned: dict[Course, dict[int, list[Person]]] = {course: {} for course in Course} # Course -> host couple_id -> visiting persons 
    
#     for each course
#     1. Build list of all individuals not hosting that course
#     2. Shuffle it
#     3. For each individual, assign to a host table where:
#         a) Table isn't full (< capacity)
#         b) Their partner isn't already at that table
#         c) (courses 2+) No one at that table is in their met set
    
#     Finish by populating all hosts guest sets and validating assignments

#     for course in Course:        
#         build list of all individuals not hosting that course
#         all = list(couples.values())
#         not_hosting_person = list() # list of Persons not hosting the course
#         hosting_couple = list() # list of Couples hosting that course
#         for c in all:
#             if c.hosting != course:
#                 not_hosting_person.append(c.person_a)
#                 not_hosting_person.append(c.person_b)
#             else:
#                 hosting_couple.append(c)
#         2. Shuffle it
#         random.shuffle(not_hosting_person)
#         random.shuffle(hosting_couple)

#         additional step - initilizing inner dicts
#         for couple in hosting_couple:
#             assigned[course][couple.couple_id] = []
#             couple.person_a.met.add(couple.person_b.person_id)
#             couple.person_b.met.add(couple.person_a.person_id)

#         3. For each individual, assign to a host table where:
#             a) Table isn't full (< capacity)
#             b) Their partner isn't already at that table
#             c) (courses 2+) No one at that table is in their met set
#         for person in not_hosting_person:
#            for couple in hosting_couple:
#                table = assigned[course][couple.couple_id]
#                not_full = len(table) < couple.capacity
#                partner_not_there = get_partner(person, couples).person_id not in [p.person_id for p in table]
#                no_prior_meetings = not met_before(table, person.met)
#                if not_full and partner_not_there and no_prior_meetings:
#                     met_updates(person, table, couples, couple.couple_id)
#                     table.append(person)
#                     person.schedule[course] = couple.couple_id
#                     break
    
#         adding visitors to hosts guest set
#         for couple in hosting_couple:
#             couple.guests = assigned[course][couple.couple_id]
    
#     call to validate
#     validate(couples, assigned)

#     return couples

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
    
    course_names = {Course.STARTER: "Förrätt", Course.MAIN: "Varmrätt", Course.DESSERT: "Efterrätt"}
    
    # Q. Should output be in ascending couple id order? 
    for couple in couples.values():
        everyone = couple.guests + [couple.person_a, couple.person_b]
        print(f"---- PAR {couple.couple_id} ----")
        print(f"Värdar: {couple.person_a.name} och {couple.person_b.name}")
        print(f"Måltid: {course_names[couple.hosting]}")
        print(f"Adress: {couple.address}")
        print(f"Gäster: {', '.join(p.name for p in couple.guests)}")
        print(f"Specialkost: {', '.join(p.name + " (" + p.dietary_requirements + ")" for p in everyone if p.dietary_requirements)}\n\n")

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

def print_stats(couples: dict[int, Couple]) -> None:
    course_names = {Course.STARTER: "Förrätt", Course.MAIN: "Varmrätt", Course.DESSERT: "Efterrätt"}

    print("\n---- STATISTIK ----")

    print(f"\n{'Bord':<25} {'Måltid':<12} {'Gäster':>6}")
    print("-" * 45)
    for couple in couples.values():
        label = f"Par {couple.couple_id} ({couple.person_a.name} & {couple.person_b.name})"
        print(f"{label:<25} {course_names[couple.hosting]:<12} {len(couple.guests):>6}")

    print(f"\n{'Person':<20} {'Möten':>6} {'Par besökta':>12}")
    print("-" * 40)
    for couple in couples.values():
        for person in [couple.person_a, couple.person_b]:
            print(f"{person.name:<20} {len(person.met):>6} {len(person.schedule):>12}")

def output(couples: dict[int, Couple]) -> None:

    # Calling each different type of output function
    print_overall_schedule(couples)
    print_hosting_schedules(couples)
    print_individual_schedules(couples)
    print_stats(couples)
    
def main():
    all_couples: dict[int, Couple] = {}
    
    all_couples = load_dummy_data()
    
    all_couples = assign_hosting(all_couples)
    all_couples = assign_attendees(all_couples)
    output(all_couples)

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
