'''
Created on 19.02.2018
Provides the database API to access the forum persistent data.

'''
from datetime import datetime
import time, sqlite3, os
#Default paths for .db and .sql files to create and populate the database.
DEFAULT_DB_PATH = '../db/flight.db'
DEFAULT_SCHEMA = "../db/flight_schema.sql"



def create_tables(db_path=DEFAULT_DB_PATH, schema_path=DEFAULT_SCHEMA):
	conn = sqlite3.connect(db_path)
	c = conn.cursor()
	try:
		with open(schema_path, encoding="utf-8") as f:
			sql = f.read()
			c.executescript(sql)
			conn.commit()
	finally:
		conn.close()

create_tables()
