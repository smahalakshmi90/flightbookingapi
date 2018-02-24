"""
Created on 23.02.2018

Database interface testing for all users related methods.
The user has a data model represented by the following User dictionary:
{
    'lastname': '',
    'firstname': '',
    'phonenumber': '',
    'email': '',
    'dateofBirth': '', (YYYY-MM-DD format)
    'gender': '',
    'registrationDate':
}


@author: Jules Larue
Note: structure of the code has been taken from the exercises, but
has been adapted for our database
"""
import unittest, sqlite3
from flight_reservation import flight_database as database

#Path to the database file, different from the deployment db
DB_PATH = 'db/flight_test.db'
ENGINE = database.Engine(DB_PATH)

#CONSTANTS DEFINING DIFFERENT USERS AND USER PROPERTIES
USER1_ID = 1
USER1 = {
    'lastname': 'Tilton',
    'firstname': 'John',
    'phonenumber': '92722736387',
    'email': 'john.tilton@jhj.jh',
    'dateofBirth': '1981-04-04',
    'gender': 'male',
    'registrationDate': 1519423463929,
}
MODIFIED_USER1 = {
    'lastname': 'Watt',
    'firstname': 'James',
    'phonenumber': '+44 871 222 3330',
    'email': 'james.watt@example.com',
    'dateofBirth': '1992-04-12',
    'gender': 'male',
    'registrationDate': 1519423463929,
}

USER2_ID = 2
USER2 = {
    'lastname': 'Sam',
    'firstname': 'Jacob',
    'phonenumber': '927656756',
    'email': 'sam.jacob@jhj.jh',
    'dateofBirth': '1981-04-05',
    'gender': 'male',
    'registrationDate': 1519423463929,
}
MODIFIED_USER2 = {
    'lastname': 'Dupont',
    'firstname': 'Pierre',
    'phonenumber': '+33665544332',
    'email': 'pierre.dupont@example.com',
    'dateofBirth': '2000-01-01',
    'gender': 'Male',
    'registrationDate': 1519423463929,
}

NEW_USER = {
    'lastname': 'Larue',
    'firstname': 'Jules',
    'phonenumber': '+33065837465',
    'email': 'jules.larue@example.com',
    'dateofBirth': '1996-07-28',
    'gender': 'Male',
}
NEW_USER_ID = 6

USER_WRONG_ID = 100
INITIAL_SIZE = 5


