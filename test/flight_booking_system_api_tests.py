"""
Created on 26.01.2013
Modified on 05.02.2017
@author: ivan sanchez
@author: mika oja
@author: Jules LARUE
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



if __name__ == "__main__":
    print("Start running tests")
    unittest.main()
