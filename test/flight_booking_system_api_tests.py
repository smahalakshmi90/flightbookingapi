"""
Created on 26.01.2013
Modified on 05.02.2017
@author: ivan sanchez
@author: mika oja
@author: Jules LARUE
@author: Mahalakshmy Seetharaman
"""
import json
import unittest

import flask

import flight_reservation.flight_database as database
import flight_reservation.resources as resources

DB_PATH = "db/flight_test.db"
ENGINE = database.Engine(DB_PATH)

MASONJSON = "application/vnd.mason+json"
JSON = "application/json"
HAL = "application/hal+json"
FLIGHT_BOOKING_SYSTEM_USER_PROFILE = "/profiles/user-profile/"
FLIGHT_BOOKING_SYSTEM_RESERVATION_PROFILE = "/profiles/reservation-profile/"
FLIGHT_BOOKING_SYSTEM_TICKET_PROFILE = "/profiles/ticket-profile/"
FLIGHT_BOOKING_SYSTEM_FLIGHT_PROFILE = "/profiles/flight-profile/"
FLIGHT_BOOKING_SYSTEM_TEMPLATE_FLIGHT_PROFILE = "/profiles/template-flight-profile/"

USER_SCHEMA_URL = "/flight-booking-system/schema/user"
RESERVATION_SCHEMA_URL = "/flight-booking-system/schema/user/reservation"
TICKET_SCHEMA_URL = "/flight-booking-system/schema/user/ticket"
FLIGHT_SCHEMA_URL = "/flight-booking-system/schema/user/flight"
TEMPLATE_FLIGHT_SCHEMA_URL="/flight-booking-system/schema/template-flight"
LINK_RELATIONS_URL = "/flight-booking-system/link-relations/"

# Tell Flask that I am running it in testing mode.
resources.app.config["TESTING"] = True
# Necessary for correct translation in url_for
resources.app.config["SERVER_NAME"] = "localhost:5000"

# Database Engine utilized in our testing
resources.app.config.update({"Engine": ENGINE})

# Other database parameters.
NB_INITIAL_USERS = 5
NB_INITIAL_FLIGHTS = 3
NB_INITIAL_TEMPLATE_FLIGHTS = 5
NB_INITIAL_RESERVATIONS = 4
NB_INITIAL_TICKETS = 5


