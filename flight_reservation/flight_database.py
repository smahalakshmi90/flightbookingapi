"""
Created on 20.02.2018

Provides the database API to access the flight booking system persistent data.

@author: Mahalakshmy Seetharaman

"""

"""
This code has been wriiten based on forum - exercise 1 
"""
from datetime import datetime
from time import gmtime, strftime
import time, sqlite3, re, os, io
#Default paths for .db and .sql files to create and populate the database.
DEFAULT_DB_PATH = "db/flight.db"
DEFAULT_SCHEMA = "db/flight_schema.sql"
DEFAULT_DATA_DUMP = "db/flight_data_dump.sql"

# Format used for dates
DATE_FORMAT = "%Y-%m-%d"

# Format used for tome
TIME_FORMAT = "%H:%M"

class Engine(object):

    """
    Abstraction of the database.

    It includes tools to create, configure,
    populate and connect to the sqlite file. You can access the Connection
    instance, and hence, to the database interface itself using the method
    :py:meth:`connection`.

    :Example:

    >>> engine = Engine()
    >>> con = engine.connect()

    :param db_path: The path of the database file (always with respect to the
        calling script. If not specified, the Engine will use the file located
        at *db/flight.db*

    """

    def __init__(self, db_path=None):
        """
        """
        super(Engine, self).__init__()
        if db_path is not None:
            self.db_path = db_path
        else:
            self.db_path = DEFAULT_DB_PATH

    def connect(self):
        """
        Creates a connection to the database.

        :return: A Connection instance
        :rtype: Connection

        """
        return Connection(self.db_path)

    def remove_database(self):
        """
        Removes the database file from the filesystem.

        """
        if os.path.exists(self.db_path):
            #THIS REMOVES THE DATABASE STRUCTURE
            os.remove(self.db_path)

    def clear(self):
        """
        Purge the database removing all records from the tables. However,
        it keeps the database schema (meaning the table structure)

        """
        keys_on = 'PRAGMA foreign_keys = ON'
        #THIS KEEPS THE SCHEMA AND REMOVE VALUES
        con = sqlite3.connect(self.db_path)
        #Activate foreing keys support
        cur = con.cursor()
        cur.execute(keys_on)
        with con:
            cur = con.cursor()
            cur.execute("DELETE FROM User")
            cur.execute("DELETE FROM TemplateFlight")
            #NOTE since we have ON DELETE CASCADE BOTH IN Flight, Reservation and Ticket
            #WE DO NOT HAVE TO WORRY TO CLEAR THOSE TABLES.

    #METHODS TO CREATE AND POPULATE A DATABASE USING DIFFERENT SCRIPTS
    def create_tables(self, schema=None):
        """
        Create programmatically the tables from a schema file.

        :param schema: path to the .sql schema file. If this parmeter is
            None, then *db/flight_schema.sql* is utilized.

        """
        con = sqlite3.connect(self.db_path)
        #Database created from schema
        if schema is None:
            schema = DEFAULT_SCHEMA
        try:
            with io.open(schema, encoding="utf-8") as f:
                sql = f.read()
                cur = con.cursor()
                cur.executescript(sql)
        finally:
            con.close()

    def populate_tables(self, dump=None):
        """
        Populate programmatically the tables from a dump file.

        :param dump:  path to the .sql dump file. If this parmeter is
            None, then *db/forum_data_dump.sql* is utilized.

        """
        keys_on = 'PRAGMA foreign_keys = ON'
        con = sqlite3.connect(self.db_path)
        #Activate foreign keys support
        cur = con.cursor()
        cur.execute(keys_on)
        #Populate database from data dump
        if dump is None:
            dump = DEFAULT_DATA_DUMP
        with io.open (dump, encoding="utf-8") as f:
            sql = f.read()
            cur = con.cursor()
            cur.executescript(sql)

    #METHODS TO CREATE THE TABLES PROGRAMMATICALLY WITHOUT USING SQL SCRIPT
    def create_user_table(self):
        """
        Create the table ``User`` programmatically, without using .sql file.

        Print an error message in the console if it could not be created.

        :return: ``True`` if the table was successfully created or ``False``
            otherwise.

        """
        keys_on = 'PRAGMA foreign_keys = ON'
        stmnt = 'CREATE TABLE User(user_id INTEGER NOT NULL PRIMARY KEY, \
                    lastName TEXT,\
                    firstName TEXT, \
                    phoneNumber TEXT, \
                    email TEXT, \
                    birthDate TEXT, \
                    gender TEXT, \
                    registrationDate INTEGER, \
                    UNIQUE(user_id))'
        #Connects to the database. Gets a connection object
        con = sqlite3.connect(self.db_path)
        with con:
            #Get the cursor object.
            #It allows to execute SQL code and traverse the result set
            cur = con.cursor()
            try:
                cur.execute(keys_on)
                #execute the statement
                cur.execute(stmnt)
            except sqlite3.Error as excp:
                print("Error %s:" % excp.args[0])
                return False
        return True

    def create_templateflights_table(self):
        """
        Create the table ``TemplateFlight`` programmatically, without using .sql file.

        Print an error message in the console if it could not be created.

        :return: ``True`` if the table was successfully created or ``False``
            otherwise.
        """
        keys_on = 'PRAGMA foreign_keys = ON'
        stmnt = 'CREATE TABLE TemplateFlight(tflight_id INTEGER NOT NULL UNIQUE PRIMARY KEY,\
                                depTime INTEGER,\
                                arrTime INTEGER,\
                                origin TEXT,\
                                destination TEXT)'
        #Connects to the database. Gets a connection object
        con = sqlite3.connect(self.db_path)
        with con:
            #Get the cursor object.
            #It allows to execute SQL code and traverse the result set
            cur = con.cursor()
            try:
                cur.execute(keys_on)
                #execute the statement
                cur.execute(stmnt)
            except sqlite3.Error as excp:
                print("Error %s:" % excp.args[0])
                return False
        return True

    def create_flight_table(self):
        """
        Create the table ``Flight`` programmatically, without using .sql file.

        Print an error message in the console if it could not be created.

        :return: ``True`` if the table was successfully created or ``False``
            otherwise.
        """
        keys_on = 'PRAGMA foreign_keys = ON'
        stmnt = 'CREATE TABLE Flight(flight_id INTEGER NOT NULL UNIQUE PRIMARY KEY, \
                                code TEXT UNIQUE,\
                                gate TEXT,\
                                price INTEGER, \
                                depDate TEXT,\
                                arrDate TEXT,\
                                nbInitialSeats INTEGER,\
                                nbSeatsLeft INTEGER,\
                                template_id INTEGER NOT NULL,\
                                FOREIGN KEY(template_id) REFERENCES  TemplateFlight(tflight_id) ON DELETE CASCADE)'
        #Connects to the database. Gets a connection object
        con = sqlite3.connect(self.db_path)
        with con:
            #Get the cursor object.
            #It allows to execute SQL code and traverse the result set
            cur = con.cursor()
            try:
                cur.execute(keys_on)
                #execute the statement
                cur.execute(stmnt)
            except sqlite3.Error as excp:
                print("Error %s:" % excp.args[0])
                return False
        return True


    def create_reservation_table(self):
        """
        Create the table ``Reservation`` programmatically, without using .sql file.

        Print an error message in the console if it could not be created.

        :return: ``True`` if the table was successfully created or ``False``
            otherwise.

        """
        keys_on = 'PRAGMA foreign_keys = ON'
        stmnt = 'CREATE TABLE Reservation(reservation_id INTEGER NOT NULL UNIQUE PRIMARY KEY,\
                                    reference TEXT UNIQUE, \
                                    re_date TEXT,\
                                    creator_id INTEGER NOT NULL, \
                                    flight_id INTEGER NOT NULL,\
                                    FOREIGN KEY(flight_id) REFERENCES  Flight(flight_id) ON DELETE CASCADE,\
                                    FOREIGN KEY(creator_id) REFERENCES  User(user_id) ON DELETE CASCADE)'
        #Connects to the database. Gets a connection object
        con = sqlite3.connect(self.db_path)
        with con:
            #Get the cursor object.
            #It allows to execute SQL code and traverse the result set
            cur = con.cursor()
            try:
                cur.execute(keys_on)
                #execute the statement
                cur.execute(stmnt)
            except sqlite3.Error as excp:
                print("Error %s:" % excp.args[0])
                return False
        return True

    def create_ticket_table(self):
        """
        Create the table ``Ticket`` programmatically, without using
        .sql file.

        Print an error message in the console if it could not be created.

        :return: ``True`` if the table was successfully created or ``False``
            otherwise.

        """
        keys_on = 'PRAGMA foreign_keys = ON'
        stmnt = 'CREATE TABLE Ticket(ticket_id INTEGER NOT NULL UNIQUE PRIMARY KEY,\
                                    firstName TEXT, \
                                    lastName TEXT, \
                                    gender TEXT, \
                                    age INTEGER, \
                                    reservation_id INTEGER NOT NULL, \
                                    seat TEXT, \
                                    FOREIGN KEY(reservation_id) REFERENCES Reservation(reservation_id) ON DELETE CASCADE)'
        
        #Connects to the database. Gets a connection object
        con = sqlite3.connect(self.db_path)
        with con:
            #Get the cursor object.
            #It allows to execute SQL code and traverse the result set
            cur = con.cursor()
            try:
                cur.execute(keys_on)
                #execute the statement
                cur.execute(stmnt)
            except sqlite3.Error as excp:
                print("Error %s:" % excp.args[0])
                return False
        return True
        
        
