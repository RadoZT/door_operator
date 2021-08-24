#Libraries
import sys
import os
from utils import conf_module
from signal import signal, SIGINT
from utils import timer33 as timererr
from utils import timer33 as timerfan # timer for fan to start
from utils import timer33 as timerfan_stop # timer for fan to stop
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
rr2 = 21 # reed relay down



pir1 = 12 # in front of garage door
pir2 = 16 # next to human door

fb = 20 # button for fan

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



p1_st = gpio.input(pir1)
p2_st = gpio.input(pir2)
#fb_st = gpio.input(20)
rev_st = gpio.input(rev)
r1_st = gpio.input(rr1)
r2_st = gpio.input(rr2)


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



close_counter = 60
open_counter = 10
#move_counter_up = 0
#move_counter_down = 0
move_counter = 0
bad_counter = 0
pir1_counter = 60
pir2_counter = 60

bt_st = 0

printflag = 0
lock_c = threading.Lock()


def reed_relay():
    global open_counter, close_counter, bad_counter, move_counter
    global rron1, rron2, ddefect, rrof
    global rr2, rr1, bt_st
    timerfan.timer_max = 1 # *90
    timerfan_stop.timer_max = 1 # *90
    r2_st = gpio.input(rr2)
    if gpio.input(rr1) == gpio.HIGH and gpio.input(rr2) == gpio.HIGH:
        rrof = 'ReedRelay defect'
        print('ReedRelay defect')
        if bad_counter == 30:
            print('bad', bad_counter)
            sync_event.set()
            bad_counter = 0
            print('rr defect')
            
        else:
            bad_counter += 1
            print('sliprrdef')
            sleep(1)
    
    elif gpio.input(rr1) == gpio.LOW and gpio.input(rr2) == gpio.LOW:
        rrof = ' '
        print ('move', move_counter)
        if move_counter == 30:
            sync_event.set()
            move_counter = 0
            print('Door defect')
            ddefect = 'Door defect'
        else:
           move_counter += 1
           print('slip door def')
           sleep(1)
    else:
        ddefect = ' ' 
        if gpio.input(rr2) == gpio.HIGH:
            print('everything is ok with pirs', close_counter)
            gpio.output(err_horn, gpio.LOW)
            gpio.output(motor, gpio.LOW)
            rron2 = 'Door is closed'
            erron = ' '
            move_counter = 0
            pir1_counter = 60
            pir2_counter = 60
            if close_counter <= 0:
                sync_event.set()
                close_counter = 60
            else:
                close_counter -= 1
                print('sliprr2')
                sleep(1)
            bt_st = 4
            
        else:
            rron2 = 'Door is NOT closed '

            
        if gpio.input(rr1) == gpio.HIGH:
            print('Door is open', open_counter)
            rron1 = 'Door is open and pir sensors are on'
            if open_counter <= 0:
                sync_event.set()
                open_counter = 10
            else:
                open_counter -= 1
                print('sliprr1')
                sleep(1)
        else:
            rron1 = ' '
    
    if gpio.input(rr2) == gpio.LOW:
        fan_s()



def pir():
    global pir1_counter, pir2_counter, open_counter, close_counter
    global piron1, piron2, fbon, revon,lamp, rron1, rron2, ddefect, rrof, erron, motst#motorstate
    global pir1, pir2, fb,rev
    global rr2, rr1
    timererr.timer_max = 1 # *6
    
    lock_c.acquire()
    
    
    fan_button()
    reed_relay()
        
        
    if gpio.input(pir1) == gpio.LOW and gpio.input(pir2) == gpio.LOW and gpio.input(rr2) == gpio.LOW:
        rr()
        piron1 = ' '
        piron2 = ' '
        revon = ' '
        lamp = 'Lamps are off'
        
        timererr.timer_callback = error
        timererr.timer_start()
        
    else:
        if gpio.input(pir1) == gpio.HIGH:
            print ('car entring', pir1_counter)
            piron1 = 'Car entring'
            gpio.output(err_horn, gpio.LOW)
            lamp = 'Lamp is on'
            if pir1_counter <= 0:
                #lamp = 'Lamp is on'
                sync_event.set()
                pir1_counter = 60
            else:
                pir1_counter -= 1
                print('slipp1')
                sleep(1)
            ddefect = ' '
            erron = ' '
            
            
        if gpio.input(pir2) == gpio.HIGH:
            print ('Human entring from lifter')
            piron2 = 'Human entring from lifter'
            gpio.output(err_horn, gpio.LOW)
            lamp = 'Lamp is on'
            if pir2_counter <= 0:
                #lamp = 'Lamp is on'
                sync_event.set()
                pir2_counter = 60
            else:
                pir2_counter -= 1
                print('slipp2')
                sleep(1)
            ddefect = ' '
        
  
        
    lock_c.release()
    

