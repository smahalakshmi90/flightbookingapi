"""
Created on 26.01.2013
Modified on 05.02.2017
@author: ivan sanchez
@author: mika oja
@author: Jules LARUE
"""
import unittest

import flight_reservation.flight_database as database
import flight_reservation.resources as resources

DB_PATH = "db/flight_test.db"
ENGINE = database.Engine(DB_PATH)

MASONJSON = "application/vnd.mason+json"
JSON = "application/json"
HAL = "application/hal+json"
FLIGHT_BOOKING_SYSTEM_USER_PROFILE = "/profiles/user-profile/"
FLIGHT_BOOKING_SYSTEM_RESERVATION_PROFILE = "/profiles/reservation-profile/"
FLIGHT_BOOKING_SYSTEM_TICKET_PROFILE = "/profiles/ticket-profile/"
FLIGHT_BOOKING_SYSTEM_FLIGHT_PROFILE = "/profiles/flight-profile/"
FLIGHT_BOOKING_SYSTEM_TEMPLATE_FLIGHT_PROFILE = "/profiles/template-flight-profile/"


# Tell Flask that I am running it in testing mode.
resources.app.config["TESTING"] = True
# Necessary for correct translation in url_for
resources.app.config["SERVER_NAME"] = "localhost:5000"

# Database Engine utilized in our testing
resources.app.config.update({"Engine": ENGINE})

# Other database parameters.
NB_INITIAL_USERS = 5
NB_INITIAL_FLIGHTS = 3
NB_INITIAL_TEMPLATE_FLIGHTS = 5
NB_INITIAL_RESERVATIONS = 4
NB_INITIAL_TICKETS = 5


class ResourcesAPITestCase(unittest.TestCase):
    """
    @author: ivan sanchez
    """
    # INITIATION AND TEARDOWN METHODS
    @classmethod
    def setUpClass(cls):
        """
        Creates the database structure. Removes first any preexisting
        database file
        """
        print("Testing ", cls.__name__)
        ENGINE.remove_database()
        ENGINE.create_tables()

    @classmethod
    def tearDownClass(cls):
        """Remove the testing database"""
        print("Testing ENDED for ", cls.__name__)
        ENGINE.remove_database()

    def setUp(self):
        """
        Populates the database
        """
        # This method load the initial values from flight_data_dump.sql
        ENGINE.populate_tables()
        # Activate app_context for using url_for
        self.app_context = resources.app.app_context()
        self.app_context.push()
        # Create a test client
        self.client = resources.app.test_client()

    def tearDown(self):
        """
        Remove all records from database
        """
        ENGINE.clear()
        self.app_context.pop()