class Connection(object):
    """
    API to access the Flight Booking database.

    The sqlite3 connection instance is accessible to all the methods of this
    class through the :py:attr:`self.con` attribute.

    An instance of this class should not be instantiated directly using the
    constructor. Instead use the :py:meth:`Engine.connect`.

    Use the method :py:meth:`close` in order to close a connection.
    A :py:class:`Connection` **MUST** always be closed once when it is not going to be
    utilized anymore in order to release internal locks.

    :param db_path: Location of the database file.
    :type dbpath: str

    """
    def __init__(self, db_path):
        super(Connection, self).__init__()
        self.con = sqlite3.connect(db_path)

    def close(self):
        """
        Closes the database connection, commiting all changes.

        """
        if self.con:
            self.con.commit()
            self.con.close()

    #FOREIGN KEY STATUS
    def check_foreign_keys_status(self):
        """
        Check if the foreign keys has been activated.

        :return: ``True`` if  foreign_keys is activated and ``False`` otherwise.
        :raises sqlite3.Error: when a sqlite3 error happen. In this case the
            connection is closed.

        """
        try:
            #Create a cursor to receive the database values
            cur = self.con.cursor()
            #Execute the pragma command
            cur.execute('PRAGMA foreign_keys')
            #We know we retrieve just one record: use fetchone()
            data = cur.fetchone()
            is_activated = data == (1,)
            print("Foreign Keys status: %s" % 'ON' if is_activated else 'OFF')
        except sqlite3.Error as excp:
            print("Error %s:" % excp.args[0])
            self.close()
            raise excp
        return is_activated

    def set_foreign_keys_support(self):
        """
        Activate the support for foreign keys.

        :return: ``True`` if operation succeed and ``False`` otherwise.

        """
        keys_on = 'PRAGMA foreign_keys = ON'
        try:
            #Get the cursor object.
            #It allows to execute SQL code and traverse the result set
            cur = self.con.cursor()
            #execute the pragma command, ON
            cur.execute(keys_on)
            return True
        except sqlite3.Error as excp:
            print("Error %s:" % excp.args[0])
            return False

    def unset_foreign_keys_support(self):
        """
        Deactivate the support for foreign keys.

        :return: ``True`` if operation succeed and ``False`` otherwise.

        """
        keys_on = 'PRAGMA foreign_keys = OFF'
        try:
            #Get the cursor object.
            #It allows to execute SQL code and traverse the result set
            cur = self.con.cursor()
            #execute the pragma command, OFF
            cur.execute(keys_on)
            return True
        except sqlite3.Error as excp:
            print("Error %s:" % excp.args[0])
            return False

    #HELPERS
    #Here the helpers that transform database rows into dictionary. They work
    #similarly to ORM

    #Helper for User
    def _create_user_object(self, row):
        """
        It takes a :py:class:`sqlite3.Row` and transform it into a dictionary.
        The resulting dictionary is targeted to build a user

        :param row: The row obtained from the database.
        :type row: sqlite3.Row
        :return: a dictionary containing the following keys:

            * ``userid``: user id for an user (INT)
            * ``lastname``: lastname of the user (TEXT)
            * ``firstname``: firstname of the user (TEXT)
            * ``phonenumber``: user's phone number (INT)
            * ``email``: user's email address (TEXT)
            * ``dateofBirth``: date of birth of the user (TEXT)
            * ``gender``: user's gender (TEXT)
            * ``registrationDate``: date of user registration (INT)

            Note that all values in the returned dictionary are string unless
            otherwise stated.

        """
        userid = 'user-' + str(row['user_id']) 
        lastname =row['lastName']
        firstname = row['firstName']
        phonenumber = row['phoneNumber'] 
        email = row['email'] 
        dateofBirth = row['birthDate']
        gender = row['gender'] 
        registrationDate = row['registrationDate']

        user = {'userid': userid,
                'lastname': lastname,
                'firstname': firstname,
                'phonenumber': phonenumber,
                'email': email,
                'dateofBirth': dateofBirth,
                'gender': gender,
                'registrationDate': registrationDate}

        return user
               
    def _create_user_list_object(self, row):
        """
        It takes a database Row and transform it into a python dictionary.
        The resulting dictionary is targeted to build a users in a list.

        :param row: The row obtained from the database.
        :type row: sqlite3.Row
        :return: a dictionary containing the following keys:

            * ``userid``: user id for an user (INT)
            * ``lastname``: lastname of the user (TEXT)
            * ``firstname``: firstname of the user (TEXT)
            * ``registrationDate``: date of user registration (INT)
            

            Note that all values in the returned dictionary are string unless
            otherwise stated.

        """
        return { 'userid': 'user-' + str(row['user_id']),
                'firstname': row['firstName'],
                'lastname': row['lastName'],
                'registrationdate': row['registrationDate']}

    #Helper for Reservation
    def _create_reservation_object(self, row):
        """
        It takes a database Row and transform it into a python dictionary.
        The resulting dictionary is targeted to build a reservation.

        :param row: The row obtained from the database.
        :type row: sqlite3.Row
        :return: a dictionary containing the following keys:

            * ``reservationid``: reservation id for a reservation (INT)
            * ``reference``: reference for a reservation (TEXT)
            * ``reservationdate``: date of reservation (TEXT)
            * ``userid``: id of the user making a reservation (INT)
            * ``flightid``: flightid for which reservation is made (INT)
            

            Note that all values in the returned dictionary are string unless
            otherwise stated.     
        """
        reservation_id = row['reservation_id']
        reference = row['reference']
        reservation_date = row['re_date']
        creator_id = row['creator_id']
        flight_id = row['flight_id']
        reservation = {'reservationid': reservation_id,
                       'reference': reference,
                       'reservationdate' : reservation_date,
                       'userid' : creator_id,
                       'flightid': flight_id}
        return reservation

    #Helper for Flight
    def _create_flight_object(self, row):
        """
        It takes a database Row and transform it into a python dictionary.
        The resulting dictionary is targeted to build a flight.

        :param row: The row obtained from the database.
        :type row: sqlite3.Row
        :return: a dictionary containing the following keys:

            * ``searchresultid``: id of entered travel details (INT)
            * ``flightid``: id of a flight (INT)
            * ``code``: reference for a reservation (TEXT)
            * ``price``: date of reservation (INT)
            * ``departuredate``: flight departure date (TEXT)
            * ``arrivaldate``: flight arrival date (TEXT)
            * ``gate``: gate number (TEXT)
            * ``totalseats``: total number of seats in the flight(INT)
            * ``seatsleft``: number seats vacant (INT)
            
            Note that all values in the returned dictionary are string unless
            otherwise stated.
        """
        result_id = row['template_id']
        flight_id = row['flight_id']
        code = row['code']
        price = row ['price']
        departure_date = row['depDate']
        arrival_date =row['arrDate']
        gate = row['gate']
        total_seats =row['nbInitialSeats']
        seats_left =row['nbSeatsLeft']

        flight = {'searchresultid': result_id ,
                  'flightid':flight_id ,
                  'code': code,
                  'price': price,
                  'departuredate':departure_date,
                  'arrivaldate':arrival_date,
                  'gate':gate ,
                  'totalseats':total_seats,
                  'seatsleft':seats_left}
        return flight

    #Helper for Template Flight
    def _create_template_flight_object(self, row):

        """
        It takes a database Row and transform it into a python dictionary.
        The resulting dictionary is targeted to build a template flight.

        :param row: The row obtained from the database.
        :type row: sqlite3.Row
        :return: a dictionary containing the following keys:

            * ``searchid``: id of entered travel details (INT)
            * ``origin`: travel from (TEXT)
            * ``destination``: travel to (TEXT)
            * ``departuretime``: intended departure time (INT)
            * ``arrivaltime``: intended arrival time (INT)
            
            Note that all values in the returned dictionary are string unless
            otherwise stated.

        """
        tflight_id ='search' +str(row['tFlight_id'])
        origin = row['origin']
        destination = row['destination']
        dep_time = row['deptime']
        arr_time=row['arrTime']
        

        templateflight = {'searchid': tflight_id,
                          'origin': origin,
                          'destination': destination,
                          'departuretime': dep_time,
                          'arrivaltime': arr_time }
        return templateflight

    #Helper for Ticket
    def _create_ticket_object(self, row):
        """
        It takes a :py:class:`sqlite3.Row` and transform it into a dictionary.
        The resulting dictionary is targeted to build a ticket.

        :param row: The row obtained from the database.
        :type row: sqlite3.Row
        :return: a dictionary containing the following keys:

            * ``ticketnumber``: user id for an user (INT)
            * ``reservationid``: reservation id of a reservation (INT)
            * ``lastname``: lastname of the passenger (TEXT)
            * ``firstname``: firstname of the passenger (TEXT)
            * ``gender``: passenger's gender (TEXT)
            * ``age``: passenger's age(INT)
            * ``seat``: seatnumber (INT)
            
            Note that all values in the returned dictionary are string unless
            otherwise stated.
        """
        ticket_id ='ticketnum-' + str( row['ticket_id'])
        reservation_id = row['reservation_id']
        firstname = row['firstName']
        lastname =row['lastName']
        gender = row['gender']
        age = row['age']
        seat = row['seat']
        

        ticket = {'ticketnumber': ticket_id,
                  'reservationid': reservation_id,
                  'firstname': firstname,
                  'lastname': lastname,
                  'gender': gender,
                  'age':age,
                  'seat':seat}

        return ticket

    #API ITSELF

    #User Table API
    def get_user(self, user_id):
        """
        Extracts all the information of a user from the database.

        :param user_id: The id of the user. 
                        The user_id is a string with format ``user-\d{1,3}``.
        :return: dictionary with the format provided in the method:
            :py:meth:`_create_user_object`

        """
        #SQL Statement for retrieving the user information for given userid
        query = 'SELECT * from User WHERE user_id = ?'
    
        #Activate foreign key support
        self.set_foreign_keys_support()
        #Cursor and row initialization
        self.con.row_factory = sqlite3.Row
        cur = self.con.cursor()
        # Execute the SQL Statement to retrieve the user information.
        # Create first the valuse
        pvalue = (user_id, )
        #execute the statement
        cur.execute(query, pvalue)
        #Process the response. Only one posible row is expected.
        row = cur.fetchone()
        if row is None:
            return None
        else:
            return self._create_user_object(row)
    

    def get_users(self):
        """
        Extracts all users in the database.

        :return: list of Users of the database. 
        None is returned if the database has no users.
        """
        #Create the SQL Statement for retrieving the users
        query = 'SELECT * FROM User'
        #Activate foreign key support
        self.set_foreign_keys_support()
        #Create the cursor
        self.con.row_factory = sqlite3.Row
        cur = self.con.cursor()
        #Execute main SQL Statement
        cur.execute(query)
        #Process the results
        rows = cur.fetchall()
        if rows is None:
            return None
        #Process the response.
        users = []
        for row in rows:
            users.append(self._create_user_list_object(row))
        return users

    def create_user(self, user):
        """
        Create a new user in the database.

        :param dict user: a dictionary for user with the information to be created. The
                dictionary has the following structure:

                .. code-block:: javascript

                    user = {'lastname': lastname,
                            'firstname': firstname,
                            'phonenumber': phonenumber,
                            'email': email,
                            'dateofBirth': dateofBirth,
                            'gender': gender,
                            'registrationDate': registrationDate}
                    

                where:

                
                    * ``userid``: user id for an user (INT)
                    * ``lastname``: lastname of the user (TEXT)
                    * ``firstname``: firstname of the user (TEXT)
                    * ``phonenumber``: user's phone number (INT)
                    * ``email``: user's email address (TEXT)
                    * ``dateofBirth``: date of birth of the user (TEXT)
                    * ``gender``: user's gender (TEXT)
                    * ``registrationDate``: date of user registration (INT)

        Note that all values are string if they are not otherwise indicated.

        :return: True when user is created
        :raises ValueError when the birth date is not well formed
        """
        
        #SQL Statement to create the row in  users table
        #SQL Statement to check if the user already exists using email
        query1 = 'SELECT * from User WHERE email = ?'
        #SQL Statement to add values to new row
        query2 = 'INSERT INTO User (lastName, firstName, phoneNumber, email, birthDate, gender, registrationDate)\
                  VALUES(?,?,?,?,?,?,?)'
                  
        #temporal variables for user table
        #timestamp will be used for lastlogin and regDate.
        timestamp = time.mktime(datetime.now().timetuple())
        lastName = user.get('lastname', None)
        firstName = user.get('firstname', None)
        phoneNumber = user.get('phonenumber', None)
        email = user.get('email', None)
        birthDate = user.get('dateofBirth', None)
        gender = user.get('gender', None)
        registrationDate = user.get('registrationDate', None)

        # Check birth date format
        try:
            datetime.strptime(birthDate, DATE_FORMAT)
        except ValueError:
            raise ValueError("Birth date format is incorrect")

        #Activate foreign key support
        self.set_foreign_keys_support()
        #Cursor and row initialization
        self.con.row_factory = sqlite3.Row
        cur = self.con.cursor()
        
        #Execute the statement to check whether the a user with same email exists
        pvalue =(email,)
        cur.execute(query1, pvalue) 
          
        #No value expected (no other user with that email expected)
        row = cur.fetchone()
        #If there is no user add rows in User
        if row is None:
            #Add the row in User table
            # Execute the statement
            pvalue = (lastName, firstName, phoneNumber, email, birthDate, gender, timestamp)
            cur.execute(query2, pvalue)
            self.con.commit()
            return cur.lastrowid
        else:
            return None

    def modify_user(self, user_id, user):
        """
        Modify the information of a user.

        :param user_id: The id of the user. 
                        The user_id is a string with format ``user-\d{1,3}``.
        :param dict user: a dictionary for user with the information to be created. The
                dictionary has the following structure:

                .. code-block:: javascript

                    user = {'lastname': lastname,
                            'firstname': firstname,
                            'phonenumber': phonenumber,
                            'email': email,
                            'dateofBirth': dateofBirth,
                            'gender': gender,
                            'registrationDate': registrationDate}
                    
                where:
                
                    * ``userid``: user id for an user (INT)
                    * ``lastname``: lastname of the user (TEXT)
                    * ``firstname``: firstname of the user (TEXT)
                    * ``phonenumber``: user's phone number (INT)
                    * ``email``: user's email address (TEXT)
                    * ``dateofBirth``: date of birth of the user (TEXT)
                    * ``gender``: user's gender (TEXT)
                    * ``registrationDate``: date of user registration (INT)

        Note that all values are string if they are not otherwise indicated.

        :return: True when user is modified or False is the user_id does not exist
        """
        #Create the SQL Statements
        #SQL Statement for extracting the User using user_id
        query1 = 'SELECT * from User WHERE user_id = ?'
           
        query2 = 'UPDATE User SET lastName = ?,firstName = ?, \
                                           phoneNumber = ?,email = ?, \
                                           birthDate = ?,gender = ?\
                                           WHERE user_id = ?'
        
        firstName = user.get('firstname', None)
        lastName = user.get('lastname', None)
        phoneNumber = user.get('phonenumber', None)
        email = user.get('email', None)
        birthDate = user.get('dateofBirth', None)
        gender = user.get('gender', None)

        # Check birth date format
        try:
            datetime.strptime(birthDate, DATE_FORMAT)
        except ValueError:
            raise ValueError("Birth date format is incorrect")

        #Activate foreign key support
        self.set_foreign_keys_support()
        #Cursor and row initialization
        self.con.row_factory = sqlite3.Row
        cur = self.con.cursor()
        #Execute the statement associated to a user_id
        pvalue = (user_id,)
        cur.execute(query1, pvalue)
        #Only one value expected
        row = cur.fetchone()
        #if does not exist, return
        if row is None:
            return False 
        else:
            #execute the main statement
            pvalue = (lastName, firstName, phoneNumber, email, birthDate, gender, user_id)
            cur.execute(query2, pvalue)
            self.con.commit()
            #Check that if the user has been modified
            if cur.rowcount < 1:
                return None
            return True

    def delete_user(self, user_id):
        """
        Remove all user information of the user with the user_id passed in as
        argument.

        :param user_id: The id of the user. 
                        The user_id is a string with format ``user-\d{1,3}``.

        :return: True if the user is deleted, False otherwise.

        """
        #Create the SQL Statements
          #SQL Statement for deleting the user information
        query = 'DELETE FROM User WHERE user_id = ?'
        #Activate foreign key support
        self.set_foreign_keys_support()
        #Cursor and row initialization
        self.con.row_factory = sqlite3.Row
        cur = self.con.cursor()
        #Execute the statement to delete
        pvalue = (user_id,)
        cur.execute(query, pvalue)
        self.con.commit()
        #Check that if the user has been deleted
        if cur.rowcount < 1:
            return False
        return True

    def contains_user(self, user_id):
        """
        :param user_id: The id of the user. 
                        The user_id is a string with format ``user-\d{1,3}``.
        :return: True if the user is in the database. False otherwise
        """
        return self.get_user(user_id) is not None

    #TemplateFlight Table API
    def get_template_flight(self, tflight_id):
        """
        Extracts all the information of a templateflight from the database.

        :param tflight_id: The id of the templateflight. 
                        The tflight_id is a string with format ``search-\d{1,4}``.
        :return: dictionary with the format provided in the method:
            :py:meth:`_create_template_flight_object`
        """

        #SQL Statement for retrieving the template information for given tflight_id
        query = 'SELECT * from TemplateFlight WHERE tflight_id = ?'
    
        #Activate foreign key support
        self.set_foreign_keys_support()
        #Cursor and row initialization
        self.con.row_factory = sqlite3.Row
        cur = self.con.cursor()
        # Execute the SQL Statement to retrieve the template flight information.
        # Create first the valuse
        pvalue = (tflight_id, )
        #execute the statement
        cur.execute(query, pvalue)
        #Process the response. Only one posible row is expected.
        row = cur.fetchone()
        if row is None:
            return None
        else:
            return self._create_template_flight_object(row)

    def create_template_flight(self, templateflight):
        """
        Create a new templateflight in the database.

        :param dict user: a dictionary for a templateflight with the information to be created. The
                dictionary has the following structure:

                .. code-block:: javascript

                    templateflight = {'searchid': tflight_id,
                                        'origin': origin,
                                        'destination': destination,
                                        'departuretime': dep_time,
                                        'arrivaltime': arr_time }
                    

                where:     
                * ``searchid``: id of entered travel details (INT)
                * ``origin`: travel from (TEXT)
                * ``destination``: travel to (TEXT)
                * ``departuretime``: intended departure time (INT)
                * ``arrivaltime``: intended arrival time (INT)
        Note that all values are string if they are not otherwise indicated.

        :return: True when templateflight is created 
        """
        query1 = 'SELECT * from TemplateFlight WHERE tflight_id = ?'
        query2 = 'INSERT INTO TemplateFlight (tflight_id, depTime, arrTime, origin, destination)\
                  VALUES(?,?,?,?,?)'

        tflight_id = templateflight.get('searchid', None)
        origin = templateflight.get('origin', None)
        destination = templateflight.get('destination', None)
        depTime = templateflight.get('departuretime', None)
        arrTime = templateflight.get('arrivaltime', None)


        #Activate foreign key support
        self.set_foreign_keys_support()
        #Cursor and row initialization
        self.con.row_factory = sqlite3.Row
        cur = self.con.cursor()
        
        #Execute the statement to check is the template flight exists
        pvalue =(tflight_id,)
        cur.execute(query1, pvalue) 
          
        #No value expected 
        row = cur.fetchone()
        #If there is no templateflight add rows in TemplateFlight
        if row is None:
            #Add the row 
            # Execute the statement
            pvalue = (tflight_id, depTime, arrTime, origin, destination)
            cur.execute(query2, pvalue)
            self.con.commit()
            return cur.lastrowid
        else:
            return None

    def modify_template_flight(self, tflight_id, templateflight):
        """
        Modify the information of a templateflight.

        :param tflight_id: The id of the templateflight. 
                        The tflight_id is a string with format ``search-\d{1,4}``.
        :param dict user: a dictionary for user with the information to be created.
                          tflight_id must be given in order to make modifications. 
                          The dictionary has the following structure:

                .. code-block:: javascript

                    templateflight = { 'origin': origin,
                                        'destination': destination,
                                        'departuretime': dep_time,
                                        'arrivaltime': arr_time }
                    

                where:     
                * ``origin`: travel from (TEXT)
                * ``destination``: travel to (TEXT)
                * ``departuretime``: intended departure time (INT)
                * ``arrivaltime``: intended arrival time (INT)

        Note that all values are string if they are not otherwise indicated.

        :return: True when templateflight is modified or False is the tflight_id does not exist
        """
        #SQL statement for template flight existence and modifications
        query1 = 'SELECT * from TemplateFlight WHERE tflight_id = ?'
           
        query2 = 'UPDATE TemplateFlight SET depTime = ?, arrTime = ?, origin = ?, destination  = ? \
                                           WHERE tflight_id = ?' 
        #temporal variables
        origin = templateflight.get('origin', None)
        destination = templateflight.get('destination', None)
        depTime = templateflight.get('departuretime', None)
        arrTime = templateflight.get('arrivaltime', None)
        #Activate foreign key support
        self.set_foreign_keys_support()
        #Cursor and row initialization
        self.con.row_factory = sqlite3.Row
        cur = self.con.cursor()
        #Execute the statement 
        pvalue = (tflight_id,)
        cur.execute(query1, pvalue)
        #Only one value expected
        row = cur.fetchone()
        #if does not exist, return
        if row is None:
            return False
        else:
            #execute the main statement
            pvalue = (depTime, arrTime, origin, destination, tflight_id)
            cur.execute(query2, pvalue)
            self.con.commit()
            #Check that if the templateflight is modified
            if cur.rowcount < 1:
                return None
            return True

    def delete_template_flight(self, tflight_id):
        """
        Remove all templateflight information with the tflight_id passed in as
        argument.

        :param tflight_id: The id of the templateflight. 
                        The tflight_id is a string with format ``search-\d{1,4}``.

        :return: True if the template flight is deleted, False otherwise.
        """

        #Create the SQL Statements
        #SQL Statement for deleting template flight information
        query = 'DELETE FROM TemplateFlight WHERE tflight_id = ?'
        #Activate foreign key support
        self.set_foreign_keys_support()
        #Cursor and row initialization
        self.con.row_factory = sqlite3.Row
        cur = self.con.cursor()
        #Execute the statement to delete
        pvalue = (tflight_id,)
        cur.execute(query, pvalue)
        self.con.commit()
        #Check that template flight has been deleted
        if cur.rowcount < 1:
            return False
        return True

    def contains_template_flight(self, tflight_id):
        """
        :param tflight_id: The id of the templateflight. 
                        The tflight_id is a string with format ``search-\d{1,4}``.
        :return: True if the templateflight is in the database. False otherwise
        """
        return self.get_template_flight(tflight_id) is not None

    #Flight Table API
    def get_flight(self, flight_id):
        """
        Extracts all the information of a flight from the database using flight_id.

        :param flight_id: The id of the flight. 
                        The flight_id is a string with format ``fl-\d{1,4}``.
        :return: dictionary with the format provided in the method:
            :py:meth:`_create_flight_object`
        """
        #SQL Statement for retrieving the flight information for given flight_id
        query = 'SELECT * from Flight WHERE flight_id = ?'
    
        #Activate foreign key support
        self.set_foreign_keys_support()
        #Cursor and row initialization
        self.con.row_factory = sqlite3.Row
        cur = self.con.cursor()
        # Execute the SQL Statement to retrieve the flight information.
        # Create first the valuse
        pvalue = (flight_id, )
        #execute the statement
        cur.execute(query, pvalue)
        #Process the response. Only one posible row is expected.
        row = cur.fetchone()
        if row is None:
            return None
        else:
            return self._create_flight_object(row)

    def get_flights_by_template(self, template_id):
        """
        Extracts all the information of flights from the database using template_id.

        :param template_id: The id of the templateflight. 
                        The template_id is a string with format ``result-\d{1,4}``.
        :return: dictionary with the format provided in the method:
            :py:meth:`_create_flight_object`
        """
        #SQL Statement for retrieving the flights information for given templateid
        query = 'SELECT * from Flight WHERE template_id = ?'
    
        #Activate foreign key support
        self.set_foreign_keys_support()
        #Cursor and row initialization
        self.con.row_factory = sqlite3.Row
        cur = self.con.cursor()
        # Execute the SQL Statement to retrieve the flights information.
        # Create first the valuse
        pvalue = (template_id, )
        #execute the statement
        cur.execute(query, pvalue)
        #Process the response. 
        rows = cur.fetchall()
        if rows is None:
            return None
        flights = [] 
        for row in rows:
            flights.append(self._create_flight_object(row))
        return flights


    def create_flight(self, flight):
        """
        Create a new flight in the database.

        :param dict flight: a dictionary for flight with the information to be created. The
                dictionary has the following structure:

                .. code-block:: javascript

                    flight = {'searchresultid': result_id ,
                                'flightid':flight_id ,
                                'code': code,
                                'price': price,
                                'departuredate':departure_date,
                                'arrivaldate':arrival_date,
                                'gate':gate ,
                                'totalseats':total_seats,
                                'seatsleft':seats_left}
                where:     
                * ``searchresultid``: id of entered travel details (INT)
                                     The result_id is a string with format ``result-\d{1,4}``.
                * ``flightid``: id of a flight (INT)
                               The flight_id is a string with format ``fl-\d{1,4}``.
                * ``code``: reference for a reservation (TEXT)
                * ``price``: date of reservation (INT)
                * ``departuredate``: flight departure date (TEXT)
                * ``arrivaldate``: flight arrival date (TEXT)
                * ``gate``: gate number (TEXT)
                * ``totalseats``: total number of seats in the flight(INT)
                * ``seatsleft``: number seats vacant (INT)
        Note that all values are string if they are not otherwise indicated.

        :return: True when flight is created
        :raises ValueError when the gate name is not well formed
        """

        query1 = 'SELECT * from Flight WHERE flight_id = ?'
        query2 = 'INSERT INTO Flight (flight_id, code, price, gate, depDate, arrDate, nbInitialSeats, nbSeatsLeft, template_id)\
                  VALUES(?,?,?,?,?,?,?,?,?)'
        #Extract information from the parameter passed

        flight_id = flight.get('flightid', None)
        template_id = flight.get('searchresultid', None)
        code = flight.get('code', None)
        gate = flight.get('gate', None)
        price = flight.get('price', None)
        depDate = flight.get('departuredate', None)
        arrDate = flight.get('arrivaldate', None)
        nbInitialSeats = flight.get('totalseats', None)
        nbSeatsLeft = flight.get('seatsleft', None)

        gate_pattern = re.compile("GATE\d{2}")
        if not gate_pattern.match(gate):
            raise ValueError("Gate is not well formed")
        
        #Activate foreign key support
        self.set_foreign_keys_support()
        #Cursor and row initialization
        self.con.row_factory = sqlite3.Row
        cur = self.con.cursor()
        
        #Execute the statement to check if a flight with same id exists
        pvalue =(flight_id,)
        cur.execute(query1, pvalue) 
          
        #No value expected 
        row = cur.fetchone()
        #If there is no flight add rows in Flight
        if row is None:
            # Execute the statement
            pvalue = (flight_id, code, price, gate, depDate, arrDate, nbInitialSeats, nbSeatsLeft, template_id)
            try:
                cur.execute(query2, pvalue)
            except sqlite3.IntegrityError:
                return None
            self.con.commit()
            return cur.lastrowid
        else:
            return None

    def modify_flight(self, flight_id, flight):
        """
        Modify the information of a flight.

        :param flight_id: The id of the flight. 
                        The flight_id is a string with format ``fl-\d{1,4}``.
        :param dict flight: a dictionary for user with the information to be created.
                          flight_id must be given in order to make modifications. 
                          The dictionary has the following structure:

                .. code-block:: javascript

                    flight = {'searchresultid': result_id ,
                                'code': code,
                                'price': price,
                                'departuredate':departure_date,
                                'arrivaldate':arrival_date,
                                'gate':gate ,
                                'totalseats':total_seats,
                                'seatsleft':seats_left}
                where:     
                * ``searchresultid``: id of entered travel details (INT)
                                    The result_id is a string with format ``result-\d{1,4}``.
                * ``code``: reference for a reservation (TEXT)
                * ``price``: date of reservation (INT)
                * ``departuredate``: flight departure date (TEXT)
                * ``arrivaldate``: flight arrival date (TEXT)
                * ``gate``: gate number (TEXT)
                * ``totalseats``: total number of seats in the flight(INT)
                * ``seatsleft``: number seats vacant (INT)
        Note that all values are string if they are not otherwise indicated.

        :return: True when flight is modified or False is the flight_id does not exist
        """
        query1 = 'SELECT * from Flight WHERE flight_id = ?'
           
        query2 = 'UPDATE Flight SET code = ?, price = ?, gate = ?, depDate = ?, \
                                        arrDate = ?, nbInitialSeats = ?, nbSeatsLeft = ?, template_id = ? \
                                           WHERE flight_id = ?' 
        #Extract information from the parameter passed
        template_id = flight.get('searchresultid')
        code = flight.get('code', None)
        gate = flight.get('gate', None)
        price = flight.get('price', None)
        depDate = flight.get('departuredate', None)
        arrDate = flight.get('arrivaldate', None)
        nbInitialSeats = flight.get('totalseats', None)
        nbSeatsLeft = flight.get('seatsleft', None)

        # Check that gate format is incorrect
        pattern = re.compile("GATE\d{2}")
        if not pattern.match(gate):
            raise ValueError("Gate format is incorrect")


        #Activate foreign key support
        self.set_foreign_keys_support()
        #Cursor and row initialization
        self.con.row_factory = sqlite3.Row
        cur = self.con.cursor()
        #Execute the statement to check if the flight exists
        pvalue = (flight_id,)
        cur.execute(query1, pvalue)
        #Only one value expected
        row = cur.fetchone()
        #if does not exist, return
        if row is None:
            return False
        else:
            #execute the main statement
            pvalue = (code, price, gate, depDate, arrDate, nbInitialSeats, nbSeatsLeft, template_id, flight_id)
            cur.execute(query2, pvalue)
            self.con.commit()
            #Check that if the flight is modified.
            if cur.rowcount < 1:
                return None
            return True

    def delete_flight(self, flight_id):
        """
        Remove all flight information of a flight with the flight_id passed in as
        argument.

        :param tflight_id: The id of the templateflight. 
                        The tflight_id is a string with format ``fl\d{1,4}``.
        :return: True if the flight is deleted, False otherwise.
        """
        #Create the SQL Statements
          #SQL Statement for deleting a flight information
        query = 'DELETE FROM Flight WHERE flight_id = ?'
        #Activate foreign key support
        self.set_foreign_keys_support()
        #Cursor and row initialization
        self.con.row_factory = sqlite3.Row
        cur = self.con.cursor()
        #Execute the statement to delete
        pvalue = (flight_id,)
        cur.execute(query, pvalue)
        self.con.commit()
        #Check that if the flight has been deleted
        if cur.rowcount < 1:
            return False
        return True

    def contains_flight(self, flight_id):
        """
        :param flight_id: The id of the flight. 
                        The flight_id is a string with format ``fl-\d{1,4}``.
        :return: True if the flight is in the database. False otherwise
        """
        return self.get_flight(flight_id) is not None

    #Reservation Table API
    def get_reservation(self, reservation_id):
        """
        Extracts all the information of a reservation from the database.

        :param reservation_id: The id of the reservation. 
                        The reservation_id is a string with format ``res-\d{1,2}``.
        :return: dictionary with the format provided in the method:
            :py:meth:`_create_reservation_object`
        """
        #Create the SQL Statements for retrieving information of a reservation
        query = 'SELECT * FROM Reservation WHERE reservation_id = ?'
        #Activate foreign key support
        self.set_foreign_keys_support()
        #Create the cursor
        self.con.row_factory = sqlite3.Row
        cur = self.con.cursor()
        #Execute main SQL Statement
        pvalue = (reservation_id,)
        cur.execute(query, pvalue)
        #Process the result
        self.con.commit()
        row = cur.fetchone()
        if row is None:
            return None
        else:
            return self._create_reservation_object(row)

    def get_reservation_list(self):
        """
        Extracts all the information of the reservations from the database.

        :return: dictionary with the format provided in the method:
            :py:meth:`_create_reservation_object`
        """
        #Create the SQL Statements for retrieving information of the reservations
        query = 'SELECT * FROM Reservation'
        #Activate foreign key support
        self.set_foreign_keys_support()
        #Create the cursor
        self.con.row_factory = sqlite3.Row
        cur = self.con.cursor()
        #Execute main SQL Statement
        cur.execute(query)
        rows = cur.fetchall()
        #Process the result
        if rows is None:
            return None
        reservations = []
        for row in rows:
            reservations.append(self._create_reservation_object(row))
        return reservations

    def get_reservations_by_user(self, creator_id):
        """

        Extracts all the information of a reservation from the database of a particular user.

        :param creator_id: The id of the user. 
                        The creator_id is a string with format ``bookedby-\d{1,3}``.
        :return: dictionary with the format provided in the method:
            :py:meth:`_create_reservation_object`
        """
        #Create the SQL Statements for retrieving information of the reservations
        query = 'SELECT * FROM Reservation WHERE creator_id = ?'
        #Activate foreign key support
        self.set_foreign_keys_support()
        #Create the cursor
        self.con.row_factory = sqlite3.Row
        cur = self.con.cursor()
        #Execute main SQL Statement
        pvalue = (creator_id,)
        cur.execute(query, pvalue)
        self.con.commit()
        rows = cur.fetchall()
        #Process the result
        if rows is None:
            return None
        reservations_user = []
        for row in rows:
            reservations_user.append(self._create_reservation_object(row))
        return reservations_user

    def get_reservations_by_flight(self, flight_id):
        """
        Extracts all the information of a reservation from the database of a particular flight.

        :param flight_id: The id of the flight. 
                        The flight_id is a string with format ``fl-\d{1,4}``.
        :return: dictionary with the format provided in the method:
            :py:meth:`_create_reservation_object`
        """
        #Create the SQL Statements for retrieving information of the reservations
        query = 'SELECT * FROM Reservation WHERE flight_id = ?'
        #Activate foreign key support
        self.set_foreign_keys_support()
        #Create the cursor
        self.con.row_factory = sqlite3.Row
        cur = self.con.cursor()
        #Execute main SQL Statement
        pvalue = (flight_id,)
        cur.execute(query, pvalue)
        self.con.commit()
        rows = cur.fetchall()
        #Process the result
        if rows is None:
            return None
        reservations_flight = []
        for row in rows:
            reservations_flight.append(self._create_reservation_list_object(row))
        return reservations_flight

    def create_reservation(self, reservation):
        """
        Create a new reservation in the database.

        :param dict reservation: a dictionary for reservation with the information to be created. The
                dictionary has the following structure:

                .. code-block:: javascript

                    reservation = {'reservationid': reservation_id,
                                    'reference': reference,
                                    'reservationdate' : reservation_date,
                                    'userid' : creator_id,
                                    'flightid': flight_id}
                    

                where:     
                * ``reservationid``: reservation id for a reservation (INT)                 
                * ``reference``: reference for a reservation (TEXT)
                * ``reservationdate``: date of reservation (TEXT)
                * ``userid``: id of the user making a reservation (INT)
                * ``flightid``: flightid for which reservation is made (INT)
                                

        :return: True when reservation is created
        """
        #SQL Statement to create the row in  Reservation table

        query1 = 'SELECT * from Reservation WHERE reservation_id = ?'

        query2 = 'INSERT INTO Reservation (reservation_id, reference, re_date, creator_id, flight_id)\
                  VALUES(?,?,?,?,?)'

        reservation_id = reservation.get('reservationid', None)
        reference = reservation.get('reference', None)
        reservation_date = reservation.get('reservationdate', None)
        creator_id = reservation.get('userid', None)
        flight_id = reservation.get('flightid', None)

        #Activate foreign key support
        self.set_foreign_keys_support()
        #Cursor and row initialization
        self.con.row_factory = sqlite3.Row
        cur = self.con.cursor()
        
        #Execute the statement to check if a reservation with the reservation_id already exists
        pvalue =(reservation_id,)
        cur.execute(query1, pvalue) 
          
        #No value expected 
        row = cur.fetchone()
        #If there is no reservation add rows in Reservation 
        if row is None:
            #Add the row in 
            # Execute the statement
            timestamp = strftime("%Y-%m-%d", gmtime())
            pvalue = (reservation_id, reference, timestamp, creator_id, flight_id)
            try:
                cur.execute(query2, pvalue)
            except sqlite3.IntegrityError:
                return None

            self.con.commit()
            return cur.lastrowid
        else:
            return None

    def modify_reservation(self, reservationid,reference, userid, flightid):
        """
        Modify the information of a reservation.

        :param str reservationid: The reservationid is a string with format ``res-\d{1,2}``.
        :param str reference: 
        :param str userid: The userid is a string with format ``bookedby-\d{1,3}``.
        :param str flightid: The flightid is a string with format ``fl-\d{1,4}``.
                    
                where:     
                * ``reservationid``: reservation id for a reservation (INT)
                * ``reference``: reference for a reservation (TEXT)
                * ``userid``: id of the user making a reservation (INT)
                * ``flightid``: flightid for which reservation is made (INT)

        Note that all values are string if they are not otherwise indicated.

        :return: True when reservation is modified or False is the reservationid does not exist
        """

        query1 = 'SELECT * from Reservation WHERE reservation_id = ?'
           
        query2 = 'UPDATE Reservation SET reference = ?,creator_id = ?, flight_id = ? \
                                           WHERE reservation_id = ?' 
        #temporal variables
        reservation_id = reservationid
        reference = reference
        creator_id = userid
        flight_id = flightid
        #Activate foreign key support
        self.set_foreign_keys_support()
        #Cursor and row initialization
        self.con.row_factory = sqlite3.Row
        cur = self.con.cursor()
        #Execute the statement to check if the particular reservation
        pvalue = (reservation_id,)
        cur.execute(query1, pvalue)
        #Only one value expected
        row = cur.fetchone()
        #if does not exist, return
        if row is None:
            return False
        else:
            #execute the main statement
            pvalue = (reference, creator_id, flight_id, reservation_id)
            cur.execute(query2, pvalue)
            self.con.commit()
            #Check that If reservation has been modified
            if cur.rowcount < 1:
                return None
            return True

    def delete_reservation(self, reservation_id):
        """
        Remove all reservation information of a reservation with the reservation_id passed in as
        argument.

        :param str reservationid: The reservationid is a string with format ``res-\d{1,2}``.

        :return: True if the reservation is deleted, False otherwise.
        """
        #Create the SQL Statements
          #SQL Statement for deleting a reservation information
        query = 'DELETE FROM Reservation WHERE reservation_id = ?'
        #Activate foreign key support
        self.set_foreign_keys_support()
        #Cursor and row initialization
        self.con.row_factory = sqlite3.Row
        cur = self.con.cursor()
        #Execute the statement to delete
        pvalue = (reservation_id,)
        cur.execute(query, pvalue)
        self.con.commit()
        #Check that if the reservation has been deleted
        if cur.rowcount < 1:
            return False
        return True

    def contains_reservation(self, reservation_id):
        """
        :param reservation_id: The id of the reservation. 
                        The reservation_id is a string with format ``res-\d{1,2}``.
        :return: True if the reservation is in the database. False otherwise
        """
        return self.get_reservation(reservation_id) is not None

    #Ticket Table API
    def get_ticket(self, ticket_id):
        """
        Extracts all the information of a ticket from the database.

        :param ticket_id: The id of the ticket. 
                        The ticket_id is a string with format ``ticketnum-\d{1,4}``.
        :return: dictionary with the format provided in the method:
            :py:meth:`_create_ticket_object`

        """
        #SQL Statement for retrieving the ticket information for given ticketid
        query = 'SELECT * FROM Ticket WHERE ticket_id = ?'
        #Activate foreign key support
        self.set_foreign_keys_support()
        #Cursor and row initialization
        self.con.row_factory = sqlite3.Row
        cur = self.con.cursor()
        # Execute the SQL Statement to retrieve the ticket information.
        pvalue = (ticket_id,)
        cur.execute(query, pvalue)
        self.con.commit()
        row = cur.fetchone()
        #Process the response. 
        if row is None:
            return None
        else:
            return self._create_ticket_object(row)

     
    def get_tickets(self):
        """
        Extracts all the information of the tickets from the database.

        :return: dictionary with the format provided in the method:
            :py:meth:`_create_ticket_object`
        """
        #SQL Statement for retrieving the ticket information
        query = 'SELECT * FROM Ticket'
        #Activate foreign key support
        self.set_foreign_keys_support()
        #Cursor and row initialization
        self.con.row_factory = sqlite3.Row
        cur = self.con.cursor()
        # Execute the SQL Statement to retrieve the ticket information.
        cur.execute(query)
        rows = cur.fetchall()
        #Process the response. 
        if rows is None:
            return None
        tickets = []
        for row in rows:
            tickets.append(self._create_ticket_object(row))
        return tickets

    def get_tickets_by_reservation(self, reservation_id):
        """
        Extracts all the information of a ticket from the database of a particular reservation.

        :param reservation_id: The id of the reservation. 
                        The reservation_id is a string with format ``res-\d{1,2}``
        :return: dictionary with the format provided in the method:
            :py:meth:`_create_ticket_object`
        """

        #SQL Statement for retrieving the ticket information for given reservationid
        query = 'SELECT * from Ticket WHERE reservation_id = ?'
    
        #Activate foreign key support
        self.set_foreign_keys_support()
        #Cursor and row initialization
        self.con.row_factory = sqlite3.Row
        cur = self.con.cursor()
        # Execute the SQL Statement to retrieve the ticket information.
        pvalue = (reservation_id, )
        #execute the statement
        cur.execute(query, pvalue)
        #Process the response. 
        rows = cur.fetchall()
        if rows is None:
            return None
        else:
            tickets = []
            for row in rows:
                tickets.append(self._create_ticket_object(row))
            return tickets


    def create_ticket(self, ticket):
        """
        Create a new ticket in the database.

        :param dict ticket: a dictionary for user with the information to be created. The
                dictionary has the following structure:

                    ticket = {'ticketnumber': ticket_id,
                                'reservationid': reservation_id,
                                'firstname': firstname,
                                'lastname': lastname,
                                'gender': gender,
                                'age':age}
                    
            where:
            * ``ticketnumber``: user id for an user (INT)
            * ``reservationid``: reservation id of a reservation (INT)
            * ``lastname``: lastname of the passenger (TEXT)
            * ``firstname``: firstname of the passenger (TEXT)
            * ``gender``: passenger's gender (TEXT)
            * ``age``: passenger's age(INT)
       
        Note that all values are string if they are not otherwise indicated.

        :return: None if the ticket can not be created; the id of the new ticket otherwise
        """
        query1 = 'SELECT * from Ticket WHERE ticket_id = ?'
        query2 = 'SELECT flight_id from Reservation WHERE reservation_id = ?'
        query3 = 'SELECT nbSeatsLeft, nbInitialSeats from Flight WHERE flight_id = ?'
        query4 = 'UPDATE Flight SET nbSeatsLeft = ? WHERE flight_id = ?'
        query = 'INSERT INTO Ticket (ticket_id, firstName, lastName, gender, age, reservation_id, seat )\
                  VALUES(?,?,?,?,?,?,?)'
    
        ticket_id = ticket.get('ticketnumber', None)
        reservation_id = ticket.get('reservationid', None)
        firstName = ticket.get('firstname', None)
        lastName = ticket.get('lastname', None)
        gender = ticket.get('gender', None)
        age = ticket.get('age', None)
        
        #Activate foreign key support
        self.set_foreign_keys_support()
        #Cursor and row initialization
        self.con.row_factory = sqlite3.Row
        cur = self.con.cursor()
        
        #Execute the statement to check if the ticket already exists
        pvalue =(ticket_id,)
        cur.execute(query1, pvalue) 
        
        #No value expected 
        row = cur.fetchone()
        #If there is no ticket add rows in Ticket
        if row is None:
            pvalue =(reservation_id,)
            cur.execute(query2, pvalue)
            res_row = cur.fetchone()
            if res_row is None:
                return None
            flight_id = res_row['flight_id']
            pvalue =(flight_id,)
            cur.execute(query3, pvalue)
            flight_row = cur.fetchone()
            if flight_row is None:
                return None
            nbInitialSeats = flight_row['nbInitialSeats']
            nbSeatsLeft = flight_row['nbSeatsLeft']
            seat = nbInitialSeats - nbSeatsLeft + 1
            # Execute the statement
            pvalue = (ticket_id, firstName, lastName, gender, age, reservation_id, seat)
            cur.execute(query, pvalue)
            self.con.commit()
            new_ticket_id = cur.lastrowid
            nbSeatsLeft = nbSeatsLeft - 1
            pvalue =(nbSeatsLeft, flight_id,)
            cur.execute(query4, pvalue)
            return new_ticket_id

        else:
            return None

    def modify_ticket(self, ticket_id, ticket):
        """
        Modify the information of a ticket.

        :param ticket_id: The id of the ticket. 
                        The ticket_id is a string with format ``ticketnum-\d{1,4}``.
        :param dict ticket: a dictionary for ticket with the information to be created.
                          ticket_id must be given in order to make modifications. 
                          The dictionary has the following structure:

                .. code-block:: javascript

                    ticket = {'reservationid': reservation_id,
                                'firstname': firstname,
                                'lastname': lastname,
                                'gender': gender,
                                'age':age}
                   
            where:
            * ``reservationid``: reservation id of a reservation 
                                The reservationd is a string with format ``res-\d{1,2}``
            * ``lastname``: lastname of the passenger (TEXT)
            * ``firstname``: firstname of the passenger (TEXT)
            * ``gender``: passenger's gender (TEXT)
            * ``age``: passenger's age(INT)
    
        Note that all values are string if they are not otherwise indicated.

        :return: True when ticket is modified or False is the ticket_id does not exist
        """

        query1 = 'SELECT * from Ticket WHERE ticket_id = ?'
           
        query2 = 'UPDATE Ticket SET firstName = ?, lastName = ?, gender = ? ,\
                                        age = ?, reservation_id = ? \
                                           WHERE ticket_id = ?'

        reservation_id = ticket.get('reservationid', None)
        firstName = ticket.get('firstname', None)
        lastName = ticket.get('lastname', None)
        gender = ticket.get('gender', None)
        age = ticket.get('age', None)
        #Activate foreign key support
        self.set_foreign_keys_support()
        #Cursor and row initialization
        self.con.row_factory = sqlite3.Row
        cur = self.con.cursor()
        #Execute the statement 
        pvalue = (ticket_id,)
        cur.execute(query1, pvalue)
        #Only one value expected
        row = cur.fetchone()
        #if does not exist, return
        if row is None:
            return False
        else:
            #execute the main statement
            pvalue = (firstName, lastName, gender, age, reservation_id, ticket_id,)
            cur.execute(query2, pvalue)
            self.con.commit()
            #Check that if ticket is modified
            if cur.rowcount < 1:
                return False
            return True

    def delete_ticket(self, ticket_id):
        """
        Remove all ticket information of the ticket with the ticket_id passed in as
        argument.

        :param ticket_id: The id of the ticket to be deleted.
                        The ticket_id is a string with format ``ticketnum-\d{1,4}``.
        :return: True if the ticket is deleted, False otherwise.
        """
        #Create the SQL Statements
          #SQL Statement for deleting the ticket information
        query = 'DELETE FROM Ticket WHERE ticket_id = ?'
        #Activate foreign key support
        self.set_foreign_keys_support()
        #Cursor and row initialization
        self.con.row_factory = sqlite3.Row
        cur = self.con.cursor()
        #Execute the statement to delete
        pvalue = (ticket_id,)
        cur.execute(query, pvalue)
        self.con.commit()
        #Check that if the ticket has been deleted
        if cur.rowcount < 1:
            return False
        return True

    def contains_ticket(self, ticket_id):
        """
        :param ticket_id: The id of the ticket. 
                        The ticket_id is a string with format ``ticketnum-\d{1,4}``.
        :return: True if the ticket is in the database. False otherwise
        """
        return self.get_ticket(ticket_id) is not None
    
    







