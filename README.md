RUN THE SERVER
------------------
To run the server, go to the root folder of the project. Then, run the main.py file:

> python3 main.py

The API can be accessed at the following URL:
/flight-booking-system/api/

RUN THE API TESTS
------------------
To run the api tests, got to the root of the project. Then, execute the following command:

> python3 -m test.flight_booking_system_api_tests

CREATE THE DATABASE
------------------

This project uses SQLite 3 to manage the database. To create the database with its tables, in the project root folder:

First, create the database file with the sqlite3 command line tool:

> sqlite3 db/flight.db

Then execute the sql file to create the database

> .read db/flight_schema.sql

The resulting database file is db/flight.db

POPULATE THE DATABASE
------------------

To populate the database with data, in the project root folder:

> sqlite3 db/flight.db

> sqlite3 \> .read db/flight_data_dump.sql

RUNNING THE DATABASE TESTS
-----------------

In the project root folder:

To run the database unit tests
> python3 -m test.database_api_tests_user

> python3 -m test.database_api_tests_reservation

> python3 -m test.database_api_tests_ticket

> python3 -m test.database_api_tests_flight

> python3 -m test.database_api_tests_template_flight
