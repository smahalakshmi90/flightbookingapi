# coding= utf-8
'''
Created on 29.03.2018
'''

import json

from urllib.parse import unquote

from flask import Flask, request, Response, g, _request_ctx_stack, redirect, send_from_directory
from flask_restful import Resource, Api, abort
from werkzeug.exceptions import NotFound, UnsupportedMediaType

from flight_reservation import flight_database as database
#import flight_database as database
from flight_reservation.flight_database import NoMoreSeatsAvailableException, EmailFormatException, DateFormatException, PhoneNumberFormatException
#from flight_database import NoMoreSeatsAvailableException, EmailFormatException, DateFormatException, PhoneNumberFormatException

# Constants for hypermedia formats and profiles
MASON = "application/vnd.mason+json"
JSON = "application/json"
FLIGHT_BOOKING_SYSTEM_USER_PROFILE = "/profiles/user-profile/"
FLIGHT_BOOKING_SYSTEM_RESERVATION_PROFILE = "/profiles/reservation-profile/"
FLIGHT_BOOKING_SYSTEM_TICKET_PROFILE = "/profiles/ticket-profile/"
FLIGHT_BOOKING_SYSTEM_FLIGHT_PROFILE = "/profiles/flight-profile/"
FLIGHT_BOOKING_SYSTEM_TEMPLATE_FLIGHT_PROFILE = "/profiles/template-flight-profile/"
ERROR_PROFILE = "/profiles/error-profile"

# Apiary documentation
STUDENT_APIARY_PROJECT = "https://flightreservationapp1.docs.apiary.io"
APIARY_PROFILES_URL = STUDENT_APIARY_PROJECT + "/#reference/profiles/"
APIARY_RELS_URL = STUDENT_APIARY_PROJECT + "/#reference/link-relations/"

USER_SCHEMA_URL = "/flight-booking-system/schema/user"
RESERVATION_SCHEMA_URL = "/flight-booking-system/schema/user/reservation"
TICKET_SCHEMA_URL = "/flight-booking-system/schema/user/ticket"
FLIGHT_SCHEMA_URL = "/flight-booking-system/schema/user/flight"
TEMPLATE_FLIGHT_SCHEMA_URL="/flight-booking-system/schema/template-flight"
LINK_RELATIONS_URL = "/flight-booking-system/link-relations/"

# Define the application and the api
app = Flask(__name__, static_folder="static", static_url_path="/.")
app.debug = True
# Set the database Engine. In order to modify the database file (e.g. for
# testing) provide the database path   app.config to modify the
# database to be used (for instance for testing)
app.config.update({"Engine": database.Engine()})
# Start the RESTful API.
api = Api(app)


# These two classes below are how we make producing the resource representation
# JSON documents manageable and resilient to errors. As noted, our mediatype is
# Mason. Similar solutions can easily be implemented for other mediatypes.

class MasonObject(dict):
    """
    A convenience class for managing dictionaries that represent Mason
    objects. It provides nice shorthands for inserting some of the more
    elements into the object but mostly is just a parent for the much more
    useful subclass defined next. This class is generic in the sense that it
    does not contain any application specific implementation details.

    @author: ivan
    """

    def add_error(self, title, details):
        """
        Adds an error element to the object. Should only be used for the root
        object, and only in error scenarios.

        Note: Mason allows more than one string in the @messages property (it's
        in fact an array). However we are being lazy and supporting just one
        message.

        :param str title: Short title for the error
        :param str details: Longer human-readable description
        """

        self["@error"] = {
            "@message": title,
            "@messages": [details],
        }

    def add_namespace(self, ns, uri):
        """
        Adds a namespace element to the object. A namespace defines where our
        link relations are coming from. The URI can be an address where
        developers can find information about our link relations.

        :param str ns: the namespace prefix
        :param str uri: the identifier URI of the namespace
        """

        if "@namespaces" not in self:
            self["@namespaces"] = {}

        self["@namespaces"][ns] = {
            "name": uri
        }

    def add_control(self, ctrl_name, **kwargs):
        """
        Adds a control property to an object. Also adds the @controls property
        if it doesn't exist on the object yet. Technically only certain
        properties are allowed for kwargs but again we're being lazy and don't
        perform any checking.

        The allowed properties can be found from here
        https://github.com/JornWildt/Mason/blob/master/Documentation/Mason-draft-2.md

        :param str ctrl_name: name of the control (including namespace if any)
        """

        if "@controls" not in self:
            self["@controls"] = {}

        self["@controls"][ctrl_name] = kwargs


