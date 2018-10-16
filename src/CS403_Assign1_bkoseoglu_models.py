# Inside models.py
from pony import orm  # 1
from pony.orm import show, db_session, PrimaryKey, Required, Set

db = orm.Database()  # 2


class Flight(db.Entity):
    f_id = PrimaryKey(str)
    dest = Required(str)
    from_where = Required(str)
    date = Required(str)
    tickets = Set('Ticket')


class Ticket(db.Entity):
    t_id = PrimaryKey(str)
    flight = Required('Flight')
    seat_num = Required(int)
    price = Required(int)



