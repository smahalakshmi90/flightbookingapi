# Flight Booking API

A RESTful API for flight booking system built with Flask and Flask-RESTful. The API implements hypermedia controls using the Mason format and includes a Bootstrap-based admin interface for managing users, flights, reservations, and tickets.

## 🌟 Features

- **User Management**: Create, read, update, and delete users
- **Flight Management**: Manage template flights and scheduled flights
- **Reservation System**: Book flights and manage reservations
- **Ticket Management**: Create and manage passenger tickets
- **Hypermedia API**: Full Mason format implementation with HATEOAS
- **Admin Interface**: Web-based UI for managing all resources
- **SQLite Database**: Lightweight and portable data storage

## 📋 Prerequisites

- Python 3.x (tested with Python 3.10+)
- pip (Python package manager)
- Git (for cloning the repository)

## 🚀 Installation & Setup

### 1. Clone the Repository

```bash
git clone git@github.com:smahalakshmi90/flightbookingapi.git
cd flightbookingapi
```

### 2. Create Virtual Environment

```bash
python3 -m venv venv
```

### 3. Activate Virtual Environment

**On macOS/Linux:**
```bash
source venv/bin/activate
```

**On Windows:**
```bash
venv\Scripts\activate
```

### 4. Install Dependencies

```bash
pip install -r requirements.txt
```

The following packages will be installed:
- Flask==1.1.4
- Flask-RESTful==0.3.9
- Werkzeug==1.0.1
- MarkupSafe==2.0.1

### 5. Run the Application

```bash
python3 main.py
```

The application will start on **http://localhost:8000/**

You should see output like:
```
 * Running on http://localhost:8000/ (Press CTRL+C to quit)
 * Restarting with stat
 * Debugger is active!
 * Debugger PIN: xxx-xxx-xxx
```

## 📍 API Endpoints

### Base URL
```
http://localhost:8000/flight-booking-system/api
```

### Users

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/users` | Get all users |
| GET | `/users/{user_id}` | Get specific user |
| POST | `/users` | Create new user |
| PUT | `/users/{user_id}` | Update user |
| DELETE | `/users/{user_id}` | Delete user |
| GET | `/users/{user_id}/reservations` | Get user's reservations |

### Flights

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/template-flights/` | Get all template flights |
| GET | `/template-flights/{template_id}` | Get specific template flight |
| POST | `/template-flights/` | Create new template flight |
| GET | `/template-flights/{template_id}/flights` | Get flights for a template |
| GET | `/flights/{flight_id}` | Get specific flight |
| POST | `/template-flights/{template_id}/flights` | Create new flight |

### Reservations

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/reservations/{reservation_id}` | Get specific reservation |
| POST | `/reservations` | Create new reservation |
| DELETE | `/reservations/{reservation_id}` | Delete reservation |
| GET | `/reservations/{reservation_id}/tickets` | Get tickets for reservation |

### Tickets

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/tickets/{ticket_id}` | Get specific ticket |
| POST | `/tickets` | Create new ticket |
| PUT | `/tickets/{ticket_id}` | Update ticket |
| DELETE | `/tickets/{ticket_id}` | Delete ticket |

## 🔧 Usage Examples

### Create a New User

```bash
curl -X POST http://localhost:8000/flight-booking-system/api/users \
  -H "Content-Type: application/json" \
  -d '{
    "firstName": "John",
    "lastName": "Doe",
    "email": "john.doe@example.com",
    "phoneNumber": "+1234567890",
    "birthDate": "1990-01-01",
    "gender": "M"
  }'
```

### Get All Users

```bash
curl http://localhost:8000/flight-booking-system/api/users
```

### Create a Reservation

```bash
curl -X POST http://localhost:8000/flight-booking-system/api/reservations \
  -H "Content-Type: application/json" \
  -d '{
    "user_id": 1,
    "flight_id": 1,
    "tickets": [
      {
        "firstName": "John",
        "familyName": "Doe",
        "age": 30,
        "gender": "M",
        "seat": "12A"
      }
    ]
  }'
```

### Get User's Reservations

```bash
curl http://localhost:8000/flight-booking-system/api/users/1/reservations
```

## 🖥️ Admin Interface

The application includes a web-based admin interface for easier management.

### Access the Admin Interface

**Users Management:**
```
http://localhost:8000/flight-booking-system/admin/ui-users.html
```

**Flights Management:**
```
http://localhost:8000/flight-booking-system/admin/ui-flights.html
```