class FlightBookingObject(MasonObject):
    """
    A convenience subclass of MasonObject that defines a bunch of shorthand
    methods for inserting application specific objects into the document. This
    class is particularly useful for adding control objects that are largely
    context independent, and defining them in the resource methods would add a
    lot of noise to our code - not to mention making inconsistencies much more
    likely!

    In the code this object should always be used for root document as
    well as any items in a collection type resource.

    @author: Jules Larue
    @author: Mahalakshmy Seetharaman
    """

    def __init__(self, **kwargs):
        """
        Calls dictionary init method with any received keyword arguments. Adds
        the controls key afterwards because hypermedia without controls is not
        hypermedia.
        """

        super(FlightBookingObject, self).__init__(**kwargs)
        self["@controls"] = {}

    def add_control_add_user(self):
        """
        This adds the add-user control to an object. Intended for the
        document object. Instead of adding a schema dictionary we are pointing
        to a schema url instead for two reasons: 1) to demonstrate both options;
        2) the user schema is relatively large.
        """

        self["@controls"]["flight-booking-system:add-user"] = {
            "href": api.url_for(Users),
            "title": "Create user",
            "encoding": "application/json",
            "method": "POST",
            "schemaUrl": USER_SCHEMA_URL
        }

    def add_control_delete_user(self, user_id):
        """
        Adds the control to delete a user.

        :param str user_id: The id of the user to remove
        """

        self["@controls"]["flight-booking-system:delete"] = {
            "href": api.url_for(User, user_id=user_id),
            "title": "Delete this user",
            "method": "DELETE"
        }

    def add_control_edit_user(self, user_id):
        """
        Adds the control to edit a user.

        :param str user_id: id of the user to edit
        """

        self["@controls"]["edit"] = {
            "href": api.url_for(User, user_id=user_id),
            "title": "Edit this user",
            "encoding": "application/json",
            "method": "PUT",
            "schemaUrl": USER_SCHEMA_URL
        }

    def add_control_author(self, author_id):
        """
        Adds the control to get the author of a reservation or a set of reservations.
        :param author_id: the id of the user we want to get the reservation(s) of
        """
        self["@controls"]["author"] = {
            "title": "User owning the reservations",
            "href": api.url_for(User, user_id=author_id),
            "encoding": "application/json",
            "method": "GET",
        }

    def add_control_reservations_history(self, user_id):
        """
        Adds the control to get all the reservations made
        by one specific user
        :param user_id: the id of the user we want to get the reservations of
        """

        self["@controls"]["flight-booking-system:reservations-history"] = {
            "title": "Reservations history",
            "href": api.url_for(UserReservations, user_id=user_id),
            "isHrefTemplate": "true"
        }

    def add_control_make_reservation(self):
        """
        Adds the control to perform one reservation for one user
        """
        self["@controls"]["flight-booking-system:make-reservation"] = {
            "title": "Make a reservation with this flight",
            "href": api.url_for(Reservations),
            "encoding": "application/json",
            "method": "POST",
            "schemaUrl": RESERVATION_SCHEMA_URL
        }

    def add_control_add_flight(self, template_id):
        """
        Adds the control to add a new flight.
        """
        self["@controls"]["flight-booking-system:add-flight"] = {
            "title": "Add a new flight",
            "href": api.url_for(Flights, template_id=template_id),
            "encoding": "application/json",
            "method": "POST",
            "schemaUrl": FLIGHT_SCHEMA_URL
        }

    def add_control_flights_scheduled(self, template_id):
        """
        Adds the control to get the scheduled flights of
        one template flight
        :param template_id: the template flight id we want to get the scheduled flights of
        """
        self["@controls"]["flight-booking-system:flights-scheduled"] = {
            "title": "Get all the flights in this template flights",
            "href": api.url_for(Flights, template_id=template_id),
            "encoding": "application/json",
            "method": "GET",
        }

    def add_control_add_ticket(self):
        """
        Adds the control to create a new ticket
        """
        self["@controls"]["flight-booking-system:add-ticket"] = {
            "title": "Add a new ticket for this reservation",
            "href": api.url_for(Tickets),
            "encoding": "application/json",
            "method": "POST",
            "schemaUrl": TICKET_SCHEMA_URL
        }

    def add_control_delete_ticket(self, ticket_id):
        """
        Adds the control to delete on ticket.
        :param ticket_id: the id of the ticket to delete
        """
        self["@controls"]["flight-booking-system:delete"] = {
            "title": "Delete ticket",
            "href": api.url_for(Ticket, ticket_id=ticket_id),
            "encoding": "application/json",
            "method": "DELETE",
        }

    def add_control_edit_ticket(self, ticket_id):
        """
        Adds the control to edit one ticket
        :param ticket_id: the id of the ticket to edit
        """
        self["@controls"]["edit"] = {
            "title": "Modify ticket",
            "href": api.url_for(Ticket, ticket_id=ticket_id),
            "encoding": "application/json",
            "method": "PUT",
            "schemaUrl": TICKET_SCHEMA_URL
        }

    def add_control_reservation_tickets(self, reservation_id):
        """
        Adds the control to get all the tickets of one specific reservation

        :param reservation_id: the id of the reservation we want to get the ticket of
        """
        self["@controls"]["flight-booking-system:reservation-tickets"] = {
            "title": "Tickets of this reservation",
            "href": api.url_for(ReservationTickets, reservation_id=reservation_id),
            "encoding": "application/json",
            "method": "GET"
        }

    def add_control_delete_reservation(self, reservation_id):
        """
        Adds the control to delete one reservation.
        :param reservation_id: the id if the reservation to delete
        :return:
        """
        self["@controls"]["flight-booking-system:delete"] = {
            "title": "Delete this reservation",
            "href": api.url_for(Reservation, reservation_id=reservation_id),
            "encoding": "application/json",
            "method": "DELETE",
        }

    def add_control_add_template_flight(self):
        """
        Adds the control to add a new template flight.
        """
        self["@controls"]["flight-booking-system:add-template-flight"] = {
            "title": "Add a new template flight",
            "href": api.url_for(TemplateFlights),
            "encoding": "application/json",
            "method": "POST",
            "schemaUrl": TEMPLATE_FLIGHT_SCHEMA_URL
        }

# ERROR HANDLERS

def create_error_response(status_code, title, message=None):
    """
    Creates a: py: class:`flask.Response` instance when sending back an
    HTTP error response

    :param integer status_code: The HTTP status code of the response
    :param str title: A short description of the problem
    :param message: A long description of the problem
    :rtype:: py: class:`flask.Response`

    @author: ivan
    """

    resource_url = None
    # We need to access the context in order to access the request.path
    ctx = _request_ctx_stack.top
    if ctx is not None:
        resource_url = request.path
    envelope = MasonObject(resource_url=resource_url)
    envelope.add_error(title, message)

    return Response(json.dumps(envelope), status_code, mimetype=MASON + ";" + ERROR_PROFILE)


@app.before_request
def connect_db():
    """
    Creates a database connection before the request is proccessed.

    The connection is stored in the application context variable flask.g .
    Hence it is accessible from the request object.

    @author: ivan
    """

    g.con = app.config["Engine"].connect()


# HOOKS
@app.teardown_request
def close_connection(exc):
    """
    Closes the database connection
    Check if the connection is created. It migth be exception appear before
    the connection is created.

    @author: ivan
    """

    if hasattr(g, "con"):
        g.con.close()


