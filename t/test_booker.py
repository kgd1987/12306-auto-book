# -*- coding: utf-8 -*-

import sys
import time

# Manage the search path to include the booker source
sys.path.insert(0, '..')
from booker.booker import Booker
from t.settings import *

def run():
    b = Booker(username, password) # new booker, this step will initialize a sesssion to interact with 'https://kyfw.12306.cn'
    b.goto_login_page()            # make a GET requsets to imiate human behavior            
    b.login()                      # depends on 'http://littlebigluo.qicp.net:47720/' which is a de_captcha system modeled by Keras, and i will improvve this issue later.

    b.get_user_status()            # make a POST requsets to imiate human behavior            
    b.get_user_contacts()          # retrieve the contacts of user, this data will be used for post passenger date to 12306 server
    b.goto_query_page()            # make a GET requsets to imiate human behavior            

    # init querier 
    b.init_querier(departure, destination, ticket_date,
                    ticket_type=ticket_type, monitor=monitor)
    # and then query tickets and then filte the query results.
    while True:
        query_result = b.query_tickets(train_id=train_id, depart_time_span=depart_time_span,
                                    acceptable_seat_type=acceptable_seat_type)
        time.sleep(query_interval)
        if query_result['items']:
            break
    # this step will resolve which train to buy for the passenger
    solution = b.resolve_tickets(passenger_name, query_result)

    # this is what happend when we click the "BOOK" button 
    b.make_an_order(solution)
    b.parse_initdc()               # extract important data of this order details from html, and it was done by js originally. 
    b.get_passenger_dtos()         # make a POST requsets to imiate browser behavior
    time.sleep(1)

    # this is wot happened when we choosed the passenger and click the 'submit' button
    b.check_order(solution)
    b.submit_order(solution)

    # click the 'confirm order'
    b.confirm_order(solution)
    time.sleep(1)

    # query orderid, this step might be failed, you can put it in a loop function
    order_id = b.query_orderid_inqueue()
    print(f'Got order id: {order_id}')

    # check book results
    ok = b.check_order_result()
    if ok:
        print(f'Book train tickets successfully, and check this: {solution}')
    else:
        print('something wrong with booker, check log at: xxxx')



if __name__ == "__main__":
    run()
