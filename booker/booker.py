# -*- coding: utf-8 -*-

"""
this module implements the central booker object.
"""

import requests
from datetime import date
import time
from time import strptime
from urllib.parse import unquote
# from time import sleep
from booker.verify_captcha import verify_captcha_auto, verify_captcha
from booker.consts import urls, headers, captcha_path, seat_type_map
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
        self.left_ticket_key = None
        self.purpose_codes = None
        self.train_location = None
        self.key_check_ischange = None
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
            'answer': verify_captcha_auto(captcha_path),
            # 'answer': verify_captcha(),
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
        self.contacts = res.json()['data']['datas']
        return self.contacts


    # first, make a request to left_ticket_page to imitate human
    def goto_query_page(self):
        self.session.get(urls['left_ticket_init'], params={'linktypeid': 'dc'})

    # initialize querier
    def init_querier(self, departure, destination, date, **kwargs):
        querier = Querier(departure, destination, date, **kwargs)
        if querier.get_sc():
            self.querier = querier
        else:
            print('err with getting station code map')
            self.err = True 
   
    # query tickets.
    def query_tickets(self, train_id=(), depart_time_span=(), acceptable_seat_type=('二等座', '硬卧')):
        def clock(t):
            return strptime(t, '%H:%M')
        def has_left_tickets(tickets_info):
            for s in tickets_info:
                if s not in ['', '无']:
                    return True
            return False
        # filter
        def ticket_filter(i):
            if i['could_buy'] != 'Y':
                return False
            if train_id and i['train_id'] not in train_id:
                return False
            if depart_time_span:
                t1, t2 = depart_time_span
                if not clock(t1) <= clock(i['depart_time']) <= clock(t2):
                    return False
            left_tickets_num = [i[seat_type] for seat_type in acceptable_seat_type]
            if not has_left_tickets(left_tickets_num):
                return False
            return True
        s = self.querier.query_tickets(self.session)
        s['acceptable_seat_type'] = acceptable_seat_type
        filted_items =[i for i in s['items'] if ticket_filter(i)]
        s['items'] = filted_items
        return s

    # query and find appropriate tickets
    def resolve_tickets(self, passenger, query_results):
        solution = None
        for i in query_results['items']:
            for seat_type in query_results['acceptable_seat_type']:
                if i[seat_type] not in ['', '无']:
                    solution = query_results
                    passenger_info = [p for p in self.contacts if p['passenger_name'] == passenger][0]
                    solution['passenger_info'] = passenger_info
                    solution['seat_type'] = seat_type
                    solution['target'] = i
                    solution['items'] = 'discarded 4 brief visual.'
                    return solution
        return solution


    # what should we do after clicking the book button
    def make_an_order(self, solution):
        # imitate the browser behavior
        self.session.post(urls['check_user'], data={'_json_att': ''})
        data = {
            'secretStr': unquote(solution['target']['secret_str']),
            'train_date': solution['date'],
            'back_train_date': str(date.today()),
            'tour_flag': 'dc',
            'purpose_codes': solution['ticket_type'],
            'query_from_station_name': solution['departure'],
            'query_to_station_name': solution['destination'],
            'undefined': ''
        }
        self.session.post(urls['make_an_order'], data=data)
    
    # get globalRepeatSubmitToken | ypInfoDetail --> requsts the initdc, get 
    def parse_initdc(self):
        res = self.session.post(urls['initdc'], data={'_json_att': ''})
        self.left_ticket_key = res.text.split("ypInfoDetail':'")[1].split("'")[0]
        self.purpose_codes = res.text.split("purpose_codes':'")[1].split("'")[0]
        self.train_location = res.text.split("'dc','train_location':'")[1].split("'")[0]
        self.key_check_ischange = res.text.split("key_check_isChange':'")[1].split("'")[0]
        txt = res.text[:800]
        self.repeat_submit_token = txt.split("globalRepeatSubmitToken = '")[1].split("'")[0]

    # get passenger dtos 
    def get_passenger_dtos(self):
        data = {'_json_att': '', 'REPEAT_SUBMIT_TOKEN': self.repeat_submit_token}
        res = self.session.post(urls['get_passenger_dtos'], data=data)
        return res.json()

    def check_order(self, solution):
        seat_type = seat_type_map[solution['seat_type']]
        ticket_type = 1 if solution['ticket_type'] == 'ADULT' else 2
        # train_info = solution['target']
        passenger_name = solution['passenger_info']['passenger_name']
        id_num = solution['passenger_info']['passenger_id_no']
        data = {
            'cancel_flag': '2',
            'bed_level_order_num': '000000000000000000000000000000',
            # 'passengerTicketStr': '3,0,1,xxx,1,xxxxxxxxxxxxxx,,N',   #座位类型,0,票类型(成人/儿童),name,身份类型(身份证/军官证….),身份证,电话号码,保存状态
            'passengerTicketStr': f'{seat_type},0,{ticket_type},{passenger_name},1,{id_num},,N',
            'oldPassengerStr': f'{passenger_name},1,{id_num},1_',  #姓名  1  身份证号码  1
            'tour_flag': 'dc',
            'randCode': '',
            'whatsSelect': '1',      
            '_json_att': '',
            'REPEAT_SUBMIT_TOKEN': self.repeat_submit_token
        }
        print(data)
        return self.session.post(urls['check_order_info'], data=data).json()

    # submit order
    def submit_order(self, solution):
        y, _, d = solution['date'].split('-')
        w_m = time.ctime()[:7]
        data={
            'train_date': f'{w_m} {d} {y} 00:00:00 GMT+0800 (China Standard Time)',
            # 'train_date': 'Mon Dec 03 2018 00:00:00 GMT+0800 (China Standard Time)',
            'train_no': solution['target']['train_num'],
            'stationTrainCode': solution['target']['train_id'],
            'seatType': seat_type_map[solution['seat_type']],   # https://kyfw.12306.cn/otn/confirmPassenger/initDc 检视元素可查看
            'fromStationTelecode': solution['departure_code'],
            'toStationTelecode': solution['destination_code'],
            'leftTicket': self.left_ticket_key,
            'purpose_codes': self.purpose_codes,
            'train_location': self.train_location,
            '_json_att': '',
            'REPEAT_SUBMIT_TOKEN': self.repeat_submit_token
        }
        return self.session.post(urls['submit_order'], data=data)

    # confirm order 
    def confirm_order(self, solution):
        seat_type = seat_type_map[solution['seat_type']]
        ticket_type = 1 if solution['ticket_type'] == 'ADULT' else 2
        # train_info = solution['target']
        passenger_name = solution['passenger_info']['passenger_name']
        id_num = solution['passenger_info']['passenger_id_no']
        data={
            'passengerTicketStr': f'{seat_type},0,{ticket_type},{passenger_name},1,{id_num},,N',
            'oldPassengerStr': f'{passenger_name},1,{id_num},1_',  #姓名  1  身份证号码  1
            'randCode': '',
            'purpose_codes': self.purpose_codes,
            'key_check_isChange': self.key_check_ischange,
            'leftTicketStr': self.left_ticket_key,
            'train_location': self.train_location,
            'choose_seats':'',       #座位类型，一般是高铁用
            'roomType': '00',   # const
            'dwAll': 'N',       # const
            '_json_att': '',
            'seatDetailType':'000', # const
            'whatsSelect': '1',     # const
            'REPEAT_SUBMIT_TOKEN': self.repeat_submit_token
        }
        return self.session.post(urls['confirm_order'], data=data).json()

    # wait order results
    def query_orderid_inqueue(self):
        data={
            'random': str(time.time()),
            'tourFlag': 'dc',
            '_json_att': '',
            'REPEAT_SUBMIT_TOKEN': self.repeat_submit_token
        }
        res = self.session.post(urls['query_orderid'], data=data)
        order_id = res.json()['data']['orderId']
        if order_id:
            self.order_id = order_id
        return order_id

    # get book result 
    def check_order_result(self):
        data={
            'REPEAT_SUBMIT_TOKEN': self.repeat_submit_token,
            '_json_att': '',
            'orderSequence_no': self.order_id
        }
        return self.session.post(urls['book_result'], data=data).json()['status']



    



