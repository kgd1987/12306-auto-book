# -*- coding: utf-8 -*-
import requests
from booker.consts import urls

# An object that implements central inquiry funcitionality
class Querier():
    def __init__(self, departure, destination, date, ticket_type = 'ADULT', **kwargs):
        self.departure = departure
        self.destination = destination
        self.date = date
        self.ticket_type = ticket_type if ticket_type != 'STUDENT' else '0X00'
        self.details = kwargs
        self.departure_code, self.destination_code = None, None

    # get station-code
    def get_sc(self):
        res = requests.get(urls['sc_map'])
        station_list = res.text.split("'")[1].split('@')
        station_list.pop(0)
        for s in station_list:
            s_info = s.split('|')
            if s_info[1] == self.departure:
                self.departure_code = s_info[2]
            elif s_info[1] == self.destination:
                self.destination_code = s_info[2]
            if self.destination_code and self.departure_code:
                return True
        return False

    # query tickets
    def query_tickets(self, session):
        # the result that would be return
        res = {
            'ticket_type': self.ticket_type,
            'departure': self.departure,
            'destination': self.destination,
            'date': self.date,
            'details': self.details,
            'items': []
        }
        params = {
            'leftTicketDTO.train_date': self.date,
            'leftTicketDTO.from_station': self.departure_code,
            'leftTicketDTO.to_station': self.destination_code,
            'purpose_codes': self.ticket_type
        }
        resp = session.get(urls['query_tickets'], params=params)
        data = resp.json()['data']
        items, maps = data['result'], data['map']
        for i in items:
            # item_info gonna be a list of infomation of a train
            # 0 -> secret_key, 1->book, 2->train_uid, 3->train_id(or name, G40 for example), 
            i_info = i.split('|')
            item = {
                'train_id': i_info[3],
                'schedual': f"from: {maps[i_info[6]]} to: {maps[i_info[7]]}, \
                            time: {i_info[8]} -- {i_info[9]}, duration: {i_info[10]}",
                'depart_time': i_info[8],
                # 'arrive_time': i_info[9],
                '商务座': i_info[-5],
                '一等座': i_info[-6],
                '二等座': i_info[-7],
                'could_buy': i_info[11],
                'secret_str': i_info[0]
            }
            res['items'].append(item)
        return res