class User(Resource):

    def get(self, user_id):
        """
            Get basic information of a user:

            INPUT PARAMETER:
           : param str user_id: identifier of the required user.

            OUTPUT:
             * Return 200 if the user id exists.
             * Return 404 if the user id is not stored in the system.

            RESPONSE ENTITY BODY:
            * Media type recommended: application/vnd.mason+json
            * Profile recommended: User

            Link relations used: self, collection, delete, edit, reservations-history

            Semantic descriptors used: userid and registrationDate

            NOTE:
            The: py: method:`Connection.get_user()` returns a dictionary with the
            the following format.

            {
                'userid':,
                'lastname': '',
                'firstname': '',
                'phonenumber': '',
                'email': '',
                'dateofBirth': '',
                'gender': '',
                'registrationDate':
            }
        """
        # Get user from database
        user_db = g.con.get_user(user_id)
        if not user_db:
            return create_error_response(404, "Unknown user",
                                         "There is no user with id " + str(user_id))

        # Create the envelope
        envelope = FlightBookingObject(
            user_id = user_id,
            lastName = user_db["lastname"],
            firstName = user_db["firstname"],
            phoneNumber = user_db["phonenumber"],
            email = user_db["email"],
            birthDate = user_db["dateofBirth"],
            gender = user_db["gender"],
            registrationdate = user_db["registrationDate"]
        )

        envelope.add_namespace("flight-booking-system", LINK_RELATIONS_URL)
        envelope.add_control("self", href=api.url_for(User, user_id=user_id))
        envelope.add_control("profile", href=FLIGHT_BOOKING_SYSTEM_USER_PROFILE)
        envelope.add_control_edit_user(user_id=user_id)
        envelope.add_control_delete_user(user_id=user_id)
        envelope.add_control_reservations_history(user_id=user_id)
        envelope.add_control("collection", href=api.url_for(Users), method="GET")

        return Response(json.dumps(envelope), 200, mimetype=MASON + ";" + FLIGHT_BOOKING_SYSTEM_USER_PROFILE)


    def put(self, user_id):
        """
            Edit the information of a user

            REQUEST ENTITY BODY:
            * Media type: JSON

            :param user_id: identifier of the user to edit.
        """

        if not g.con.contains_user(user_id):
            return create_error_response(404, "Unknown user", "There is no user with id " + str(user_id))

        request_body = request.get_json()
        if not request_body:
            return create_error_response(415, "Unsupported Media Type", "Use  JSON format")

        # Get the user info from database
        user_db = g.con.get_user(user_id)

        try:
            # Create a dict with the updated info of the user
            # We don't need the id and registration date as
            # we DO NOT allow to edit these attributes
            updated_user = {
                "firstname": request_body["firstName"],
                "lastname": request_body["lastName"],
                "email": request_body["email"],
                "phonenumber": request_body["phoneNumber"],
                "dateofBirth": request_body["birthDate"],
                "gender": request_body["gender"],
            }
        except KeyError:
            return create_error_response(400, "Wrong request format", "Be sure to include all mandatory properties")

        try:
            if g.con.modify_user(user_id, updated_user) is None:
                return create_error_response(400, "Wrong request format",
                                             "Be sure that all attributes have correct format.")

        except (EmailFormatException, DateFormatException, PhoneNumberFormatException, ):
            return create_error_response(400, "Wrong request format", "Be sure that all attributes have correct format.")

        # Update success
        return "", 204


    def delete(self, user_id):
        """
            Delete a user in the system.

           : param str user_id: identifier of the user to delete.

            RESPONSE STATUS CODE:
             * If the user is deleted returns 204.
             * If the user id does not exist return 404
        """

        # Try to delete the user. If it could not be deleted, the database
        # returns False.
        if g.con.delete_user(user_id):
            # RENDER RESPONSE
            return '', 204
        else:
            # GENERATE ERROR RESPONSE
            return create_error_response(404, "Unknown user",
                                         "There is no a user with id " + str(user_id))

class Users(Resource):

    def get(self):
        """
            Gets a list of all the users in the database.

            This method always returns the status 200.

            RESPONSE ENTITITY BODY:

             OUTPUT:
                * Media type: application/vnd.mason+json
                    https://github.com/JornWildt/Mason
                * Profile: User
                    /profiles/user-profile

            Link relations used in items: add-user

            Semantic descriptions used in items: user_id, registrationdate

            Semantic descriptors used in template: lastName, firstName,
            phoneNumber, email, birthDate, gender
        """

        # Get the list of users from the database
        users_db = g.con.get_users()

        # Create the envelope (response)
        envelope = FlightBookingObject()

        envelope.add_namespace("flight-booking-system", LINK_RELATIONS_URL)

        envelope.add_control("self", href=api.url_for(Users))
        envelope.add_control_add_user()

        items = envelope["items"] = []

        for user in users_db:
            item = FlightBookingObject(
                user_id=user["userid"],
                registrationdate=user["registrationdate"],
                lastName=user["lastname"],
                firstName=user["firstname"],
            )
            item.add_control("self", href=api.url_for(User, user_id=user["userid"]))
            item.add_control("profile", href=FLIGHT_BOOKING_SYSTEM_USER_PROFILE)
            item.add_control_reservations_history(user_id=user["userid"])
            items.append(item)

        # RENDER
        return Response(json.dumps(envelope), 200, mimetype=MASON + ";" + FLIGHT_BOOKING_SYSTEM_USER_PROFILE)


    def post(self):
        """
        Adds a new user in the database.

        REQUEST ENTITY BODY:
         * Media type: JSON
         * Profile: User

        Semantic descriptors used in template: lastName, firstName, phoneNumber,
        email, birthDate, gender

        RESPONSE STATUS CODE:
         * Returns 201 + the url of the new resource in the Location header if the user is created
         * Return 409 if a user with the same email exists in the database
         * Return 400 if the request body is not well formed
         * Return 415 if it receives a media type != application/json

        NOTE:
        The: py: method:`Connection.append_user()` receives as a parameter a
        dictionary with the following format.
        {
            'lastname': lastname,
            'firstname': firstname,
            'phonenumber': phonenumber,
            'email': email,
            'dateofBirth': dateofBirth,
            'gender': gender,
            'registrationDate': registrationDate
        }

        """

        # Check Content-Type
        if JSON != request.headers.get("Content-Type", ""):
            abort(415)
        # PARSE THE REQUEST:
        request_body = request.get_json(force=True)

        # Check that body is JSON
        if not request_body:
            return create_error_response(415, "Unsupported Media Type",
                                         "Use a JSON compatible format",
                                         )

        # Check conflict with email
        try:
            email = request_body["email"]
        except KeyError:
            return create_error_response(400, "Wrong request format", "User email was missing from the request")

        # Conflict if the email already exists
        if g.con.contains_user_with_email(email):
            return create_error_response(409, "Wrong email",
                                         "There is already a user with the same email: " + email)

        # pick up rest of the mandatory fields
        try:
            first_name = request_body["firstName"]
            last_name = request_body["lastName"]
            phone_number = request_body["phoneNumber"]
            email = request_body["email"]
            birth_date = request_body["birthDate"]
            gender = request_body["gender"]
        except KeyError:
            return create_error_response(400, "Wrong request format", "Be sure to include all mandatory properties")

        user = {
            'firstname': first_name,
            'lastname': last_name,
            'phonenumber': phone_number,
            'email': email,
            'dateofBirth': birth_date,
            'gender': gender,
        }

        try:
            user_id = g.con.create_user(user)
            if user_id is None:
                return create_error_response(400, "Wrong request format",
                                             "Be sure that all parameters are correct.")

        except ValueError:
            return create_error_response(400, "Wrong request format",
                                         "Be sure you include all mandatory properties")

        # CREATE RESPONSE AND RENDER
        return Response(status=201,
                        headers={"Location": api.url_for(User, user_id=user_id)})


