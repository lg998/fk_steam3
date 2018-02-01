import threading
import requests
import logging
from settings import *
from enum import Enum
from views.common import *


ORDER_STATE = Enum('ORDER_STATE',('RUNNING', 'PAUSED', 'COMPLETED','EXIT_UNEXPECTEDLY'))

class OrderInfo:
    # order_name = ""
    # skin_url = ""
    # max_price = -1
    # max_float = -1
    # min_float = -1
    # scan_count =-1
    # now_count = 0
    # need_count = -1
    # pattern_index = -1
    # order_state = ORDER_STATE.PAUSED
    # order_thread = Orderthread

    def __init__(self, weapon_name, order_name = "", min_float = -0.1, max_float = 1.1, pattern_index = -1, max_price = 99999999, scan_count = SCAN_SKINLIST_COUNT, need_count = -1):
        self.min_float = min_float
        self.max_float = max_float
        self.pattern_index = pattern_index
        self.need_count = need_count
        self.max_float = max_price
        self.scan_count = scan_count
        self.order_state = ORDER_STATE.PAUSE
        if order_name == "":
            self.order_name = weapon_name
        self.skin_url = "http://steamcommunity.com/market/listings/730/%s/render/?query=&start=0&count=%d&country=CN&language=schinese&currency=23" %(weapon_name,scan_count) #TODO 不同国家不同URL

class OrderThread(threading.Thread):
    session = requests.Session()
    order_info = OrderInfo

    def __init__(self, session, order_info):
        threading.Thread.__init__(self)
        self.session = session
        self.order_info = order_info
        self.iterations = 0
        self.daemon = True
        self.paused = True
        self.state = threading.Condition()
        self.setName(order_info.order_name)

    def run(self):
        self.resume()
        while self.order_info.now_count < self.order_info.need_count:
            try:
                self.get_skin_info_and_buy()
            except:
                self.order_info.order_state = ORDER_STATE.EXIT_UNEXPECTEDLY
                #TODO 暂停线程
        self.order_info.order_state = ORDER_STATE.COMPLETED
        print ("Order %s is completed" % self.order_info.order_name)

    #TODO 写的像字典那样整齐点?
    @retry_if_fail(REQUEST_RETRY_TIMES)
    def get_skin_info_and_buy(self):
        logging.debug("Getting skin information from market")
        html_get = requests.get(self.order_info.skin_url)
        list_info = eval(html_get.text)
        logging.debug("generate skin information")
        for each in list_info['listinginfo']:
            item_info = list_info['listinginfo'][each]
            tempStr = list_info['asset']['market_actions'][0]['link']
            tempStr = tempStr.replace('%listingid%', list_info['listingid'])
            tempStr = tempStr.replace('%assetid%', list_info['asset']['id'])
            inspect_url = tempStr.replace('\/', '/')
            get_float_url = float_url + inspect_url
            skin_detail_info = self.get_skin_detail_info(get_float_url)
            skin_detail_info['iteminfo']['price'] = (item_info['converted_price'] + item_info['converted_fee']) / 100

            skin_info = {
                'm_nSubtotal' : list_info['converted_price_per_unit'],
                'm_nFeeAmount' : list_info['converted_fee_per_unit'],
                'm_nTotal' : list_info['converted_price_per_unit'] + list_info['converted_fee_per_unit'],
                'inspect_url' : inspect_url,
                'list_id' : each,
                'skin_detail_info' : skin_detail_info
            }
            logging.debug("Testing if this skin is available")
            if self.skin_available(skin_detail_info):
                logging.debug("this skin is available")
                if self.buy_skin(skin_info):
                    self.order_info.now_count += 1
                else:
                    logging.debug("this skin is not available")



    @retry_if_fail(REQUEST_RETRY_TIMES)
    def get_skin_detail_info(self, float_url):
        logging.debug("Getting skin detail info")
        res = requests.get(float_url)
        skin_detail_info = eval(res.text)
        return skin_detail_info

    def skin_available(self, skin_detail_info):
        order_info = self.order_info
        float = skin_detail_info['iteminfo']['floatvalue']
        pattern = skin_detail_info['iteminfo']['paintseed']
        price = skin_detail_info['iteminfo']['price']
        logging.debug("orderName:%s  float:%s  pattern:%s  price:%d" % (order_info.name, float, pattern, price))
        if float >= order_info.minFloat and float <= order_info.maxFloat and price <= order_info.maxPrice and (order_info.patternIndex == -1 or order_info.patternIndex == pattern):
            return True
        else:
            return False

    def buy_skin(self, skin_info):
        buy_post_data = {
            "sessionid": self.session.cookies.get_dict()['sessionid'],
            "currency": 23, #TODO 不同国家不同货币单位
            "subtotal": skin_info['m_nSubtotal'],
            "fee": skin_info['m_nFeeAmount'],
            "total": skin_info['m_nTotal'],
            "quantity": 1
        }
        headers = {
            'Referer': 'http://steamcommunity.com/market/'
        }
        buy_url = 'https://steamcommunity.com/market/buylisting/'+skin_info['list_id']
        buy_res = self.session.post(buy_url, buy_post_data, headers=headers)
        if buy_res.status_code == 200:
            logging.debug("You buy the skin successfully")
            return True
        else:
            logging.debug("Couldn't buy this skin, state_code: %s, msg:%s" % (buy_res.status_code, buy_res.text))
            return False

