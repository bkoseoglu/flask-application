from flask import Flask, request
from pony.orm import *
from flask_restful import Resource, Api
from models import *
import uuid, threading, timer
import random,time
import json
import pycountry
import datetime
import requests
from tasks import *

CAPACITY = 50
Countries = []
for country in pycountry.countries:
   Countries.append(country.alpha_3)

app = Flask(__name__)
api = Api(app)
app.config.update(
    CELERY_BROKER_URL='pyamqp://guest@localhost//',
    CELERY_RESULT_BACKEND='rpc://'
)

db.bind('sqlite', 'todo_api.db', create_db=True)
db.generate_mapping(create_tables=True)

API_URL = 'http://127.0.0.1:5000'

item_name = 'admin/details'
endpoint = '{}/{}'.format(API_URL, item_name)
celery = make_celery(app)
now= datetime.datetime.now()
clock = datetime.datetime.now()
clockIncrement = -1
#dateOfPassanger = datetime.datetime.now()
#nowToDate = now.strftime("%m-%d-%y")
increment = 0
#passangerIncrement = -1
def initialErase():
    with orm.db_session:
        for flight in Flight.select():
            Flight[flight.f_id].delete()



def keepClock(f_stop):
    global clockIncrement
    clockIncrement+=1
    global clock
    clock = clock + datetime.timedelta(days=+clockIncrement)
    if not f_stop.is_set():
        # call f() again in 60 seconds
        threading.Timer(60, keepClock, [clockThread]).start()

clockThread = threading.Event()
# start calling f now and every 60 sec thereafter
keepClock(clockThread)
initialErase()
@celery.task()
def create_new_flights():
    while True:
        global increment
        increment += 1
        #global passangerIncrement
        #passangerIncrement +=1
        #print(passangerIncrement)
        #global dateOfPassanger
        #dateOfPassanger = dateOfPassanger + datetime.timedelta(days=+passangerIncrement)
        #print(dateOfPassanger.strftime("%m-%d-%y"))
        global now
        date = now + datetime.timedelta(days=+increment)
        dateToDate = date.strftime("%m-%d-%y")
        now1 = time.time()
        print(now1)
        future = now1 + 60
        print
        count1 = 0
        #requests.get(endpoint)
        while time.time() < future:
            if(count1<10):
                with orm.db_session:
                    flight_id = str(uuid.uuid4().hex[:33].lower())
                    value = '{}-{}-{}-{}-{}-{}'.format(flight_id[:8], flight_id[8:12], flight_id[12:16], flight_id[16:20],
                                                           flight_id[20:24], flight_id[24:32])
                    dest = random.choice(Countries)
                    from_where = random.choice(Countries)
                    Flight(f_id=value, dest=dest, from_where=from_where, date=dateToDate)
                    count1+=1




result = create_new_flights.delay()

class Admin(Resource):
    def get(self):
        with orm.db_session:  # 1
            return {
                flight.f_id:{
                    'sale_amount_for_this flight': len(flight.tickets),
                    'revenue_for_this_flight': sum([ticket.price for ticket in flight.tickets]),
                }
                for flight in Flight.select()  # 2
            },200
class ListFlights(Resource):#superok
    def get(self):
        with orm.db_session:  # 1
            return {
                flight.f_id:{
                    'dest': flight.dest,
                    'from': flight.from_where,
                    'date':flight.date,
                    'u_id':flight.f_id
                }
                for flight in Flight.select()  # 2
            },200
                #result.append({"dest":f.dest,"from":f.from_where,"date":f.date,"uid":f.f_id})


class BuyRandomTicket(Resource):
    def get(self,flight_id):
        with orm.db_session:  # 1
            try:
                flight = Flight[flight_id]
                tickets_of_flight = [ticket.seat_num for ticket in flight.tickets]
                dateOfP = (clock + datetime.timedelta(days=+1)).strftime("%m-%d-%y")
                print(flight.date,"flight")
                print(dateOfP,"p")
                if(len(tickets_of_flight) != 50 and flight.date == dateOfP ):
                    seatNumbers = []
                    for seat_num in tickets_of_flight:
                        seatNumbers.append(seat_num)
                    seatNumber = random.choice(list(set(range(1,51))-set(seatNumbers)))
                    ticket_id = str(uuid.uuid4().hex[:33].lower())
                    value = '{}-{}-{}-{}-{}-{}'.format(ticket_id[:8], ticket_id[8:12], ticket_id[12:16],
                                                       ticket_id[16:20], ticket_id[20:24], ticket_id[24:32])
                    Ticket(t_id=value, flight=flight, seat_num=seatNumber, price=1 * (CAPACITY - (CAPACITY - len(tickets_of_flight)) + 1) * 10)
                    return {"flight_uid": flight.f_id, "msg":"ok", "seat_number": seatNumber, "ticket_uid": value}, 200
                else:
                    if(len(tickets_of_flight) == 50):
                        return {'msg':'flight is full'},404
                    else:
                        return{'msg':'you can only buy ticket one day before flight'},404
            except orm.ObjectNotFound:
                return {'status': 'no such flight'}, 404