class Reservation(Resource):


    def get(self, reservation_id):
        """
            Get basic information of a reservation:

            INPUT PARAMETER:
           : param str reservation_id: identifier of the required reservation.

            OUTPUT:
             * Return 200 if the reservation id exists.
             * Return 404 if the reservation id is not stored in the system.

            RESPONSE ENTITY BODY:
            * Media type recommended: application/vnd.mason+json
            * Profile recommended: Reservation

            Link relations used: self, author, delete

            NOTE:
            The: py: method:`Connection.get_reservation()` returns a dictionary with the
            the following format.

            {
               'reservationid': ,
               'reference': '',
               'reservationdate' : '',
               'userid' : ,
               'flightid':
           }
        """
        # Get reservation from database
        reservation_db = g.con.get_reservation(reservation_id)
        if not reservation_db:
            return create_error_response(404, "Unknown reservation",
                                         "There is no reservation with id " + str(reservation_id))

        # Create the envelope
        envelope = FlightBookingObject(
            reservationid=reservation_id,
            reference=reservation_db["reference"],
            re_date=reservation_db["reservationdate"],
            user_id=reservation_db["userid"],
            flight_id=reservation_db["flightid"]
        )

        envelope.add_namespace("flight-booking-system", LINK_RELATIONS_URL)
        envelope.add_control("self", href=api.url_for(Reservation, reservation_id=reservation_id))
        envelope.add_control("profile", href=FLIGHT_BOOKING_SYSTEM_RESERVATION_PROFILE)
        envelope.add_control_delete_reservation(reservation_id)
        envelope.add_control_author(reservation_db["userid"])
        envelope.add_control("subsection",
                             title="Get the flight details",
                             href=api.url_for(Flight, flight_id=reservation_db["flightid"]),
                             encoding="application/json",
                             method="GET")

        return Response(json.dumps(envelope), 200, mimetype=MASON + ";" + FLIGHT_BOOKING_SYSTEM_RESERVATION_PROFILE)


    def delete(self, reservation_id):
        """
            Delete a reservation in the system.

           : param str reservation_id: identifier of the reservation to delete.

            RESPONSE STATUS CODE:
             * If the reservation id is deleted returns 204.
             * If the reservation id does not exist return 404
        """

        # Try to delete the reservation. If it could not be deleted, the database
        # returns False.
        if g.con.delete_reservation(reservation_id):
            # RENDER RESPONSE
            return '', 204
        else:
            # GENERATE ERROR RESPONSE
            return create_error_response(404, "Unknown reservation",
                                         "There is no reservation with id " + str(reservation_id))

class UserReservations(Resource):


    def get(self, user_id):
        """
            Gets a list of all the reservations of a specific user.

            RESPONSE STATUS CODE:
             * 200 if the reservations of the user are found
             * 404 if the user_id does not exist in the database

            RESPONSE ENTITITY BODY:

             OUTPUT:
                * Media type: application/vnd.mason+json
                    https://github.com/JornWildt/Mason
                * Profile: User
                    /profiles/reservation-profile

            Link relations used in items: delete, author, reservation-tickets

            Semantic descriptions used in items: reservation_id, reference, re_date

            Link relations used in links: author

            Semantic descriptors used in template: reservation_id, reference, re_date,
            user_id, flight_id
        """

        if not g.con.contains_user(user_id):
            return create_error_response(404,
                              title="Unknown user",
                              message="There is no user with id " + str(user_id))

        # Get the list of the user reservations
        reservations_db = g.con.get_reservations_by_user(user_id)

        # Create the envelope (response)
        envelope = FlightBookingObject()

        envelope.add_namespace("flight-booking-system", LINK_RELATIONS_URL)

        envelope.add_control("self", href=api.url_for(UserReservations, user_id=user_id))
        envelope.add_control_author(user_id)

        items = envelope["items"] = []

        for reservation in reservations_db:
            item = FlightBookingObject(
                reservation_id=reservation["reservationid"],
                reference=reservation["reference"],
                re_date=reservation["reservationdate"]
            )
            item.add_control("self", href=api.url_for(Reservation, reservation_id=reservation["reservationid"]))
            item.add_control("profile", href=FLIGHT_BOOKING_SYSTEM_RESERVATION_PROFILE)
            item.add_control_reservation_tickets(reservation["reservationid"])
            item.add_control_add_ticket()

            items.append(item)

        # RENDER
        return Response(json.dumps(envelope), 200, mimetype=MASON + ";" + FLIGHT_BOOKING_SYSTEM_RESERVATION_PROFILE)

