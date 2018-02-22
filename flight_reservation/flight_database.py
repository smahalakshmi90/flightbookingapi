'''
Created on 20.02.2018
Provides the database API to access the flight booking system persistent data.

@author: Mahalakshmy Seetharaman

'''

from datetime import datetime
import time, sqlite3, re, os, io
#Default paths for .db and .sql files to create and populate the database.
DEFAULT_DB_PATH = "db/flight.db"
DEFAULT_SCHEMA = "db/flight_schema.sql"
DEFAULT_DATA_DUMP = "db/flight_data_dump.sql"

class Engine(object):

    '''
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

    '''

    def __init__(self, db_path=None):
        '''
        '''
        super(Engine, self).__init__()
        if db_path is not None:
            self.db_path = db_path
        else:
            self.db_path = DEFAULT_DB_PATH

    def connect(self):
        '''
        Creates a connection to the database.

        :return: A Connection instance
        :rtype: Connection

        '''
        return Connection(self.db_path)

    def remove_database(self):
        '''
        Removes the database file from the filesystem.

        '''
        if os.path.exists(self.db_path):
            #THIS REMOVES THE DATABASE STRUCTURE
            os.remove(self.db_path)

    def clear(self):
        '''
        Purge the database removing all records from the tables. However,
        it keeps the database schema (meaning the table structure)

        '''
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
        '''
        Create programmatically the tables from a schema file.

        :param schema: path to the .sql schema file. If this parmeter is
            None, then *db/flight_schema.sql* is utilized.

        '''
        con = sqlite3.connect(self.db_path)
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
        '''
        Populate programmatically the tables from a dump file.

        :param dump:  path to the .sql dump file. If this parmeter is
            None, then *db/forum_data_dump.sql* is utilized.

        '''
        keys_on = 'PRAGMA foreign_keys = ON'
        con = sqlite3.connect(self.db_path)
        #Activate foreing keys support
        cur = con.cursor()
        cur.execute(keys_on)
        #Populate database from dump
        if dump is None:
            dump = DEFAULT_DATA_DUMP
        with io.open (dump, encoding="utf-8") as f:
            sql = f.read()
            cur = con.cursor()
            cur.executescript(sql)

    #METHODS TO CREATE THE TABLES PROGRAMMATICALLY WITHOUT USING SQL SCRIPT
    def create_user_table(self):
        '''
        Create the table ``User`` programmatically, without using .sql file.

        Print an error message in the console if it could not be created.

        :return: ``True`` if the table was successfully created or ``False``
            otherwise.

        '''
        keys_on = 'PRAGMA foreign_keys = ON'
        stmnt = 'CREATE TABLE User(user_id INTEGER NOT NULL PRIMARY KEY, \
                    lastName TEXT,\
                    firstName TEXT, \
                    phoneNumber TEXT, \
                    email TEXT, \
                    birthDate INTEGER, \
                    gender TEXT, \
                    registrationDate INTEGER, \
                    UNIQUE(user_id))'
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
        '''
        Create the table ``template flights`` programmatically, without using .sql file.

        Print an error message in the console if it could not be created.

        :return: ``True`` if the table was successfully created or ``False``
            otherwise.
        '''
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
        return None

    def create_flight_table(self):
        '''
        Create the table ``Flight`` programmatically, without using .sql file.

        Print an error message in the console if it could not be created.

        :return: ``True`` if the table was successfully created or ``False``
            otherwise.
        '''
        keys_on = 'PRAGMA foreign_keys = ON'
        stmnt = 'CREATE TABLE Flight(flight_id INTEGER NOT NULL UNIQUE PRIMARY KEY, \
                                code TEXT UNIQUE,\
                                gate TEXT,\
                                price INTEGER, \
                                depDate INTEGER,\
                                arrDate INTEGER,\
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
        return None


    def create_reservation_table(self):
        '''
        Create the table ``Reservation`` programmatically, without using .sql file.

        Print an error message in the console if it could not be created.

        :return: ``True`` if the table was successfully created or ``False``
            otherwise.

        '''
        keys_on = 'PRAGMA foreign_keys = ON'
        stmnt = 'CREATE TABLE Reservation(reservation_id INTEGER NOT NULL UNIQUE PRIMARY KEY,\
                                    reference TEXT UNIQUE, \
                                    re_date INTEGER,\
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
        '''
        Create the table ``Ticket`` programmatically, without using
        .sql file.

        Print an error message in the console if it could not be created.

        :return: ``True`` if the table was successfully created or ``False``
            otherwise.

        '''
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
    '''
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

    '''
    def __init__(self, db_path):
        super(Connection, self).__init__()
        self.con = sqlite3.connect(db_path)

    def close(self):
        '''
        Closes the database connection, commiting all changes.

        '''
        if self.con:
            self.con.commit()
            self.con.close()

    #FOREIGN KEY STATUS
    def check_foreign_keys_status(self):
        '''
        Check if the foreign keys has been activated.

        :return: ``True`` if  foreign_keys is activated and ``False`` otherwise.
        :raises sqlite3.Error: when a sqlite3 error happen. In this case the
            connection is closed.

        '''
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
        '''
        Activate the support for foreign keys.

        :return: ``True`` if operation succeed and ``False`` otherwise.

        '''
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
        '''
        Deactivate the support for foreign keys.

        :return: ``True`` if operation succeed and ``False`` otherwise.

        '''
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

    #Helper for user
    def _create_user_object(self, row):
        '''

        '''
        return {'userid': 'user-' + row['user_id'],
                'lastname': row['lastName'],
                'firstname': row['firstName'],
                'phonenumber': row['phoneNumber'],
                'email': row['email'],
                'dateofBirth': ['birthDate'],
                'gender': row['gender'],
                'registrationdate': row['regDate']}
                
    def _create_user_list_object(self, row):
        '''

        '''
        return { 'userid': row['user_id'],
                'firstname': row['firstName'],
                'lastname': row['lastnName'],
                'registrationdate': row['regDate']}

    def _create_reservation_object(self, row):
        '''
        
        '''
        reservation_id = 'res-' + str(row['reservation_id'])
        reference = row['reference']
        reservation_date = row['re_date']
        creator_id = row['creator_id']
        flight_id =row['flight_id']
        reservation = {'reservationid': reservation_id,
                       'reference': reference,
                       'reservationdate' : reservation_date,
                       'userid' : creator_id,
                       'flightid': flight_id}
        return reservation

    def _create_reservation_list_object(self, row):
        '''
        
        '''
        reservation_id = 'res-' + str( row['reservation_id'])
        creator_id = 'bookedby'+ str( row['creator_id'])
        flight_id =row['flight_id']
        reservation_date = row['re_date']
        reservations = {'reservationid': reservation_id,
                       'userid' : creator_id,
                       'flightid': flight_id,
                       'reservationdate' : reservation_date}

        return reservations

    #Helpers for users
    def _create_flight_object(self, row):
        '''
        

        '''
        result_id ='result' + str(row['template_id'])
        flight_id = 'fl-' + str(row['flight_id'])
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

    def _create_template_flight_object(self, row):
        '''

        '''
        tflight_id ='search' +str(row['tFlight_id'])
        origin = row['origin']
        departure = row['departure']
        dep_time = row['deptime']
        arr_time=row['arrTime']
        

        templateflight = {'searchid': tflight_id,
                          'origin': origin,
                          'departure': departure,
                          'departuretime': dep_time,
                          'arrivaltime': arr_time }
        return templateflight

    def _create_ticket_object(self, row):
        '''
        
        '''
        ticket_id ='ticketnum' + str( row['ticket_id'])
        reservation_id = 'res' + str( row['reservation_id'])
        fullname = row['origin']
        age = row['age']
        seat = row['seat']
        

        ticket = {'ticketnumber': ticket_id,
                  'reservationid': reservation_id,
                  'passengername': fullname,
                  'age':age,
                  'seat':seat}

        return ticket

    #API ITSELF

    #User Table API

    def get_user(self, user_id):
        '''
        Extracts all the information of a user.

        :param str nickname: The nickname of the user to search for.
        :return: dictionary with the format provided in the method:
            :py:meth:`_create_user_object`

        '''
        #Create the SQL Statements
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
        return self._create_user_object(row)

    def get_users(self):
        '''
        '''
        #Create the SQL Statements
          #SQL Statement for retrieving the users
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
        '''
        Create a new user in the database.
        '''
        
          #SQL Statement to create the row in  users table
        query = 'INSERT INTO User (lastName, firstName, phoneNumber, email, birthDate, gender, registrationDate)\
                  VALUES(?,?,?,?,?,?,?)'
                  
        #temporal variables for user table
        #timestamp will be used for lastlogin and regDate.
        timestamp = time.mktime(datetime.now().timetuple()
        #Activate foreign key support
        self.set_foreign_keys_support()
        #Cursor and row initialization
        self.con.row_factory = sqlite3.Row
        cur = self.con.cursor()
        #Execute the statement to extract the id associated to a nickname
        pvalue = (lastName, firstName, phoneNumber, email, birthDate, gender, registrationDate)
        cur.execute(query, pvalue) 
        #No value expected (no other user with that nickname expected)
        row = cur.fetchone()
        #If there is no user add rows in user and user profile
        if row is None:
            #Add the row in users table
            # Execute the statement
            pvalue = (nickname, timestamp, timestamp, timesviewed)
            cur.execute(query2, pvalue)
            #Extrat the rowid => user-id
            lid = cur.lastrowid
            #Add the row in users_profile table
            # Execute the statement
            pvalue = (lid, _firstname, _lastname, _email, _website,
                      _picture, _mobile, _skype, _age, _residence, _gender,
                      _signature, _avatar)
            cur.execute(query3, pvalue)
            self.con.commit()
            #We do not do any comprobation and return the nickname
            return nickname
        else:
            return None

    def modify_user(self, user_id, user):
        '''
        
        '''
                #Create the SQL Statements
           #SQL Statement for extracting the userid given a nickname
           
        query = 'UPDATE User SET lastName = ?,firstName = ?, \
                                           phoneNumber = ?,email = ?, \
                                           birthDate = ?,gender = ?\
                                           WHERE user_id = ?'
        #temporal variables
        firstname = User.get('firstName', None)
        lastname = User.get('lastName', None)
        phonenumber = User.get('phoneNumber', None)
        email = User.get('email', None)
        birthdate = User.get('birthDate', None)
        gender = User.get('gender', None)

        #Activate foreign key support
        self.set_foreign_keys_support()
        #Cursor and row initialization
        self.con.row_factory = sqlite3.Row
        cur = self.con.cursor()
        #Execute the statement to extract the id associated to a nickname
        pvalue = (nickname,)
        cur.execute(query1, pvalue)
        #Only one value expected
        row = cur.fetchone()
        #if does not exist, return
        if row is None:
            return None
        else:
            user_id = row["user_id"]
            #execute the main statement
            pvalue = (lastname, firstname, phonenumber, email, birthdare, gender)
            cur.execute(query, pvalue)
            self.con.commit()
            #Check that I have modified the user
            if cur.rowcount < 1:
                return None
            return user_id

    def delete_user(self, user_id):
        '''
        
        '''
        #Create the SQL Statements
          #SQL Statement for deleting the user information
        query = 'DELETE FROM users WHERE user_id = ?'
        #Activate foreign key support
        self.set_foreign_keys_support()
        #Cursor and row initialization
        self.con.row_factory = sqlite3.Row
        cur = self.con.cursor()
        #Execute the statement to delete
        pvalue = (user_id,)
        cur.execute(query, pvalue)
        self.con.commit()
        #Check that it has been deleted
        if cur.rowcount < 1:
            return False
        return True

    def get_reservation(self, res_id):
        '''
        '''
        query = 'SELECT * FROM Reservation WHERE res_id = ?'
        self.set_foreign_keys_support()
        self.con.row_factory = sqlite3.Row
        cur = self.con.cursor()
        pvalue = (res_id,)
        cur.execute(query, pvalue)
        self.con.commit()
        row = cur.fetchone()
        return self._create_reservation_object(row)

    def get_reservation_list(self):
        '''
        '''
        query = 'SELECT * FROM Reservation'
        self.set_foreign_keys_support()
        self.con.row_factory = sqlite3.Row
        cur = self.con.cursor()
        cur.execute(query)
        rows = cur.fetchall()
        if rows is None:
            return None
        reservations = []
        for row in rows:
            reservations.append(_create_reservation_list_object(row))
        return reservations

    def get_reservations_by_user(self, creator_id):
        '''
        '''
        query = 'SELECT * FROM Reservation WHERE creator_id = ?'
        self.set_foreign_keys_support()
        self.con.row_factory = sqlite3.Row
        cur = self.con.cursor()
        pvalue = (creator_id,)
        cur.execute(query, pvalue)
        self.con.commit()
        rows = cur.fetchall()
        if rows is None:
            return None
        reservations_user = []
        for row in rows:
            reservations_user.append(_create_reservation_list_object(row))
        return reservations_user

    def get_reservations_by_flight(self, flight_id):
        '''
        '''
        query = 'SELECT * FROM Reservation WHERE flight_id = ?'
        self.set_foreign_keys_support()
        self.con.row_factory = sqlite3.Row
        cur = self.con.cursor()
        pvalue = (creator_id,)
        cur.execute(query, pvalue)
        self.con.commit()
        rows = cur.fetchall()
        if rows is None:
            return None
        reservations_user = []
        for row in rows:
            reservations_user.append(_create_reservation_list_object(row))
        return reservations_user

    def create_reservation(self):

    def modify_reservation(self):

    def delete_reservation(self):

    def get_ticket(self, ticket_id):

    def get_tickets(self):

    def get_tickets_by_reservation(self, reservation_id):

    def create_ticket(self):

    def modify_ticket(self, ticket_id):

    def delete_ticket(self, ticket_id):

    def get_flight(self, flight_id):

    def get_flights_by_template(self, temmplate_id):

    def create_flight(self):

    def modify_flight(self, flight_id):

    def delete_flight(self, flight_id):

    def get_template_flight(self, flight_id):

    def create_template_flight(self):

    def modify_template_flight(self, tflight_id):

    def delete_template_flight(self, tflight_id):








