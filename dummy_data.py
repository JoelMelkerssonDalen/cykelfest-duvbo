from couple import Course, Couple, Person

def load_dummy_data() -> dict[int, Couple]:
    couples: dict[int, Couple] = {}

    data = [
        Couple(1,  Person("Erik"),                    Person("Anna"),                  "Storgatan 1",         hosted_last_year=Course.STARTER),
        Couple(2,  Person("Lars"),                    Person("Maria"),                 "Kungsgatan 4",        hosted_last_year=Course.MAIN),
        Couple(3,  Person("Johan"),                   Person("Sara"),                  "Vasagatan 7",         hosted_last_year=Course.DESSERT),
        Couple(4,  Person("Mikael"),                  Person("Lena"),                  "Drottninggatan 2"),
        Couple(5,  Person("Anders"),                  Person("Karin"),                 "Birger Jarlsgatan 9", hosted_last_year=Course.STARTER),
        Couple(6,  Person("Stefan"),                  Person("Eva"),                   "Sveavägen 12",        hosted_last_year=Course.DESSERT),
        Couple(7,  Person("Peter"),                   Person("Annika"),                "Hornsgatan 3"),
        Couple(8,  Person("Magnus"),                  Person("Cecilia"),               "Götgatan 15",         hosted_last_year=Course.MAIN),
        Couple(9,  Person("Fredrik"),                 Person("Helena", "Vegan"),       "Folkungagatan 8"),
        Couple(10, Person("Niklas"),                  Person("Johanna"),               "Odengatan 5",         hosted_last_year=Course.STARTER),
        Couple(11, Person("Henrik"),                  Person("Petra"),                 "Upplandsgatan 6"),
        Couple(12, Person("David"),                   Person("Malin"),                 "Karlbergsvägen 11",   hosted_last_year=Course.DESSERT),
        Couple(13, Person("Daniel"),                  Person("Sofia"),                 "Fleminggatan 14",     hosted_last_year=Course.MAIN),
        Couple(14, Person("Martin"),                  Person("Emma"),                  "Scheelegatan 2"),
        Couple(15, Person("Andreas"),                 Person("Ida"),                   "Polhemsgatan 9",      hosted_last_year=Course.STARTER),
        Couple(16, Person("Tobias", "Gluten-free"),   Person("Jenny"),                 "Norr Mälarstrand 3"),
        Couple(17, Person("Oskar"),                   Person("Linda"),                 "Hantverkargatan 7",   hosted_last_year=Course.DESSERT),
        Couple(18, Person("Gustav"),                  Person("Elin"),                  "Kungsholmsgatan 5"),
    ]

    for couple in data:
        couples[couple.couple_id] = couple

    return couples