class Reservations(Resource):

    def post(self):
        """
            Create a new reservation in the system.

            REQUEST ENTITY BODY:
             * Media type: JSON
             * Profile: Reservation

            RESPONSE STATUS CODE:
             * Returns 201 + the url of the new resource in the Location header if the reservation is created
             * Return 409 if the user has already booked the flight
             * Return 400 if the request body is not well formed or user id / flight id is incorrect
             * Return 415 if it receives a media type != application/json
             * Return 500 if there is a database error

            NOTE:
            The: py: method:`Connection.create_reservation()` receives as a parameter a
            dictionary with the following format.
            {
                'userid': ,
                'flightid': ,
            }

        """

        # Check Content-Type
        if JSON != request.headers.get("Content-Type", ""):
            abort(415)
        # PARSE THE REQUEST:
        request_body = request.get_json(force=True)

        # Check that body is JSON
        if not request_body:
            return create_error_response(415, "Unsupported Media Type",
                                         "Use a JSON compatible format")

        # pick up rest of the mandatory fields
        try:
            user_id = request_body["user_id"]
            flight_id = request_body["flight_id"]
            tickets = request_body.get("tickets", [])
        except KeyError:
            return create_error_response(400, "Wrong request format",
                                         "Be sure to include all mandatory properties")

        # Check if user exists
        if not g.con.contains_user(user_id):
            return create_error_response(400, "Invalid user",
                                         "The user chosen to book the flight does not exist.")

        # Check if flight exists
        if not g.con.contains_flight(flight_id):
            return create_error_response(400, "Invalid flight",
                                         "The flight chosen to make a reservation does not exist.")

        # Check if user has already booked the flight
        user_reservations = g.con.get_reservations_by_user(user_id)
        has_booked = False
        for reservation in user_reservations:
            if reservation["flightid"] == flight_id:
                has_booked = True

        if has_booked:
            return create_error_response(409, "Already booked",
                                         "The user " + str(user_id) + " has already booked the flight " + str(flight_id))
        reservation = {
            'userid': user_id,
            'flightid': flight_id
        }

        try:
            reservation_id = g.con.create_reservation(reservation)
        except ValueError:
            return create_error_response(400, "Wrong request format",
                                         "Be sure you include all mandatory properties")

        # Create the tickets specified (if any)
        for ticket in tickets:
            # Check fields
            try:
                first_name = ticket["firstName"]
                last_name = ticket["familyName"]
                age = ticket["age"]
                gender = ticket["gender"]
                seat = ticket["seat"]
            except ValueError:
                return create_error_response(400, "Wrong request format",
                                             "Be sure you include all mandatory properties")

            # Try to create the ticket
            try:
                ticket["reservationid"] = reservation_id
                g.con.create_ticket(ticket)
            except NoMoreSeatsAvailableException:
                return create_error_response(500, "Flight is full",
                                             "No more seats are available for the flight")

        # CREATE RESPONSE AND RENDER
        return Response(status=201,
                        headers={"Location": api.url_for(Reservation, reservation_id=reservation_id)})

class Ticket(Resource):
    def get(self, ticket_id):
        """
            Get ticket details:

            INPUT PARAMETER:
           : param str ticket_id: identifier of the required ticket.

            OUTPUT:
             * Return 200 if the ticket id exists.
             * Return 404 if the ticket id is not stored in the system.

            RESPONSE ENTITY BODY:
            * Media type recommended: application/vnd.mason+json
            * Profile recommended: Ticket

            Link relations used: self, collection, delete, edit, reservation-tickets

            Semantic descriptors used: ticket_id and reservation_id

            NOTE:
            The: py: method:`Connection.get_ticket()` returns a dictionary with the
            the following format.

            {
                'ticket_id':,
                'firstname': '',
                'familyName': '',
                'age': '',
                'gender': '',
                'seat': '',
                'reservation_id':
            }
        """
        # Get ticket from database
        ticket_db = g.con.get_ticket(ticket_id)
        if not ticket_db:
            return create_error_response(404, "Unknown ticket id",
                                         "There is no ticket with id " + str(ticket_id))

        # Create the envelope
        envelope = FlightBookingObject(
            ticket_id = ticket_db["ticketnumber"],
            firstName = ticket_db["firstname"],
            familyName = ticket_db["lastname"],
            age = ticket_db["age"],
            gender = ticket_db["gender"],
            seat = ticket_db["seat"],
            reservation_id = ticket_db["reservationid"]
        )

        envelope.add_namespace("flight-booking-system", LINK_RELATIONS_URL)
        envelope.add_control("self", href=api.url_for(Ticket, ticket_id=ticket_id))
        envelope.add_control("profile", href=FLIGHT_BOOKING_SYSTEM_TICKET_PROFILE)
        envelope.add_control_edit_ticket(ticket_id=ticket_id)
        envelope.add_control_delete_ticket(ticket_id=ticket_id)
        envelope.add_control_reservation_tickets(reservation_id = ticket_db["reservationid"])
        envelope.add_control("collection", href=api.url_for(Tickets), method="GET")

        return Response(json.dumps(envelope), 200, mimetype=MASON + ";" + FLIGHT_BOOKING_SYSTEM_TICKET_PROFILE)


    def put(self, ticket_id):
        """
            Edit the ticket

            REQUEST ENTITY BODY:
            * Media type: JSON

            :param ticket_id: identifier of the ticket to edit.
        """

        if not g.con.contains_ticket(ticket_id):
            return create_error_response(404, "Unknown ticket", "There is no ticket with id " + str(ticket_id))

        request_body = request.get_json()
        if not request_body:
            return create_error_response(415, "Unsupported Media Type", "Use  JSON format")

        # Get the ticket info from database
        ticket = g.con.get_ticket(ticket_id)
        try:
            # Create a dict with the updated info of the ticket
            # We don't need the id
            # we DO NOT allow to edit these attributes
            updated_ticket = {
                "firstname": request_body["firstName"],
                "lastname": request_body["familyName"],
                "age": request_body["age"],
                "gender": request_body["gender"],
                "seat": request_body["seat"],
            }
        except KeyError:
            return create_error_response(400, "Wrong request format", "Be sure to include all mandatory properties")

        updated_ticket["reservationid"] = g.con.get_ticket(ticket_id)["reservationid"]
        if g.con.modify_ticket(ticket_id, updated_ticket) is None:
            return create_error_response(400, "Wrong request format",
                                         "Be sure that all attributes have correct format.")

        # Update success
        return "", 204


    def delete(self, ticket_id):
        """
            Delete a ticket in the system.

           : param str ticket_id: identifier of the ticket to delete.

            RESPONSE STATUS CODE:
             * If the ticket is deleted returns 204.
             * If the ticket id does not exist return 404
        """

        # Try to delete the ticket. If it could not be deleted, the database
        # returns False.
        if g.con.delete_ticket(ticket_id):
            # RENDER RESPONSE
            return '', 204
        else:
            # GENERATE ERROR RESPONSE
            return create_error_response(404, "Unknown ticket",
                                         "There is no a ticket with id " + str(ticket_id))