class BuyTicket(Resource):
    def get(self,flight_id,seat_number):
        with orm.db_session:  # 1
            try:
                flight = Flight[flight_id]
                tickets_of_flight = [ticket.seat_num for ticket in flight.tickets]
                dateOfP = (clock + datetime.timedelta(days=+1)).strftime("%m-%d-%y")
                if(len(tickets_of_flight) != 50 and flight.date==dateOfP ):
                    if(seat_number in tickets_of_flight):
                        return {'msg': 'the seat is not avaliable to buy'},404
                    else:
                        ticket_id = str(uuid.uuid4().hex[:33].lower())
                        value = '{}-{}-{}-{}-{}-{}'.format(ticket_id[:8], ticket_id[8:12], ticket_id[12:16],
                                                           ticket_id[16:20], ticket_id[20:24], ticket_id[24:32])
                        Ticket(t_id=value, flight=flight, seat_num=seat_number, price=1 * (CAPACITY - (CAPACITY - len(tickets_of_flight)) + 1) * 10)
                        return {"flight_uid": flight.f_id, "msg":"ok", "seat_number": seat_number, "ticket_uid": value}, 200
                else:
                    if(len(tickets_of_flight) == 50):
                        return {'msg':'flight is full'},404
                    else:
                        return{'msg':'you can only buy ticket one day before flight'},404
            except orm.ObjectNotFound:
                return {'msg': 'no such flight'}, 404

class GetDetailsOfFlight(Resource): #superok
    def get(self,flight_id):
        notAvaliableSeats = []
        with orm.db_session:
            try:
                flight = Flight[flight_id]
                tickets_of_flight = [ticket for ticket in flight.tickets]
                numberOfPassangers = len(tickets_of_flight)
                if (numberOfPassangers == 0):
                    return {"dest": flight.dest, "from": flight.from_where, "date": flight.date, "uid": flight.f_id,'price':1 *(CAPACITY - (CAPACITY - numberOfPassangers) + 1) * 10,
                            "not_avaliable_seats": notAvaliableSeats}, 200
                elif (numberOfPassangers == CAPACITY):
                    return {"dest": flight.dest, "from": flight.from_where, "date": flight.date, "uid": flight.f_id,
                            "not_avaliable_seats": 'all seats'}, 200
                else:
                    for t in tickets_of_flight:
                        notAvaliableSeats.append(t.seat_num)
                    price = 1 * (CAPACITY - (CAPACITY - numberOfPassangers) + 1) * 10
                    return {"dest": flight.dest, "from": flight.from_where, "date": flight.date, "uid": flight.f_id,'price':1 *(CAPACITY - (CAPACITY - numberOfPassangers) + 1) * 10,
                            "not_avaliable_seats": notAvaliableSeats}, 200
            except orm.ObjectNotFound:
                return {'msg':'no such flight'},404


class AddFlight(Resource):#ok
    def get(self):
        with orm.db_session:
            dateOfFlight = clock + datetime.timedelta(days=+1)
            dateOfFlight = dateOfFlight.strftime("%m-%d-%y")
            flight_id = str(uuid.uuid4().hex[:33].lower())
            value = '{}-{}-{}-{}-{}-{}'.format(flight_id[:8],flight_id[8:12],flight_id[12:16],flight_id[16:20],flight_id[20:24],flight_id[24:32])
            dest = random.choice(Countries)
            from_where = random.choice(Countries)
            Flight(f_id=value,dest=dest,from_where=from_where,date= dateOfFlight)
        #random = ''.join([random.choice(string.ascii_letters + string.digits) for n in xrange(32)])
            return {'f_uid':value,'status':'added'},200
class TicketInformation(Resource):#superok
    def get(self,ticket_id):
        with orm.db_session:
            try:
                ticket = Ticket[ticket_id]
                return {"dest": ticket.flight.dest, "from": ticket.flight.from_where, "date": ticket.flight.date,
                        "uid": ticket.t_id, "seat_number": ticket.seat_num,
                        "price": ticket.price, "flight_uid": ticket.flight.f_id}, 200
            except orm.ObjectNotFound:
                return {'msg': 'no such ticket'}, 404

    def delete(self,ticket_id):
        with orm.db_session:
            try:
                Ticket[ticket_id].delete()
                return {'t_uid': ticket_id, 'status': 'deleted'}, 200
            except orm.ObjectNotFound:
                return {'msg':'ticket not found,so cannot delete'},404

class HelloWorld(Resource):
    def get(selfself):
        return "Welcome to airline ticket system"

api.add_resource(ListFlights, '/flights/')
api.add_resource(HelloWorld, '/')
api.add_resource(AddFlight,'/flights/add/')
api.add_resource(GetDetailsOfFlight,'/flight/<flight_id>')
api.add_resource(BuyRandomTicket,'/flight/<flight_id>/buy/')
api.add_resource(BuyTicket,'/flight/<flight_id>/buy/<int:seat_number>')
api.add_resource(TicketInformation,'/ticket/<ticket_id>')
api.add_resource(Admin,'/admin/details')




if __name__ == '__main__':
    app.run(debug=True)