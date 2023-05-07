from flask import *
from database import init_db, db_session
from models import *
from datetime import datetime

app = Flask(__name__)

app.secret_key = "LInPyX4PpZx6hAHofg=="

# take info about a race and store a corresponding race object into the database
def store_race(race_name, race_city, race_state, race_date, race_distance, race_website="", race_description=""):
    race = Race(race_name=race_name, race_city=race_city, race_state=race_state, race_date=race_date, race_distance=race_distance, race_website=race_website, race_description=race_description)

    db_session.add(race)

    db_session.commit()

    return race

# query the user for info about the race object to be created
def get_race_info():
    done = False

    while not done:
        race_name = input("Race name: ")
        race_location = input("Race location: ")
        race_date = input("Race date: ")
        race_distance = input("Race distance: ")
        race_website = input("Race website: ")
        race_description = input("Race description: ")

        store_race(race_name, race_location, race_date, race_distance, race_website, race_description)

# delete all the race reviews in the database
def delete_race_reviews():
    Review.query.delete()
    db_session.commit()

# delete all the races in the database
def delete_all_races():
    Race.query.delete()
    db_session.commit()

# adds the preset default races to the database
def add_default_races():
    default_races = [
        ("Boston Marathon", "Boston", "MA", "4/17/24", "26.2", "https://www.baa.org/races/boston-marathon", "The Boston Marathon is an annual race that takes place in Boston, Massachusetts"),
        ("Chicago Marathon", "Chicago", "IL", "8/8/23", "26.2", "https://www.chicagomarathon.com/", "The Chicago Marathon is a marathon in Chicago"),
        ("Los Angeles Marathon", "Los Angeles", "CA", "3/17/24", "26.2", "https://www.lamarathon.com/", "A marathon in Los Angeles."),
        ("New York City Marathon", "New York City", "NY", "11/6/23", "26.2", "https://www.nyrr.org/tcsnycmarathon", "A marathon in New York.")
    ]

    for race in default_races:
        race_date = datetime.strptime(race[3], "%m/%d/%y").date()
        store_race(race[0], race[1], race[2], race_date, race[4], race[5], race[6])

    print("Default races have been added.")

# initialize the database
def initialize_database():
    init_db()
    print("Database has been initialized.")

# edit the race (currently I've just implemented functionality to edit the race description)
def edit_race():
    race_id = input("Race id: ")

    race = db_session.query(Race).filter(Race.id == race_id).first()

    if not race:
        print("Race not found!\n")
        return

    field_to_edit = input("What field do you want to edit (eg description): ")

    if field_to_edit == "description":
        race.race_description = input("Updated description: ")

        db_session.commit()
    else:
        print("invalid field type!\n")

# display a menu of functionality
def menu():
    print("Please choose an option:")
    print("1. Initialize database")
    print("2. Add a race")
    print("3. Add all default races")
    print("4. Delete all reviews")
    print("5. Delete all races")
    print("6. Update a race")
    print("7. Quit")
    choice = input("Enter the number of your choice: ")
    return int(choice)

# run the function that corresponds to the menu selection
if __name__ == "__main__":
    while True:
        choice = menu()

        if choice == 1:
            initialize_database()
        elif choice == 2:
            get_race_info()
        elif choice == 3:
            add_default_races()
        elif choice == 4:
            delete_race_reviews()
            print("All reviews have been deleted.")
        elif choice == 5:
            delete_all_races()
            print("All races have been deleted.")
        elif choice == 6:
            edit_race()
        elif choice == 7:
            print("Exiting the program.")
            break
        else:
            print("Invalid choice. Please try again.")
