"""
Created on 23.02.2018

Database interface testing for all flights related methods.
A flight has a data model represented by the following Flight dictionary:

flight = {'searchresultid': ,
          'code': '',
          'price': ,
          'departuredate': '',
          'arrivaldate': '',
          'gate': '',
          'totalseats': ,
          'seatsleft': ,
        }
@author: Jules Larue
Note: only the setUpClass, tearDownClass, setUp and tearDown methods have been taken
from the exercises.
"""
import unittest, sqlite3
from flight_reservation import flight_database as database

#Path to the database file, different from the deployment db
DB_PATH = 'db/flight_test.db'
ENGINE = database.Engine(DB_PATH)

#CONSTANTS DEFINING DIFFERENT USERS AND USER PROPERTIES
FLIGHTID_1111 = 1111
FLIGHT_1111 = {
      'searchresultid': 1234,
      'code': 'AY101',
      'price': 200,
      'departuredate': '2018-05-06',
      'arrivaldate': '2018-05-07',
      'gate': 'GATE02',
      'totalseats': 90,
      'seatsleft': 10,
}

MODIFIED_FLIGHT_1111 = {
      'searchresultid': 1234,
      'code': 'AY101',
      'price': 230,
      'departuredate': '2018-05-06',
      'arrivaldate': '2018-05-07',
      'gate': 'GATE05',
      'totalseats': 90,
      'seatsleft': 10,
}

NEW_FLIGHT = {
      'searchresultid': 1234,
      'code': 'AY164',
      'price': 190,
      'departuredate': '2018-05-20',
      'arrivaldate': '2018-05-21',
      'gate': 'GATE03',
      'totalseats': 90,
      'seatsleft': 5,
}

NEW_FLIGHT_WRONG_TEMPLATE = {
      'searchresultid': 9876,
      'code': 'AY164',
      'price': 190,
      'departuredate': '2018-05-20',
      'arrivaldate': '2018-05-21',
      'gate': 'GATE03',
      'totalseats': 90,
      'seatsleft': 5,
}

NEW_FLIGHT_EXISTING_CODE = {
      'searchresultid': 1234,
      'code': 'AY101',
      'price': 190,
      'departuredate': '2018-05-20',
      'arrivaldate': '2018-05-21',
      'gate': 'GATE03',
      'totalseats': 90,
      'seatsleft': 5,
}

TEMPLATE_FLIGHTID_1234 = 1234
NB_FLIGHTS_OF_TEMPLATE_1234 = 1

FLIGHT_WRONG_ID = 64
TEMPLATE_FLIGHT_WRONG_ID = 65
INITIAL_SIZE = 3


