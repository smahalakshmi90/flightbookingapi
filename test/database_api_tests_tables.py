"""
Created on 21.02.2018

A Database interface to test that the tables
have been created correctly.

@author: Jules LARUE
"""

import sqlite3, unittest, collections

from flight_reservation import flight_database as database

# Path to the database file, different from the deployment db
DB_PATH = 'db/flight_test.db'
ENGINE = database.Engine(DB_PATH)

# Table names
TABLE_USER = 'User'
TABLE_RESERVATION = 'Reservation'
TABLE_TICKET = 'Ticket'
TABLE_FLIGHT = 'Flight'
TABLE_TEMPLATE_FLIGHT = 'TemplateFlight'

# Initial number of rows for each table
INITIAL_SIZE_USER = 5  # 5 users
INITIAL_SIZE_RESERVATION = 4  # 4 reservations
INITIAL_SIZE_TICKET = 5  # 5 tickets
INITIAL_SIZE_FLIGHT = 3  # 3 flights
INITIAL_SIZE_TEMPLATE_FLIGHT = 5  # 5 template flights


class CreatedTablesTestCase(unittest.TestCase):
    """
    Test cases for the created tables.

    NOTE: the code of this class has mostly been taken from
    Ivan Sanchez Milara (forum database). Jules LARUE has brought
    changes to adapt the code to the flight booking database.
    """

    # INITIATION AND TEARDOWN METHODS
    @classmethod
    def setUpClass(cls):
        """ Creates the database structure. Removes first any preexisting
            database file
        """
        print("Testing ", cls.__name__)
        # Remove database if already present
        ENGINE.remove_database()
        ENGINE.create_tables()

    @classmethod
    def tearDownClass(cls):
        """
        Remove the testing database
        """
        print("Testing ENDED for ", cls.__name__)
        ENGINE.remove_database()

    def setUp(self):
        """
        Populates the database
        """
        ENGINE.populate_tables()

    def tearDown(self):
        """
        Close underlying connection and remove all records from database
        """
        self.connection.close()
        ENGINE.clear()

    def test_user_table_schema(self):
        """
        Checks that the user table has the right schema.

        NOTE: Do not use Connection instance but
        call directly SQL.
        """
        print('(' + self.test_user_table_schema.__name__ + ')',
              self.test_user_table_schema.__doc__)

        # Creates a Connection instance to use the API
        self.connection = ENGINE.connect()
        con = self.connection.con
        with con:
            cursor = con.cursor()
            """
                Retrieve all the user column information.
                Each column will have the following tuple structure:
                (id, name, type, not_null, default_value, primary_key)
            """
            cursor.execute('PRAGMA TABLE_INFO({})'.format(TABLE_USER))

            # Get all results
            result = cursor.fetchall()

            # Get list of column names
            names = [tup[1] for tup in result]

            # Get list of column types
            types = [tup[2] for tup in result]

            # List of names expected
            real_names = ['user_id', 'lastName', 'firstName', 'phoneNumber', 'email', 'birthDate',
                          'gender', 'registrationDate']
            # List of types expected
            real_types = ['INTEGER', 'TEXT', 'TEXT', 'TEXT', 'TEXT', 'INTEGER', 'TEXT', 'INTEGER']

            # Check the equality between names / types got and expected values
            self.assertEqual(names, real_names)
            self.assertEqual(types, real_types)

    def test_reservation_table_schema(self):
        """
        Checks that the reservation table has the right schema.

        NOTE: Do not use Connection instance but
        call directly SQL.
        """
        print('(' + self.test_reservation_table_schema.__name__ + ')',
              self.test_reservation_table_schema.__doc__)

        # Creates a Connection instance to use the API
        self.connection = ENGINE.connect()
        con = self.connection.con
        with con:
            cursor = con.cursor()
            """
                Retrieve all the reservation columns information.
                Each column will have the following tuple structure:
                (id, name, type, not_null, default_value, primary_key)
            """
            cursor.execute('PRAGMA TABLE_INFO({})'.format(TABLE_RESERVATION))

            # Get all results
            result = cursor.fetchall()

            # Get list of column names
            names = [tup[1] for tup in result]

            # Get list of column types
            types = [tup[2] for tup in result]

            # List of names expected
            real_names = ['reservation_id', 'reference', 're_date', 'creator_id', 'flight_id']
            # List of types expected
            real_types = ['INTEGER', 'TEXT', 'INTEGER', 'INTEGER', 'INTEGER']

            # Check the equality between names / types got and expected values
            self.assertEqual(names, real_names)
            self.assertEqual(types, real_types)

            # Check that foreign keys are correctly set
            foreign_keys = [(TABLE_FLIGHT, 'flight_id', 'flight_id'), (TABLE_USER, 'creator_id', 'user_id')]
            cursor.execute('PRAGMA FOREIGN_KEY_LIST({})'.format(TABLE_RESERVATION))
            result = cursor.fetchall()
            result_filtered = [(tup[2], tup[3], tup[4]) for tup in result]
            for tup in result_filtered:
                self.assertIn(tup, foreign_keys)

    def test_ticket_table_schema(self):
        """
        Checks that the Ticket table has the right schema.

        NOTE: Do not use Connection instance but
        call directly SQL.
        """
        print('(' + self.test_ticket_table_schema.__name__ + ')',
              self.test_ticket_table_schema.__doc__)

        # Creates a Connection instance to use the API
        self.connection = ENGINE.connect()
        con = self.connection.con
        with con:
            cursor = con.cursor()
            """
                Retrieve all the ticket columns information.
                Each column will have the following tuple structure:
                (id, name, type, not_null, default_value, primary_key)
            """
            cursor.execute('PRAGMA TABLE_INFO({})'.format(TABLE_TICKET))

            # Get all results
            result = cursor.fetchall()

            # Get list of column names
            names = [tup[1] for tup in result]

            # Get list of column types
            types = [tup[2] for tup in result]

            # List of names expected
            real_names = ['ticket_id', 'firstName', 'lastName', 'gender', 'age', 'reservation_id', 'seat']
            # List of types expected
            real_types = ['INTEGER', 'TEXT', 'TEXT', 'TEXT', 'INTEGER', 'INTEGER', 'TEXT']

            # Check the equality between names / types got and expected values
            self.assertEqual(names, real_names)
            self.assertEqual(types, real_types)

            # Check that foreign keys are correctly set
            foreign_keys = [(TABLE_RESERVATION, 'reservation_id', 'reservation_id')]
            cursor.execute('PRAGMA FOREIGN_KEY_LIST({})'.format(TABLE_TICKET))
            result = cursor.fetchall()
            result_filtered = [(tup[2], tup[3], tup[4]) for tup in result]
            for tup in result_filtered:
                self.assertIn(tup, foreign_keys)

    def test_flight_table_schema(self):
        """
        Checks that the Flight table has the right schema.

        NOTE: Do not use Connection instance but
        call directly SQL.
        """
        print('(' + self.test_flight_table_schema.__name__ + ')',
              self.test_flight_table_schema.__doc__)

        # Creates a Connection instance to use the API
        self.connection = ENGINE.connect()
        con = self.connection.con
        with con:
            cursor = con.cursor()
            """
                Retrieve all the Flight columns information.
                Each column will have the following tuple structure:
                (id, name, type, not_null, default_value, primary_key)
            """
            cursor.execute('PRAGMA TABLE_INFO({})'.format(TABLE_FLIGHT))

            # Get all results
            result = cursor.fetchall()

            # Get list of column names
            names = [tup[1] for tup in result]

            # Get list of column types
            types = [tup[2] for tup in result]

            # List of names expected
            real_names = ['flight_id', 'code', 'price', 'gate', 'depDate', 'arrDate', 'nbInitialSeats',
                          'nbSeatsLeft', 'template_id']
            # List of types expected
            real_types = ['INTEGER', 'TEXT', 'INTEGER', 'TEXT', 'INTEGER', 'INTEGER', 'INTEGER', 'INTEGER', 'INTEGER']

            # Check the equality between names / types got and expected values
            self.assertEqual(names, real_names)
            self.assertEqual(types, real_types)

            # Check that foreign keys are correctly set
            foreign_keys = [(TABLE_TEMPLATE_FLIGHT, 'template_id', 'tflight_id')]
            cursor.execute('PRAGMA FOREIGN_KEY_LIST({})'.format(TABLE_FLIGHT))
            result = cursor.fetchall()
            result_filtered = [(tup[2], tup[3], tup[4]) for tup in result]
            for tup in result_filtered:
                self.assertIn(tup, foreign_keys)

    def test_template_flight_table_schema(self):
        """
        Checks that the TemplateFlight table has the right schema.

        NOTE: Do not use Connection instance but
        call directly SQL.
        """
        print('(' + self.test_template_flight_table_schema.__name__ + ')',
              self.test_template_flight_table_schema.__doc__)

        # Creates a Connection instance to use the API
        self.connection = ENGINE.connect()
        con = self.connection.con
        with con:
            cursor = con.cursor()
            """
                Retrieve all the TemplateFlight columns information.
                Each column will have the following tuple structure:
                (id, name, type, not_null, default_value, primary_key)
            """
            cursor.execute('PRAGMA TABLE_INFO({})'.format(TABLE_TEMPLATE_FLIGHT))

            # Get all results
            result = cursor.fetchall()

            # Get list of column names
            names = [tup[1] for tup in result]

            # Get list of column types
            types = [tup[2] for tup in result]

            # List of names expected
            real_names = ['tflight_id', 'depTime', 'arrTime', 'origin', 'destination']
            # List of types expected
            real_types = ['INTEGER', 'INTEGER', 'INTEGER', 'TEXT', 'TEXT']

            # Check the equality between names / types got and expected values
            self.assertEqual(names, real_names)
            self.assertEqual(types, real_types)

    def test_user_table_created(self):
        """
        Checks that the User table initially contains 5 users
        (according to the flight_data_dump.sql file)

        NOTE: Do not use Connection instance but
        call directly SQL.
        """
        print('(' + self.test_user_table_created.__name__ + ')',
              self.test_user_table_created.__doc__)

        # Creates a Connection instance to use the API
        self.connection = ENGINE.connect()

        # Create the SQL Statement
        keys_on = 'PRAGMA foreign_keys = ON'
        query = 'SELECT * FROM ' + TABLE_USER
        # Get the sqlite3 con from the Connection instance
        con = self.connection.con
        with con:
            # Cursor and row initialization
            con.row_factory = sqlite3.Row
            cursor = con.cursor()

            # Provide support for foreign keys
            cursor.execute(keys_on)

            # Execute SQL query to get all the users
            cursor.execute(query)
            users = cursor.fetchall()

            # Check we got the corretc number of users
            self.assertEqual(len(users), INITIAL_SIZE_USER)

    def test_reservation_table_created(self):
        """
        Checks that the Reservation table initially contains 4 reservations
        (according to the flight_data_dump.sql file)

        NOTE: Do not use Connection instance but
        call directly SQL.
        """
        print('(' + self.test_reservation_table_created.__name__ + ')',
              self.test_reservation_table_created.__doc__)

        # Creates a Connection instance to use the API
        self.connection = ENGINE.connect()
        # Create the SQL Statement
        keys_on = 'PRAGMA foreign_keys = ON'
        query = 'SELECT * FROM ' + TABLE_RESERVATION
        # Get the sqlite3 con from the Connection instance
        con = self.connection.con
        with con:
            # Cursor and row initialization
            con.row_factory = sqlite3.Row
            cursor = con.cursor()

            # Provide support for foreign keys
            cursor.execute(keys_on)

            # Execute SQL query to get all the reservations
            cursor.execute(query)
            reservations = cursor.fetchall()

            # Check we got the corretc number of users
            self.assertEqual(len(reservations), INITIAL_SIZE_RESERVATION)

    def test_ticket_table_created(self):
        """
        Checks that the User table initially contains 5 tickets
        (according to the flight_data_dump.sql file)

        NOTE: Do not use Connection instance but
        call directly SQL.
        """
        print('(' + self.test_ticket_table_created.__name__ + ')',
              self.test_ticket_table_created.__doc__)

        # Creates a Connection instance to use the API
        self.connection = ENGINE.connect()
        # Create the SQL Statement
        keys_on = 'PRAGMA foreign_keys = ON'
        query = 'SELECT * FROM ' + TABLE_TICKET
        # Get the sqlite3 con from the Connection instance
        con = self.connection.con
        with con:
            # Cursor and row initialization
            con.row_factory = sqlite3.Row
            cursor = con.cursor()

            # Provide support for foreign keys
            cursor.execute(keys_on)

            # Execute SQL query to get all the tickets
            cursor.execute(query)
            tickets = cursor.fetchall()

            # Check we got the corretc number of users
            self.assertEqual(len(tickets), INITIAL_SIZE_TICKET)

    def test_flight_table_created(self):
        """
        Checks that the User table initially contains 3 flights
        (according to the flight_data_dump.sql file)

        NOTE: Do not use Connection instance but
        call directly SQL.
        """
        print('(' + self.test_flight_table_created.__name__ + ')',
              self.test_flight_table_created.__doc__)

        # Creates a Connection instance to use the API
        self.connection = ENGINE.connect()
        # Create the SQL Statement
        keys_on = 'PRAGMA foreign_keys = ON'
        query = 'SELECT * FROM ' + TABLE_FLIGHT
        # Get the sqlite3 con from the Connection instance
        con = self.connection.con
        with con:
            # Cursor and row initialization
            con.row_factory = sqlite3.Row
            cursor = con.cursor()

            # Provide support for foreign keys
            cursor.execute(keys_on)

            # Execute SQL query to get all the flights
            cursor.execute(query)
            flights = cursor.fetchall()

            # Check we got the corretc number of users
            self.assertEqual(len(flights), INITIAL_SIZE_FLIGHT)

    def test_template_flight_table_created(self):
        """
        Checks that the User table initially contains 5 template flights
        (according to the flight_data_dump.sql file)

        NOTE: Do not use Connection instance but
        call directly SQL.
        """
        print('(' + self.test_template_flight_table_created.__name__ + ')',
              self.test_template_flight_table_created.__doc__)

        # Creates a Connection instance to use the API
        self.connection = ENGINE.connect()
        # Create the SQL Statement
        keys_on = 'PRAGMA foreign_keys = ON'
        query = 'SELECT * FROM ' + TABLE_TEMPLATE_FLIGHT
        # Get the sqlite3 con from the Connection instance
        con = self.connection.con
        with con:
            # Cursor and row initialization
            con.row_factory = sqlite3.Row
            cursor = con.cursor()

            # Provide support for foreign keys
            cursor.execute(keys_on)

            # Execute SQL query to get all the template flights
            cursor.execute(query)
            template_flights = cursor.fetchall()

            # Check we got the corretc number of users
            self.assertEqual(len(template_flights), INITIAL_SIZE_TEMPLATE_FLIGHT)


if __name__ == '__main__':
    print('Start running database tests')
    unittest.main()
