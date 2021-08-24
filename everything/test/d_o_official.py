
#Libraries
import sys
import os
from utils import conf_module
from utils import timer33
from signal import signal, SIGINT
import RPi.GPIO as gpio
print('import requests')
import requests
import json
from collections import namedtuple
from datetime import datetime, date, time, timezone
import pytz
from time import sleep
import threading


gpio.setwarnings(False)



gpio.cleanup()



#GPIO Mode (BOARD / BCM)
gpio.setmode(gpio.BCM)


fan = 17
motor = 27



rr1 = 23 # reed relay up
rr2 = 24 # reed relay down



pir1 = 12 # in front of garage door
pir2 = 16 # next to kotelno door
pir3 = 20 # next to human door
pir4 = 21 # next to last door, in the bottom ap.4/5



err_horn = 26 # start error horn



#set GPIO direction (IN / OUT)
gpio.setup(rr1, gpio.IN, pull_up_down=gpio.PUD_DOWN)
gpio.setup(rr2, gpio.IN, pull_up_down=gpio.PUD_DOWN)
gpio.setup(motor, gpio.OUT)
gpio.setup(err_horn, gpio.OUT)
gpio.setup(fan, gpio.OUT)
gpio.setup(pir1, gpio.IN, pull_up_down=gpio.PUD_DOWN)
gpio.setup(pir2, gpio.IN, pull_up_down=gpio.PUD_DOWN)
gpio.setup(pir3, gpio.IN, pull_up_down=gpio.PUD_DOWN)
gpio.setup(pir4, gpio.IN, pull_up_down=gpio.PUD_DOWN)



p1_st = gpio.input(pir1)
p2_st = gpio.input(pir2)
p3_st = gpio.input(pir3)
p4_st = gpio.input(pir4)
r1_st = gpio.input(rr1)
r2_st = gpio.input(rr2)


piron1 = ' '
piron2 = ' '
piron3 = ' '
piron4 = ' '
rron1 = ' '
rron2 = ' '
rrof = ' '
ddefect = ' '
erron = ' '
lamp = ' '


close_counter = 0
open_counter = 10
#move_counter_up = 0
#move_counter_down = 0
move_counter = 0
bad_counter = 0
lamp_counter = 0


printflag = 0
lock_c = threading.Lock()


def pir():
    global lamp_counter
    global piron1, piron2, piron3, piron4,lamp, rron1, rron2, ddefect, rrof, erron, motst#motorstate
    global pir1, pir2, pir3, pir4
    global rr2
    lock_c.acquire()

    if gpio.input(pir1) == gpio.LOW and gpio.input(pir2) == gpio.LOW and gpio.input(pir3) == gpio.LOW and gpio.input(pir4) == gpio.LOW:
        rr()
        rr_err()
        lamp_counter = 0
        piron1 = ' '
        piron2 = ' '
        piron3 = ' '
        piron4 = ' '
        lamp = 'Lamps are off'
        gpio.output(fan, gpio.LOW)
        
    else:
        if gpio.input(pir1) == gpio.HIGH:
            print ('car entring', lamp_counter)
            piron1 = 'Car entring'
            gpio.output(err_horn, gpio.LOW)
            lamp = 'Lamp is on'
            if lamp_counter <= 0:
                #lamp = 'Lamp is on'
                sync_event.set()
                lamp_counter = 60
            else:
                lamp_counter -= 1
                print('slipp1')
                sleep(1)
            close_counter = 0
            ddefect = ' '
            erron = ' '
            
            
        if gpio.input(pir2) == gpio.HIGH:
            print ('human entring from kotelno')
            piron2 = 'Human entring from kotelno'
            gpio.output(err_horn, gpio.LOW)
            lamp = 'Lamp is on'
            if lamp_counter <= 0:
                #lamp = 'Lamp is on'
                sync_event.set()
                lamp_counter = 60
            else:
                lamp_counter -= 1
                print('slipp2')
                sleep(1)
                
            ddefect = ' '
        
        if gpio.input(pir3) == gpio.HIGH:
            print ('Human entring from lifter')
            piron3 = 'Human entring from lifter'
            gpio.output(err_horn, gpio.LOW)
            lamp = 'Lamp is on'
            if lamp_counter <= 0:
                #lamp = 'Lamp is on'
                sync_event.set()
                lamp_counter = 60
            else:
                lamp_counter -= 1
                print('slipp3')
                sleep(1)
                
            ddefect = ' '
        
        if gpio.input(pir4) == gpio.HIGH:
            print ('human entring from abonatno')
            piron3 = 'Human entring from abonatno'
            gpio.output(err_horn, gpio.LOW)
            lamp = 'Lamp is on'
            if lamp_counter <= 0:
                #lamp = 'Lamp is on'
                sync_event.set()
                lamp_counter = 60
            else:
                lamp_counter -= 1
                print('slipp4')
                sleep(1)
                
            ddefect = ' '
    
    if gpio.input(rr1) == gpio.HIGH:
        print('Door is open')
        rron1 = 'Door is open'
    else:
        rron1 = ' '
        
    if gpio.input(rr2) == gpio.HIGH:
        print('Door is closed')
        gpio.output(err_horn, gpio.LOW)
        gpio.output(motor, gpio.LOW)
        rron2 = 'Door is closed'
    else:
        rron2 = 'Door is NOT closed '
    
    if gpio.input(rr2) == gpio.LOW:
        gpio.output(fan, gpio.HIGH)
        sleep(10)
        gpio.output(fan, gpio.LOW)
        sleep(10)
    else:
        gpio.output(fan, gpio.LOW)
        
    lock_c.release()
    

def error():
    global erron
    print ('WARNING DOOR IS OPEN')
    erron = 'WARNING DOOR IS OPEN'
    gpio.output(err_horn, gpio.HIGH)
    sync_event.set()
    
def rr_err():
    global rr2
    timer33.timer_max = 1 # *6
    if gpio.input(rr2) == gpio.LOW:
        timer33.timer_callback = error
        timer33.timer_start()

def rr():
    global lock_c, printflag
    global open_counter, close_counter, bad_counter, move_counter
    global rron1, rron2, ddefect, rrof
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
        
    if gpio.input(rr1) == gpio.HIGH and gpio.input(rr2) == gpio.HIGH:
        rrof = 'ReedRelay defect'
        if bad_counter == 30:
            print('bad', bad_counter)
            sync_event.set()
            bad_counter = 0
            print('rr defect')
            
        else:
            bad_counter += 1
            print('sliprrdef')
            sleep(1)
    else :
        rrof = ' '
    
    if gpio.input(rr1) == gpio.LOW and gpio.input(rr2) == gpio.LOW:
        print ('move', move_counter)
        ddefect = 'Door defect'
        if move_counter == 30:
            sync_event.set()
            move_counter = 0
            print('Door defect')
        else:
           move_counter += 1
           print('slip door def')
           sleep(1)
    else:
        ddefect = ' '
        

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
                'data_f':[float (p1_st), float (p2_st), float (p3_st), float (p4_st), float (r1_st), float (r2_st)],
                #'data_d':[uptime()],
                'data_t':[piron1, piron2, piron3, piron4, lamp, rron1, rron2, ddefect, rrof, erron]
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
        print('slip while')
        if gpio.input(rr2) == gpio.HIGH:
            print('recicle the timers and everything is okkkkkkk, stop everything')
            open_counter = 0
            #move_counter_up = 0
            #move_counter_down = 0
            move_counter = 0
            bad_counter = 0
            
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
