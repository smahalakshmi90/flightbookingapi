# coding= utf-8
'''
Created on 29.03.2018
'''

import json

from urllib.parse import unquote

from flask import Flask, request, Response, g, _request_ctx_stack, redirect, send_from_directory
from flask_restful import Resource, Api, abort
from werkzeug.exceptions import NotFound, UnsupportedMediaType

from flight_reservation import database

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
            "encoding": "json",
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
            "encoding": "json",
            "method": "PUT",
            "schema": self._user_schema()
        }

    def add_control_author(self, author_id):
        """
        Adds the control to get the author of a reservation or a set of reservations.
        :param author_id: the id of the user we want to get the reservation(s) of
        """
        self["@controls"]["author"] = {
            "title": "User owning the reservations",
            "href": api.url_for(User, user_id=author_id),
            "encoding": "json",
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

    def add_control_make_reservation(self, user_id):
        """
        Adds the control to perform one reservation for one user
        :param user_id: the id of the user that will make the reservation
        """
        self["@controls"]["flight-booking-system:make-reservation"] = {
            "title": "Make a reservation with this flight",
            "href": api.url_for(UserReservations, user_id=user_id),
            "encoding": "json",
            "method": "POST",
            "schemaUrl": RESERVATION_SCHEMA_URL
        }

    def add_control_add_flight(self):
        """
        Adds the control to add a new flight.
        """
        self["@controls"]["flight-booking-system:add-flight"] = {
            "title": "Add a new flight",
            "href": api.url_for(Flights),
            "encoding": "json",
            "method": "POST",
            "schemaUrl": FLIGHT_SCHEMA_URL
        }

    def add_control_flights_scheduled(self, template_flight_id):
        """
        Adds the control to get the scheduled flights of
        one template flight
        :param template_flight_id: the template flight id we want to get the scheduled flights of
        """
        self["@controls"]["flight-booking-system:flights-scheduled"] = {
            "title": "Get all the flights in this template flights",
            "href": api.url_for(Flights, template_flight_id=template_flight_id),
            "encoding": "json",
            "method": "GET",
        }

    def add_control_add_ticket(self, reservation_id):
        """
        Adds the control to cretae a new ticket for one specific reservation
        :param reservation_id: the id of the reservation to which we want to add a new ticket
        """
        self["@controls"]["flight-booking-system:add-ticket"] = {
            "title": "Add a new ticket for this reservation",
            "href": api.url_for(ReservationTickets, reservation_id=reservation_id),
            "encoding": "json",
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
            "encoding": "json",
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
            "encoding": "json",
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
            "href": api.url_for(Reservation, reservation_id=reservation_id),
            "encoding": "json",
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
            "encoding": "json",
            "method": "DELETE",
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
            userid = user_id,
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
        envelope.add_control("profile", USER_SCHEMA_URL)
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

        if not g.con.modify_user(user_id, updated_user):
            return NotFound()

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
    pass


class Reservation(Resource):
    pass


class UserReservations(Resource):
    pass


class Ticket(Resource):
    pass


class ReservationTickets(Resource):
    pass


class Flight(Resource):
    pass


class Flights(Resource):
    pass


class TemplateFlight(Resource):
    pass


class TemplateFlights(Resource):
    pass