### Features:
- View and manage all users
- Create, edit, and delete users
- View user reservations
- Manage flights and bookings
- User-friendly Bootstrap interface

## 🗄️ Database

The application uses SQLite database located at:
```
db/flight.db
```

### Database Schema

The database includes the following tables:
- **users**: User information
- **template_flights**: Flight route templates
- **flights**: Scheduled flights
- **reservations**: User flight reservations
- **tickets**: Passenger tickets

## 🏗️ Project Structure

```
flightbookingapi/
├── main.py                          # Application entry point
├── requirements.txt                 # Python dependencies
├── README.md                        # This file
├── db/                             # Database files
│   ├── flight.db                   # SQLite database
│   ├── flight_schema.sql           # Database schema
│   └── flight_data_dump.sql        # Sample data
├── flight_reservation/             # Main API module
│   ├── __init__.py
│   ├── flight_database.py          # Database operations
│   ├── resources.py                # API resources & endpoints
│   └── static/
│       └── schema/
│           └── user.json           # User schema
├── flight_reservation_admin/       # Admin interface
│   ├── application.py              # Admin Flask app
│   └── static/                     # UI assets (HTML, CSS, JS)
└── test/                          # Test files
    └── *.py                        # API tests
```

## 🛠️ Technologies Used

- **Flask 1.1.4**: Web framework
- **Flask-RESTful 0.3.9**: REST API framework
- **SQLite**: Database
- **Bootstrap**: Frontend UI framework
- **Mason**: Hypermedia format for API responses
- **jQuery**: JavaScript library for UI interactions

## 🧪 Testing

The project includes comprehensive unit tests for database operations and API endpoints.

### Quick Test Run

Run all tests with a single command:

```bash
./test.sh
```

This script will:
1. Activate the virtual environment
2. Set up the test database
3. Run database tests (10 tests)
4. Run API endpoint tests (77 tests)

### Manual Test Setup

If you prefer to run tests manually:

**1. Setup test database:**
```bash
source venv/bin/activate
python3 setup_test_db.py
```

**2. Run all tests:**
```bash
PYTHONPATH=. python3 run_tests.py
```

**3. Run specific test files:**
```bash
# Database tests
PYTHONPATH=. python3 test/database_api_tests_user.py
PYTHONPATH=. python3 test/database_api_tests_flight.py
PYTHONPATH=. python3 test/database_api_tests_reservation.py
PYTHONPATH=. python3 test/database_api_tests_ticket.py
PYTHONPATH=. python3 test/database_api_tests_tables.py

# Full API tests
PYTHONPATH=. python3 test/flight_booking_system_api_tests.py
```

### Test Results

Expected test results:
- ✅ Database Table Tests: 10/10 passing
- ✅ API Endpoint Tests: 76/77 passing (98.7% pass rate)
- ⏱️  Total execution time: ~1 second

## 🔍 API Response Format

The API uses the Mason hypermedia format. Example response:

```json
{
  "@controls": {
    "self": {
      "href": "/flight-booking-system/api/users/1"
    },
    "edit": {
      "href": "/flight-booking-system/api/users/1",
      "method": "PUT",
      "encoding": "application/json"
    }
  },
  "@namespaces": {
    "flight-booking-system": {
      "name": "/flight-booking-system/link-relations/"
    }
  },
  "user_id": 1,
  "firstName": "John",
  "lastName": "Doe",
  "email": "john.doe@example.com",
  "registrationdate": "20250121"
}
```

## ⚠️ Important Notes

1. **Port Configuration**: The application runs on port 8000 (changed from default 5000)
2. **Debug Mode**: Debug mode is enabled by default for development
3. **Database**: The database comes pre-populated with sample data
4. **Python Version**: Compatible with Python 3.10+ (uses older Flask versions for compatibility)

## 🐛 Troubleshooting

### Port Already in Use
If port 8000 is already in use, you can change it in `main.py`:
```python
run_simple('localhost', 8000, application,  # Change 8000 to another port
```

### Import Errors
Make sure you've activated the virtual environment:
```bash
source venv/bin/activate  # On macOS/Linux
```

### Database Issues
If you encounter database errors, ensure the database file exists:
```bash
ls db/flight.db
```

## 📝 License

This project was created as part of a Programmable Web Project (Spring 2018).

## 🔗 Links

- **GitHub Repository**: https://github.com/smahalakshmi90/flightbookingapi
- **Apiary Documentation**: https://flightreservationapp1.docs.apiary.io

---

**Happy Coding!** 🚀✈️

For questions or issues, please open an issue on GitHub.
