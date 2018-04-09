PRAGMA foreign_keys=OFF;
BEGIN TRANSACTION;

CREATE TABLE IF NOT EXISTS User(
     user_id INTEGER PRIMARY KEY AUTOINCREMENT,
     lastName   TEXT,
     firstName  TEXT,
     phoneNumber    TEXT,
     email  TEXT,
     birthDate  TEXT,
     gender     TEXT,
     registrationDate INTEGER);

CREATE TABLE IF NOT EXISTS TemplateFlight(
     tflight_id INTEGER PRIMARY KEY AUTOINCREMENT,
     depTime    TEXT,
     arrTime    TEXT,
     origin     TEXT,
     destination TEXT);

CREATE TABLE IF NOT EXISTS Flight(
     flight_id  INTEGER PRIMARY KEY AUTOINCREMENT,
     code   TEXT UNIQUE,
     price  INTEGER,
     gate   TEXT,
     depDate    TEXT,
     arrDate    TEXT,
     nbInitialSeats     INTEGER,
     nbSeatsLeft    INTEGER,
     template_id    INTEGER NOT NULL,
    FOREIGN KEY( template_id ) REFERENCES  TemplateFlight(tflight_id ) ON DELETE CASCADE);

CREATE TABLE IF NOT EXISTS Reservation(
     reservation_id INTEGER PRIMARY KEY AUTOINCREMENT,
     reference  TEXT,
     re_date    TEXT,
     creator_id     INTEGER NOT NULL,
     flight_id  INTEGER NOT NULL,
     unique (creator_id, flight_id),
    FOREIGN KEY( flight_id ) REFERENCES  Flight ( flight_id ) ON DELETE CASCADE,
    FOREIGN KEY( creator_id ) REFERENCES  User( user_id ) ON DELETE CASCADE);

CREATE TABLE IF NOT EXISTS Ticket(
     ticket_id  INTEGER PRIMARY KEY AUTOINCREMENT,
	 firstName   TEXT,
	 lastName   TEXT,
	 gender   TEXT,
     age    INTEGER,
     reservation_id     INTEGER NOT NULL,
     seat   TEXT,
    FOREIGN KEY( reservation_id ) REFERENCES  Reservation ( reservation_id ) ON DELETE CASCADE);




COMMIT;
PRAGMA foreign_keys=ON;
