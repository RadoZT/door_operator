#Libraries
import sys
from datetime import datetime
import os
from utils import conf_module
from signal import signal, SIGINT
from utils.timer33 import Timer34 as Timer34
import RPi.GPIO as gpio
print('import requests')
import requests
print('ready with importing')
import json
from collections import namedtuple
from datetime import datetime, date, time, timezone
import pytz
from time import sleep
import threading

gpio.setwarnings(False)

gpio.cleanup()

#gpio Mode (BOARD / BCM)
gpio.setmode(gpio.BCM)

fan = 17
motor = 27

rr1 = 23 # reed relay up
rr2 = 24 # reed relay down

pir1 = 12 # in front of garage door
pir2 = 16 # next to human door

fb = 13 # button for fan

rev = 21 # reserve

err_horn = 26 # start error horn

#set gpio direction (IN / OUT)
gpio.setup(rr1, gpio.IN, pull_up_down=gpio.PUD_DOWN)
gpio.setup(rr2, gpio.IN, pull_up_down=gpio.PUD_DOWN)
gpio.setup(motor, gpio.OUT)
gpio.setup(err_horn, gpio.OUT)
gpio.setup(fan, gpio.OUT)
gpio.setup(pir1, gpio.IN, pull_up_down=gpio.PUD_DOWN)
gpio.setup(pir2, gpio.IN, pull_up_down=gpio.PUD_DOWN)
gpio.setup(fb, gpio.IN, pull_up_down=gpio.PUD_DOWN)
gpio.setup(rev, gpio.IN, pull_up_down=gpio.PUD_DOWN)


piron1 = ' '
piron2 = ' '
fbon = ' '
revon = ' '
rron1 = ' '
rron2 = ' '
rrof = ' '
ddefect = ' '
erron = ' '
lamp = ' '

bt_st = 0

timererr = Timer34()
timer_doоropenalarm_expired = Timer34()
timer_reedrelayalarm_expired = Timer34()
timer_downup_expired = Timer34()
timer_updown_expired = Timer34()
timer_main = Timer34()
timerfan_stop = Timer34()


dtime = datetime.now()
printflag = 0
lock_c = threading.Lock()

def openalarm():
    global erron
    print ('WARNING DOOR IS OPEN')
    erron = 'WARNING DOOR IS OPEN'
    gpio.output(err_horn, gpio.HIGH)
    gpio.output(motor, gpio.HIGH)
    sleep(1)
    gpio.output(motor, gpio.LOW)
    sync_event.set()
    
def reedrelay_defect():
    global erron
    print ('WARNING REED RELAY DEFFECT')
    erron = 'WARNING REED RELAY DEFFECT'
    sync_event.set()
    
def pir_state():
    global lamp, piron1, piron2, timererr
    p1_st = gpio.input(pir1)
    p2_st = gpio.input(pir2)
    r2_st = gpio.input(rr2)
    
    
    if not p1_st and not p2_st and not r2_st:
        piron1 = 'pir1 NO'
        piron2 = 'pir2 Door is open'
        lamp = 'There is no one in the garage and door is open'
        print('There is no one in the garage and door is open')
        timererr.timer_callback = openalarm
        timererr.timer_start(s = 'err')
    elif not p1_st and not p2_st and r2_st:
        piron1 = 'pir1 NO'
        piron2 = 'pir2 NO'
        lamp = 'There is no one in the garage'
        print('There is no one in the garage')
    else:
        lamp = 'There is someone in the garage'
        print('There is someone in the garage')

