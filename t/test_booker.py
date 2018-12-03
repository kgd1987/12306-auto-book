# -*- coding: utf-8 -*-

import sys
from datetime import date

# Manage the search path to include the booker souce
sys.path.insert(0, '..')
from booker.booker import Booker

# presettings
username = 'benmooo'
password = '*********'
departure = '杭州东'
destination = '徐州东'
passenger_name = 'John Doe'
ticket_type = 'ADULT'
ticket_date = str(date.today())
train_id = ('G40', 'G62', "G7610", "T32")
depart_time_span = ('10:00', '17:00')
acceptable_seat_type = ('二等座', '软卧')
monitor = 'ON'



b = Booker(username, password)
b.goto_login_page()
b.login()
b.get_user_status()
b.get_user_contacts()
b.goto_query_page()

# init querier and query tickets
b.init_querier(departure, destination, ticket_date, ticket_type=ticket_type, monitor=monitor)
query_result = b.query_tickets(train_id=train_id, depart_time_span=depart_time_span, acceptable_seat_type=acceptable_seat_type)
solution = b.resolve_tickets(passenger_name, query_result)

#click book button
b.make_an_order(solution)
b.parse_initdc()
b.get_passenger_dtos()

# submit order 
b.check_order(solution)
b.submit_order(solution)
# confirm order
b.confirm_order(solution)
# query orderid 
b.query_orderid_inqueue()
#check book results
b.check_order_result()

