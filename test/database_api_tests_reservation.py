"""
Created on 23.02.2018

Database interface testing for all reservations related methods.
A reservation has a data model represented by the following Reservation dictionary:
{
    'reservationid': ,
    'reference': '',
    'reservationdate': '',
    'userid': ,
    'flightid':
}


@author: Jules Larue
Note: only the setUpClass, tearDownClass, setUp and tearDown methods have been taken
from the exercises.
"""
from time import gmtime, strftime
import unittest, sqlite3
from flight_reservation import flight_database as database

#Path to the database file, different from the deployment db
DB_PATH = 'db/flight_test.db'
ENGINE = database.Engine(DB_PATH)

#CONSTANTS DEFINING DIFFERENT USERS AND USER PROPERTIES
RESERVATION1_ID = 11
RESERVATION1 = {
    'reference': 'AB12CS',
    'reservationdate': '2018-02-20',
    'userid': 1,
    'flightid': 1111
}

RESERVATION1_LIST_OBJECT = {
    'reference': 'AB12CS',
    'userid': 1,
    'flightid': 1111
}

RESERVATION2_ID = 22
RESERVATION2 = {
    'reference': 'HJJJHW',
    'reservationdate': '2018-02-28',
    'userid': 2,
    'flightid': 1122
}

RESERVATION2_LIST_OBJECT = {
    'reference': 'HJJJHW',
    'userid': 2,
    'flightid': 1122
}

NEW_RESERVATION = {
    'reference': 'FR23H',
    'reservationdate': strftime("%Y-%m-%d", gmtime()),
    'userid': 3,
    'flightid': 1122
}

NEW_RESERVATION_WRONG_USERID = {
    'reference': 'FR23H',
    'reservationdate': '2018-02-28',
    'userid':40,
    'flightid': 1122
}

NEW_RESERVATION_WRONG_FLIGHTID = {
    'reference': 'FR23H',
    'reservationdate': '2018-02-28',
    'userid': 3,
    'flightid': 8754
}

OWNER_RES_11 = 1
OWNER_RES_22 = 2
OWNER_WRONG_ID = 99

FLIGHTID_RES_11 = 1111
FLIGHTID_RES_22 = 1122
FLIGHT_WRONG_ID = 9876

RESERVATION_WRONG_ID = 100
INITIAL_SIZE = 4