class FlightDBAPITestCase(unittest.TestCase):
    """
    Test cases for the Tickets related methods.
    """
    #INITIATION AND TEARDOWN METHODS
    @classmethod
    def setUpClass(cls):
        """ Creates the database structure. Removes first any preexisting
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
        #This method load the initial values from flight_data_dump.sql
        ENGINE.populate_tables()
        #Creates a Connection instance to use the API
        self.connection = ENGINE.connect()

    def tearDown(self):
        """
        Close underlying connection and remove all records from database
        """
        self.connection.close()
        ENGINE.clear()

    def test_flight_table_created(self):
        """
        Checks that the table flight initially contains 3 tickets (check
        flight_data_dump.sql).
        NOTE: Do not use Connection instance but
        call directly SQL.
        """
        print('('+self.test_flight_table_created.__name__+')', \
              self.test_flight_table_created.__doc__)
        #Create the SQL Statement
        keys_on = 'PRAGMA foreign_keys = ON'
        query1 = 'SELECT * FROM Flight'
        #Connects to the database.
        con = self.connection.con
        with con:
            #Cursor and row initialization
            con.row_factory = sqlite3.Row
            cur = con.cursor()
            #Provide support for foreign keys
            cur.execute(keys_on)
            #Execute main SQL Statement
            cur.execute(query1)
            flights = cur.fetchall()
            # Check number of flights
            self.assertEqual(len(flights), INITIAL_SIZE)

    def test_create_flight_object(self):
        """
        Check that the method test_create_flight_object works and returns adequate values
        for the first database row. NOTE: Do not use Connection instance to
        extract data from database but call directly SQL.
        """
        print('('+self.test_create_flight_object.__name__+')', \
              self.test_create_flight_object.__doc__)
        #Create the SQL Statement
        keys_on = 'PRAGMA foreign_keys = ON'
        query = 'SELECT * FROM Flight'
        #Get the sqlite3 con from the Connection instance
        con = self.connection.con

        #try:
        with con:
            #Cursor and row initialization
            con.row_factory = sqlite3.Row
            cur = con.cursor()
            #Provide support for foreign keys
            cur.execute(keys_on)
            #Execute main SQL Statement
            cur.execute(query)
            #Extrac the row
            row = cur.fetchone()
        #finally:
        #    con.close()
        #Test the method
        flight = self.connection._create_flight_object(row)
        self.assertDictContainsSubset(FLIGHT_1111, flight)

    def test_get_flight(self):
        """
        Checks that we can get a flight from the database
        """
        print('(' + self.test_get_flight.__name__ + ')',
              self.test_get_flight.__doc__)

        flight = self.connection.get_flight(FLIGHTID_1111)
        self.assertDictContainsSubset(FLIGHT_1111, flight)

    def test_get_flight_nonexisting_id(self):
        """
        Checks that trying to get flight with non existing id
        returns None
        """
        print('(' + self.test_get_flight_nonexisting_id.__name__ + ')', \
              self.test_get_flight_nonexisting_id.__doc__)

        resp = self.connection.get_flight(FLIGHT_WRONG_ID)
        self.assertIsNone(resp)


    def test_get_flights_by_template(self):
        """
        Checks that we can get flights of a specific
        template flight with correct data structure
        """
        print('(' + self.test_get_flights_by_template.__name__ + ')', \
              self.test_get_flights_by_template.__doc__)

        flights = self.connection.get_flights_by_template(TEMPLATE_FLIGHTID_1234)

        # Check correct number of flights (1)
        self.assertEqual(len(flights), 1)

        # Check flights structure of results
        for flight in flights:
            if flight["flightid"] == FLIGHTID_1111:
                self.assertDictContainsSubset(FLIGHT_1111, flight)

    def test_get_flights_by_template_nonexisting_id(self):
        """
        Check that getting flights of a non existing template
        returns None
        """
        print('(' + self.test_get_flights_by_template_nonexisting_id.__name__ + ')', \
              self.test_get_flights_by_template_nonexisting_id.__doc__)

        resp = self.connection.get_flights_by_template(TEMPLATE_FLIGHT_WRONG_ID)
        self.assertEqual(len(resp), 0)


    def test_create_flight(self):
        """
        Check that we can create a new flight
        """
        print('(' + self.test_create_flight.__name__ + ')', \
              self.test_create_flight.__doc__)

        # Create the new flight
        new_flight_id = self.connection.create_flight(NEW_FLIGHT)
        self.assertIsNotNone(new_flight_id)

        # Check that flight has been inserted
        # correctly in database
        flight = self.connection.get_flight(new_flight_id)
        self.assertDictContainsSubset(NEW_FLIGHT, flight)


    def test_create_flight_nonexisting_template(self):
        """
        Checks that we can not create a flight for
        a non existing template flight
        """
        print('(' + self.test_create_flight_nonexisting_template.__name__ + ')', \
              self.test_create_flight_nonexisting_template.__doc__)

        resp = self.connection.create_flight(NEW_FLIGHT_WRONG_TEMPLATE)
        self.assertIsNone(resp)


    def test_create_flight_existing_code(self):
        """
        Checks that we can not create a flight with an
        existing code
        """
        print('(' + self.test_create_flight_existing_code.__name__ + ')', \
              self.test_create_flight_existing_code.__doc__)

        resp = self.connection.create_flight(NEW_FLIGHT_EXISTING_CODE)
        self.assertIsNone(resp)

    def test_modify_flight(self):
        """
        Checks that we can modify a flight
        """
        print('(' + self.test_modify_flight.__name__ + ')', \
              self.test_modify_flight.__doc__)

        # Modify the flight 1111
        resp = self.connection.modify_flight(FLIGHTID_1111, MODIFIED_FLIGHT_1111)
        self.assertTrue(resp)

        # Check that flight 1111 has correct info in database
        flight = self.connection.get_flight(FLIGHTID_1111)
        self.assertDictContainsSubset(MODIFIED_FLIGHT_1111, flight)


    def test_modify_flight_nonexisting_id(self):
        """
        Checks that we can not modify a flight with
        a nonexisting id
        """
        print('(' + self.test_modify_flight_nonexisting_id.__name__ + ')', \
              self.test_modify_flight_nonexisting_id.__doc__)

        resp = self.connection.modify_flight(FLIGHT_WRONG_ID, MODIFIED_FLIGHT_1111)
        self.assertFalse(resp)


    def test_delete_flight(self):
        """
        Checks that we can delete a flight
        """
        print('(' + self.test_delete_flight.__name__ + ')', \
              self.test_delete_flight.__doc__)
        # Delete the flight
        resp = self.connection.delete_flight(FLIGHTID_1111)
        self.assertTrue(resp)

        # Check that the flight AND all reservations
        # do not exist anymore in database

        # Check flight deleted
        resp_flight = self.connection.get_flight(FLIGHTID_1111)
        self.assertIsNone(resp_flight)

        # Check reservations
        resp_reservations = self.connection.get_reservations_by_flight(FLIGHTID_1111)
        self.assertIsNone(resp_flight)

    def test_delete_flight_nonexisting_id(self):
        """
        Checks that we can not delete a flight with a non existing id
        (None returned)
        """
        print('(' + self.test_delete_flight_nonexisting_id.__name__ + ')', \
              self.test_delete_flight_nonexisting_id.__doc__)

        resp = self.connection.delete_flight(FLIGHT_WRONG_ID)
        self.assertFalse(resp)

if __name__ == '__main__':
    print('Start running flight tests')
    unittest.main()
