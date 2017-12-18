# -*- coding: utf-8 -*-
import json

import time
from flask import Flask, request, render_template, session,redirect,url_for
from crawl import GrabTicket
app = Flask(__name__)
app.secret_key='\xf1\x92Y\xdf\x8ejY\x04\x96\xb4V\x88\xfb\xfc\xb5\x18F\xa3\xee\xb9\xb9t\x01\xf0\x96'

grabTicket = GrabTicket()

#用来填写订票信息
@app.route('/', methods=['GET', 'POST'])
def home():
    return render_template('index.html')

#登出
@app.route('/logout', methods=['GET', 'POST'])
def logout():
    if 'username' in session:
        session.pop('username')
    return render_template('index.html')

#进入12306账号登录界面
@app.route('/signin', methods=['GET'])
def signin():
    return render_template('log.html')

#12306表单提交 ， 进入index页面
@app.route('/signin', methods=['POST'])
def signin_form():
    username = request.form['user_name']
    password = request.form['user_password']
    #print(username)
    #print(password)
    #False or realname
    result = grabTicket.login(user_name=username,user_password=password)
    # result = 'tan'
    if result == False:
        return render_template('log.html', message='Bad username or password', username=username)
    else:
        session['username'] = result
        #print(result)
        return render_template('index.html',username=result)

@app.route('/show',methods=['POST','GET'])
def show():
    _from = request.form['_from']
    _to = request.form['_to']
    _d = request.form['_d']
    _d = time.strftime("%Y-%m-%d", time.strptime(_d, "%Y-%m-%d"))
    tick_info = grabTicket.ticket_info(_from,_to,_d)
    if tick_info == False:
        return render_template('show.html',_from = _from , _to = _to,_d = _d )
    tick_info = eval(tick_info)
    tickets_info = []
    cnt = 0
    for info in tick_info:
        tmp = {}
        tmp['_from'] = _from
        tmp['_to'] = _to
        tmp['_d'] = _d
        tmp['no'] = info['车次']
        tmp['secretStr'] = info['secretStr']
        tmp['start_time'] = info['出发时间']
        tmp['arrive_time'] = info['到达时间']
        tmp['len'] = info['历时']
        tmp['t_perice'] = info['商务座特等座'] if info['商务座特等座'] else '--'
        tmp['y_perice'] = info['一等座'] if info['一等座'] else '--'
        tmp['e_perice'] = info['二等座'] if info['二等座'] else '--'
        tmp['g_perice'] = info['高级软卧'] if info['高级软卧'] else '--'
        tmp['r_perice'] = info['软卧'] if info['软卧'] else '--'
        tmp['d_perice'] = info['动卧'] if info['动卧'] else '--'
        tmp['yw_perice'] = info['硬卧'] if info['硬卧'] else '--'
        tmp['rz_perice'] = info['软座'] if info['软座'] else '--'
        tmp['yz_perice'] = info['硬座'] if info['硬座'] else '--'
        tmp['wz_perice'] = info['无座'] if info['无座'] else '--'
        tmp['other_perice']=info['其它'] if info['其它'] else '--'
        tmp['index'] = cnt
        cnt = cnt + 1
        tickets_info.append(tmp)
    return render_template('show.html',_from = _from , _to = _to,_d = _d , tickets_info = tickets_info)

@app.route('/cdate',methods=['POST','GET'])
def show2():
    data = json.loads(request.form.get('data'))
    _from = data['_from']
    _to = data['_to']
    _d = data['_d']
    _d =  time.strftime("%Y-%m-%d",time.strptime(_d, "%Y-%m-%d"))
    tick_info = grabTicket.ticket_info(_from,_to,_d)
    if tick_info == False:
        return render_template('show.html',_from = _from , _to = _to,_d = _d )
    tick_info = eval(tick_info)
    tickets_info = []
    for info in tick_info:
        tmp = {}
        tmp['_from'] = _from
        tmp['_to'] = _to
        tmp['_d'] = _d
        tmp['no'] = info['车次']
        tmp['secretStr'] = info['secretStr']
        tmp['start_time'] = info['出发时间']
        tmp['arrive_time'] = info['到达时间']
        tmp['len'] = info['历时']
        tmp['t_perice'] = info['商务座特等座'] if info['商务座特等座'] else '--'
        tmp['y_perice'] = info['一等座'] if info['一等座'] else '--'
        tmp['e_perice'] = info['二等座'] if info['二等座'] else '--'
        tmp['g_perice'] = info['高级软卧'] if info['高级软卧'] else '--'
        tmp['r_perice'] = info['软卧'] if info['软卧'] else '--'
        tmp['d_perice'] = info['动卧'] if info['动卧'] else '--'
        tmp['yw_perice'] = info['硬卧'] if info['硬卧'] else '--'
        tmp['rz_perice'] = info['软座'] if info['软座'] else '--'
        tmp['yz_perice'] = info['硬座'] if info['硬座'] else '--'
        tmp['wz_perice'] = info['无座'] if info['无座'] else '--'
        tmp['other_perice']=info['其它'] if info['其它'] else '--'
        tickets_info.append(tmp)
    a = {'123':'123'}
    return json.dumps(a,ensure_ascii=False)

@app.route('/choose',methods=['POST','GET'])
def choose():
    seats_info = []
    if request.form == []:
        a = {'a': 'a'}
        return json.dumps(a, ensure_ascii=False)
    data = json.loads(request.form.get('data'))
    k = data['secretStr'].strip()
    _from = data['startStation'].strip()
    _to = data['endStation'].strip()

    k = int(k)
    train_info = grabTicket.info[k]
    session['train_info'] = train_info
    data = grabTicket.submit_order(_from,_to,k)
    if type(data) == type('123'):
        data = eval(data)
    for d in data:
        tmp = {}
        tmp['seattype'] = d.split('(')[0]
        tmp['price'] = d.split('(')[1].split(')')[0]
        tmp['have_ticket'] = d.split('(')[1].split(')')[1]
        seats_info.append(tmp)

    if 'ticket' in session:
        session.pop('ticket')

    session['ticket'] = seats_info
    a={'a':'a'}
    return json.dumps(a,ensure_ascii=False)

@app.route('/bookticket',methods=['POST','GET'])
def book_ticket():
    print(session['username'])
    seats_info = session['ticket']
    if 'train_info' in session:
        train_info = session['train_info']
        train = {
            '_code':train_info['车次'],
            'start_date':str2date_format1(train_info['出发日']),
            'end_date': str2date_format1(train_info['出发日']),
            'start_time':train_info['出发时间'],
            'end_time':train_info['到达时间'],
            'start_station':train_info['出发站'],
            'end_station':train_info['到达站'],
            'ls':train_info['历时']
        }
        return render_template('order.html',seats_info = seats_info , train_info = train )
    return   render_template('order.html',seats_info = seats_info)

@app.route('/confirm_book',methods=['POST','GET'])
def last():
    seat = request.form.get('seat')
    price = request.form.get('price')
    print(seat,price)
    if seat == '硬座':
        grabTicket.confirm_passenger2('1',seat+'('+price+')')
    elif seat == '硬卧':
        grabTicket.confirm_passenger2('1',seat+'('+price+')')
    return render_template('success.html')

def str2date_format1(str):
    """字符串转日期格式 yyyy-MM-dd"""
    l = list(str)
    l.insert(4, '-')
    l.insert(-2, '-')
    return ''.join(l)

if __name__ == '__main__':
    app.run(host='0.0.0.0',port=5000)