def fan_button():
    # state
    # 0 start up.  LEDs off.
    # 1 button pressed.  Red LED on
    # 2 button not pressed.  Red LED on
    # 3 button pressed.  Red LED off
    # 4 button not pressed.  Red LED on
    
    global bt_st, fb_st
    
    fb_st = gpio.input(20)
    
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
        if fb_st:
            bt_st=3
            
    elif bt_st==3:
        gpio.output(17,False)
        fbon = 'Fan is stopped'
        if not(fb_st):
            bt_st=4
                
    elif bt_st==4:
        gpio.output(17,False)
        fbon = 'Fan is stopped'
        if fb_st:
            bt_st=1
    print('state', bt_st)
    


def error():
    global erron
    print ('WARNING DOOR IS OPEN')
    erron = 'WARNING DOOR IS OPEN'
    gpio.output(err_horn, gpio.HIGH)
    gpio.output(motor, gpio.HIGH)
    sync_event.set()
    
def fan_s():
    global fbon, bt_st
    bt_st = 2
    print ('Fan is started')
    fbon = 'Fan is started'
    timerfan_stop.timer_callback = fan_stop
    timerfan.timer_start()
    
def fan_stop():
    global fbon, bt_st
    bt_st = 4
    print ('Fan is stoped')
    fbon = 'Fan is stoped'
    timerfan.timer_callback = fan_s
    timerfan.timer_start()

def rr():
    global lock_c, printflag
    global open_counter, close_counter
    global rron1, rron2
    global rr1, rr2

        
    if gpio.input(rr1) == gpio.HIGH:
        print('have to close the door', open_counter)
        rron1 = 'Door is open'
        if open_counter <= 0:
            sync_event.set()
            gpio.output(motor, gpio.HIGH)
            open_counter = 10
        else:
            open_counter -= 1
            print('sliprr1')
            sleep(1)
            gpio.output(motor, gpio.LOW)
    else:
        gpio.output(motor, gpio.LOW)
        rron1 = ' '
        
    if gpio.input(rr2) == gpio.HIGH:
        print('everything is ok', close_counter)
        gpio.output(err_horn, gpio.LOW)
        gpio.output(motor, gpio.LOW)
        rron2 = 'Door is closed'
        erron = ' '
        if close_counter <= 0:
            sync_event.set()
            close_counter = 60
        else:
            close_counter -= 1
            print('sliprr2')
            sleep(1)
    else:
        close_counter = 0
        rron2 = ' '
        
def upload_data():
    global check_counter, config
    data = get_data()
    rjson = {'return_code':'not-accesibble', 'return_message':'exception', 'return_data':None}
    #print(data)
    try:
        #print (config["service_url"])
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
    pir()
    dattmn = datetime.now()
    dattmn = tmz.localize(dattmn)
    dattmn_str = str(dattmn)
    
    
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
        upload_data()

        if exit_flag:
            break

def exit_handler(signal_recieved, frame):
    global exit_flag
    exit_flag = True
    sync_event.set()
    #print('gracefully finish counter thread - 2, Ctrl - C')
    exit(0)

if __name__ == '__main__':
    print('START THE PROGRAMMMMMMMMM')
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
    tmz = pytz.timezone('EET')
    dattmn = tmz.localize(dattmn)
    dattmn_str = str(dattmn)

    script_dir = os.path.dirname(os.path.abspath(__file__))
    conf_dir = os.path.join(script_dir, 'conf')

    confpath = os.path.join(conf_dir,conf_name)

    config = conf_module.load_conf(confpath)
    if config == None:
        exit(1)
    
    th = threading.Thread(target=upload_thread_function)
    th.start()
    while True:
        pir()

        sleep(0.1) #1
    #sync_event.set()
        if exit_flag:
            break

    #TODO: join the thread
    exit_flag = True
    sync_event.set()
    th.join()
    print('Gracefully finish the counter thread - 1')
    exit(0)