def door_state():
    global rrof, rron1, rron2, ddefect, erron, lamp, piron1, piron2, fbon
    global timer_downup_expired
    global timer_updown_expired
    global timer_doоropenalarm_expired
    global timer_reedrelayalarm_expired
    
   
    r1_st = gpio.input(rr1)
    r2_st = gpio.input(rr2)
    p1_st = gpio.input(pir1)
    p2_st = gpio.input(pir2)
    
    
    rto = r1_st # reedtop_old
    rbo = r2_st # reedbottom_old
    print('reed relay top old',rto)
    print('reed relay bottom old',rbo)
    if r1_st and r2_st:
        timer_reedrelayalarm_expired.timer_callback = reedrelay_defect
        timer_reedrelayalarm_expired.timer_start(s = 'reed relay')
        door_st = 5 # reed relay are stuck
        print('door_st = ', door_st)
        rron1 = 'REED RELAY IS UP AND DOWN'
        rron2 = 'REED RELAY IS UP AND DOWN'
    
    elif r2_st:
        door_st = 0 # door is closed
        print('door_st, door is closed = ', door_st)
        rron2 = 'Door is closed, everything is OK'
        rron1 = 'NO'
        erron = 'No problem'
        gpio.output(err_horn, gpio.LOW)
        gpio.output(motor, gpio.LOW)
    elif r1_st:
        door_st = 1 # door is open
        print('door_st, door is open = ', door_st)
        rron1 = 'Door is open, have to be closed in time'
        rron2 = ' '
        timer_doоropenalarm_expired_callback = openalarm
        timer_doоropenalarm_expired.timer_start(s = 'door open0')
    elif not r1_st and not r2_st:
        door_st = 4 # dood is moving
        print('door_st, dood is moving = ', door_st)
        rron1 = 'MOVING'
        rron2 = 'MOVING'
        timer_doоropenalarm_expired_callback = openalarm
        timer_doоropenalarm_expired.timer_start(s = 'door open1')
        
def fan_button():
    # state
    # 0 start up.  FAN off.
    # 1 button pressed.  Red FAN on
    # 2 button not pressed.  Red FAN on
    
    
    global bt_st, fb_st, fb, timerfan_stop
    
    fb_st = gpio.input(fb)
    
    if bt_st==0:
        gpio.output(17,False)
        if fb_st:
            bt_st=1
            
    elif bt_st==1:
        gpio.output(17,True)
        fbon = 'Fan is started'
        if not(fb_st):
            bt_st=2
    elif bt_st==2:
        gpio.output(17,True)
        fbon = 'Fan is working'
        timerfan_stop.timer_callback = fan_stop
        timerfan_stop.timer_start(s = 'fan')
        if fb_st:
            bt_st=3
            
    elif bt_st==3:
        gpio.output(17,False)
        fbon = 'Fan is stoped'
        if not(fb_st):
            bt_st=4
    elif bt_st==2:
        gpio.output(17,True)
        fbon = 'Fan is stoped'
        if fb_st:
            bt_st=1
    print('bt_st = ', bt_st)         

def fan_stop():
    global fbon, bt_st
    print ('Fan is stoped')
    fbon = 'Fan is stoped'
    bt_st = 0

def main():
    global open_counter, close_counter, move_counter, bad_counter, pir1_counter, pir2_counter
    global rrof, rron1, rron2, ddefect, erron, lamp, piron1, piron2, fbon
    global rr1, rr2, pir1, pir2, fan, motor, fb, err_horn
    global timer_main, timerfan_stop
    global bt_st
    lock_c.acquire()
    
    door_state()
    pir_state()
    

    #print('settt', timer_main.timer_max)
    timer_main.timer_callback = syncing
    timer_main.timer_start(s = 'main')
    #print('tmtmt', timer_main.timer_max)
    lock_c.release()

def syncing():
    sync_event.set()
    print ('-------------------------------------------------syncinggg with the cloud--------------------------------------------------------------------')
    timer_main.timer_start(s = 'main')
    
def upload_data():
    global check_counter, config
    data = get_data()
    
    rjson = {'return_code':'not-accesibble', 'return_message':'exception', 'return_data':None}
    #print(data)
    try:
        #print ('service_url=',config["service_url"])
        response = requests.post(config["service_url"],
                     json = data, verify=False)

        rjson['return_code'] = 'OK'
        rjson['return_message'] = 'success'
        try:
            rjson['return_data'] = response.json()
        except:
            pass
        #print('data sent')
        return ('success sending data',rjson)
    except Exception as e1:
        check_counter =0
        rjson['return_code'] = 'error connecting to host'
        rjson['return_message'] = str(e1)
        #print('exception sending data')
        return ('exception sending data',rjson)

    response.encoding = 'utf-8'

    try:
        rjson = response.json()
    except  Exception as e2:
        rjson['return_code'] = 'error parsing response'
        rjson['return_message'] = str(e2)

    return (response.status_code,rjson)

