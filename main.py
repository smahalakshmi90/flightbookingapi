from werkzeug.serving import run_simple
from werkzeug.middleware.dispatcher import DispatcherMiddleware
from flight_reservation.resources import app as flight_reservation
from flight_reservation_admin.application import app as flight_reservation_admin

application = DispatcherMiddleware(flight_reservation, {
    '/flight-booking-system/admin': flight_reservation_admin
})
if __name__ == '__main__':
    run_simple('localhost', 8000, application,
               use_reloader=True, use_debugger=True, use_evalex=True)