class Tickets(Resource):
    def post(self):
        """
        Adds a new ticket in the database.

        REQUEST ENTITY BODY:
         * Media type: JSON
         * Profile: Ticket

        Semantic descriptors used in template: firstName, familyName,
        age, gender, seat, reservation_id

        RESPONSE STATUS CODE:
         * Returns 201 + the url of the new resource in the Location header if the ticket is created
         * Return 409 if a ticket with the same seat exists in the database
         * Return 400 if the request body is not well formed
         * Return 415 if it receives a media type != application/json

        NOTE:
        The: py: method:`Connection.append_user()` receives as a parameter a
        dictionary with the following format.
        {
            'firstName': firstName,
            'familyName': familyName,
            'age': age,
            'gender': gender,
            'seat': seat,
            'reservation_id': reservation_id
        }

        """

        # Check Content-Type
        if JSON != request.headers.get("Content-Type", ""):
            abort(415)
        # PARSE THE REQUEST:
        request_body = request.get_json(force=True)

        # Check that body is JSON
        if not request_body:
            return create_error_response(415, "Unsupported Media Type",
                                         "Use a JSON compatible format",
                                         )
        """
        # Check conflict with email
        try:
            email = request_body["email"]
        except KeyError:
            return create_error_response(400, "Wrong request format", "User email was missing from the request")

        # Conflict if the email already exists
        if g.con.contains_user_with_email(email):
            return create_error_response(409, "Wrong email",
                                         "There is already a user with the same email: " + email)
        """

        # pick up rest of the mandatory fields
        try:
            firstName = request_body["firstName"]
            familyName = request_body["familyName"]
            age = request_body["age"]
            gender = request_body["gender"]
            reservation_id = request_body["reservation_id"]
        except KeyError:
            return create_error_response(400, "Wrong request format", "Be sure to include all mandatory properties")

        ticket = {
            'firstname': request_body["firstName"],
            'lastname': familyName,
            'age': age,
            'gender': gender,
            'reservationid': reservation_id,
        }

        try:
            ticket_id = g.con.create_ticket(ticket)
            if ticket_id is None:
                return create_error_response(400, "Wrong request format",
                                             "Be sure that all parameters are correct.")

        except ValueError:
            return create_error_response(400, "Wrong request format",
                                         "Be sure you include all mandatory properties")

        # CREATE RESPONSE AND RENDER
        return Response(status=201,
                        headers={"Location": api.url_for(Ticket, ticket_id=ticket_id)})


class ReservationTickets(Resource):

    def get(self, reservation_id):
        """
            Gets a list of all the reservations of a specific user.

            RESPONSE STATUS CODE:
             * 200 if the reservations of the user are found
             * 404 if the user_id does not exist in the database

            RESPONSE ENTITITY BODY:

             OUTPUT:
                * Media type: application/vnd.mason+json
                    https://github.com/JornWildt/Mason
                * Profile: User
                    /profiles/reservation-profile

            Link relations used in items: delete, author, reservation-tickets

            Semantic descriptions used in items: reservation_id, reference, re_date

            Link relations used in links: author

            Semantic descriptors used in template: reservation_id, reference, re_date,
            user_id, flight_id
        """

        if not g.con.contains_reservation(reservation_id):
            return create_error_response(404,
                              title="Unknown reservation",
                              message="There is no reservation with id " + str(reservation_id))

        # Get the list of the user reservations
        tickets = g.con.get_tickets_by_reservation(reservation_id)

        # Create the envelope (response)
        envelope = FlightBookingObject()

        envelope.add_namespace("flight-booking-system", LINK_RELATIONS_URL)

        envelope.add_control("self", href=api.url_for(ReservationTickets, reservation_id=reservation_id))
        envelope.add_control("collection", href=api.url_for(Reservations))

        items = envelope["items"] = []

        for ticket in tickets:
            item = FlightBookingObject(
                ticket_id=ticket["ticketnumber"],
                firstName=ticket["firstname"],
                familyName=ticket["lastname"]
            )
            item.add_control("self", href=api.url_for(Ticket, ticket_id=ticket["ticketnumber"]))
            item.add_control("profile", href=FLIGHT_BOOKING_SYSTEM_TICKET_PROFILE)
            item.add_control_edit_ticket(ticket_id=ticket["ticketnumber"])
            item.add_control_delete_ticket(ticket_id=ticket["ticketnumber"])
            items.append(item)

        # RENDER
        return Response(json.dumps(envelope), 200, mimetype=MASON + ";" + FLIGHT_BOOKING_SYSTEM_TICKET_PROFILE)


class Flight(Resource):
    def get(self, flight_id):
        """
            Get basic information of a flight:

            INPUT PARAMETER:
            : param str flight_id: identifier of the required flight.

            OUTPUT:
            * Return 200 if the flight id exists.
            * Return 404 if the flight id is not stored in the system.

            RESPONSE ENTITY BODY:
            * Media type recommended: application/vnd.mason+json
            * Profile recommended: Flight

            Link relations used: self, profile, collection, make-reservation, subsection
            Semantic descriptors used in template: flight_id, template_id, code, gate ,
            price,depDate,arrDate, nbInitialSeats, nbSeatsLeft

            NOTE:
            The: py: method:`Connection.get_flight()` returns a dictionary with the
            the following format.

            {'searchresultid': ,
            'flightid': ,
            'code': '',
            'price': ,
            'departuredate':'',
            'arrivaldate': '',
            'gate': '' ,
            'totalseats':,
            'seatsleft':
            }
            """

        # Get user from database
        flight_db = g.con.get_flight(flight_id)
        if not flight_db:
            return create_error_response(404,
                                         title="Unknown flight",
                                         message="There is no flight with id " + str(flight_id))

        # Create the envelope
        envelope = FlightBookingObject(
                    flight_id = flight_id,
                    template_id = flight_db["searchresultid"],
                    code = flight_db["code"],
                    gate = flight_db["gate"],
                    price = flight_db["price"],
                    depDate = flight_db["departuredate"],
                    arrDate = flight_db["arrivaldate"],
                    nbInitialSeats = flight_db["totalseats"],
                    nbSeatsLeft = flight_db["seatsleft"]
                    )

        envelope.add_namespace("flight-booking-system", LINK_RELATIONS_URL)

        envelope.add_control("self", href=api.url_for(Flight, flight_id=flight_id))
        envelope.add_control("profile", href=FLIGHT_BOOKING_SYSTEM_FLIGHT_PROFILE)
        envelope.add_control("collection", href=api.url_for(Flights, template_id=flight_db["searchresultid"]), method="GET")
        envelope.add_control("subsection", href=api.url_for(TemplateFlights, template_id = flight_db["searchresultid"]),
                                                            method="GET")
        envelope.add_control_make_reservation()


        return Response(json.dumps(envelope), 200, mimetype=MASON + ";" + FLIGHT_BOOKING_SYSTEM_FLIGHT_PROFILE)