class ResourcesAPITestCase(unittest.TestCase):
    """
    @author: ivan sanchez
    """

    # INITIATION AND TEARDOWN METHODS
    @classmethod
    def setUpClass(cls):
        """
        Creates the database structure. Removes first any preexisting
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
        # This method load the initial values from flight_data_dump.sql
        ENGINE.populate_tables()
        # Activate app_context for using url_for
        self.app_context = resources.app.app_context()
        self.app_context.push()
        # Create a test client
        self.client = resources.app.test_client()

    def tearDown(self):
        """
        Remove all records from database
        """
        ENGINE.clear()
        self.app_context.pop()


class UserTestCase(ResourcesAPITestCase):
    user1_id = 1
    user1 = {
        'lastname': 'Tilton',
        'firstname': 'John',
        'phonenumber': '92722736387',
        'email': 'john.tilton@jhj.jh',
        'dateofBirth': '1981-04-04',
        'gender': 'male',
        'registrationDate': 1519423463929,
    }
    modified_user1_req = {
        'lastName': 'Watt',
        'firstName': 'James',
        'phoneNumber': '+44 871 222 3330',
        'email': 'james.watt@example.com',
        'birthDate': '1992-04-12',
        'gender': 'male',
    }

    modified_user1_too_young = {
        'lastNname': 'Watt',
        'firstName': 'James',
        'phoneNumber': '+44 871 222 3330',
        'email': 'james.watt@example.com',
        'birthDate': '2015-04-12',
        'gender': 'male',
    }

    modified_user1_malformed_phone_req = {
        'lastName': 'Tilton',
        'firstName': 'John',
        'phoneNumber': 'A92722736387',
        'email': 'john.tilton@jhj.jh',
        'birthDate': '1981-04-04',
        'gender': 'male',
    }

    modified_user1_malformed_email_req = {
        'lastName': 'Tilton',
        'firstName': 'John',
        'phoneNumber': '92722736387',
        'email': 'john.tilton.example.com',
        'birthDate': '1981-04-04',
        'gender': 'male',
    }

    user_id_wrong = 99

    def setUp(self):
        super(UserTestCase, self).setUp()
        self.url1 = resources.api.url_for(resources.User,
                                          user_id=self.user1_id,
                                          _external=False)
        self.url_wrong = resources.api.url_for(resources.User,
                                               user_id=self.user_id_wrong,
                                               _external=False)

    def test_url(self):
        """
        Checks that the URL points to the right resource
        """
        print("(" + self.test_url.__name__ + ")", self.test_url.__doc__)
        url = "/flight-booking-system/api/users/1"
        with resources.app.test_request_context(url):
            rule = flask.request.url_rule
            view_point = resources.app.view_functions[rule.endpoint].view_class
            self.assertEqual(view_point, resources.User)

    def test_wrong_url(self):
        """
        Checks that GET User return correct status code if given a
        wrong user (non existing)
        """
        print("(" + self.test_wrong_url.__name__ + ")", self.test_wrong_url.__doc__)
        resp = self.client.get(self.url_wrong)
        self.assertEqual(resp.status_code, 404)

    def test_get_user(self):
        """
        Checks that GET user returns correct response
        with a correct user
        """
        print("(" + self.test_get_user.__name__ + ")", self.test_get_user.__doc__)
        with resources.app.test_client() as client:
            resp = client.get(self.url1)
            self.assertEqual(resp.status_code, 200)
            data = json.loads(resp.data.decode("utf-8"))

            self.assertIn("@namespaces", data)
            self.assertIn("user_id", data)
            self.assertIn("lastName", data)
            self.assertIn("firstName", data)
            self.assertIn("phoneNumber", data)
            self.assertIn("email", data)
            self.assertIn("birthDate", data)
            self.assertIn("gender", data)
            self.assertIn("registrationdate", data)
            self.assertIn("@controls", data)

            self.assertIn("flight-booking-system", data["@namespaces"])
            self.assertIn("name", data["@namespaces"]["flight-booking-system"])
            self.assertEqual(data["@namespaces"]["flight-booking-system"]["name"],
                             "/flight-booking-system/link-relations/")

            self.assertEqual(data["user_id"], self.user1_id)
            self.assertEqual(data["lastName"], self.user1["lastname"])
            self.assertEqual(data["firstName"], self.user1["firstname"])
            self.assertEqual(data["phoneNumber"], self.user1["phonenumber"])
            self.assertEqual(data["email"], self.user1["email"])
            self.assertEqual(data["birthDate"], self.user1["dateofBirth"])
            self.assertEqual(data["gender"], self.user1["gender"])
            self.assertEqual(data["registrationdate"], self.user1["registrationDate"])

            self.assertIn("self", data["@controls"])
            self.assertIn("profile", data["@controls"])
            self.assertIn("edit", data["@controls"])
            self.assertIn("flight-booking-system:delete", data["@controls"])
            self.assertIn("collection", data["@controls"])
            self.assertIn("flight-booking-system:reservations-history", data["@controls"])

            self.assertIn("href", data["@controls"]["self"])
            self.assertIn("href", data["@controls"]["profile"])
            self.assertIn("title", data["@controls"]["edit"])
            self.assertIn("href", data["@controls"]["edit"])
            self.assertIn("encoding", data["@controls"]["edit"])
            self.assertIn("method", data["@controls"]["edit"])
            self.assertIn("title", data["@controls"]["edit"])
            self.assertIn("href", data["@controls"]["flight-booking-system:delete"])
            self.assertIn("method", data["@controls"]["flight-booking-system:delete"])
            self.assertIn("href", data["@controls"]["flight-booking-system:delete"])
            self.assertIn("href", data["@controls"]["collection"])
            self.assertIn("method", data["@controls"]["collection"])
            self.assertIn("title", data["@controls"]["flight-booking-system:reservations-history"])
            self.assertIn("href", data["@controls"]["flight-booking-system:reservations-history"])
            self.assertIn("isHrefTemplate", data["@controls"]["flight-booking-system:reservations-history"])

            self.assertEqual(data["@controls"]["self"]["href"],
                             resources.api.url_for(resources.User, user_id=self.user1_id))
            self.assertEqual(data["@controls"]["profile"]["href"], FLIGHT_BOOKING_SYSTEM_USER_PROFILE)
            self.assertEqual(data["@controls"]["edit"]["href"],
                             resources.api.url_for(resources.User, user_id=self.user1_id))
            self.assertEqual(data["@controls"]["edit"]["encoding"], JSON)
            self.assertEqual(data["@controls"]["edit"]["method"].lower(), "put")
            self.assertEqual(data["@controls"]["edit"]["schemaUrl"], USER_SCHEMA_URL)
            self.assertEqual(data["@controls"]["flight-booking-system:delete"]["href"],
                             resources.api.url_for(resources.User, user_id=self.user1_id))
            self.assertEqual(data["@controls"]["flight-booking-system:delete"]["method"].lower(), "delete")
            self.assertEqual(data["@controls"]["collection"]["href"].lower(), resources.api.url_for(resources.Users))
            self.assertEqual(data["@controls"]["collection"]["method"].lower(), "get")
            self.assertEqual(data["@controls"]["flight-booking-system:reservations-history"]["href"],
                             resources.api.url_for(resources.UserReservations, user_id=self.user1_id))
            self.assertEqual(data["@controls"]["flight-booking-system:reservations-history"]["isHrefTemplate"], "true")

    def test_get_user_mimetype(self):
        """
        Checks that GET User return correct status code and data format
        """
        print("(" + self.test_get_user_mimetype.__name__ + ")", self.test_get_user_mimetype.__doc__)

        # Check that I receive status code 200
        resp = self.client.get(self.url1)
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(resp.headers.get("Content-Type", None),
                         "{};{}".format(MASONJSON, FLIGHT_BOOKING_SYSTEM_USER_PROFILE))

    def test_get_nonexisting_user(self):
        """
        Checks that GET User returns correct status and data
        with a nonexisting user id
        """
        print("(" + self.test_get_nonexisting_user.__name__ + ")", self.test_get_nonexisting_user.__doc__)

        # Check that we have 404 not found
        resp = self.client.get(self.url_wrong)
        self.assertEqual(resp.status_code, 404)
        err_data = json.loads(resp.data.decode("utf-8"))

        self.assertIn("@error", err_data)
        self.assertIn("resource_url", err_data)

        error = err_data["@error"]
        self.assertIn("@message", error)
        self.assertIn("@messages", error)

        self.assertEqual(err_data["resource_url"],
                         resources.api.url_for(resources.User, user_id=self.user_id_wrong, _external=False))

    def test_modify_user(self):
        """
        Checks that PUT User modifies the user correctly in the system
        and returns correct response
        """
        print("(" + self.test_modify_user.__name__ + ")", self.test_modify_user.__doc__)
        # Send PUT request
        resp = self.client.put(self.url1,
                               data=json.dumps(self.modified_user1_req),
                               headers={"Content-Type": JSON})

        self.assertEqual(resp.status_code, 204)

        # Check that the message has been modified
        resp2 = self.client.get(self.url1)
        self.assertEqual(resp2.status_code, 200)
        data = json.loads(resp2.data.decode("utf-8"))
        # Check the information of the user
        self.assertEqual(data["lastName"], self.modified_user1_req["lastName"])
        self.assertEqual(data["firstName"], self.modified_user1_req["firstName"])
        self.assertEqual(data["phoneNumber"], self.modified_user1_req["phoneNumber"])
        self.assertEqual(data["birthDate"], self.modified_user1_req["birthDate"])
        self.assertEqual(data["email"], self.modified_user1_req["email"])
        self.assertEqual(data["gender"], self.modified_user1_req["gender"])

    def test_modify_user_malformed_phone(self):
        """
            Checks that PUT User with malformed phone number
            returns correct response code
        """
        print("(" + self.test_modify_user_malformed_phone.__name__ + ")", self.test_modify_user_malformed_phone.__doc__)
        # Send PUT request
        resp = self.client.put(self.url1,
                               data=json.dumps(self.modified_user1_malformed_phone_req),
                               headers={"Content-Type": JSON})

        self.assertEqual(resp.status_code, 400)

    def test_modify_user_malformed_email(self):
        """
            Checks that PUT User with malformed email
            returns correct response code
        """
        print("(" + self.test_modify_user_malformed_email.__name__ + ")", self.test_modify_user_malformed_email.__doc__)
        # Send PUT request
        resp = self.client.put(self.url1,
                               data=json.dumps(self.modified_user1_malformed_email_req),
                               headers={"Content-Type": JSON})

        self.assertEqual(resp.status_code, 400)

    def test_modify_user_malformed_birthdate(self):
        """
            Checks that PUT User with malformed birth date
            returns correct response code
        """
        print("(" + self.test_modify_user_malformed_birthdate.__name__ + ")",
              self.test_modify_user_malformed_birthdate.__doc__)

        # Set a malformed email
        modified_user_malformed_birthdate_req = dict(self.modified_user1_req)
        modified_user_malformed_birthdate_req["birthDate"] = "21-04-1996"

        # Send PUT request
        resp = self.client.put(self.url1,
                               data=json.dumps(modified_user_malformed_birthdate_req),
                               headers={"Content-Type": JSON})

        self.assertEqual(resp.status_code, 400)

    def test_modify_user_too_young(self):
        """
            Checks that PUT User with a birth date < 18 years old
            returns correct response code
        """
        print("(" + self.test_modify_user_too_young.__name__ + ")",
              self.test_modify_user_too_young.__doc__)

        # Send PUT request
        resp = self.client.put(self.url1,
                               data=json.dumps(self.modified_user1_too_young),
                               headers={"Content-Type": JSON})

        self.assertEqual(resp.status_code, 400)

    def test_modify_nonexisting_user(self):
        """
            Checks that PUT User with a nonexisting user id
            returns correct response code
        """
        print("(" + self.test_modify_nonexisting_user.__name__ + ")",
              self.test_modify_nonexisting_user.__doc__)

        # Send PUT request
        resp = self.client.put(self.url_wrong,
                               data=json.dumps(self.modified_user1_req),
                               headers={"Content-Type": JSON})

        self.assertEqual(resp.status_code, 404)

    def test_delete_user(self):
        """
            Checks that DELETE User with a correct user id
            returns correct response code and deletes user in the system
        """
        print("(" + self.test_delete_user.__name__ + ")", self.test_delete_user.__doc__)

        # Send DELETE request
        resp = self.client.delete(self.url1)
        self.assertEqual(resp.status_code, 204)

        # Checks that user does not exist in the system
        resp2 = self.client.get(self.url1)
        self.assertEqual(resp2.status_code, 404)

    def test_delete_nonexisting_user(self):
        """
            Checks that DELETE User with a nonexisting user id
            returns correct response code
        """
        print("(" + self.test_delete_nonexisting_user.__name__ + ")", self.test_delete_nonexisting_user.__doc__)

        # Send DELETE request
        resp = self.client.delete(self.url_wrong)
        self.assertEqual(resp.status_code, 404)

    def test_modify_user_wrong_type(self):
        """
        Checks PUT User returns correct status code with wrong Content-Type
        """
        print("(" + self.test_modify_user_wrong_type.__name__ + ")", self.test_modify_user_wrong_type.__doc__)
        resp = self.client.put(self.url1,
                               data=json.dumps(self.modified_user1_req),
                               headers={"Content-Type": "text/html"})
        self.assertEqual(resp.status_code, 415)


class UsersTestCase(ResourcesAPITestCase):
    user1_list_object = {
        'userid': 1,
        'lastname': 'Tilton',
        'firstname': 'John',
        'registrationdate': 1519423463929,
    }

    user2_list_object = {
        'userid': 2,
        'lastname': 'Sam',
        'firstname': 'Jacob',
        'registrationdate': 1519423463929,
    }

    new_user = {
        'lastname': 'Larue',
        'firstname': 'Jules',
        'phonenumber': '+33065837465',
        'email': 'jules.larue@example.com',
        'dateofBirth': '1996-07-28',
        'gender': 'Male',
    }

    new_user_malformed_birthdate = {
        'lastname': 'Larue',
        'firstname': 'Jules',
        'phonenumber': '+33065837465',
        'email': 'jules.larue@example.com',
        'dateofBirth': '28-07-1996',
        'gender': 'Male',
    }

    new_user_too_young = {
        'lastname': 'Larue',
        'firstname': 'Jules',
        'phonenumber': '+33065837465',
        'email': 'jules.larue@example.com',
        'dateofBirth': '2017-07-28',
        'gender': 'Male',
    }

    new_user_malformed_phone_number = {
        'lastname': 'Tilton',
        'firstname': 'John',
        'phonenumber': 'P 92722736387',
        'email': 'john.tilton2@jhj.jh',
        'dateofBirth': '1981-04-04',
        'gender': 'male',
    }

    new_user_malformed_email = {
        'lastname': 'Tilton',
        'firstname': 'John',
        'phonenumber': '92722736387',
        'email': 'john.tilton.example.com',
        'dateofBirth': '1981-04-04',
        'gender': 'male',
    }

    new_user_existing_email = {
        'lastname': 'Tilton',
        'firstname': 'John',
        'phonenumber': '92722736387',
        'email': 'john.tilton@jhj.jh',
        'dateofBirth': '1981-04-04',
        'gender': 'male',
    }

    def setUp(self):
        super(UsersTestCase, self).setUp()
        self.url = resources.api.url_for(resources.Users, _external=False)

    def test_url(self):
        """
        Checks that the URL points to the right resource
        """
        print("(" + self.test_url.__name__ + ")", self.test_url.__doc__)
        url = "/flight-booking-system/api/users"
        with resources.app.test_request_context(url):
            rule = flask.request.url_rule
            view_point = resources.app.view_functions[rule.endpoint].view_class
            self.assertEqual(view_point, resources.Users)

    def test_get_users(self):
        """
        Checks that GET Users returns correct response
        with correct users
        """
        print("(" + self.test_get_users.__name__ + ")", self.test_get_users.__doc__)
        with resources.app.test_client() as client:
            resp = client.get(self.url)
            self.assertEqual(resp.status_code, 200)
            data = json.loads(resp.data.decode("utf-8"))

            # Check data
            # namespaces
            self.assertIn("@namespaces", data)
            self.assertIn("flight-booking-system", data["@namespaces"])
            self.assertIn("name", data["@namespaces"]["flight-booking-system"])
            self.assertEqual(data["@namespaces"]["flight-booking-system"]["name"], LINK_RELATIONS_URL)

            # items (users found)
            self.assertIn("items", data)
            for user in data["items"]:
                self.assertIn("user_id", user)
                self.assertIn("registrationdate", user)
                user_id = user["user_id"]

                self.assertIn("@controls", user)
                user_ctrl = user["@controls"]
                self.assertIn("self", user_ctrl)
                self.assertIn("href", user_ctrl["self"])
                self.assertEqual(user_ctrl["self"]["href"], resources.api.url_for(resources.User,
                                                                                  user_id=user_id))
                self.assertIn("profile", user_ctrl)
                self.assertIn("href", user_ctrl["profile"])
                self.assertEqual(user_ctrl["profile"]["href"], FLIGHT_BOOKING_SYSTEM_USER_PROFILE)

                self.assertIn("flight-booking-system:reservations-history", user_ctrl)
                user_history = user_ctrl["flight-booking-system:reservations-history"]
                self.assertIn("title", user_history)
                self.assertIn("href", user_history)
                self.assertEqual(user_history["href"], resources.api.url_for(resources.UserReservations,
                                                                             user_id=user_id))
                self.assertIn("isHrefTemplate", user_history)
                self.assertEqual(user_history["isHrefTemplate"], "true")
            # End for users (items)

            self.assertIn("@controls", data)
            self.assertIn("self", data["@controls"])
            self.assertIn("href", data["@controls"]["self"])
            self.assertEqual(data["@controls"]["self"]["href"], resources.api.url_for(resources.Users))
            self.assertIn("flight-booking-system:add-user", data["@controls"])
            self.assertIn("title", data["@controls"]["flight-booking-system:add-user"])
            self.assertIn("href", data["@controls"]["flight-booking-system:add-user"])
            self.assertEqual(data["@controls"]["flight-booking-system:add-user"]["href"],
                             resources.api.url_for(resources.Users))
            self.assertIn("encoding", data["@controls"]["flight-booking-system:add-user"])
            self.assertEqual(data["@controls"]["flight-booking-system:add-user"]["encoding"],
                             JSON)
            self.assertIn("method", data["@controls"]["flight-booking-system:add-user"])
            self.assertEqual(data["@controls"]["flight-booking-system:add-user"]["method"].lower(),
                             "post")
            self.assertIn("schemaUrl", data["@controls"]["flight-booking-system:add-user"])
            self.assertEqual(data["@controls"]["flight-booking-system:add-user"]["schemaUrl"],
                             USER_SCHEMA_URL)

    def test_add_user(self):
        """
        Checks that POST User returns correct status code and adds the user to the system
        """
        print("(" + self.test_add_user.__name__ + ")", self.test_add_user.__doc__)

        # Make POST request
        resp = self.client.post(resources.api.url_for(resources.Users),
                                headers={"Content-Type": JSON},
                                data=json.dumps(self.new_user))

        self.assertEqual(resp.status_code, 201)
        self.assertIn("Location", resp.headers)
        url = resp.headers["Location"]
        resp2 = self.client.get(url)
        self.assertEqual(resp2.status_code, 200)

    def test_add_user_malformed_email(self):
        """
            Checks that POST User with a malformed email returns correct status code
        """
        print("(" + self.test_add_user_malformed_email.__name__ + ")", self.test_add_user_malformed_email.__doc__)
        resp = self.client.post(resources.api.url_for(resources.Users),
                                headers={"Content-Type": JSON},
                                data=json.dumps(self.new_user_malformed_email))

        self.assertEqual(resp.status_code, 400)

    def test_add_user_existing_email(self):
        """
            Checks that POST User with an existing email returns correct status code
        """
        print("(" + self.test_add_user_existing_email.__name__ + ")", self.test_add_user_existing_email.__doc__)
        resp = self.client.post(resources.api.url_for(resources.Users),
                                headers={"Content-Type": JSON},
                                data=json.dumps(self.new_user_existing_email))

        self.assertEqual(resp.status_code, 409)

    def test_add_user_malformed_phone(self):
        """
            Checks that POST User with an malformed phone returns correct status code
        """
        print("(" + self.test_add_user_malformed_phone.__name__ + ")", self.test_add_user_malformed_phone.__doc__)
        resp = self.client.post(resources.api.url_for(resources.Users),
                                headers={"Content-Type": JSON},
                                data=json.dumps(self.new_user_malformed_phone_number))

        self.assertEqual(resp.status_code, 400)

    def test_add_user_malformed_birthdate(self):
        """
            Checks that POST User with an malformed birth date returns correct status code
        """
        print("(" + self.test_add_user_malformed_birthdate.__name__ + ")",
              self.test_add_user_malformed_birthdate.__doc__)
        resp = self.client.post(resources.api.url_for(resources.Users),
                                headers={"Content-Type": JSON},
                                data=json.dumps(self.new_user_malformed_birthdate))

        self.assertEqual(resp.status_code, 400)

    def test_add_user_too_young(self):
        """
            Checks that POST User with an birth date > 18 years old
             returns correct status code
        """
        print("(" + self.test_add_user_too_young.__name__ + ")",
              self.test_add_user_too_young.__doc__)
        resp = self.client.post(resources.api.url_for(resources.Users),
                                headers={"Content-Type": JSON},
                                data=json.dumps(self.new_user_too_young))

        self.assertEqual(resp.status_code, 400)

    def test_add_user_wrong_type(self):
        """
        Checks that POST User with a wrong Content-Type returns correct status code
        """
        print("(" + self.test_add_user_wrong_type.__name__ + ")",
              self.test_add_user_wrong_type.__doc__)
        resp = self.client.post(resources.api.url_for(resources.Users),
                                headers={"Content-Type": "text/html"},
                                data=json.dumps(self.new_user))

        self.assertEqual(resp.status_code, 415)

    def test_get_users_mimetype(self):
        """
        Checks that GET Users return correct status code and data format
        """
        print("(" + self.test_get_users_mimetype.__name__ + ")", self.test_get_users_mimetype.__doc__)

        # Check that I receive status code 200
        resp = self.client.get(self.url)
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(resp.headers.get("Content-Type", None),
                         "{};{}".format(MASONJSON, FLIGHT_BOOKING_SYSTEM_USER_PROFILE))


class ReservationTestCase(ResourcesAPITestCase):
    reservation11_id = 11
    reservation11 = {
        "reference": "AB12CS",
        "re_date": "2018-02-20",
        "user_id": 1,
        "flight_id": 1111
    }
    reservation22_id = 22
    reservation_id_wrong = 888

    def setUp(self):
        super(ReservationTestCase, self).setUp()

        self.url1 = resources.api.url_for(resources.Reservation,
                                          reservation_id=self.reservation11_id,
                                          _external=False)
        self.url2 = resources.api.url_for(resources.Reservation,
                                          reservation_id=self.reservation22_id,
                                          _external=False)
        self.url_wrong = resources.api.url_for(resources.Reservation,
                                               reservation_id=self.reservation_id_wrong,
                                               _external=False)

    def test_url(self):
        """
        Checks that the URL points to the right resource
        """
        print("(" + self.test_url.__name__ + ")", self.test_url.__doc__)
        url = "/flight-booking-system/api/reservations/11"
        with resources.app.test_request_context(url):
            rule = flask.request.url_rule
            view_point = resources.app.view_functions[rule.endpoint].view_class
            self.assertEqual(view_point, resources.Reservation)

    def test_wrong_url(self):
        """
        Checks that GET Reservation return correct status code if given a
        wrong reservation (non existing)
        """
        print("(" + self.test_wrong_url.__name__ + ")", self.test_wrong_url.__doc__)
        resp = self.client.get(self.url_wrong)
        self.assertEqual(resp.status_code, 404)

    def test_get_reservation(self):
        """
        Checks that GET Reservation returns correct status code and
        response
        """
        print("(" + self.test_get_reservation.__name__ + ")", self.test_get_reservation.__doc__)
        with resources.app.test_client() as client:
            resp = client.get(self.url1)
            self.assertEqual(resp.status_code, 200)
            data = json.loads(resp.data.decode("utf-8"))

            self.assertIn("@namespaces", data)
            self.assertIn("flight-booking-system", data["@namespaces"])
            self.assertIn("name", data["@namespaces"]["flight-booking-system"])
            self.assertIn(data["@namespaces"]["flight-booking-system"]["name"], LINK_RELATIONS_URL)

            # Reservation attributes
            self.assertIn("reservationid", data)
            self.assertEqual(data["reservationid"], self.reservation11_id)
            self.assertIn("reference", data)
            self.assertEqual(data["reference"], self.reservation11["reference"])
            self.assertIn("re_date", data)
            self.assertEqual(data["re_date"], self.reservation11["re_date"])
            self.assertIn("user_id", data)
            self.assertEqual(data["user_id"], self.reservation11["user_id"])
            self.assertIn("flight_id", data)
            self.assertEqual(data["flight_id"], self.reservation11["flight_id"])

            self.assertIn("@controls", data)
            self.assertIn("self", data["@controls"])
            self.assertIn("href", data["@controls"]["self"])
            self.assertEqual(data["@controls"]["self"]["href"], resources.api.url_for(resources.Reservation,
                                                                                      reservation_id=self.reservation11_id))

            self.assertIn("profile", data["@controls"])
            self.assertIn("href", data["@controls"]["profile"])
            self.assertEqual(data["@controls"]["profile"]["href"], FLIGHT_BOOKING_SYSTEM_RESERVATION_PROFILE)

            self.assertIn("flight-booking-system:delete", data["@controls"])
            self.assertIn("title", data["@controls"]["flight-booking-system:delete"])
            self.assertIn("href", data["@controls"]["flight-booking-system:delete"])
            self.assertEqual(data["@controls"]["flight-booking-system:delete"]["href"],
                             resources.api.url_for(resources.Reservation, reservation_id=self.reservation11_id))
            self.assertIn("encoding", data["@controls"]["flight-booking-system:delete"])
            self.assertEqual(data["@controls"]["flight-booking-system:delete"]["encoding"], JSON)
            self.assertIn("method", data["@controls"]["flight-booking-system:delete"])
            self.assertEqual(data["@controls"]["flight-booking-system:delete"]["method"].lower(), "delete")

            self.assertIn("author", data["@controls"])
            self.assertIn("href", data["@controls"]["author"])
            self.assertEqual(data["@controls"]["author"]["href"],
                             resources.api.url_for(resources.User, user_id=data["user_id"]))
            self.assertIn("method", data["@controls"]["author"])
            self.assertEqual(data["@controls"]["author"]["method"].lower(), "get")

            self.assertIn("subsection", data["@controls"])
            self.assertIn("title", data["@controls"]["subsection"])
            self.assertIn("href", data["@controls"]["subsection"])
            self.assertEqual(data["@controls"]["subsection"]["href"],
                             resources.api.url_for(resources.Flight, flight_id=data["flight_id"]))
            self.assertIn("encoding", data["@controls"]["subsection"])
            self.assertEqual(data["@controls"]["subsection"]["encoding"], JSON)
            self.assertIn("method", data["@controls"]["subsection"])
            self.assertEqual(data["@controls"]["subsection"]["method"].lower(), "get")

    def test_get_nonexsting_reservation(self):
        """
        Checks that GET Reservation with nonexisting id
        returns correct response
        """
        print("(" + self.test_get_nonexsting_reservation.__name__ + ")", self.test_get_nonexsting_reservation.__doc__)
        resp = self.client.get(self.url_wrong)
        self.assertEqual(resp.status_code, 404)


    def test_delete_reservation(self):
        """
        Checks that DELETE Reservation returns correct response
        and deletes the reservation from the system
        """
        print("(" + self.test_delete_reservation.__name__ + ")", self.test_delete_reservation.__doc__)

        # Send DELETE request
        resp_del1 = self.client.delete(self.url1)
        self.assertEqual(resp_del1.status_code, 204)
        resp_del2 = self.client.delete(self.url2)
        self.assertEqual(resp_del2.status_code, 204)

        # Checks that reservations do not exist in the system
        resp_get1 = self.client.get(self.url1)
        self.assertEqual(resp_get1.status_code, 404)
        resp_get2 = self.client.get(self.url2)
        self.assertEqual(resp_get2.status_code, 404)


    def test_delete_nonexisting_oreservation(self):
        """
        Checks that DELETE Reservation with wrong id
        returns correct status code
        """
        print("(" + self.test_delete_nonexisting_oreservation.__name__ + ")", self.test_delete_nonexisting_oreservation.__doc__)
        resp = self.client.get(self.url_wrong)
        self.assertEqual(resp.status_code, 404)



class ReservationsTestCase(ResourcesAPITestCase):

    # New reservation (correct) with 2 tickets
    new_reservation = {
        'user_id': 3,
        'flight_id': 1122,
        "tickets": [
            {
                "firstName": "Jon",
                "familyName": "Doe",
                "age": 24,
                "gender": "male",
                "seat": "21A"
            },
            {
                "firstName": "Peter",
                "familyName": "Jackson",
                "age": 35,
                "gender": "male",
                "seat": "10B"
            }
        ]
    }

    # New reservation (correct) with 2 tickets
    new_reservation_already_made = {
        'user_id': 1,
        'flight_id': 1111,
        "tickets": [
            {
                "firstName": "Jon",
                "familyName": "Doe",
                "age": 24,
                "gender": "male",
                "seat": "21A"
            },
            {
                "firstName": "Peter",
                "familyName": "Jackson",
                "age": 35,
                "gender": "male",
                "seat": "10B"
            }
        ]
    }

    # new reservation with wrong creator
    new_reservation_wrong_userid = {
        'user_id': 40,
        'flight_id': 1122,
        "tickets": [
            {
                "firstName": "Jon",
                "familyName": "Doe",
                "age": 24,
                "gender": "male",
                "seat": "21A"
            },
            {
                "firstName": "Peter",
                "familyName": "Jackson",
                "age": 35,
                "gender": "male",
                "seat": "10B"
            }
        ]
    }

    # new reservation with wrong flight
    new_reservation_wrong_flightid = {
        'user__id': 3,
        'flight_id': 8754,
        "tickets": [
            {
                "firstName": "Jon",
                "familyName": "Doe",
                "age": 24,
                "gender": "male",
                "seat": "21A"
            },
            {
                "firstName": "Peter",
                "familyName": "Jackson",
                "age": 35,
                "gender": "male",
                "seat": "10B"
            }
        ]
    }

    # new reservation for a full flight
    new_reservation_full_flight = {
        'user_id': 1,
        'flight_id': 1133,
        "tickets": [
            {
                "firstName": "Jon",
                "familyName": "Doe",
                "age": 24,
                "gender": "male",
                "seat": "21A"
            },
            {
                "firstName": "Peter",
                "familyName": "Jackson",
                "age": 35,
                "gender": "male",
                "seat": "10B"
            }
        ]
    }

    def setUp(self):
        super(ReservationsTestCase, self).setUp()
        self.url = resources.api.url_for(resources.Reservations, _external=False)

    def test_url(self):
        """
        Checks that the URL points to the right resource
        """
        print("(" + self.test_url.__name__ + ")", self.test_url.__doc__)
        url = "/flight-booking-system/api/reservations"
        with resources.app.test_request_context(url):
            rule = flask.request.url_rule
            view_point = resources.app.view_functions['reservations'].view_class
            self.assertEqual(view_point, resources.Reservations)


    def test_add_reservation(self):
        """
        Checks that POST Reservations returns correct status code
        and creates the reservation in the system
        """
        print("(" + self.test_add_reservation.__name__ + ")", self.test_add_reservation.__doc__)

        # Send POST request
        resp = self.client.post(resources.api.url_for(resources.Reservations),
                                headers={"Content-Type": JSON},
                                data=json.dumps(self.new_reservation))

        self.assertEqual(resp.status_code, 201)
        self.assertIn("Location", resp.headers)
        url = resp.headers["Location"]
        resp2 = self.client.get(url)
        self.assertEqual(resp2.status_code, 200)


    def test_add_reservation_wrong_user(self):
        """
        Checks that POST Reservation with a wrong user id
        returns correct status code
        """
        print("(" + self.test_add_reservation_wrong_user.__name__ + ")", self.test_add_reservation_wrong_user.__doc__)

        # Send POST request
        resp = self.client.post(resources.api.url_for(resources.Reservations),
                                headers={"Content-Type": JSON},
                                data=json.dumps(self.new_reservation_wrong_userid))

        self.assertEqual(resp.status_code, 400)


    def test_add_reservation_wrong_flight(self):
        """
        Checks that POST Reservation with a wrong user id
        returns correct status code
        """
        print("(" + self.test_add_reservation_wrong_flight.__name__ + ")", self.test_add_reservation_wrong_flight.__doc__)

        # Send POST request
        resp = self.client.post(resources.api.url_for(resources.Reservations),
                                headers={"Content-Type": JSON},
                                data=json.dumps(self.new_reservation_wrong_flightid))

        self.assertEqual(resp.status_code, 400)


    def test_add_reservation_wrong_type(self):
        """
        Checks that POST Reservations with wrong Content-Type returns correct
        status code
        """
        print("(" + self.test_add_reservation_wrong_type.__name__ + ")", self.test_add_reservation_wrong_type.__doc__)

        # Send POST request
        resp = self.client.post(resources.api.url_for(resources.Reservations),
                                headers={"Content-Type": "text/html"},
                                data=json.dumps(self.new_reservation))

        self.assertEqual(resp.status_code, 415)


    def test_add_reservation_already_made(self):
        """
        Checks that POST Reservation with a user id that has already booked
        a flight with flight id returns correct status code
        """
        print("(" + self.test_add_reservation_already_made.__name__ + ")", self.test_add_reservation_already_made.__doc__)

        # Send POST request
        resp = self.client.post(resources.api.url_for(resources.Reservations),
                                headers={"Content-Type": JSON},
                                data=json.dumps(self.new_reservation_already_made))

        self.assertEqual(resp.status_code, 409)


    def test_add_reservation_full_flight(self):
        """
        Checks that POST Reservation for a full flight
         returns correct status code
        """
        print("(" + self.test_add_reservation_full_flight.__name__ + ")", self.test_add_reservation_full_flight.__doc__)

        # Send POST request
        resp = self.client.post(resources.api.url_for(resources.Reservations),
                                headers={"Content-Type": JSON},
                                data=json.dumps(self.new_reservation_full_flight))

        self.assertEqual(resp.status_code, 500)


class UserReservationsTestCase(ResourcesAPITestCase):

    user1_id = 1
    reservation11_id = 11
    reservation11_list_object = {
        'reference': 'AB12CS',
        'reservationdate': '2018-02-20'
    }
    user_wrong_id = 999

    def setUp(self):
        super(UserReservationsTestCase, self).setUp()

        self.url1 = resources.api.url_for(resources.UserReservations,
                                          user_id = self.user1_id,
                                          _external=False)
        self.url_wrong = resources.api.url_for(resources.UserReservations,
                                               user_id=self.user_wrong_id,
                                               _external=False)

    def test_url(self):
        """
        Checks that the URL points to the right resource
        """
        print("(" + self.test_url.__name__ + ")", self.test_url.__doc__)
        url = "/flight-booking-system/api/users/1/reservations"
        with resources.app.test_request_context(url):
            rule = flask.request.url_rule
            view_point = resources.app.view_functions[rule.endpoint].view_class
            self.assertEqual(view_point, resources.UserReservations)

    def test_wrong_url(self):
        """
        Checks that GET UserReservations return correct status code if given a
        wrong user (non existing)
        """
        print("(" + self.test_wrong_url.__name__ + ")", self.test_wrong_url.__doc__)
        resp = self.client.get(self.url_wrong)
        self.assertEqual(resp.status_code, 404)


    def test_get_user_reservations(self):
        """
        Checks that GET UserReservations returns correct status
        and response
        """
        print("(" + self.test_get_user_reservations.__name__ + ")", self.test_get_user_reservations.__doc__)
        with resources.app.test_client() as client:
            resp = client.get(self.url1)
            self.assertEqual(resp.status_code, 200)
            data = json.loads(resp.data.decode("utf-8"))

            self.assertIn("@namespaces", data)
            self.assertIn("flight-booking-system", data["@namespaces"])
            self.assertIn("name", data["@namespaces"]["flight-booking-system"])
            self.assertIn(data["@namespaces"]["flight-booking-system"]["name"], LINK_RELATIONS_URL)

            # Reservation attributes
            for reservation in data["items"]:
                self.assertIn("reservation_id", reservation)

                reservation_id = reservation["reservation_id"]
                if reservation_id == 11:
                    self.assertEqual(reservation["reservation_id"], self.reservation11_id)
                    self.assertIn("reference", reservation)
                    self.assertEqual(reservation["reference"], self.reservation11_list_object["reference"])
                    self.assertIn("re_date", reservation)
                    self.assertEqual(reservation["re_date"], self.reservation11_list_object["reservationdate"])

                self.assertIn("@controls", reservation)
                self.assertIn("self", reservation["@controls"])
                self.assertIn("href", reservation["@controls"]["self"])
                self.assertEqual(reservation["@controls"]["self"]["href"], resources.api.url_for(resources.Reservation,
                                                                                                 reservation_id=self.reservation11_id,
                                                                                                 _external=False))

                self.assertIn("profile", reservation["@controls"])
                self.assertIn("href", reservation["@controls"]["profile"])
                self.assertEqual(reservation["@controls"]["profile"]["href"], FLIGHT_BOOKING_SYSTEM_RESERVATION_PROFILE)

                self.assertIn("flight-booking-system:reservation-tickets", reservation["@controls"])
                self.assertIn("title", reservation["@controls"]["flight-booking-system:reservation-tickets"])
                self.assertIn("href", reservation["@controls"]["flight-booking-system:reservation-tickets"])
                self.assertEqual(reservation["@controls"]["flight-booking-system:reservation-tickets"]["href"],
                                 resources.api.url_for(resources.ReservationTickets,
                                                       reservation_id=reservation_id,
                                                       _external=False))
                self.assertIn("encoding", reservation["@controls"]["flight-booking-system:reservation-tickets"])
                self.assertEqual(reservation["@controls"]["flight-booking-system:reservation-tickets"]["encoding"], JSON)
                self.assertIn("method", reservation["@controls"]["flight-booking-system:reservation-tickets"])
                self.assertEqual(reservation["@controls"]["flight-booking-system:reservation-tickets"]["method"].lower(), "get")

                self.assertIn("flight-booking-system:add-ticket", reservation["@controls"])
                self.assertIn("title", reservation["@controls"]["flight-booking-system:add-ticket"])
                self.assertIn("href", reservation["@controls"]["flight-booking-system:add-ticket"])
                self.assertEqual(reservation["@controls"]["flight-booking-system:add-ticket"]["href"],
                                 resources.api.url_for(resources.Tickets, _external=False))
                self.assertIn("encoding", reservation["@controls"]["flight-booking-system:add-ticket"])
                self.assertEqual(reservation["@controls"]["flight-booking-system:add-ticket"]["encoding"], JSON)
                self.assertIn("method", reservation["@controls"]["flight-booking-system:add-ticket"])
                self.assertEqual(reservation["@controls"]["flight-booking-system:add-ticket"]["method"].lower(), "post")
                self.assertIn("schemaUrl", reservation["@controls"]["flight-booking-system:add-ticket"])
                self.assertEqual(reservation["@controls"]["flight-booking-system:add-ticket"]["schemaUrl"], TICKET_SCHEMA_URL)

            self.assertIn("@controls", data)
            self.assertIn("self", data["@controls"])
            self.assertIn("href", data["@controls"]["self"])
            self.assertEqual(data["@controls"]["self"]["href"], resources.api.url_for(resources.UserReservations,
                                                                                      user_id=self.user1_id,
                                                                                      _external=False))

            self.assertIn("author", data["@controls"])
            self.assertIn("title", data["@controls"]["author"])
            self.assertIn("href", data["@controls"]["author"])
            self.assertEqual(data["@controls"]["author"]["href"], resources.api.url_for(resources.User, user_id=self.user1_id, _external=False))
            self.assertIn("encoding", data["@controls"]["author"])
            self.assertEqual(data["@controls"]["author"]["encoding"], JSON)
            self.assertIn("method", data["@controls"]["author"])
            self.assertEqual(data["@controls"]["author"]["method"].lower(), "get")



    def test_get_user_reservations_mimetype(self):
        """
        Checks that GET UserReservations return correct status code and data format
        """
        print("(" + self.test_get_user_reservations_mimetype.__name__ + ")", self.test_get_user_reservations_mimetype.__doc__)

        # Check that I receive status code 200
        resp = self.client.get(self.url1)
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(resp.headers.get("Content-Type", None),
                         "{};{}".format(MASONJSON, FLIGHT_BOOKING_SYSTEM_RESERVATION_PROFILE))

class FlightTestCase(ResourcesAPITestCase):
    flight_id = 1111
    flight = {
        'searchresultid': 1234 ,
        'code': 'AY101',
        'price': 200,
        'departuredate':'2018-05-06',
        'arrivaldate':'2018-05-07',
        'gate':'GATE02' ,
        'totalseats':90,
        'seatsleft':10}
    flight_id_incorrect = 1155

    def setUp(self):
        super(FlightTestCase, self).setUp()

        self.url = resources.api.url_for(resources.Flight,
                                          flight_id=self.flight_id,
                                          _external=False)
        self.url_incorrect = resources.api.url_for(resources.Flight,
                                               flight_id=self.flight_id_incorrect,
                                               _external=False)

    def test_url(self):
        """
        Checks that the URL points to the right resource
        """
        print("(" + self.test_url.__name__ + ")", self.test_url.__doc__)
        url = "/flight-booking-system/api/flights/1111"
        with resources.app.test_request_context(url):
            rule = flask.request.url_rule
            view_point = resources.app.view_functions[rule.endpoint].view_class
            self.assertEqual(view_point, resources.Flight)

    def test_wrong_url(self):
        """
        Checks that GET Flight return correct status code if given a
        not existing flight id
        """
        print("(" + self.test_wrong_url.__name__ + ")", self.test_wrong_url.__doc__)
        resp = self.client.get(self.url_incorrect)
        self.assertEqual(resp.status_code, 404)

    def test_get_flight(self):
        """
        Checks that GET Flight returns correct status code and
        response
        """
        print("(" + self.test_get_flight.__name__ + ")", self.test_get_flight.__doc__)
        with resources.app.test_client() as client:
            resp = client.get(self.url)
            self.assertEqual(resp.status_code, 200)
            data = json.loads(resp.data.decode("utf-8"))

            self.assertIn("@namespaces", data)
            self.assertIn("flight-booking-system", data["@namespaces"])
            self.assertIn("name", data["@namespaces"]["flight-booking-system"])
            self.assertIn(data["@namespaces"]["flight-booking-system"]["name"], LINK_RELATIONS_URL)

            # Flight attributes
            self.assertIn("flight_id", data)
            self.assertEqual(data["flight_id"], self.flight_id)
            self.assertIn("code", data)
            self.assertEqual(data["code"], self.flight["code"])
            self.assertIn("price", data)
            self.assertEqual(data["price"], self.flight["price"])
            self.assertIn("gate", data)
            self.assertEqual(data["gate"], self.flight["gate"])
            self.assertIn("depDate", data)
            self.assertEqual(data["depDate"], self.flight["departuredate"])

            self.assertIn("arrDate", data)
            self.assertEqual(data["arrDate"], self.flight["arrivaldate"])

            self.assertIn("nbInitialSeats", data)
            self.assertEqual(data["nbInitialSeats"], self.flight["totalseats"])
            self.assertIn("nbSeatsLeft", data)
            self.assertEqual(data["nbSeatsLeft"], self.flight["seatsleft"])
            self.assertIn("template_id", data)
            self.assertEqual(data["template_id"], self.flight["searchresultid"])

            self.assertIn("@controls", data)

            self.assertIn("self", data["@controls"])
            self.assertIn("href", data["@controls"]["self"])
            self.assertEqual(data["@controls"]["self"]["href"], resources.api.url_for(resources.Flight,
                                                                                      flight_id=self.flight_id))

            self.assertIn("profile", data["@controls"])
            self.assertIn("href", data["@controls"]["profile"])
            self.assertEqual(data["@controls"]["profile"]["href"], FLIGHT_BOOKING_SYSTEM_FLIGHT_PROFILE)

            self.assertIn("collection", data["@controls"])
            self.assertIn("href", data["@controls"]["collection"])
            self.assertEqual(data["@controls"]["collection"]["href"], resources.api.url_for(resources.Flights, template_id=self.flight["searchresultid"]))
            self.assertIn("method", data["@controls"]["collection"])
            self.assertEqual(data["@controls"]["collection"]["method"].lower(), "get")

            self.assertIn("subsection", data["@controls"])
            self.assertIn("href", data["@controls"]["subsection"])
            self.assertEqual(data["@controls"]["subsection"]["href"],
                             resources.api.url_for(resources.TemplateFlights, template_id=self.flight["searchresultid"]))
            self.assertIn("method", data["@controls"]["subsection"])
            self.assertEqual(data["@controls"]["subsection"]["method"].lower(), "get")


            self.assertIn("flight-booking-system:make-reservation", data["@controls"])
            self.assertIn("title", data["@controls"]["flight-booking-system:make-reservation"])
    
            self.assertIn("href", data["@controls"]["flight-booking-system:make-reservation"])
            self.assertEqual(data["@controls"]["flight-booking-system:make-reservation"]["href"],
                             resources.api.url_for(resources.Reservations))
            self.assertIn("encoding", data["@controls"]["flight-booking-system:make-reservation"])
            self.assertEqual(data["@controls"]["flight-booking-system:make-reservation"]["encoding"], JSON)
            self.assertIn("method", data["@controls"]["flight-booking-system:make-reservation"])
            self.assertEqual(data["@controls"]["flight-booking-system:make-reservation"]["method"].lower(), "post")
            self.assertIn("schemaUrl", data["@controls"]["flight-booking-system:make-reservation"])
            self.assertEqual(data["@controls"]["flight-booking-system:make-reservation"]["schemaUrl"],
                             RESERVATION_SCHEMA_URL)

    def test_get_nonexisting_flight(self):
        """
        Checks that GET Flight returns correct status and data
        with a nonexisting flight id
        """
        print("(" + self.test_get_nonexisting_flight.__name__ + ")", self.test_get_nonexisting_flight.__doc__)

        # Check that we have 404 not found
        resp = self.client.get(self.url_incorrect)
        self.assertEqual(resp.status_code, 404)
        err_data = json.loads(resp.data.decode("utf-8"))

        self.assertIn("@error", err_data)
        self.assertIn("resource_url", err_data)

        error = err_data["@error"]
        self.assertIn("@message", error)
        self.assertIn("@messages", error)

        self.assertEqual(err_data["resource_url"],
                         resources.api.url_for(resources.Flight, flight_id=self.flight_id_incorrect, _external=False))

class FlightsTestCase(ResourcesAPITestCase):
    template1111_id = 1234
    flight = {
        'code': 'AY101',
        'price': 200,
        'departuredate':'2018-05-06',
        'arrivaldate':'2018-05-07',
        'gate':'GATE02' ,
        'totalseats':90,
        'seatsleft':10 }
    flight_id = 1111
    template_id_incorrect = 2222
    flight_wrong_id = 1144
    flight_new ={
        'searchresultid': 1237 ,
        'flightid':1144,
        'code': 'AY123',
        'price': 400,
        'departuredate':'2018-09-03',
        'arrivaldate':'2018-09-04',
        'gate':'GATE10' ,
        'totalseats':100,
        'seatsleft':15}

    flight_new_existing_code ={
        'searchresultid': 1234 ,
        'flightid':1145,
        'code': 'AY101',
        'price': 150,
        'departuredate':'2018-09-03',
        'arrivaldate':'2018-09-04',
        'gate':'GATE10' ,
        'totalseats':110,
        'seatsleft':14}

    flight_new_existing_flightid ={
        'searchresultid': 1234 ,
        'flightid':1111,
        'code': 'AY126',
        'price': 400,
        'departuredate':'2018-05-03',
        'arrivaldate':'2018-05-04',
        'gate':'GATE10' ,
        'totalseats':90,
        'seatsleft':13}

    flight_new_nonexisting_template ={
        'searchresultid': 1232 ,
        'flightid':1146,
        'code': 'AY125',
        'price': 500,
        'departuredate':'2018-08-03',
        'arrivaldate':'2018-08-04',
        'gate':'GATE10' ,
        'totalseats':95,
        'seatsleft':16}
    flight_new_malformed_gate ={
        'searchresultid': 1247 ,
        'flightid':1144,
        'code': 'AY124',
        'price': 300,
        'departuredate':'2018-09-03',
        'arrivaldate':'2018-09-04',
        'gate':'10' ,
        'totalseats':100,
        'seatsleft':15}


    def setUp(self):
        super(FlightsTestCase, self).setUp()

        self.url = resources.api.url_for(resources.Flights,
                                          template_id=self.template1111_id,
                                          _external=False)
        self.url_incorrect = resources.api.url_for(resources.Flights,
                                               template_id=self.template_id_incorrect,
                                               _external=False)

    def test_url(self):
        """
        Checks that the URL points to the right resource
        """
        print("(" + self.test_url.__name__ + ")", self.test_url.__doc__)
        url = "/flight-booking-system/api/template-flights/1234/flights"
        with resources.app.test_request_context(url):
            rule = flask.request.url_rule
            view_point = resources.app.view_functions[rule.endpoint].view_class
            self.assertEqual(view_point, resources.Flights)

    def test_wrong_url(self):
        """
        Checks that GET Flights return correct status code if given a
        not existing template id
        """
        print("(" + self.test_wrong_url.__name__ + ")", self.test_wrong_url.__doc__)
        resp = self.client.get(self.url_incorrect)
        self.assertEqual(resp.status_code, 404)

    def test_get_flights(self):
        """
        Checks that GET flights return correct status and response (for an existing template flight id)
        """
        print("(" + self.test_get_flights.__name__ + ")", self.test_get_flights.__doc__)
        with resources.app.test_client() as client:
            resp = client.get(self.url)
            self.assertEqual(resp.status_code, 200)
            data = json.loads(resp.data.decode("utf-8"))

            self.assertIn("@namespaces", data)
            self.assertIn("flight-booking-system", data["@namespaces"])
            self.assertIn("name", data["@namespaces"]["flight-booking-system"])
            self.assertIn(data["@namespaces"]["flight-booking-system"]["name"], LINK_RELATIONS_URL)

            # Flight attributes
            for flight in data["items"]:
                self.assertIn("flightid", flight)

                flight_id = self.flight_id
                if flight_id == 1111:
                    self.assertEqual(flight["flightid"], self.flight_id)
                    self.assertIn("code", flight)
                    self.assertEqual(flight["code"], self.flight["code"])
                    self.assertIn("price", flight)
                    self.assertEqual(flight["price"], self.flight["price"])
                    self.assertIn("gate", flight)
                    self.assertEqual(flight["gate"], self.flight["gate"])
                    self.assertIn("depDate", flight)
                    self.assertEqual(flight["depDate"], self.flight["departuredate"])
                    self.assertIn("arrDate", flight)
                    self.assertEqual(flight["arrDate"], self.flight["arrivaldate"])
                    self.assertIn("nbInitialSeats", flight)
                    self.assertEqual(flight["nbInitialSeats"], self.flight["totalseats"])
                    self.assertIn("nbSeatsLeft", flight)
                    self.assertEqual(flight["nbSeatsLeft"], self.flight["seatsleft"])
                    self.assertIn("template_id", flight)
                    self.assertEqual(flight["template_id"], self.template1111_id)
                
                self.assertIn("@controls", flight)

                self.assertIn("self", flight["@controls"])
                self.assertIn("href", flight["@controls"]["self"])
                self.assertEqual(flight["@controls"]["self"]["href"], resources.api.url_for(resources.Flight, flight_id=self.flight_id, _external=False))
                self.assertIn("profile", flight["@controls"])
                self.assertIn("href", flight["@controls"]["profile"])
                self.assertEqual(flight["@controls"]["profile"]["href"], FLIGHT_BOOKING_SYSTEM_FLIGHT_PROFILE)

                self.assertIn("flight-booking-system:make-reservation", flight["@controls"])
                self.assertIn("title", flight["@controls"]["flight-booking-system:make-reservation"])
    
                self.assertIn("href", flight["@controls"]["flight-booking-system:make-reservation"])
                self.assertEqual(flight["@controls"]["flight-booking-system:make-reservation"]["href"],
                             resources.api.url_for(resources.Reservations))
                self.assertIn("encoding", flight["@controls"]["flight-booking-system:make-reservation"])
                self.assertEqual(flight["@controls"]["flight-booking-system:make-reservation"]["encoding"], JSON)
                self.assertIn("method", flight["@controls"]["flight-booking-system:make-reservation"])
                self.assertEqual(flight["@controls"]["flight-booking-system:make-reservation"]["method"].lower(), "post")
                self.assertIn("schemaUrl", flight["@controls"]["flight-booking-system:make-reservation"])
                self.assertEqual(flight["@controls"]["flight-booking-system:make-reservation"]["schemaUrl"],
                             RESERVATION_SCHEMA_URL)

            self.assertIn("@controls", data)
            self.assertIn("self", data["@controls"])
            self.assertIn("href", data["@controls"]["self"])
            self.assertEqual(data["@controls"]["self"]["href"], resources.api.url_for(resources.Flights, template_id=self.template1111_id))

            self.assertIn("flight-booking-system:add-flight", data["@controls"])
            self.assertIn("title", data["@controls"]["flight-booking-system:add-flight"])
            self.assertIn("href", data["@controls"]["flight-booking-system:add-flight"])
            self.assertEqual(data["@controls"]["flight-booking-system:add-flight"]["href"],
                             resources.api.url_for(resources.Flights, template_id=self.template1111_id))
            self.assertIn("encoding", data["@controls"]["flight-booking-system:add-flight"])
            self.assertEqual(data["@controls"]["flight-booking-system:add-flight"]["encoding"], JSON)
            self.assertIn("method", data["@controls"]["flight-booking-system:add-flight"])
            self.assertEqual(data["@controls"]["flight-booking-system:add-flight"]["method"].lower(), "post")
            self.assertIn("schemaUrl", data["@controls"]["flight-booking-system:add-flight"])
            self.assertEqual(data["@controls"]["flight-booking-system:add-flight"]["schemaUrl"],
                             FLIGHT_SCHEMA_URL)

    def test_get_nonexisting_templateflight(self):
        """
        Checks that GET Flight returns correct status and data
        with a nonexisting user id
        """
        print("(" + self.test_get_nonexisting_templateflight.__name__ + ")", self.test_get_nonexisting_templateflight.__doc__)

        # Check that we have 404 not found
        resp = self.client.get(self.url_incorrect)
        self.assertEqual(resp.status_code, 404)
        err_data = json.loads(resp.data.decode("utf-8"))

        self.assertIn("@error", err_data)
        self.assertIn("resource_url", err_data)

        error = err_data["@error"]
        self.assertIn("@message", error)
        self.assertIn("@messages", error)

        self.assertEqual(err_data["resource_url"], resources.api.url_for(resources.Flights,template_id=self.template_id_incorrect,
                                               _external=False))

    def test_add_flight(self):
        """
        Checks that POST Flight returns correct status code and adds the flight to the system
        """
        print("(" + self.test_add_flight.__name__ + ")", self.test_add_flight.__doc__)

        # Make POST request
        resp = self.client.post(resources.api.url_for(resources.Flights,template_id=self.flight_new['searchresultid'], _external=False),
                                headers={"Content-Type": JSON},
                                data=json.dumps(self.flight_new))

        self.assertEqual(resp.status_code, 201)
        self.assertIn("Location", resp.headers)
        url = resp.headers["Location"]
        resp2 = self.client.get(url)
        self.assertEqual(resp2.status_code, 200)

    def test_add_flight_existing_flightid(self):
        """
            Checks that POST Flight with an existing code returns correct status code
        """
        print("(" + self.test_add_flight_existing_flightid.__name__ + ")", self.test_add_flight_existing_flightid.__doc__)
        resp = self.client.post(resources.api.url_for(resources.Flights, template_id=self.flight_new_existing_flightid['searchresultid']),
                                headers={"Content-Type": JSON},
                                data=json.dumps(self.flight_new_existing_flightid))

        self.assertEqual(resp.status_code, 409)

    def test_add_flight_malformed_gate(self):
        """
            Checks that POST Flight with a malformed gate returns correct status code
        """
        print("(" + self.test_add_flight_malformed_gate.__name__ + ")", self.test_add_flight_malformed_gate.__doc__)
        resp = self.client.post(resources.api.url_for(resources.Flights, template_id=self.flight_new_malformed_gate['searchresultid']),
                                headers={"Content-Type": JSON},
                                data=json.dumps(self.flight_new_malformed_gate))

        self.assertEqual(resp.status_code, 400)

    def test_add_flight_nonexisting_templateid(self):
        """
            Checks that POST Flight with an nonexisting template id returns correct status code
        """
        print("(" + self.test_add_flight_nonexisting_templateid.__name__ + ")", self.test_add_flight_nonexisting_templateid.__doc__)
        resp = self.client.post(resources.api.url_for(resources.Flights, template_id=self.flight_new_nonexisting_template['searchresultid']),
                                headers={"Content-Type": JSON},
                                data=json.dumps(self.flight_new_nonexisting_template))

        self.assertEqual(resp.status_code, 400)

class TemplateFlightTestCase(ResourcesAPITestCase):
    template_id = 1234
    templateflight = {
        'searchid': 1234 ,
        'origin': 'Finland',
        'destination': 'France',
        'departuretime': '20:52',
        'arrivaltime': '23:40',}

    template_id_incorrect = 65

    def setUp(self):
        super(TemplateFlightTestCase, self).setUp()

        self.url = resources.api.url_for(resources.TemplateFlight,
                                          template_id=self.template_id,
                                          _external=False)
        self.url_incorrect = resources.api.url_for(resources.TemplateFlight,
                                               template_id=self.template_id_incorrect,
                                               _external=False)

    def test_url(self):
        """
        Checks that the URL points to the right resource
        """
        print("(" + self.test_url.__name__ + ")", self.test_url.__doc__)
        url = "/flight-booking-system/api/template-flights/1234"
        with resources.app.test_request_context(url):
            rule = flask.request.url_rule
            view_point = resources.app.view_functions[rule.endpoint].view_class
            self.assertEqual(view_point, resources.TemplateFlight)

    def test_wrong_url(self):
        """
        Checks that GET Template Flight return correct status code if given a
        not existing template flight id
        """
        print("(" + self.test_wrong_url.__name__ + ")", self.test_wrong_url.__doc__)
        resp = self.client.get(self.url_incorrect)
        self.assertEqual(resp.status_code, 404)

    def test_get_templateflight(self):
        """
        Checks that GET Template Flight returns correct status code and
        response
        """
        print("(" + self.test_get_templateflight.__name__ + ")", self.test_get_templateflight.__doc__)
        with resources.app.test_client() as client:
            resp = client.get(self.url)
            self.assertEqual(resp.status_code, 200)
            data = json.loads(resp.data.decode("utf-8"))

            self.assertIn("@namespaces", data)
            self.assertIn("flight-booking-system", data["@namespaces"])
            self.assertIn("name", data["@namespaces"]["flight-booking-system"])
            self.assertIn(data["@namespaces"]["flight-booking-system"]["name"], LINK_RELATIONS_URL)

            # Flight attributes
            self.assertIn("tflight_id", data)
            self.assertEqual(data["tflight_id"], self.template_id)
            self.assertIn("dep_time", data)
            self.assertEqual(data["dep_time"], self.templateflight["departuretime"])
            self.assertIn("arr_time", data)
            self.assertEqual(data["arr_time"], self.templateflight["arrivaltime"])
            self.assertIn("origin", data)
            self.assertEqual(data["origin"], self.templateflight["origin"])
            self.assertIn("destination", data)
            self.assertEqual(data["destination"], self.templateflight["destination"])

            self.assertIn("@controls", data)

            self.assertIn("self", data["@controls"])
            self.assertIn("href", data["@controls"]["self"])
            self.assertEqual(data["@controls"]["self"]["href"], resources.api.url_for(resources.TemplateFlight,
                                                                                      template_id=self.template_id,_external=False))

            self.assertIn("profile", data["@controls"])
            self.assertIn("href", data["@controls"]["profile"])
            self.assertEqual(data["@controls"]["profile"]["href"], FLIGHT_BOOKING_SYSTEM_TEMPLATE_FLIGHT_PROFILE)

            self.assertIn("collection", data["@controls"])
            self.assertIn("href", data["@controls"]["collection"])
            self.assertEqual(data["@controls"]["collection"]["href"], resources.api.url_for(resources.TemplateFlights))
            self.assertIn("method", data["@controls"]["collection"])
            self.assertEqual(data["@controls"]["collection"]["method"].lower(), "get")

            self.assertIn("flight-booking-system:flights-scheduled", data["@controls"])
            self.assertIn("title", data["@controls"]["flight-booking-system:flights-scheduled"])
    
            self.assertIn("href", data["@controls"]["flight-booking-system:flights-scheduled"])
            self.assertEqual(data["@controls"]["flight-booking-system:flights-scheduled"]["href"],
                             resources.api.url_for(resources.Flights, template_id=self.template_id))
            self.assertIn("encoding", data["@controls"]["flight-booking-system:flights-scheduled"])
            self.assertEqual(data["@controls"]["flight-booking-system:flights-scheduled"]["encoding"], JSON)
            self.assertIn("method", data["@controls"]["flight-booking-system:flights-scheduled"])
            self.assertEqual(data["@controls"]["flight-booking-system:flights-scheduled"]["method"].lower(), "get")


    def test_get_nonexisting_templateflight(self):
        """
        Checks that GET Template Flight returns correct status and data
        with a nonexisting template flight id
        """
        print("(" + self.test_get_nonexisting_templateflight.__name__ + ")", self.test_get_nonexisting_templateflight.__doc__)

        # Check that we have 404 not found
        resp = self.client.get(self.url_incorrect)
        self.assertEqual(resp.status_code, 404)
        err_data = json.loads(resp.data.decode("utf-8"))

        self.assertIn("@error", err_data)
        self.assertIn("resource_url", err_data)

        error = err_data["@error"]
        self.assertIn("@message", error)
        self.assertIn("@messages", error)

        self.assertEqual(err_data["resource_url"],
                         resources.api.url_for(resources.TemplateFlight, template_id=self.template_id_incorrect, _external=False))

class TemplateFlightsTestCase(ResourcesAPITestCase):
    template_id_1234 = 1234
    template_id_1234 = {
    'origin': 'Finland',
    'destination': 'France',
    'departuretime': '20:52',
    'arrivaltime': '23:40',
    }
    new_tflight = {
    'searchid':5665,
    'origin': 'Oslo',
    'destination': 'Oulu',
    'departuretime': '19:30',
    'arrivaltime': '20:30',
    }

    def setUp(self):
        super(TemplateFlightsTestCase, self).setUp()
        self.url = resources.api.url_for(resources.TemplateFlights)

    def test_url(self):
        """
        Checks that the URL points to the right resource
        """
        print("(" + self.test_url.__name__ + ")", self.test_url.__doc__)
        url = "/flight-booking-system/api/template-flights/"
        with resources.app.test_request_context(url):
            rule = flask.request.url_rule
            view_point = resources.app.view_functions[rule.endpoint].view_class
            self.assertEqual(view_point, resources.TemplateFlights)


    def test_get_template_flights(self):
        """
        Checks that GET TemplateFlights returns correct status
        and response
        """
        print("(" + self.test_get_template_flights.__name__ + ")", self.test_get_template_flights.__doc__)
        with resources.app.test_client() as client:
            resp = client.get(self.url)
            self.assertEqual(resp.status_code, 200)
            data = json.loads(resp.data.decode("utf-8"))

            self.assertIn("@namespaces", data)
            self.assertIn("flight-booking-system", data["@namespaces"])
            self.assertIn("name", data["@namespaces"]["flight-booking-system"])
            self.assertIn(data["@namespaces"]["flight-booking-system"]["name"], LINK_RELATIONS_URL)

            # Reservation attributes
            for tflight in data["items"]:
                self.assertIn("search_id", tflight)
                tflight_id = self.template_id_1234 = 1234

                if tflight_id == 1234:
                    self.assertIn("@controls", tflight)
                    
            self.assertIn("@controls", data)
            self.assertIn("self", data["@controls"])
            self.assertIn("href", data["@controls"]["self"])
            self.assertEqual(data["@controls"]["self"]["href"], resources.api.url_for(resources.TemplateFlights))

            self.assertIn("flight-booking-system:add-template-flight", data["@controls"])
            self.assertIn("title", data["@controls"]["flight-booking-system:add-template-flight"])
            self.assertIn("href", data["@controls"]["flight-booking-system:add-template-flight"])
            self.assertEqual(data["@controls"]["flight-booking-system:add-template-flight"]["href"],
                             resources.api.url_for(resources.TemplateFlights))
            self.assertIn("encoding", data["@controls"]["flight-booking-system:add-template-flight"])
            self.assertEqual(data["@controls"]["flight-booking-system:add-template-flight"]["encoding"],JSON)
            self.assertIn("method", data["@controls"]["flight-booking-system:add-template-flight"])
            self.assertEqual(data["@controls"]["flight-booking-system:add-template-flight"]["method"].lower(),
                             "post")
            self.assertIn("schemaUrl", data["@controls"]["flight-booking-system:add-template-flight"])
            self.assertEqual(data["@controls"]["flight-booking-system:add-template-flight"]["schemaUrl"],
                             TEMPLATE_FLIGHT_SCHEMA_URL)
    
    def test_add_templateflight(self):
        """
        Checks that POST Template Flight returns correct status code and adds the template flight to the system
        """
        print("(" + self.test_add_templateflight.__name__ + ")", self.test_add_templateflight.__doc__)

        # Make POST request
        resp = self.client.post(resources.api.url_for(resources.TemplateFlights),
                                headers={"Content-Type": JSON},
                                data=json.dumps(self.new_tflight))

        self.assertEqual(resp.status_code, 201)
        self.assertIn("Location", resp.headers)
        url = resp.headers["Location"]
        resp2 = self.client.get(url)
        self.assertEqual(resp2.status_code, 200)

if __name__ == "__main__":
    print("Start running tests")
    unittest.main()