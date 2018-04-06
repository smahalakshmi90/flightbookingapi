"""
Created on 23.02.2018

Database interface testing for all template flights related methods.
A template flight has a data model represented by the following Template Flight dictionary:

template_flight = {'searchid': ,
          'origin': '',
          'destination': ,
          'departuretime': '',
          'arrivaltime': '',
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

#CONSTANTS DEFINING DIFFERENT TEMPLATE FLIGHTS PROPERTIES
TEMPLATE_FLIGHTID_1234 = 1234
TEMPLATE_FLIGHT_1234 = {
    'origin': 'Finland',
    'destination': 'France',
    'departuretime': '20:52',
    'arrivaltime': '23:40',
}

MODIFIED_TEMPLATE_FLIGHTID_1234 = 1234
MODIFIED_TEMPLATE_FLIGHT_1234 = {
    'origin': 'Finland',
    'destination': 'France',
    'departuretime': '19:30',
    'arrivaltime': '23:30',
}

NEW_TEMPLATE_FLIGHT = {
    'origin': 'Oslo',
    'destination': 'Oulu',
    'departuretime': '19:30',
    'arrivaltime': '20:30',
}

TEMPLATE_FLIGHT_WRONG_ID = 65
INITIAL_SIZE = 5


class TemplateFlightDBAPITestCase(unittest.TestCase):
    """
    Test cases for the Template Flights related methods.
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

    def test_template_flight_table_created(self):
        """
        Checks that the table template flight initially contains 5 template flights (check
        flight_data_dump.sql).
        NOTE: Do not use Connection instance but
        call directly SQL.
        """
        print('('+self.test_template_flight_table_created.__name__+')', \
              self.test_template_flight_table_created.__doc__)
        #Create the SQL Statement
        keys_on = 'PRAGMA foreign_keys = ON'
        query1 = 'SELECT * FROM TemplateFlight'
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
            tflights = cur.fetchall()
            # Check number of flights
            self.assertEqual(len(tflights), INITIAL_SIZE)

    def test_create_template_flight_object(self):
        """
        Check that the method test_create_template_flight_object works and returns adequate values
        for the first database row. NOTE: Do not use Connection instance to
        extract data from database but call directly SQL.
        """
        print('('+self.test_create_template_flight_object.__name__+')', \
              self.test_create_template_flight_object.__doc__)
        #Create the SQL Statement
        keys_on = 'PRAGMA foreign_keys = ON'
        query = 'SELECT * FROM TemplateFlight'
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
        tflight = self.connection._create_template_flight_object(row)
        self.assertDictContainsSubset(TEMPLATE_FLIGHT_1234, tflight)

    def test_get_template_flight(self):
        """
        Checks that we can get the information
        of a template flight
        """
        print('(' + self.test_get_template_flight.__name__ + ')', \
              self.test_get_template_flight.__doc__)

        tflight = self.connection.get_template_flight(TEMPLATE_FLIGHTID_1234)
        self.assertDictContainsSubset(TEMPLATE_FLIGHT_1234, tflight)


    def test_get_template_flight_nonexisting_id(self):
        """
        Checks that we can not get the information of a template
        flight with a non existing id
        """
        print('(' + self.test_get_template_flight_nonexisting_id.__name__ + ')', \
              self.test_get_template_flight_nonexisting_id.__doc__)

        resp = self.connection.get_template_flight(TEMPLATE_FLIGHT_WRONG_ID)
        self.assertIsNone(resp)


    def test_modify_template_flight(self):
        """
        Checks that we can modify the information of
        a template flight
        """
        print('(' + self.test_modify_template_flight.__name__ + ')', \
              self.test_modify_template_flight.__doc__)

        resp = self.connection.modify_template_flight(MODIFIED_TEMPLATE_FLIGHTID_1234,
                                                      MODIFIED_TEMPLATE_FLIGHT_1234)

        # Check that we effectively modified the template flight
        self.assertIsNotNone(resp)

        # Check information of template flight in database
        modified_tflight = self.connection.get_template_flight(MODIFIED_TEMPLATE_FLIGHTID_1234)
        self.assertDictContainsSubset(MODIFIED_TEMPLATE_FLIGHT_1234, modified_tflight)


    def test_modify_template_flight_nonexisting_id(self):
        """
        Checks that we can not modify a template flight with
        a non existing id
        """
        print('(' + self.test_modify_template_flight_nonexisting_id.__name__ + ')', \
              self.test_modify_template_flight_nonexisting_id.__doc__)

        resp = self.connection.modify_template_flight(TEMPLATE_FLIGHT_WRONG_ID,
                                                      MODIFIED_TEMPLATE_FLIGHT_1234)
        self.assertFalse(resp)


    def test_delete_flight(self):
        """
        Checks that we can delete a template flight
        """
        print('(' + self.test_delete_flight.__name__ + ')', \
              self.test_delete_flight.__doc__)

        resp = self.connection.delete_template_flight(TEMPLATE_FLIGHTID_1234)
        self.assertTrue(resp)

        # Check that template flight is removed from database
        resp = self.connection.get_template_flight(TEMPLATE_FLIGHTID_1234)
        self.assertIsNone(resp)


    def test_delete_flight_nonexisting_id(self):
        """
        Checks that we can not delete a flight with non existing
        id (returns None)
        """
        print('(' + self.test_delete_flight_nonexisting_id.__name__ + ')', \
              self.test_delete_flight_nonexisting_id.__doc__)

        resp = self.connection.delete_flight(TEMPLATE_FLIGHT_WRONG_ID)
        self.assertFalse(resp)

if __name__ == '__main__':
    print('Start running template flight tests')
    unittest.main()