def get_data():
    global lock_c, old_timestamp, time_delay, printflag
    global bad_situation_message, upload_sensor_data_timestamp
    global piron1, piron2, piron3, piron4, rron1, rron2, ddefect, rrof, erron, lamp
    global p1_st, p2_st, p3_st, p4_st, r1_st, r2_st
    
    dattmn = datetime.now()
    dattmn = tmz.localize(dattmn)
    dattmn_str = str(dattmn)
    
    r1_st = gpio.input(rr1)
    r2_st = gpio.input(rr2)
    p1_st = gpio.input(pir1)
    p2_st = gpio.input(pir2)
    fb_st = gpio.input(fb)

    
    return_obj = {'command':'data',
                'timestamp':dattmn_str,
                'ids':{
                        'checknode':config['checknode'],
                        'controller':config['controller'],
                        'sensor':config['sensor']
                    },
                'data_f':[float (p1_st), float (p2_st), float (fb_st), float (r1_st), float (r2_st)],
                #'data_d':[uptime()],
                'data_t':[piron1, piron2, fbon, lamp, rron1, rron2, ddefect, rrof, erron]
            }
    return return_obj

sync_event = threading.Event()
exit_flag = False

def upload_thread_function():
    global sync_event, exit_flag, printflag

    while True:
        sync_event.wait()
        sync_event.clear()
        #print('thread sync')
        res = upload_data()
        #print(res)
        if exit_flag:
            break

def exit_handler(signal_recieved, frame):
    global exit_flag
    exit_flag = True
    sync_event.set()
    #print('gracefully finish counter thread - 2, Ctrl - C')
    exit(0)



if __name__ == '__main__':
    global conf_module
    signal(SIGINT, exit_handler)
    gpio.setmode(gpio.BCM)

    conf_name = 'sensors.conf'
    log_name = None

    if (len(sys.argv) > 1):
        conf_name = sys.argv[1]
    if (len(sys.argv) > 2):
        log_name = sys.argv[2]

    dattmn = datetime.now()
    print('calling pytz', dattmn)
    tmz = pytz.timezone('EET')
    print('ready pytz', dattmn)
    dattmn = tmz.localize(dattmn)
    dattmn_str = str(dattmn)
    script_dir = os.path.dirname(os.path.abspath(__file__))
    conf_dir = os.path.join(script_dir, 'conf')

    confpath = os.path.join(conf_dir,conf_name)

    config = conf_module.load_conf(confpath)
    if config == None:
        exit(1)
    #print(config)
    
    th = threading.Thread(target=upload_thread_function)
    th.start()
    #print('proverka 2')
    x = 0
    
    
    timer_main.timer_max = 18 # 18 = 3min
    timerfan_stop.timer_max = 2 # 90 = 15min
    timer_downup_expired.timer_max = 3 # 3 = 30sec
    timer_updown_expired.timer_max = 3 # 3 = 30sec
    timer_doоropenalarm_expired.timer_max = 1 # 6 = 1min 
    timer_reedrelayalarm_expired.timer_max = 6 # 6 = 1min
    timererr.timer_max = 5 # 30 = 5min
    
    main()
    
    while True:
        #print('while loop')
        x = x + 1
        print(x)
        fan_button()
        if bt_st==2:
            timerfan_stop.timer_callback = fan_stop
            timerfan_stop.timer_start(s = 'fan')
        sleep(1)
        #sync_event.set()
        if exit_flag:
            break

    #TODO: join the thread
    exit_flag = True
    sync_event.set()
    th.join()
    print('Gracefully finish the counter thread - 1')
    exit(0)
    
    