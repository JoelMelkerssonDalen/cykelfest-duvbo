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

def validate(couples: dict[int, Couple], assigned: dict[Course, dict[int, list[Person]]]) -> bool:
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

    # Check that every non-hosting person is assigned to exactly one table per visiting course
    for couple in couples.values():
        for person in [couple.person_a, couple.person_b]:
            if len(person.schedule) > 2:
                errors.append(f"{person.person_id} is assigned to more than 2 courses")
            elif len(person.schedule) < 2:
                errors.append(f"{person.person_id} is assigned to less than 2 courses")
    
    # Check that no two persons appear together at more than one course
    seen_pairs: set[frozenset[str]] = set()
    for course, tables in assigned.items():
        for host_id, visitors in tables.items():
            host = couples[host_id]
            at_table = visitors + [host.person_a, host.person_b]
            for i, person in enumerate(at_table):
                for other_person in at_table[i+1:]:
                    pair = frozenset({person.person_id, other_person.person_id})
                    if pair in seen_pairs:
                        a, b = pair
                        errors.append(f"{a} and {b} meet at multiple courses")
                    else:
                        seen_pairs.add(pair)
            
                

    if errors:
        for e in errors:
            print(f"FAIL: {e}")
        return True
    else:
        print("All checks passed!")
        return False

def met_updates(person: Person, table: list[Person], couples: dict[int, Couple], host_id: int) -> list:
    added = []
    for p in table:
        if person.person_id not in p.met:
            p.met.add(person.person_id)
            added.append((p.met, person.person_id))
        if p.person_id not in person.met:
            person.met.add(p.person_id)
            added.append((person.met, p.person_id))

    host_a = couples[host_id].person_a
    host_b = couples[host_id].person_b
    if host_a.person_id not in person.met:
        person.met.add(host_a.person_id)
        added.append((person.met, host_a.person_id))
    if person.person_id not in host_a.met:
        host_a.met.add(person.person_id)
        added.append((host_a.met, person.person_id))
    if host_b.person_id not in person.met:
        person.met.add(host_b.person_id)
        added.append((person.met, host_b.person_id))
    if person.person_id not in host_b.met:
        host_b.met.add(person.person_id)
        added.append((host_b.met, person.person_id))
    return added

def met_undo(added: list) -> None:
    for met_set, person_id in added:
        met_set.discard(person_id)

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
        
        # Helper function to forwardcheck if there are any persons with no valid tables
        def has_valid_tables(person: Person, tables: dict[int, list[Person]], hosting_couples: list[Couple], couples: dict[int, Couple]) -> bool:

            for couple in hosting_couples:
                table = tables[couple.couple_id]
                not_full = len(table) < couple.capacity
                partner_not_there = get_partner(person, couples).person_id not in [p.person_id for p in table]
                no_prior_meetings = (not met_before(table, person.met)
                                     and couple.person_a.person_id not in person.met
                                     and couple.person_b.person_id not in person.met)
                if not_full and partner_not_there and no_prior_meetings:
                    return True

            return False

        if index == len(persons):
            return True

        for couple in hosting_couples:
            table = tables[couple.couple_id]
            not_full = len(table) < couple.capacity
            partner_not_there = get_partner(persons[index], couples).person_id not in [p.person_id for p in table]
            no_prior_meetings = (not met_before(table, persons[index].met)
                                 and couple.person_a.person_id not in persons[index].met
                                 and couple.person_b.person_id not in persons[index].met)
            if not_full and partner_not_there and no_prior_meetings:
                added = met_updates(persons[index], table, couples, couple.couple_id)
                table.append(persons[index])
                persons[index].schedule[course] = couple.couple_id

                # boolean flag
                forward_ok = True

                # Forward loop check - if any fails then we should undo
                for person in persons[index+1:]:
                    if not has_valid_tables(person, tables, hosting_couples, couples):
                        forward_ok = False
                        break

                # If not forward ok - undo assignment
                if not forward_ok:
                    table.remove(persons[index])
                    met_undo(added)
                    del persons[index].schedule[course]
                    continue

                # Try backwards propagation for next person - if all fails undo assignment
                if backtrack(persons, index+1, tables, hosting_couples, couples, course):
                    return True
                else:
                    table.remove(persons[index])
                    met_undo(added)
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

    if validate(couples, assigned):
        return None
    else:
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
    MAX_RETRIES = 1000
    
    for attempt in range(MAX_RETRIES):
    
        all_couples: dict[int, Couple] = {}
    
        all_couples = load_dummy_data()
    
        all_couples = assign_hosting(all_couples)
        result = assign_attendees(all_couples)
        if result is not None:
            break
    
    if result is None:
        print(f"FAIL: could not find valid assignment after {MAX_RETRIES} retries")
    else:
        # output(all_couples)
        None
    
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
