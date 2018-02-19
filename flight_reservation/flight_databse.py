'''
Created on 19.02.2018
Provides the database API to access the forum persistent data.

'''
from datetime import datetime
import time, sqlite3, re, os
#Default paths for .db and .sql files to create and populate the database.
DEFAULT_DB_PATH = '../db/flight.db'
DEFAULT_SCHEMA = "../db/flight_schema.sql"