class ReservationDBAPITestCase(unittest.TestCase):
    """
    Test cases for the Reservations related methods.
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

    def test_reservation_table_created(self):
        """
        Checks that the table reservation initially contains 4
        reservations (check flight_data_dump.sql).
        NOTE: Do not use Connection instance but call directly SQL.
        """
        print('('+self.test_reservation_table_created.__name__+')', \
              self.test_reservation_table_created.__doc__)
        #Create the SQL Statement
        keys_on = 'PRAGMA foreign_keys = ON'
        query1 = 'SELECT * FROM Reservation'
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
            reservations = cur.fetchall()
            # Check number of users
            self.assertEqual(len(reservations), INITIAL_SIZE)

    def test_create_reservation_object(self):
        """
        Check that the method create_user_object works and returns adequate values
        for the first database row. NOTE: Do not use Connection instance to
        extract data from database but call directly SQL.
        """
        print('('+self.test_create_reservation_object.__name__+')', \
              self.test_create_reservation_object.__doc__)
        #Create the SQL Statement
        keys_on = 'PRAGMA foreign_keys = ON'
        query = 'SELECT * FROM Reservation'
        #Get the sqlite3 con from the Connection instance
        con = self.connection.con
        #I am doing operations after with, so I must explicitly close the
        # the connection to be sure that no locks are kept. The with, close
        # the connection when it has gone out of scope
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
        reservation = self.connection._create_reservation_object(row)
        self.assertDictContainsSubset(RESERVATION1, reservation)

    def test_get_reservation(self):
        """
        Checks that getting a reservation by id returns
        the correct reservation with corretc data structure
        """
        print('(' + self.test_get_reservation.__name__ + ')', \
              self.test_get_reservation.__doc__)

        # Test existing reservations
        res1 = self.connection.get_reservation(RESERVATION1_ID)
        res2 = self.connection.get_reservation(RESERVATION2_ID)
        self.assertDictContainsSubset(RESERVATION1, res1)
        self.assertDictContainsSubset(RESERVATION2, res2)

    def test_get_reservation_nonexisting_id(self):
        """
        Test get_reservation with non existing id (100)
        """
        print('(' + self.test_get_reservation_nonexisting_id.__name__ + ')', \
              self.test_get_reservation_nonexisting_id.__doc__)
        reservation = self.connection.get_reservation(RESERVATION_WRONG_ID)
        self.assertIsNone(reservation)


    def test_get_reservations(self):
        """
        Test get_reservations returns correct data structure
        and reservations
        """
        print('(' + self.test_get_reservation_nonexisting_id.__name__ + ')', \
              self.test_get_reservation_nonexisting_id.__doc__)

        reservations = self.connection.get_reservation_list()
        for res in reservations:
            if res["reservationid"] == RESERVATION1_ID:
                self.assertDictContainsSubset(RESERVATION1, res)
            elif res["reservationid"] == RESERVATION2_ID:
                self.assertDictContainsSubset(RESERVATION2, res)

    def test_get_reservations_user(self):
        """
        Test that get_reservations_by_user(user_id) returns the correct
        reservations of the specified user with correct structure
        """
        print('(' + self.test_get_reservations_user.__name__ + ')', \
              self.test_get_reservations_user.__doc__)

        reservations = self.connection.get_reservations_by_user(OWNER_RES_11)
        for reservation in reservations:
            if reservation["reservationid"] == 11:
                self.assertDictContainsSubset(RESERVATION1, reservation)

    def test_get_reservations_nonexisting_user(self):
        """
        Test that get_reservations_by_user(user_id) returns None
        with nonexisting user id (99)
        """
        reservations = self.connection.get_reservations_by_user(RESERVATION_WRONG_ID)
        self.assertEqual(len(reservations), 0)

    def test_get_reservations_flight(self):
        """
        Test that get_reservations_by_flight(flight_id) returns the correct
        reservations of the specified flight with correct structure
        """
        print('(' + self.test_get_reservations_flight.__name__ + ')', \
              self.test_get_reservations_flight.__doc__)

        # Reservations for flight 1111
        reservations = self.connection.get_reservations_by_flight(FLIGHTID_RES_11)
        for reservation in reservations:
            if reservation["reservationid"] == 11:
                self.assertDictContainsSubset(RESERVATION1_LIST_OBJECT, reservation)

        # Reservations for flight 1122
        reservations = self.connection.get_reservations_by_flight(FLIGHTID_RES_22)
        for reservation in reservations:
            if reservation["reservationid"] == 22:
                self.assertDictContainsSubset(RESERVATION2_LIST_OBJECT, reservation)

    def test_get_reservations_nonexisting_flight(self):
        """
        Test that get_reservations_by_flight(flight_id) returns None
        with nonexisting flight id (9876)
        """
        print('(' + self.test_get_reservations_nonexisting_flight.__name__ + ')', \
              self.test_get_reservations_nonexisting_flight.__doc__)

        reservations = self.connection.get_reservations_by_flight(FLIGHT_WRONG_ID)
        self.assertEqual(len(reservations), 0)

    def test_create_reservation(self):
        """
        Test that create_reservation adds a new reservation
        in the database
        """
        print('(' + self.test_create_reservation.__name__ + ')', \
              self.test_create_reservation.__doc__)

        new_res_id = self.connection.create_reservation(NEW_RESERVATION)
        self.assertIsNotNone(new_res_id)

        # Check that reservation information are correct
        resp2 = self.connection.get_reservation(new_res_id)
        self.assertDictContainsSubset(NEW_RESERVATION, resp2)

    def test_create_reservation_nonexisting_user(self):
        """
        Test that I can not add a reservation with a non existing user
        """
        print('(' + self.test_create_reservation_nonexisting_user.__name__ + ')', \
              self.test_create_reservation_nonexisting_user.__doc__)

        new_res_id = self.connection.create_reservation(NEW_RESERVATION_WRONG_USERID)
        self.assertIsNone(new_res_id)

    def test_create_reservation_nonexisting_user(self):
        """
        Test that I can not add a reservation with a non existing flight (8754)
        """
        print('(' + self.test_create_reservation_nonexisting_user.__name__ + ')', \
              self.test_create_reservation_nonexisting_user.__doc__)

        new_res_id = self.connection.create_reservation(NEW_RESERVATION_WRONG_FLIGHTID)
        self.assertIsNone(new_res_id)


    def test_delete_reservation(self):
        """
        Test that I can delete all the information of a reservation
        """
        print('(' + self.test_delete_reservation.__name__ + ')', \
              self.test_delete_reservation.__doc__)

        # Remove the two first reservations
        resp1 = self.connection.delete_reservation(RESERVATION1_ID)
        resp2 = self.connection.delete_reservation(RESERVATION2_ID)

        # Check that reservations do not exist anymore in database
        reservation1 = self.connection.get_reservation(RESERVATION1_ID)
        reservation2 = self.connection.get_reservation(RESERVATION1_ID)
        self.assertIsNone(reservation1)
        self.assertIsNone(reservation2)

        # Check that we do not have tickets for the reservations
        tickets_res1 = self.connection.get_tickets_by_reservation(RESERVATION1_ID)
        tickets_res2 = self.connection.get_tickets_by_reservation(RESERVATION2_ID)
        self.assertEqual(len(tickets_res1), 0)
        self.assertEqual(len(tickets_res2), 0)


    def test_delete_reservation_nonexisting_id(self):
        """
        Test that deleting a reservation with nonexisting id
        does not work
        """
        print('(' + self.test_delete_reservation_nonexisting_id.__name__ + ')', \
              self.test_delete_reservation_nonexisting_id.__doc__)

        resp = self.connection.delete_reservation(RESERVATION_WRONG_ID)
        self.assertFalse(resp)

if __name__ == '__main__':
    print('Start running reservation tests')
    unittest.main()
