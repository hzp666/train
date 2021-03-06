# -*- coding: utf-8 -*-
import json
import random
import re
from urllib import parse
from urllib.parse import quote, unquote
import time
import datetime
import requests
import urllib3
from PIL import Image
# 禁用安全请求警告
from bs4 import BeautifulSoup
from urllib3.exceptions import InsecureRequestWarning
import lianzhong_api

class GrabTicket():
    urllib3.disable_warnings(InsecureRequestWarning)
    headers = {
        "Accept": "*/*",
        "User-Agent": "Mozilla/5.0(Windows NT 10.0; Win64; x64) AppleWebKit/537.36(KHTML, like Gecko)\
             Chrome/62.0.3202.89 Safari/537.36",
        "Content-Type": "application/x-www-form-urlencoded; charset=UTF-8",
        "Accept-Language": "zh-CN, zh; q=0.9",
    }
    session = requests.session()
    session.verify = False
    session.headers = headers

    @staticmethod
    def get_code_by_input(value):
        """车站与对应字典之间的转换"""
        stations = json.load(open('stations.json', 'r', encoding='utf-8'))
        try:
            for key in stations.keys():
                if value in stations[key].values():
                    return key
            else:
                return stations[value]['汉字']
        except TypeError as e:
            print("!41")

    def __init__(self):
        self.D = None
        self.M = []
        self.ay = []
        self.id_type_code = ''
        self.ticket_submit_order = GrabTicket.ticket_submit_order()
        self.init_seatTypes = {}
        self.defaultTicketTypes = {}
        self.init_cardTypes = {}
        self.ticket_seat_codeMap = {}
        self.ticketInfoForPassengerForm = {}
        self.orderRequestDTO = {}
        self.limit_tickets = []
        self.current_train = {}  # 当前选择的车次
        self.info = []
        self.token=""
    @staticmethod
    def ticket_submit_order():
        """获取车票提交订单信息"""
        tso = json.load(open('ticket_submit_order.json', 'r', encoding='utf-8'))
        return tso

    def login(self, user_name, user_password):
        # 打开登录页面
        url = "https://kyfw.12306.cn/otn/login/init"
        self.session.get(url, headers=self.headers)
        # 发送验证码
        if not self.captcha() and not self.captcha2() :
            return False

        # 发送登录信息
        data = {
            "username":user_name,
            "password":user_password,
            "appid":"otn"
        }
        url = "https://kyfw.12306.cn/passport/web/login"
        response = self.session.post(url, headers=self.headers, data=data)
        if response.status_code == 200:
            result = json.loads(response.text)
            print(result.get("result_message"), result.get("result_code"))
            if result.get("result_code") != 0:
                return False

        data = {
            "appid": "otn"
        }
        url = "https://kyfw.12306.cn/passport/web/auth/uamtk"
        newapptk=''
        response = self.session.post(url, headers=self.headers, data=data)
        if response.status_code == 200:
            result = json.loads(response.text)
            print(result.get("result_message"))
            newapptk = result.get("newapptk")
        data = {
            "tk":newapptk
        }
        username=''
        url = "https://kyfw.12306.cn/otn/uamauthclient"
        response = self.session.post(url, headers=self.headers, data=data)

        if response.status_code == 200:
             username=eval(response.text)['username']
        print(username)
        url = "https://kyfw.12306.cn/otn/index/initMy12306"
        response = self.session.get(url, headers=self.headers)
        if response.status_code == 200 and response.text.find(username) != -1:
            return username
        return False

    def captcha(self):
        """检查验证码"""
        data = {
            "login_site": "E",
            "module": "login",
            "rand": "sjrand",
            "0.17231872703389062":""
        }

        # 获取验证码
        param = parse.urlencode(data)
        url = "https://kyfw.12306.cn/passport/captcha/captcha-image?{}".format(param)
        response = self.session.get(url, headers=self.headers)
        if response.status_code == 200:
            with open("./tmp.jpg", 'wb') as fp:
                fp.write(response.content)
        positions = lianzhong_api.yzm('favomj',
            '...',
            './tmp.jpg',
            "http://v1-http-api.jsdama.com/api.php?mod=php&act=upload",
            '',
            '',
            '1303',
            '')
        index = positions.find('result')
        positions = positions[0:index - 2] + '}'
        positions = eval(positions)
        positions = (',').join(positions['data']['val'].split('|'))
        print(positions)
        # 发送验证码
        data = {
            "answer": positions,
            "login_site": "E",
            "rand": "sjrand"
        }

        url = "https://kyfw.12306.cn/passport/captcha/captcha-check"
        response = self.session.post(url, headers=self.headers, data=data)
        if response.status_code == 200:
            result = json.loads(response.text)
            # print(result.get("result_message"))
            return True if result.get("result_code") == "4" else False
        return False

    def captcha2(self):
        data = {
            "login_site": "E",
            "module": "login",
            "rand": "sjrand",
            "0.17231872703389062":""
        }

        # 获取验证码
        param = parse.urlencode(data)
        url = "https://kyfw.12306.cn/passport/captcha/captcha-image?{}".format(param)
        response = self.session.get(url, headers=self.headers)
        if response.status_code == 200:
            with open("./tmp.jpg", 'wb') as fp:
                fp.write(response.content)
            img = Image.open("./tmp.jpg")
            img.show()

        positions = input("请输入验证码")
        # 发送验证码
        data = {
            "answer": positions,
            "login_site": "E",
            "rand": "sjrand"
        }

        url = "https://kyfw.12306.cn/passport/captcha/captcha-check"
        response = self.session.post(url, headers=self.headers, data=data)
        if response.status_code == 200:
            result = json.loads(response.text)
            # print(result.get("result_message"))
            return True if result.get("result_code") == "4" else False
        return False

    def get_left_ticket_log(self, d, f, t):
        """检查票是否剩余"""
        url = 'https://kyfw.12306.cn/otn/leftTicket/log?leftTicketDTO.train_date=' + d +\
              '&leftTicketDTO.from_station=' + f + '&leftTicketDTO.to_station=' + t + '&purpose_codes=ADULT'
        res = self.session.get(url, verify=False)
        try:
            msg = json.loads(res.text)
        except Exception as e:
            return False
        #print(msg)
        if msg['status'] and msg['validateMessagesShowId'] == '_validatorMessage':
            return True
        else:
            print(msg)
        return False

    def ticket_info(self,_from,_to,_d):
        """获取票信息"""
        _from = self.get_code_by_input(_from)
        _to = self.get_code_by_input(_to)

        from_station = quote(self.get_code_by_input(_from) + ',' + _from).replace('\\', '%')
        to_station = quote(self.get_code_by_input(_to) + ',' + _to).replace('\\', '%')

        cookies = {
            "_jc_save_fromDate": _d,
            "_jc_save_fromStation": from_station,
            "_jc_save_toDate": _d,
            "_jc_save_toStation": to_station,
            "_jc_save_wfdc_flag": "dc",
        }

        #添加cookies
        requests.utils.add_dict_to_cookiejar(self.session.cookies, cookies)

        #检查是否有剩余
        if not self.get_left_ticket_log(_d, _from, _to):
            return None

        url = 'https://kyfw.12306.cn/otn/leftTicket/queryZ?leftTicketDTO.train_date=' + _d + '&leftTicketDTO.from_station=' \
              + _from + '&leftTicketDTO.to_station=' + _to + '&purpose_codes=ADULT'

        response = self.session.get(url,verify=False)
        try:
            msg = json.loads(response.text)
            results = msg['data']['result']
        except Exception as e:
            return False

        #分析返回结果，生成json返回
        self.info = []
        for result in results:
            cols = result.split('|')
            train = {}
            train['train_no'] = cols[2]
            train['车次'] = cols[3]
            train['出发站'] = self.get_code_by_input(cols[4])
            train['到达站'] = self.get_code_by_input(cols[5])
            train['出发时间'] = cols[8]
            train['到达时间'] = cols[9]

            train['历时'] = cols[10]
            train['当日到达'] = cols[11]
            train['出发日'] = cols[13]
            train['商务座特等座'] = cols[32]
            train['一等座'] = cols[31]
            train['二等座'] = cols[30]
            train['高级软卧'] = cols[21]
            train['软卧'] = cols[23]
            train['动卧'] = cols[33]
            train['硬卧'] = cols[28]
            train['软座'] = cols[24]
            train['硬座'] = cols[29]
            train['无座'] = cols[26]
            train['其它'] = cols[22]
            train['secretStr'] = cols[0]
            if cols[0]:
                self.info.append(train)
        print(self.info)
        return json.dumps(self.info, sort_keys=True, indent=2, ensure_ascii=False)

    @staticmethod
    def str2date_format1(str):
        """字符串转日期格式 yyyy-MM-dd"""
        l = list(str)
        l.insert(4, '-')
        l.insert(-2, '-')
        return ''.join(l)

    def submit_order(self, _f, _t,k):
        """提交预订单"""
        self.current_train = self.info[k]
        url = 'https://kyfw.12306.cn/otn/leftTicket/submitOrderRequest'
        train_date = self.str2date_format1(self.current_train['出发日'])
        back_date = train_date
        #print("secretStr", unquote(self.current_train['secretStr']))
        data = {
            "secretStr": unquote(self.current_train['secretStr']),
            "train_date": train_date,
            "back_train_date": back_date,
            "tour_flag": "dc",
            "purpose_codes": "ADULT",
            "query_from_station_name": _f,
            "query_to_station_name": _t,
            "undefined": None
        }

        if not self.check_user():
            return False

        res = self.session.post(url,
                                data=data,
                                headers={"Content-Type": "application/x-www-form-urlencoded"},
                                verify=False)

        msg = json.loads(res.text)

        if msg['status']:
            if msg['data'] == 'Y':
                print('您选择的列车距开车时间很近了，\n请确保有足够的时间抵达车站，\n并办理换取纸质车票、安全检查、\
                实名制验证及检票等手续，以免耽误您的旅行。')
            # 跳转到确认乘客人页面
            return self.confirm_passenger()
        else:
            print(msg['messages'])
            return False


    def check_user(self):
        """验证用户"""
        url = 'https://kyfw.12306.cn/otn/login/checkUser'
        data = {'_json_att': ''}
        res = self.session.post(url,
                                data=data,
                                verify=False,
                                headers={'If-Modified-Since': '0',
                                         'Cache-Control': 'no-cache',
                                         'Content-Type': 'application/x-www-form-urlencoded; charset=utf-8'})
        msg = json.loads(res.text)
        print('验证用户')
        #print(msg)
        if msg['status']:
            if msg['data']['flag']:
                return True

        else:
            print(msg['messages'])
        return False

    @staticmethod
    def get_dict(pattern, text):
        """根据模式匹配相应的字符串"""
        _str = re.findall(pattern, text)[0]
        _str = _str.replace('\'', '"')
        return json.loads(_str)

    def confirm_passenger(self):
        """确认乘客信息"""
        url = 'https://kyfw.12306.cn/otn/confirmPassenger/initDc'
        res = self.session.get(url, verify=False)

        token_pattern = r'var globalRepeatSubmitToken = \'(.*?)\';'
        self.token = re.findall(token_pattern, res.text)[0]

        self.get_common_data(res.text)
        #print('@234', res.text)

        train_info = self.ticketInfoForPassengerForm['queryLeftTicketRequestDTO']  # 列车信息
        left_ticket_str = self.ticketInfoForPassengerForm['leftTicketStr']
        train_date = train_info['train_date']

        # 星期几
        weekday = self.get_week(
            datetime.date(int(train_date[:4]), int(train_date[4:6]), int(train_date[6:8])))

        print("列车信息(以下余票信息仅供参考)")
        print(self.str2date_format1(train_date)
              + '（' + weekday + '） '
              + train_info['station_train_code']
              + '次 '
              + train_info['from_station_name']
              + '站（'
              + train_info['start_time']
              + '开）'
              + "--"
              + train_info['to_station_name']
              + '站（'
              + train_info['arrive_time'] + '到）')
        print('-----------------------------------------------------------------')
        left_details = self.ticketInfoForPassengerForm['leftDetails']
        return  left_details


    def confirm_passenger2(self,seat_type,seat_price):
    # 获取乘客信息
        token = self.token
        normal_passengers = self.get_passengers(token)
        if normal_passengers:
            print("乘客信息")
            for i, passenger in enumerate(normal_passengers):
                print(str(i + 1) + '. ' + passenger['passenger_name'])

        af = 'normalPassenger_0'
        aj = self.ay[int(af.split('_')[1])]
        #print(aj)
        ac = self.ticket_type2(aj['passenger_type'])  # index=3
        args = [af, seat_type, seat_price, '1', '成人票', aj['passenger_name'], aj['passenger_id_type_code'], \
                aj['passenger_id_type_name'], aj['passenger_id_no'], aj['mobile_no'], '', \
                self.ticketInfoForPassengerForm['tour_flag'], True, aj['passenger_type'], False, None]

        self.add_limit_tickets(*args)

        # 验证订单
        flag = self.check_order_info(token)

        if flag:  # 验证成功
            print('验证成功')
            return self.get_queue_count(token)  # 获取队列计数
        else:
            return False


    def Y(self):
        if len(self.limit_tickets) < 1:
            return len(self.limit_tickets)
        else:
            b = 0
            for a in self.limit_tickets:
                z = int(a['only_id'].split('_')[1])
                if z > b:
                    b = z
            return b + 1

    def get_queue_count(self, token):
        """获取队列计数"""
        url = 'https://kyfw.12306.cn/otn/confirmPassenger/getQueueCount'

        data = {
            'train_date': self.get_standard_time(
                datetime.datetime.fromtimestamp(int(self.orderRequestDTO['train_date']['time']) / 1000)),
            'train_no': self.orderRequestDTO['train_no'],
            'stationTrainCode': self.orderRequestDTO['station_train_code'],
            'seatType': self.limit_tickets[0]['seat_type'],
            'fromStationTelecode': self.orderRequestDTO['from_station_telecode'],
            'toStationTelecoe': self.orderRequestDTO['to_station_telecode'],
            'leftTicket': self.ticketInfoForPassengerForm['queryLeftTicketRequestDTO']['ypInfoDetail'],
            'purpose_codes': self.ticketInfoForPassengerForm['purpose_codes'],
            'train_location': self.ticketInfoForPassengerForm['train_location'],
            '_json_att': '',
            'REPEAT_SUBMIT_TOKEN': token
        }
        #print(data)
        res = self.session.post(url, data=data, verify=False)
        msg = json.loads(res.text)
        print(msg)

        if msg['status']:
            return self.confirm_single_for_queue(token)
        else:
            print(msg['messages'])
            return False

    def confirm_single_for_queue(self, token):
        """确认队列单"""
        url = 'https://kyfw.12306.cn/otn/confirmPassenger/confirmSingleForQueue'
        data = {
            'passengerTicketStr': self.get_passenger_tickets(),
            'oldPassengerStr': self.get_old_passengers(),
            'randCode': '',
            'purpose_codes': self.ticketInfoForPassengerForm['purpose_codes'],
            'key_check_isChange': self.ticketInfoForPassengerForm['key_check_isChange'],
            'leftTicketStr': self.ticketInfoForPassengerForm['leftTicketStr'],
            'train_location': self.ticketInfoForPassengerForm['train_location'],
            'choose_seats': '',
            'seatDetailType': '000',
            'roomType': '00',
            'dwAll': 'N',
            '_json_att': '',
            'REPEAT_SUBMIT_TOKEN': token
        }
        res = self.session.post(url, data=data, verify=False)
        msg = json.loads(res.text)
        #print(res.text)
        flag = False

        if msg['status']:

            if not msg['data']['submitStatus']:
                print('出票失败！原因：' + msg['data']['errMsg'])

            else:
                time.sleep(2)
                flag = self.query_order_wait_time(token)

        else:
            print('订票失败！很抱歉！请重新订票')

        return flag

    def query_order_wait_time(self, token):
        """获取下次请求等待时间"""
        t = str(int(time.time() * 1000))
        url = 'https://kyfw.12306.cn/otn/confirmPassenger/queryOrderWaitTime?random=' + t \
              + '&tourFlag=' + self.ticketInfoForPassengerForm['tour_flag'] + '&_json_att=&REPEAT_SUBMIT_TOKEN=' + token
        res = self.session.get(url, verify=False)
        print(res.text)
        msg = json.loads(res.text)

        if msg['data'] and msg['data']['queryOrderWaitTimeStatus']:
            waitObj = msg['data']
            if waitObj['waitTime'] != -100 and waitObj['waitTime'] != -1:
                if waitObj['waitTime'] == -2:
                    print(waitObj['msg'])
                    return False
                else:
                    time.sleep(3)
                    self.query_order_wait_time(token)
            else:
                return self.finish_method(waitObj['tourFlag'], waitObj['waitTime'], waitObj, token)

        else:
            return False

    def finish_method(self, tour_flag, wait_time, wait_obj, token):
        """订单完成"""
        url = ''
        if wait_time == -1 or wait_time == -100:
            if tour_flag == self.ticket_submit_order['tour_flag']['dc']:
                url = 'https://kyfw.12306.cn/otn/confirmPassenger/resultOrderForDcQueue'
            elif tour_flag == self.ticket_submit_order['tour_flag']['wc']:
                url = 'https://kyfw.12306.cn/otn/confirmPassenger/resultOrderForWcQueue'
            elif tour_flag == self.ticket_submit_order['tour_flag']['fc']:
                url = 'https://kyfw.12306.cn/otn/confirmPassenger/resultOrderForFcQueue'
            elif tour_flag == self.ticket_submit_order['tour_flag']['gc']:
                url = 'https://kyfw.12306.cn/otn/confirmPassenger/resultOrderForGcQueue'
            data = {
                'orderSequence_no': wait_obj['orderId'],
                '_json_att': '',
                'REPEAT_SUBMIT_TOKEN': token
            }
            res = self.session.post(url, data=data, verify=False)
            print(res.text)
            msg = json.loads(res.text)
            if msg['status']:
                if msg['data']['submitStatus']:
                    self.ots_redirect()
                    return True
                else:
                    print(msg['data']['errMsg'])
        return False

    def ots_redirect(self):
        """跳转到此"""
        t = str(int(time.time() * 1000))
        url = 'https://kyfw.12306.cn/otn//payOrder/init?random=' + t
        res = self.session.post(url, verify=False)
        pattern = r'var parOrderDTOJson = \'(.*?)\';'
        parOrderDTOStr = re.findall(pattern, res.text)[0].replace(r'\"', '"')
        parOrderDTOJson = json.loads(parOrderDTOStr)

        pattern2 = r'var passangerTicketList = (.*?);'
        passangerTicketListStr = re.findall(pattern2, res.text)[0].replace(r'null', "''").replace(r"'", '"')
        passangerTicketListJson = json.loads(passangerTicketListStr)

        pattern3 = r'var insInfos = (.*?);'
        insInfosStr = re.findall(pattern3, res.text)[0].replace(r'null', "''").replace(r"'", '"')
        insInfosJson = json.loads(insInfosStr)

        print("车票信息：")
        #print(json.dumps(parOrderDTOJson, sort_keys=True, indent=2, ensure_ascii=False))
        #print(json.dumps(passangerTicketListJson, sort_keys=True, indent=2, ensure_ascii=False))
        #print(json.dumps(insInfosJson, sort_keys=True, indent=2, ensure_ascii=False))

    @staticmethod
    def get_week(date):
        """根据日期获取当前是星期几"""
        weekday = ['周一', '周二', '周三', '周四', '周五', '周六', '周日']
        return weekday[date.weekday()]

    @staticmethod
    def get_standard_time(date):
        """获取标准时间"""
        return date.strftime('%a %b %d %Y %H:%M:%S ') + 'GMT+0800 (中国标准时间)'

    def get_passenger_tickets(self):
        _str = ''
        for v in self.limit_tickets:
            av = v['seat_type'] + ',0,' + v['ticket_type'] + ',' + v['name'] + ',' \
                 + v['id_type'] + ',' + v['id_no'] + ',' + v['phone_no'] + ',' \
                 + 'N' if v['save_status'] == '' else 'Y'
            _str += av + '_'
        return _str[:len(_str) - 1]

    def get_old_passengers(self):
        _str = ''
        for d in self.limit_tickets:
            if self.ticketInfoForPassengerForm['tour_flag'] == self.ticket_submit_order['tour_flag']['fc'] \
                    or self.ticketInfoForPassengerForm['tour_flag'] == self.ticket_submit_order['tour_flag']['gc']:
                a = d['name'] + ',' + d['id_type'] + ',' + d['id_no'] + ',' + d['passenger_type']
                _str += a + '_'
            else:
                if 'djPassenger_' in d['only_id']:
                    b = d['only_id'].split('_')[1]
                    a = self.M[b]['passenger_name'] + ',' + self.M[b]['passenger_id_type_code'] + ',' + \
                        self.M[b]['passenger_id_no'] + ',' + self.M[b]['passenger_type']
                    _str += a + '_'
                else:
                    if 'normalPassenger' in d['only_id']:
                        b = int(d['only_id'].split('_')[1])
                        a = self.ay[b]['passenger_name'] + ',' + self.ay[b]['passenger_id_type_code'] + ',' + \
                            self.ay[b]['passenger_id_no'] + ',' + self.ay[b]['passenger_type']
                        _str += a + '_'
                    else:
                        _str += '_ '
        return _str

    def add_limit_tickets(self, *args):
        """获取限购车票的列表"""
        if len(self.limit_tickets) >= 5:
            print("最多只能购买 5 张车票")
        ticket_type = self.get_ticket_type(args[13], args[6], args[3])
        d = {
            'only_id': args[0],
            'seat_type': args[1],  # 座位类型
            'seat_type_name': args[2],  # 座位类型名称
            'ticket_type': args[3],  # ticket_type,  # 车票类型
            'ticket_type_name': args[4],  # 车票类型名称
            'name': args[5],  # 乘客名字
            'id_type': args[6],  # 证件类型
            'id_type_name': args[7],  # 证件类型名称
            'id_no': args[8],  # 证件编号
            'phone_no': args[9],  # 手机号
            'passenger_type': args[13],  # 乘客类型
            'seatTypes': self.ticket_seat_codeMap[self.ticket_submit_order['ticket_type']['adult'] \
                if ticket_type == '' else ticket_type],  # 座位所有类型
            # seatTypes 排序根据ag
            'ticketTypes': self.D,
            'cardTypes': self.init_cardTypes,  # 初始所有证件类型
            'save_status': args[10],  # 保存状态
            'tour_flag': args[11],  # 旅行标识 单程或返程
            'isDisabled': True if args[13] == self.ticket_submit_order['ticket_type']['student'] else args[12],  #
            'isDefaultUsed': False,
            'checkboxStatus': args[14],
            'isAccompanyChild': args[15] if args[15] else None
        }
        # if not args[15]:
        #     args[15] = False
        self.limit_tickets.append(d)

    def get_ticket_type(self, t1, t2, t3):
        return self.ticket_type1(t1, t2, t3)

    def ticket_type1(self, t1, t2, t3):
        t0 = self.ticket_type2(t1)
        if self.ticketInfoForPassengerForm['purpose_codes'] == self.ticket_submit_order['ticket_query_flag'] \
                ['query_student']:
            return self.ticket_submit_order['ticket_type']['student']
        else:
            if t1 == self.ticket_submit_order['passenger_type']['disability']:
                t4 = self.id_type_code
                if t4 != self.ticket_submit_order['passenger_card_type']['two'] or \
                                t2 != self.ticket_submit_order['passenger_card_type']['two']:
                    return self.ticket_submit_order['ticket_type']['adult']
                else:
                    return t0
            else:
                return (self.ticket_submit_order['ticket_type']['adult'] if t3 == '' else t3) if t0 == '' else t0

    def ticket_type2(self, t1):
        for v in self.ticket_submit_order['passenger_type'].values():
            if t1 == v:
                return v
        else:
            return ''

    @staticmethod
    def ticket_submit_order():
        """获取车票提交订单信息"""
        tso = json.load(open('ticket_submit_order.json', 'r', encoding='utf-8'))
        return tso

    def check_order_info(self, token):
        """验证订单信息"""
        url = 'https://kyfw.12306.cn/otn/confirmPassenger/checkOrderInfo'
        data = {
            'cancel_flag': '2',
            'bed_level_order_num': '000000000000000000000000000000',
            'passengerTicketStr': self.get_passenger_tickets(),
            'oldPassengerStr': self.get_old_passengers(),
            'tour_flag': self.ticketInfoForPassengerForm['tour_flag'],
            'randCode': '',
            '_json_att': '',
            'REPEAT_SUBMIT_TOKEN': token
        }

        res = self.session.post(url, data=data, verify=False)

        msg = json.loads(res.text)
        print('check_order_info:')
        print(msg)

        if msg['status']:
            if msg['data']['submitStatus']:
                if 'get608Msg' not in msg['data'] or not msg['data']['get608Msg']:
                    return True
        else:
            print(msg['messages'])
            return False

    @staticmethod
    def str2date_format1(str):
        """字符串转日期格式 yyyy-MM-dd"""
        l = list(str)
        l.insert(4, '-')
        l.insert(-2, '-')
        return ''.join(l)


    def get_passengers(self, token):
        """获取乘客信息"""
        url = 'https://kyfw.12306.cn/otn/confirmPassenger/getPassengerDTOs'
        data = {
            '_json_att': '',
            'REPEAT_SUBMIT_TOKEN': token
        }
        res = self.session.post(url, data=data, verify=False)
        html = res.text
        msg = json.loads(html)
        if msg['status'] and msg['data']['isExist']:
            self.M = msg['data']['dj_passengers']
            self.ay = msg['data']['normal_passengers']
            return msg['data']['normal_passengers']
        else:
            print("没有获取到乘客信息")
            return None


    def get_common_data(self, text):
        """获取订单确认页面里面的通用数据"""
        self.ticketInfoForPassengerForm = self.get_dict(r'var ticketInfoForPassengerForm=(.*?);', text)  # 车票信息
        self.init_seatTypes = self.get_dict(r'var init_seatTypes=(.*?);', text)  # 初始所有座位类型
        self.defaultTicketTypes = self.get_dict(r'var defaultTicketTypes=(.*?);', text)  # 默认车票类型
        self.init_cardTypes = self.get_dict(r'var init_cardTypes=(.*?);', text)  # 初始证件类型
        self.ticket_seat_codeMap = self.get_dict(r'var ticket_seat_codeMap=(.*?);', text)  # 车票座位代码地图
        self.orderRequestDTO = self.get_dict(r'var orderRequestDTO=(.*?);', text)  # 订单请求DTO
        self.id_type_code = re.findall(r'var id_type_code = \'(.*?)\'', text)[0]
        #print(json.dumps(self.ticketInfoForPassengerForm, sort_keys=True, indent=2, ensure_ascii=False))
        # print(json.dumps(self.ticket_submit_order, sort_keys=True, indent=2, ensure_ascii=False))
        self.D = self.P(self.ticket_seat_codeMap, self.defaultTicketTypes)

    def P(self, ticket_seat_codeMap, defaultTicketTypes):
        arr = []
        for m in ticket_seat_codeMap:
            for t in defaultTicketTypes:
                if t['id'] == m:
                    arr.append(t)
                    break
        return sorted(arr, key=lambda t: t['id'])
