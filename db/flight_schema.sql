PRAGMA foreign_keys=OFF;
BEGIN TRANSACTION;

CREATE TABLE IF NOT EXISTS User(
     user_id    INTEGER NOT NULL UNIQUE,
     lastName   TEXT,
     firstName  TEXT,
     phoneNumber    TEXT,
     email  TEXT,
     birthDate  INTEGER,
     gender     TEXT,
     registrationDate   INTEGER,
    PRIMARY KEY(user_id ));

CREATE TABLE IF NOT EXISTS Reservation(
     reservation_id     INTEGER NOT NULL UNIQUE,
     reference  TEXT,
     re_date    INTEGER,
     creator_id     INTEGER NOT NULL,
     flight_id  INTEGER NOT NULL,
    PRIMARY KEY( reservation_id ),
    FOREIGN KEY( flight_id ) REFERENCES  Flight ( flight_id ) ON DELETE CASCADE,
    FOREIGN KEY( creator_id ) REFERENCES  Users ( user_id ) ON DELETE CASCADE);

CREATE TABLE IF NOT EXISTS Ticket(
     ticket_id  INTEGER NOT NULL UNIQUE,
     fullName   TEXT,
     age    INTEGER,
     reservation_id     INTEGER NOT NULL,
     price  INTEGER,
     seat   TEXT,
    PRIMARY KEY( ticket_id ),
    FOREIGN KEY( reservation_id ) REFERENCES  Reservation ( reservation_id ) ON DELETE CASCADE);

CREATE TABLE IF NOT EXISTS Flight(
     flight_id  INTEGER NOT NULL UNIQUE,
     code   TEXT UNIQUE,
     gate   TEXT,
     depDate    INTEGER,
	 arrDate    INTEGER,
     nbInitialSeats     INTEGER,
     nbSeatsLeft    INTEGER,
     template_id    INTEGER NOT NULL,
    FOREIGN KEY( template_id ) REFERENCES  TemplateFlights ( tflight_id ) ON DELETE CASCADE,
    PRIMARY KEY( flight_id ));

CREATE TABLE IF NOT EXISTS TemplateFlight(
     tflight_id     INTEGER NOT NULL UNIQUE,
     depTime    INTEGER,
     arrTime    INTEGER,
     origin     TEXT,
     destination    TEXT,
    PRIMARY KEY( tflight_id ));

COMMIT;
PRAGMA foreign_keys=ON;