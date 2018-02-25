"""
Created on 23.02.2018

Database interface testing for all tickets related methods.
A ticket has a data model represented by the following Reservation dictionary:

ticket = {'ticketnumber': ,
          'reservationid': ,
          'firstname': '',
          'lastname': '',
          'gender': '',
          'age': ,
          'seat':''
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
TICKETID_1010 = 1010
TICKET_1010 = {
    'reservationid': 11,
    'firstname': 'John',
    'lastname': 'Tilton',
    'gender': 'male',
    'age': 20,
    'seat':'21A'
}

MODIFIED_TICKET_1010 = {
    'reservationid': 11,
    'firstname': 'James',
    'lastname': 'Arthur',
    'gender': 'male',
    'age': 24,
}

MODIFIED_TICKET_1010_UNAVAILABLE_SEAT = {
    'reservationid': 11,
    'firstname': 'James',
    'lastname': 'Arthur',
    'gender': 'male',
    'age': 24,
}

TICKETID_1020 = 1020
TICKET_1020 = {
    'reservationid': 11,
    'firstname': 'Jacob',
    'lastname': 'Tilton',
    'gender': 'male',
    'age': 25,
    'seat':'21B'
}

TICKETID_1040 = 1040
TICKET_1040 = {
    'reservationid': 22,
    'firstname': 'Molly',
    'lastname': 'Jacob',
    'gender': 'female',
    'age': 40,
}

NEW_TICKET = {
    'reservationid': 22,
    'firstname': 'James',
    'lastname': 'Watt',
    'gender': 'male',
    'age': 34,
}

NEW_TICKET_UNAVAILABLE_SEAT = {
    'reservationid': 22,
    'firstname': 'James',
    'lastname': 'Watt',
    'gender': 'male',
    'age': 34,
}

# To get tickets by reservation
TICKET_1010_AND_1020_RESID = 11
NB_TICKETS_RES_11 = 2

NEW_TICKET_FLIGHT_FULL = {
    'reservationid': 33,
    'firstname': 'James',
    'lastname': 'Watt',
    'gender': 'male',
    'age': 34,
}

TICKET_WRONG_ID = 35
RESERVATION_WRONG_ID = 300
INITIAL_SIZE = 5

class TicketDBAPITestCase(unittest.TestCase):
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

    def test_ticket_table_created(self):
        """
        Checks that the table ticket initially contains 5 tickets (check
        flight_data_dump.sql).
        NOTE: Do not use Connection instance but
        call directly SQL.
        """
        print('('+self.test_ticket_table_created.__name__+')', \
              self.test_ticket_table_created.__doc__)
        #Create the SQL Statement
        keys_on = 'PRAGMA foreign_keys = ON'
        query1 = 'SELECT * FROM Ticket'
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
            tickets = cur.fetchall()
            # Check number of tickets
            self.assertEqual(len(tickets), INITIAL_SIZE)

    def test_create_ticket_object(self):
        """
        Check that the method test_create_ticket_object works and returns adequate values
        for the first database row. NOTE: Do not use Connection instance to
        extract data from database but call directly SQL.
        """
        print('('+self.test_create_ticket_object.__name__+')', \
              self.test_create_ticket_object.__doc__)
        #Create the SQL Statement
        keys_on = 'PRAGMA foreign_keys = ON'
        query = 'SELECT * FROM Ticket'
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
        ticket = self.connection._create_ticket_object(row)
        self.assertDictContainsSubset(TICKET_1010, ticket)


    def test_get_ticket(self):
        """
        Checks that we can get a ticket by id with a
        correct data structure
        """
        print('(' + self.test_get_ticket.__name__ + ')', \
              self.test_get_ticket.__doc__)

        resp = self.connection.get_ticket(TICKETID_1010)
        self.assertDictContainsSubset(TICKET_1010, resp)

        resp = self.connection.get_ticket(TICKETID_1040)
        self.assertDictContainsSubset(TICKET_1040, resp)

    def test_get_ticket_nonexisting_id(self):
        """
        Checks that get_ticket with non existing id
        returns None
        """
        print('(' + self.test_get_ticket_nonexisting_id.__name__ + ')', \
              self.test_get_ticket_nonexisting_id.__doc__)

        resp = self.connection.get_ticket(TICKET_WRONG_ID)
        self.assertIsNone(resp)

    def test_get_tickets(self):
        """
        Checks that get_tickets returns the list of all tickets
        with correct data structure
        """
        print('(' + self.test_get_tickets.__name__ + ')', \
              self.test_get_tickets.__doc__)

        tickets = self.connection.get_tickets()
        for ticket in tickets:
            if ticket["ticketnumber"] == TICKETID_1010:
                self.assertDictContainsSubset(ticket, TICKETID_1010)
            elif ticket["ticketnumber"] == TICKETID_1040:
                self.assertDictContainsSubset(TICKETID_1040, ticket)


    def test_get_tickets_by_reservation(self):
        """
        Checks that we can get the list of tickets of
        a given reservation
        """
        print('(' + self.test_get_tickets_by_reservation.__name__ + ')', \
              self.test_get_tickets_by_reservation.__doc__)

        tickets = self.connection.get_tickets_by_reservation(TICKET_1010_AND_1020_RESID)

        # Check the number rof tickets
        self.assertEqual(len(tickets), NB_TICKETS_RES_11)

        # Check that tickets info are correct
        for ticket in tickets:
            if ticket["ticketnumber"] == TICKETID_1010:
                self.assertSequenceEqual(ticket, TICKET_1010)
            elif ticket["ticketnumber"] == TICKETID_1020:
                self.assertSequenceEqual(ticket, TICKET_1020)

    def test_get_tickets_by_nonexisting_reservation(self):
        """
        Check that we can not get tickets of a non existing
        reservation
        """
        print('(' + self.test_get_tickets_by_nonexisting_reservation.__name__ + ')', \
              self.test_get_tickets_by_nonexisting_reservation.__doc__)

        resp = self.connection.get_tickets_by_reservation(RESERVATION_WRONG_ID)
        self.assertEqual(len(resp), 0)


    def test_create_ticket(self):
        """
        Check that we can create a new ticket in the database
        """
        print('(' + self.test_create_ticket.__name__ + ')', \
              self.test_create_ticket.__doc__)

        new_ticket_id = self.connection.create_ticket(NEW_TICKET)
        self.assertIsNotNone(new_ticket_id)

        # Check that ticket is correctly registered in database
        ticket = self.connection.get_ticket(new_ticket_id)
        self.assertDictContainsSubset(NEW_TICKET, ticket)


    def test_create_ticket_no_seat_available(self):
        """
        Checks that we can not create ticket if all seats of
        the flight are booked
        """
        print('(' + self.test_create_ticket_no_seat_available.__name__ + ')', \
              self.test_create_ticket_no_seat_available.__doc__)

        from flight_reservation.flight_database import NoMoreSeatsAvailableException
        with self.assertRaises(NoMoreSeatsAvailableException):
            # Creation of the ticket raises an error
            self.connection.create_ticket(NEW_TICKET_FLIGHT_FULL)


    def test_modify_ticket(self):
        """
        Checks that we can modify a ticket
        """
        print('(' + self.test_modify_ticket.__name__ + ')', \
              self.test_modify_ticket.__doc__)

        # Modify the ticket 1010
        resp = self.connection.modify_ticket(TICKETID_1010, MODIFIED_TICKET_1010)
        self.assertTrue(resp)

        # Check that ticket 1010 has correct info in database
        ticket = self.connection.get_ticket(TICKETID_1010)
        self.assertDictContainsSubset(MODIFIED_TICKET_1010, ticket)

    def test_modify_ticket_nonexisting_id(self):
        """
        Checks that we can not modify a ticket with a
        non existing id
        """
        print('(' + self.test_modify_ticket_nonexisting_id.__name__ + ')', \
              self.test_modify_ticket_nonexisting_id.__doc__)

        resp = self.connection.modify_ticket(TICKET_WRONG_ID, MODIFIED_TICKET_1010)
        self.assertFalse(resp)

    def test_delete_ticket(self):
        """
        Checks that we can delete a ticket
        """
        print('(' + self.test_delete_ticket.__name__ + ')', \
              self.test_delete_ticket.__doc__)

        # Delete ticket 1010
        resp = self.connection.delete_ticket(TICKETID_1010)
        self.assertTrue(resp)

        # Check that ticket is not in database
        resp = self.connection.get_ticket(TICKETID_1010)
        self.assertIsNone(resp)


    def test_delete_ticket_nonexisting_id(self):
        """
        Checks that we can not delete a ticket with a
        non existing id
        """
        print('(' + self.test_delete_ticket_nonexisting_id.__name__ + ')', \
              self.test_delete_ticket_nonexisting_id.__doc__)

        resp = self.connection.delete_ticket(TICKET_WRONG_ID)
        self.assertFalse(resp)

    def test_contains_ticket(self):
        """
        Checks that we can check that the database contains a ticket
        """
        print('(' + self.test_contains_ticket.__name__ + ')', \
              self.test_contains_ticket.__doc__)

        resp = self.connection.contains_ticket(TICKETID_1010)
        self.assertTrue(resp)
        resp = self.connection.contains_ticket(TICKETID_1020)
        self.assertTrue(resp)
        resp = self.connection.contains_ticket(TICKETID_1040)
        self.assertTrue(resp)

    def test_contains_ticket_nonexisting_id(self):
        """
        Checks that we can check that a ticket id does NOT exist
        in the database
        """
        print('(' + self.test_contains_ticket_nonexisting_id.__name__ + ')', \
              self.test_contains_ticket_nonexisting_id.__doc__)

        resp = self.connection.contains_ticket(TICKET_WRONG_ID)
        self.assertFalse(resp)

if __name__ == '__main__':
    print('Start running ticket tests')
    unittest.main()