class Flights(Resource):
    def get(self, template_id):
        """
            Get information of all flight for a particular template flight.

            INPUT PARAMETER:
            : param str template_id: identifier of the required flights of particular template flight.

            OUTPUT:
            * Return 200 if the template id exists.
            * Return 404 if the template id is not stored in the system/ no flights for the template id exists.

            RESPONSE ENTITITY BODY:

            OUTPUT:
            * Media type recommended: application/vnd.mason+json
            * Profile recommended: Flight

            Link relations used in items: self, profile, add-flight, make-reservation

            Semantic descriptions used in items: flight_id, template_id, code, gate ,
            price, depDate, arrDate, nbInitialSeats, nbSeatsLeft
            """
        # Check if the template flight exists
        if not g.con.contains_template_flight(template_id):
            return create_error_response(404,
                              title="Unknown template flight",
                              message="There is no template flight with id " + str(template_id))
        # Get the list of users from the database
        flights_db = g.con.get_flights_by_template(template_id)

        if not flights_db:
            return create_error_response(404,
                                    title="Flights not found",
                                    message="There are no flights with TemplateFlight %s " % template_id)

        # Create the envelope (response)
        envelope = FlightBookingObject()

        envelope.add_namespace("flight-booking-system", LINK_RELATIONS_URL)

        envelope.add_control("self", href=api.url_for(Flights, template_id=template_id))
        envelope.add_control_add_flight(template_id=template_id)

        items = envelope["items"] = []

        for flight in flights_db:
            item = FlightBookingObject(
                    flightid = flight["flightid"],
                    template_id = template_id,
                    code = flight["code"],
                    gate = flight["gate"],
                    price = flight["price"],
                    depDate = flight["departuredate"],
                    arrDate = flight["arrivaldate"],
                    nbInitialSeats = flight["totalseats"],
                    nbSeatsLeft = flight["seatsleft"]
                    )
            item.add_control("self", href=api.url_for(Flight, flight_id=flight["flightid"]))
            item.add_control("profile", href=FLIGHT_BOOKING_SYSTEM_FLIGHT_PROFILE)
            item.add_control_make_reservation()

            items.append(item)

            # RENDER
            return Response(json.dumps(envelope), 200, mimetype=MASON + ";" + FLIGHT_BOOKING_SYSTEM_FLIGHT_PROFILE)

    def post(self, template_id):
        """
        Adds a new flight in the database.

        REQUEST ENTITY BODY:
         * Media type: JSON
         * Profile: Flight

        Semantic descriptors used in flight: flight_id, template_id, code, gate ,
                                                price, depDate, arrDate, nbInitialSeats, nbSeatsLeft

        RESPONSE STATUS CODE:
         * Returns 201 + the url of the new resource in the Location header if the flight is created
         * Return 409 if a flight with the same flight id exists in the database
         * Return 400 if the request body is not well formed
         * Return 415 if it receives a media type != application/json

        NOTE:
        The: py: method:`Connection.create_flight()` receives as a parameter a
        dictionary with the following format.
            {
            'searchresultid': result_id ,
            'flightid':flight_id ,
            'code': code,
            'price': price,
            'departuredate':departure_date,
            'arrivaldate':arrival_date,
            'gate':gate ,
            'totalseats':total_seats,
            'seatsleft':seats_left
            }

        """

        # Check Content-Type
        if JSON != request.headers.get("Content-Type", ""):
            abort(415)
        # PARSE THE REQUEST:
        request_body = request.get_json(force=True)

        # Check that body is JSON
        if not request_body:
            return create_error_response(415, "Unsupported Media Type",
                                         "Use a JSON compatible format")
        # pick up rest of the mandatory fields
        try:
            flight_id=request_body["flightid"]
            template_id = template_id
            code = request_body["code"]
            price = request_body["price"]
            departure_date = request_body["departuredate"]
            arrival_date = request_body["arrivaldate"]
            gate = request_body["gate"]
            total_seats = request_body["totalseats"]
            seats_left = request_body["seatsleft"]
        except KeyError:
            return create_error_response(400, "Wrong request format", "Be sure to include all mandatory properties")
        # Check if the  template flight exists
        if g.con.contains_flight(flight_id):
            return create_error_response(409, "Wrong flight id",
                                         "There is already a flight with the same id: " + str(flight_id))
        # Check if the  template flight exists
        if not g.con.contains_template_flight(template_id):
            return create_error_response(400, "Wrong template flight id",
                                         "The template flight does not exist")

        flight = {
            'searchresultid': template_id ,
            'flightid':flight_id ,
            'code': code,
            'price': price,
            'departuredate':departure_date,
            'arrivaldate':arrival_date,
            'gate':gate ,
            'totalseats':total_seats,
            'seatsleft':seats_left
        }

        try:
            flight_id = g.con.create_flight(flight)
        except ValueError:
            return create_error_response(400, "Wrong request format",
                                         "Be sure you include all mandatory properties")

        # CREATE RESPONSE AND RENDER
        return Response(status=201,
                        headers={"Location": api.url_for(Flight, flight_id=flight_id)})

class TemplateFlight(Resource):
    def get(self, template_id):
        """
            Get basic information of a template flight:

            INPUT PARAMETER:
           : param str template_id: identifier of the required template flight.

            OUTPUT:
             * Return 200 if the template flight id exists.
             * Return 404 if the template flight id is not stored in the system.

            RESPONSE ENTITY BODY:
            * Media type recommended: application/vnd.mason+json
            * Profile recommended: Template Flight

            Link relations used: self, profile, collection, flights-scheduled
            Semantic descriptors used: tflight_id, depTime, arrTime, origin, destination

            NOTE:
            The: py: method:`Connection.get_template_flight()` returns a dictionary with the
            the following format.

            {'searchid': ,
             'origin': '',
             'destination': '',
             'departuretime': ,
             'arrivaltime':
            }
        """
        # Get user from database
        tflight_db = g.con.get_template_flight(template_id)
        if not tflight_db:
            return create_error_response(404, "Unknown template flight",
                                         "There is no template flight with id " + str(template_id))

        # Create the envelope
        envelope = FlightBookingObject(
            tflight_id = template_id,
            origin = tflight_db["origin"],
            destination = tflight_db["destination"],
            dep_time = tflight_db["departuretime"],
            arr_time = tflight_db["arrivaltime"],

        )

        envelope.add_namespace("flight-booking-system", LINK_RELATIONS_URL)
        envelope.add_control("self", href=api.url_for(TemplateFlight, template_id=template_id))
        envelope.add_control("profile", href=FLIGHT_BOOKING_SYSTEM_TEMPLATE_FLIGHT_PROFILE)
        envelope.add_control("collection", href=api.url_for(TemplateFlights), method="GET")
        envelope.add_control_flights_scheduled(template_id=template_id)

        return Response(json.dumps(envelope), 200, mimetype=MASON + ";" + FLIGHT_BOOKING_SYSTEM_TEMPLATE_FLIGHT_PROFILE)


