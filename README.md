# 12306-BOOKER

![version](https://img.shields.io/badge/version-1.0.0-blue.svg) ![license](https://img.shields.io/badge/license-MIT-blue.svg)

```____________  ________ _______    ________                                       
/_   \_____  \ \_____  \\   _  \  /  _____/                                       
 |   |/  ____/   _(__  </  /_\  \/   __  \                                        
 |   /       \  /       \  \_/   \  |__\  \                                       
 |___\_______ \/______  /\_____  /\_____  /                                       
             \/       \/       \/       \/                                        
   _____          __                  __________               __                 
  /  _  \  __ ___/  |_  ____          \______   \ ____   ____ |  | __ ___________ 
 /  /_\  \|  |  \   __\/  _ \   ______ |    |  _//  _ \ /  _ \|  |/ // __ \_  __ \
/    |    \  |  /|  | (  <_> ) /_____/ |    |   (  <_> |  <_> )    <\  ___/|  | \/
\____|__  /____/ |__|  \____/          |______  /\____/ \____/|__|_ \\___  >__|   
        \/                                    \/                   \/    \/       
```
 

This is a very simple project that can keep retrieving data of train tickets from https://kyfw.12306.cn until it catches one ticket which satisfyes ur schedual, written in python with libs: requests, etc.

Why?
A couple days ago, when ggf, my friend.. maybe, asked me that if i can write an application to book tickets automaticly. I said: 'well, emm.., urhah.. it depends'. But i thought it should be simple and i need a tool of this kind, because it's December and the new year is coming. Just 4 myself, ggf and fun.

## Table of Contents
- [12306-BOOKER](#12306-booker)
    - [Table of Contents](#table-of-contents)
    - [Demo](#demo)
    - [About De-Captcha](#about-de-captcha)
    - [Reporting Issues](#reporting-issues)
    - [Technical Support or Questions](#technical-support-or-questions)


## Demo
First clone the repository of course,
```sh
git clone https://github.com/benmooo/12306-auto-book.git
cd 12306-auto-book/t
```
Second, config the settings file
```sh
vim settings.py
# chang the username and password etc. then run:
py test_booker.py
```
The following code is a copy of test_booker.py
```py
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
```


## About De-Captcha
The de_captcha process is handled by [littlebigluo](http://littlebigluo.qicp.net:47720/), it is unstable because the server runs on his laptop. -_-... fine. I'm trying to build a simple model with tensorflow to de_captcha. I'm a green hand in deep learning, any suggestions and communications would be appreciated.


## Reporting Issues
[github](https://github.com/benmooo/12306-auto-book.git)


## Technical Support or Questions
My email: benmo0802@163.com