class UserDBAPITestCase(unittest.TestCase):
    """
    Test cases for the Users related methods.
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
        #This method load the initial values from forum_data_dump.sql
        ENGINE.populate_tables()
        #Creates a Connection instance to use the API
        self.connection = ENGINE.connect()

    def tearDown(self):
        """
        Close underlying connection and remove all records from database
        """
        self.connection.close()
        ENGINE.clear()

    def test_user_table_created(self):
        """
        Checks that the table initially contains 5 users (check
        flight_data_dump.sql). NOTE: Do not use Connection instance but
        call directly SQL.
        """
        print('('+self.test_user_table_created.__name__+')', \
              self.test_user_table_created.__doc__)
        #Create the SQL Statement
        keys_on = 'PRAGMA foreign_keys = ON'
        query1 = 'SELECT * FROM User'
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
            users = cur.fetchall()
            # Check number of users
            self.assertEqual(len(users), INITIAL_SIZE)

    def test_create_user_object(self):
        """
        Check that the method create_user_object works and returns adequate values
        for the first database row. NOTE: Do not use Connection instace to
        extract data from database but call directly SQL.
        """
        print('('+self.test_create_user_object.__name__+')', \
              self.test_create_user_object.__doc__)
        #Create the SQL Statement
        keys_on = 'PRAGMA foreign_keys = ON'
        query = 'SELECT * FROM User'
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
        user = self.connection._create_user_object(row)
        self.assertDictContainsSubset(USER1, user)

    def test_get_user(self):
        """
        Test get_user with id 1 and 2
        """
        print('('+self.test_get_user.__name__+')', \
              self.test_get_user.__doc__)

        #Test with an existing user
        user = self.connection.get_user(USER1_ID)
        self.assertDictContainsSubset(USER1, user)
        user = self.connection.get_user(USER2_ID)
        self.assertDictContainsSubset(USER2, user)

    def test_get_user_noexistingid(self):
        """
        Test get_user with id 100 (does not exist)
        """
        print('('+self.test_get_user_noexistingid.__name__+')', \
              self.test_get_user_noexistingid.__doc__)

        #Test with an existing user
        user = self.connection.get_user(USER_WRONG_ID)
        self.assertIsNone(user)

    def test_get_users(self):
        """
        Test that get_users work correctly and extract required user info
        """
        print('('+self.test_get_users.__name__+')', \
              self.test_get_users.__doc__)
        users = self.connection.get_users()
        #Check that the size is correct
        self.assertEqual(len(users), INITIAL_SIZE)
        #Iterate throug users and check if the users with USER1_ID and
        #USER2_ID are correct:
        for user in users:
            if user['userid'] == USER1_ID:
                self.assertDictContainsSubset(USER1, user)
            elif user['userid'] == USER2_ID:
                self.assertDictContainsSubset(USER2, user)

    def test_delete_user(self):
        """
        Test that the user 1 is deleted
        """
        print('('+self.test_delete_user.__name__+')', \
              self.test_delete_user.__doc__)
        resp = self.connection.delete_user(USER1_ID)
        self.assertTrue(resp)
        #Check that the users has been really deleted through a get
        resp2 = self.connection.get_user(USER1_ID)
        self.assertIsNone(resp2)
        #Check that the user does not have associated any reservation
        resp3 = self.connection.get_reservations_by_user(USER1_ID)
        self.assertEqual(len(resp3), 0)

    def test_delete_user_noexistingid(self):
        """
        Test delete_user with 100 (no-existing)
        """
        print('('+self.test_delete_user_noexistingid.__name__+')', \
              self.test_delete_user_noexistingid.__doc__)
        #Test with an existing user
        resp = self.connection.delete_user(USER_WRONG_ID)
        self.assertFalse(resp)

    def test_modify_user(self):
        """
        Test that the user Mystery is modifed
        """
        print('('+self.test_modify_user.__name__+')', \
              self.test_modify_user.__doc__)
        #Get the modified user
        resp = self.connection.modify_user(USER1_ID, MODIFIED_USER1)
        self.assertEqual(resp, USER1_ID)
        #Check that the user has been really modified through a get
        modified_user = self.connection.get_user(USER1_ID)
        #Check the expected values
        self.assertDictContainsSubset(MODIFIED_USER1, modified_user)

    def test_modify_user_noexistingid(self):
        """
        Test modify_user with ID 100 (no-existing)
        """
        print('('+self.test_modify_user_noexistingid.__name__+')', \
              self.test_modify_user_noexistingid.__doc__)
        #Test with an existing user
        resp = self.connection.modify_user(USER_WRONG_ID, MODIFIED_USER1)
        self.assertFalse(resp)

    def test_append_user(self):
        """
        Test that I can add a new user
        """
        print('('+self.test_append_user.__name__+')', \
              self.test_append_user.__doc__)
        new_user_id = self.connection.create_user(NEW_USER)
        self.assertIsNotNone(new_user_id)
        self.assertEqual(new_user_id, NEW_USER_ID)
        #Check that user information are correct
        resp2 = self.connection.get_user(new_user_id)
        self.assertDictContainsSubset(NEW_USER, resp2)

    def test_append_user_existing_email(self):
        """
        Test that I cannot add two users with the same email
        """
        print('('+self.test_append_user_existing_email.__name__+')', \
              self.test_append_user_existing_email.__doc__)
        resp = self.connection.create_user(USER1)
        self.assertIsNone(resp)


    def test_not_contains_user(self):
        """
        Check if the database does not contain user with id 100
        """
        print('('+self.test_not_contains_user.__name__+')', \
              self.test_not_contains_user.__doc__)
        self.assertFalse(self.connection.contains_user(USER_WRONG_ID))

    def test_contains_user(self):
        """
        Check if the database contains users with IDs 1 and 2
        """
        print('('+self.test_contains_user.__name__+')', \
              self.test_contains_user.__doc__)
        self.assertTrue(self.connection.contains_user(USER1_ID))
        self.assertTrue(self.connection.contains_user(USER2_ID))

if __name__ == '__main__':
    print('Start running user tests')
    unittest.main()
