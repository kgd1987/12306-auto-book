# -*- coding: utf-8 -*-

"""
this module implements the central booker object.
"""

import requests
from datetime import date
from time import strptime
from urllib.parse import unquote
# from time import sleep
from booker.verify_captcha import verify_captcha
from booker.consts import urls, headers, captcha_path
from booker.tickets_querier import Querier


class Booker():
    def __init__(self, username, passwd):
        # self.num = 1
        self.username = username
        self.passwd = passwd
        # mantained data
        self.err = False
        self.contacts = None
        self.repeat_submit_token = None
        # initialize a session 
        self.session = requests.Session()
        self.session.headers.update(headers)

    # def req(self, url, method='GET', **kwargs):
    #     if method == 'GET':
    #         return self.session.get(url, kwargs)
    #     else:
    #         return self.session.post(url, kwargs)

    # check if something is wrong
    def has_err(self):
        return self.err

    # check if user is logged in or not
    def user_is_loggedin(self):
        res = self.session.get(urls['check_user'])
        try:
            return res.json()['data']['flag']
        except:
            return False

    # go to the login page to imitate human actons
    def goto_login_page(self):
        self.session.get(urls['login_url'])

    # login 
    def login(self):
        if self.user_is_loggedin():
            return True
        self.goto_login_page()
        # get captcha and verify
        res = self.session.get(urls['get_captcha'])
        with open(captcha_path, 'wb') as f:
            f.write(res.content)
        data = {
            # 'answer': verify_captcha(captcha_path),
            'answer': verify_captcha(),
            'login_site': 'E',
            'rand': 'sjrand'
        }
        resp = self.session.post(urls['verify_captcha'], data=data)
        if resp.json()['result_code'] == '4':
            # user login
            user = {
                'username' :self.username,
                'password' :self.passwd,
                'appid': 'otn'
            }
            resp = self.session.post(urls['web_login'], data=user)
            if resp.json()['result_code'] == 0:
                # web authorization
                resp = self.session.post(urls['web_auth'], data={'appid': 'otn'})
                token = resp.json()['newapptk']
                # otn authrization
                resp = self.session.post(urls['otn_auth'], data={'tk': token})
                print(resp.text)
        else:
            print('login failed...')
            self.err = True
            return False

    # get user current status
    def get_user_status(self):
        return self.session.post(urls['get_user_status']).json()

    # get user_contacts:
    def get_user_contacts(self):
        data = {
            'pageIndex': '1',
            'pageSize': '10'
        }
        res = self.session.post(urls['get_user_contacts'], data=data)
        return res.json()['data']['datas']


    # first, make a request to left_ticket_page to imitate human
    def goto_query_page(self):
        self.session.get(urls['left_ticket_init'], params={'linktypeid': 'dc'})

    # initialize querier
    def init_querier(self, departure, destination, date, **kwargs):
        querier = Querier(departure, destination, date, **kwargs)
        if querier.get_sc():
            self.querier = querier
        else
            print('err with getting station code map')
            self.err = True

    # query tickets.
    def query_tickets(self):
        return self.querier.query_tickets(self.session)

    # get user 

    # query and find appropriate tickets
    def resolve_tickets(self, passenger, train_id=(), depart_time_span=('00:00', '23:59'))
        pass

    # click book button
    def book(self, train_id=(), depart_time_span=('00:00', '23:59')):
        # check user -> query -> book 
        pick = None  # the train ticket that would be booked
        def clock(t):
            return strptime(t, '%H:%M')
        if self.user_is_loggedin():
            self.session.post(urls['check_user'], data={'_json_att': None})
            _, solution = self.querier.query_tickets(self.session)  # query
            # filter by could buy
            solution['items'] = [i for i in solution['items'] if i['could_buy'] == 'Y']
            # filter by train_id
            if train_id:
                solution['items'] = [ i for i in solution['items'] if i['train_id'] in train_id]
            # filter by span of time
            t1, t2 = depart_time_span
            solution['items'] = [ i for i in solution['items'] if clock(t1) < clock(i['depart_time']) <= clock(t2)]
            # if got at least one solution
            if solution['items']:
                pick = solution['items'].pop(0)
                # construct the form data
                data = {
                    'secretStr': unquote(pick['secret_str']),
                    'train_date': solution['date'],
                    'back_train_date': str(date.today()),
                    'tour_flag': 'dc',
                    'purpose_codes': solution['ticket_type'],
                    'query_from_station_name': solution['departure'],
                    'query_to_station_name': solution['destination'],
                    'undefined': None
                }
                print(data)
                res = self.session.post(urls['make_an_order'], data=data)
                # to be improved 
                print res.json()
                return res.json()['status']
        return False

    # get globalRepeatSubmitToken
    def get_submit_token(self):
        res = self.session.get(urls['get_submit_token'], data={'_json_att': None})
        txt = res.text[:800]
        self.repeat_submit_token = txt.split("globalRepeatSubmitToken = '")[1].split("'")[0]

    def get_passenger_info(self):
        data = {
            '_json_att': None,
            'REPEAT_SUBMIT_TOKEN': self.repeat_submit_token
        }
        res = self.session.post(urls['get_passenger_info'], data=data)
        self.passenger_info = res.json()
        return self.passenger_info


    def check_order_info(self):
        passengers = self.passenger_info['data']['normal_passengers']
        data = {
            'cancel_flag':'2',
            'bed_level_order_num':'000000000000000000000000000000',
            'passengerTicketStr':'3,0,1,xxx,1,xxxxxxxxxxxxxx,,N',   #座位类型,0,票类型(成人/儿童),name,身份类型(身份证/军官证….),身份证,电话号码,保存状态
            'passengerTicketStr': f'3,0,1,{passengers[]}'
            'oldPassengerStr':'xxx,1,xxxxxxxxxxxxxxxx,1',  #姓名  1  身份证号码  1
            'tour_flag':'dc',
            'randCode':'',       #随机数
            'whatsSelect':'1',      
            '_json_att':'',
            'REPEAT_SUBMIT_TOKEN': self.repeat_submit_token
        }

    
    def submit_order(self):
        pass

    def confirm_order(self):
        pass

    def wait_book_result(self):
        pass

    def logger(self):
        pass

    def monitor(self):
        pass
    



