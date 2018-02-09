import threading
import requests
import logging
import time
from settings import *
from enum import Enum
from views.common import *
import traceback


ORDER_STATE = Enum('ORDER_STATE',('RUNNING', 'PAUSED', 'COMPLETED','EXIT_UNEXPECTEDLY'))

# #TODO 这个东西不能序列化
# class ORDER_STATE(Enum):
#     RUNNING = 0
#     PAUSED = 1
#     COMPLETED = 2
#     EXIT_UNEXPECTEDLY = 3




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

    def __init__(self, weapon_name, order_name = "", min_float = -0.1, max_float = 1.1, pattern_index = -1, max_price = 99999999, scan_count = SCAN_SKINLIST_COUNT, now_count = 0, need_count = -1):
        self.weapon_name = weapon_name
        self.min_float = float(min_float)
        self.max_float = float(max_float)
        self.pattern_index = int(pattern_index) #TODO 测试一下?
        self.need_count = int(need_count)
        self.max_price = float(max_price)
        self.scan_count = int(scan_count)
        self.order_state = ORDER_STATE.PAUSED
        self.now_count = now_count
        if order_name == '':
            self.order_name = weapon_name
        self.skin_url = "http://steamcommunity.com/market/listings/730/%s/render/?query=&start=0&count=%s&country=CN&language=schinese&currency=23" %(weapon_name,scan_count) #TODO 不同国家不同URL
        logging.debug("create order: %s" % self.get_order_info())

    def get_order_info(self):
        return {
            'weapon_name' : self.weapon_name,
            'order_name': self.order_name,
            'min_float': self.min_float,
            'max_float': self.max_float,
            'pattern_index': self.pattern_index,
            'max_price': self.max_price,
            'scan_count': self.scan_count,
            'need_count': self.need_count,
            'now_count' : self.now_count,
            'order_state' : self.order_state.value
        }

class OrderThread(threading.Thread):
    session = requests.Session()
    order_info = OrderInfo

    def __init__(self, session, username, order_info):
        self.session = session
        self.username = username
        self.order_info = order_info
        threading.Thread.__init__(self)
        self.iterations = 0
        self.daemon = True
        self.paused = True
        self.stopped = False
        self.state = threading.Condition()
        self.setName(order_info.order_name)

    def run(self):
        self.resume()
        self.order_info.order_state = ORDER_STATE.RUNNING
        while self.order_info.now_count < self.order_info.need_count:
            try:
                self.get_skin_info_and_buy()
                if self.stopped == True:
                    return
                while self.paused == True:
                    continue
            except:
                traceback.print_exc()
                self.order_info.order_state = ORDER_STATE.EXIT_UNEXPECTEDLY
            time.sleep(20)
        self.order_info.order_state = ORDER_STATE.COMPLETED
        print ("Order %s is completed" % self.order_info.order_name)

    def resume(self):
        logging.debug("thread resume")
        with self.state:
            self.paused = False
            self.state.notify()


    def pause(self):
        logging.debug("thread pause")
        with self.state:
            self.paused = True


    def stop(self):
        logging.debug("thread stop")
        self.stopped = True

    #TODO 写的像字典那样整齐点?
    @retry_if_fail(REQUEST_RETRY_TIMES)
    def get_skin_info_and_buy(self):
        logging.debug("Getting skin information from market")
        html_get = requests.get(self.order_info.skin_url)
        list_info = eval(html_get.text)
        logging.debug("generate skin information")
        for each in list_info['listinginfo']:
            if self.stopped == True:
                return
            while self.paused == True:
                continue
            logging.debug(list_info['listinginfo'][each])
            item_info = list_info['listinginfo'][each]
            tempStr = item_info['asset']['market_actions'][0]['link']
            tempStr = tempStr.replace('%listingid%', item_info['listingid'])
            tempStr = tempStr.replace('%assetid%', item_info['asset']['id'])
            inspect_url = tempStr.replace('\/', '/')
            get_float_url = float_url + inspect_url
            skin_detail_info = self.get_skin_detail_info(get_float_url)
            #TODO 这里老是出错
            skin_detail_info['iteminfo']['price'] = (item_info['converted_price'] + item_info['converted_fee']) / 100

            skin_info = {
                'm_nSubtotal' : item_info['converted_price_per_unit'],
                'm_nFeeAmount' : item_info['converted_fee_per_unit'],
                'm_nTotal' : item_info['converted_price_per_unit'] + item_info['converted_fee_per_unit'],
                'inspect_url' : inspect_url,
                'list_id' : each,
                'skin_detail_info' : skin_detail_info
            }
            logging.debug("Testing if this skin is available: %s" % skin_detail_info)
            if self.skin_available(skin_detail_info):
                logging.debug("this skin is available")
                if self.buy_skin(skin_info):
                    self.order_info.now_count += 1
                    if self.order_info.now_count >= self.order_info.need_count:
                        return
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
        logging.debug("this_item: orderName:%s  float:%s  pattern:%s  price:%s" % (order_info.order_name, float, pattern, price))
        logging.debug("order info: min_float: %s, max_float:%s, max_price:%s, pattern_index:%s" % (order_info.min_float,order_info.max_float,order_info.max_price,order_info.pattern_index))
        if float >= order_info.min_float and float <= order_info.max_float and price <= order_info.max_price and (order_info.pattern_index == -1 or order_info.pattern_index == pattern):
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
            logging.info("You buy the skin successfully")
            return True
        else:
            logging.info("Couldn't buy this skin, state_code: %s, msg:%s" % (buy_res.status_code, buy_res.text))
            return False