class TemplateFlights(Resource):
    def get(self):
        """
            Gets a list of all the template flights in the database.

            This method always returns the status 200.

            RESPONSE ENTITITY BODY:

             OUTPUT:
                * Media type: application/vnd.mason+json
                    https://github.com/JornWildt/Mason
                * Profile: Template Flight
                    /profiles/template-profile/

            Link relations used in items: add-template-flight

            Semantic descriptions used: tflight_id, depTime, arrTime, origin, destination
            NOTE:
            The: py: method:`Connection.get_template_flights()` returns a dictionary with the
            the following format.

            {'searchid': ,
             'origin': '',
             'destination': '',
             'departuretime': ,
             'arrivaltime':
            }
        """

        # Get the list of users from the database
        tflights_db = g.con.get_template_flights()

        # Create the envelope (response)
        envelope = FlightBookingObject()

        envelope.add_namespace("flight-booking-system", LINK_RELATIONS_URL)


        items = envelope["items"] = []

        for tflight in tflights_db:
            item = FlightBookingObject(
                search_id = tflight["searchid"],
                origin = tflight["origin"],
                destination = tflight["destination"],
                dep_time = tflight["departuretime"],
                arr_time = tflight["arrivaltime"],
            )
            envelope.add_control("self", href=api.url_for(TemplateFlight, template_id=tflight["searchid"]))
            envelope.add_control("profile", href=FLIGHT_BOOKING_SYSTEM_TEMPLATE_FLIGHT_PROFILE)
            envelope.add_control_flights_scheduled(template_id=tflight["searchid"])
            items.append(item)

        envelope.add_control("self", href=api.url_for(TemplateFlights))
        envelope.add_control_add_template_flight()

        # RENDER
        return Response(json.dumps(envelope), 200, mimetype=MASON + ";" + FLIGHT_BOOKING_SYSTEM_TEMPLATE_FLIGHT_PROFILE)

    def post(self):
        """
        Adds a new template flight in the database.

        REQUEST ENTITY BODY:
         * Media type: JSON
         * Profile: Template Flight

        Link relations used: self, add-template-flight
        Semantic descriptors used: tflight_id, depTime, arrTime, origin, destination

        RESPONSE STATUS CODE:
         * Returns 201 + the url of the new resource in the Location header if the flight is created
         * Return 409 if a template flight with the same template flight id exists in the database
         * Return 400 if the request body is not well formed
         * Return 415 if it receives a media type != application/json

        NOTE:
        The: py: method:`Connection.create_template_flight()` receives as a parameter a
        dictionary with the following format.
            {
            'searchresultid':tflight_id,
             'origin': origin,
             'destination': destination,
             'departuretime': dep_time,
             'arrivaltime': arr_time
             }

        """

        # Check Content-Type
        if JSON != request.headers.get("Content-Type", ""):
            abort(415)
        # PARSE THE REQUEST:
        request_body = request.get_json(force=True)

        # Check that body is JSON
        if not request_body:
            return create_error_response(415, "Unsupported Media Type",
                                         "Use a JSON compatible format")

        # pick up rest of the mandatory fields
        try:
            tflight_id = request_body["searchid"],
            origin = request_body["origin"],
            destination = request_body["destination"],
            dep_time = request_body["departuretime"],
            arr_time = request_body["arrivaltime"],
        except KeyError:
            return create_error_response(400, "Wrong request format", "Be sure to include all mandatory properties")

        # Check if the  template flight exists
        if g.con.contains_template_flight(tflight_id=request_body["searchid"]):
          return create_error_response(409, "Wrong template flight id",
                                        "The template flight already exists")
        templateflight = {
             'searchid':request_body["searchid"],
             'origin': request_body["origin"],
             'destination': request_body["destination"],
             'departuretime': request_body["departuretime"],
             'arrivaltime': request_body["arrivaltime"]}

        try:
            tflightid = g.con.create_template_flight(templateflight)
        except ValueError:
            return create_error_response(400, "Wrong request format",
                                         "Be sure you include all mandatory properties")

        # CREATE RESPONSE AND RENDER
        return Response(status=201,
                        headers={"Location": api.url_for(TemplateFlight, template_id=request_body["searchid"])})

api.add_resource(Users, "/flight-booking-system/api/users",
                 endpoint="users")
api.add_resource(User, "/flight-booking-system/api/users/<int:user_id>",
                 endpoint="user")
api.add_resource(UserReservations, "/flight-booking-system/api/users/<int:user_id>/reservations",
                 endpoint="user_reservations")
api.add_resource(Reservations, "/flight-booking-system/api/reservations",
                 endpoint="reservations")
api.add_resource(Reservation, "/flight-booking-system/api/reservations/<int:reservation_id>",
                 endpoint="reservation")
api.add_resource(ReservationTickets, "/flight-booking-system/api/reservations/<int:reservation_id>/tickets",
                 endpoint="reservation_tickets")
api.add_resource(Tickets, "/flight-booking-system/api/tickets",
                 endpoint="tickets")
api.add_resource(Ticket, "/flight-booking-system/api/tickets/<int:ticket_id>",
                 endpoint="ticket")
api.add_resource(Flight, "/flight-booking-system/api/flights/<int:flight_id>",
                 endpoint="flight")
api.add_resource(Flights, "/flight-booking-system/api/template-flights/<int:template_id>/flights",
                 endpoint="flights")
api.add_resource(TemplateFlight, "/flight-booking-system/api/template-flights/<int:template_id>",
                 endpoint="templateflight")
api.add_resource(TemplateFlights, "/flight-booking-system/api/template-flights/",
                 endpoint="templateflights")

#Send our schema file(s)
@app.route("/flight-booking-system/schema/<schema_name>/")
def send_json_schema(schema_name):
    return send_from_directory(app.static_folder, "schema/{}.json".format("user"))

#Start the application
#DATABASE SHOULD HAVE BEEN POPULATED PREVIOUSLY
if __name__ == '__main__':
    #Debug true activates automatic code reloading and improved error messages
    app.run(debug=True)
