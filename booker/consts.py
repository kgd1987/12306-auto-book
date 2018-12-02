# -*- coding: utf-8 -*-


# consts of urls
urls = {
  'domain': 'kyfw.12306.cn',
  'base_url': 'https://kyfw.12306.cn',
  'login_url': 'https://kyfw.12306.cn/otn/login/init',
  # section of login and authorization
  'get_captcha': 'https://kyfw.12306.cn/passport/captcha/captcha-image?login_site=E&module=login&rand=sjrand',
  'verify_captcha': 'https://kyfw.12306.cn/passport/captcha/captcha-check',
  'web_login': 'https://kyfw.12306.cn/passport/web/login',
  'web_auth': 'https://kyfw.12306.cn/passport/web/auth/uamtk',
  'otn_auth': 'https://kyfw.12306.cn/otn/uamauthclient',

  # get user status
  'get_user_status': 'https://kyfw.12306.cn/otn/login/conf',
  # get user contacts (info of avaiable passengers)
  'get_user_contacts': 'https://kyfw.12306.cn/otn/passengers/query',

  # section of booking

  # go to query page  to imitate a hunman
  'left_ticket_init': 'https://kyfw.12306.cn/otn/leftTicket/init', #params: linktypeid=dc
  # query tickets, method: get, params: leftTicketDTO.train_date & leftTicketDTO.from_station & leftTicketDTO.to_station & purpose_code = ADULT
  'query_tickets': 'https://kyfw.12306.cn/otn/leftTicket/query', 

  'check_user': 'https://kyfw.12306.cn/otn/login/checkUser',
  'make_an_order': 'https://kyfw.12306.cn/otn/leftTicket/submitOrderRequest',
  # get globalRepeatSubmitToken
  'initdc': 'https://kyfw.12306.cn/otn/confirmPassenger/initDc',
  'get_passenger_dtos': 'https://kyfw.12306.cn/otn/confirmPassenger/getPassengerDTOs',
  'check_order_info': 'https://kyfw.12306.cn/otn/confirmPassenger/checkOrderInfo',
  'submit_order': 'https://kyfw.12306.cn/otn/confirmPassenger/getQueueCount',
  'confirm_order': 'https://kyfw.12306.cn/otn/confirmPassenger/confirmSingleForQueue',
  'wait': 'https://kyfw.12306.cn/otn/confirmPassenger/queryOrderWaitTime',
  'book_results': 'https://kyfw.12306.cn/otn/confirmPassenger/resultOrderForDcQueue',

  # third party for punching captcha in 12306
  'punch_captcha': 'http://littlebigluo.qicp.net:47720/',

  # all station code map
  'sc_map': 'https://kyfw.12306.cn/otn/resources/js/framework/station_name.js',
}


# fake headers
headers = {
  'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/70.0.3538.102 Safari/537.36',
}

captcha_path = r'C:\Users\Administrator\Desktop\12306_captcha.png'

seat_type_map = {
    '商务座': '9',
    '一等座': 'M',
    '二等座': '0',
    '硬卧': '3',
    '硬座': '1',
    '软卧': '4'
}