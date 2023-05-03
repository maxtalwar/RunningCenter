from flask import *
from database import init_db, db_session
from models import *
from datetime import datetime

app = Flask(__name__)

app.secret_key = "LInPyX4PpZx6hAHofg=="

def store_race(race_name, race_city, race_state, race_date, race_distance, race_website="", race_description=""):
    race = Race(race_name=race_name, race_city=race_city, race_state=race_state, race_date=race_date, race_distance=race_distance, race_website=race_website, race_description=race_description)

    db_session.add(race)

    db_session.commit()

    return race

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

def delete_race_reviews():
    Review.query.delete()
    db_session.commit()

def delete_all_races():
    Race.query.delete()
    db_session.commit()

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

def initialize_database():
    init_db()
    print("Database has been initialized.")

def menu():
    print("Please choose an option:")
    print("1. Initialize database")
    print("2. Add a race")
    print("3. Add all default races")
    print("4. Delete all reviews")
    print("5. Delete all races")
    print("6. Quit")
    choice = input("Enter the number of your choice: ")
    return int(choice)

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
            print("Exiting the program.")
            break
        else:
            print("Invalid choice. Please try again.")
