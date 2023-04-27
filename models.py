"""
The file that holds the schema/classes
that will be used to create objects
and connect to data tables.
"""

from sqlalchemy import ForeignKey, Column, INTEGER, TEXT
from sqlalchemy.orm import relationship
from database import Base

class User:
    __tablename__ = "users"

    # columns
    user_id = Column("id", INTEGER, primary_key=True)
    username = Column("username", TEXT, nullable=False)
    email = Column("email", TEXT, nullable=False)
    password = Column("password", TEXT, nullable=False)
    first_name = Column("first_name", TEXT, nullable=False)
    last_name = Column("last_name", TEXT, nullable=False)
    profile_pic = Column("profile_pic", TEXT, nullable=False)

    # relationships
    reviews = relationship("Review", back_populates="user")

    # constructor
    def __init__(self, user_id, username, email, password, first_name, last_name, profile_pic):
        self.user_id = user_id
        self.username = username
        self.email = email
        self.password = password
        self.first_name = first_name
        self.last_name = last_name
        self.profile_pic = profile_pic

class Review:
    __tablename__ = "reviews"

    # columns
    review_id = Column("id", INTEGER, primary_key=True)
    user_id = Column("user_id", ForeignKey, nullable=False)
    race_id = Column("race_id", ForeignKey, nullable=False)
    rating = Column("rating", INTEGER, nullable=False)
    review_date = Column("review_date", TEXT, nullable=False)
    review_text = Column("review_text", TEXT, nullable=True)

    # relationships
    user = relationship("User", back_populates="reviews")
    race = relationship("Race", back_populates="reviews")

    # constructor
    def __init__(self, review_id, user_id, rating, review_date, review_text):
        self.review_id = review_id
        self.user_id = user_id
        self.rating = rating
        self.review_date = review_date
        self.review_text = review_text

class Race:
    __tablename__ = "races"

    # columns
    race_id = Column("race_id", INTEGER, primary_key=True)
    race_name = Column("race_name", TEXT, nullable=False)
    race_location = Column("race_location", TEXT, nullable=False)
    race_date = Column("race_date", TEXT, nullable=False)
    race_distance = Column("race_distance", TEXT, nullable=False)
    race_website = Column("race_website", TEXT, nullable=True)
    race_description = Column("race_description", TEXT, nullable=True)

    # relationships
    reviews = relationship("Review", back_populates="race")

    # constructor
    def __init__(self, race_id, race_name, race_location, race_date, race_distance, race_website, race_description):
        self.race_id = race_id
        self.race_name = race_name
        self.race_location = race_location
        self.race_date = race_date
        self.race_distance = race_distance
        self.race_website = race_website
        self.race_description = race_description
