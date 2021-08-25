
# -*- coding: utf-8 -*-
import sys
import os
from signal import signal, SIGINT
#from sys import exit
import utils
from utils import conf_module, write_log
import requests
import json
from collections import namedtuple
from datetime import datetime, date, time, timezone
import pytz
import RPi.GPIO as gpio
from time import sleep
import threading
from subprocess import check_output, call, PIPE, STDOUT, DEVNULL
from urllib.parse import urlparse

config = None
masterhost = ''
sleep_time = 20.0
check_counter = 0
ips = ''

old_timestamp = datetime.now()
curr_timestamp = datetime.now()

def host_is_accessible(host):
    """
    Return 0 if there is route to host and !=0 in other cases
    """
    return call(['ping','-c','1',host],stdout=DEVNULL, stderr=DEVNULL)


def upload_data():
    global check_counter
    #print('start upload data')
    #print(data)
    data = get_data()
    #print(data)
    rjson = {'return_code':'not-accesibble', 'return_message':'exception', 'return_data':None}
    try:
        response = requests.post(config["service_url"],
                     json = data, verify=False)
        #sleep_time = 600
        #gpio.output(ch_n, gpio.HIGH)
        rjson['return_code'] = 'OK'
        rjson['return_message'] = 'success'
        try:
            rjson['return_data'] = response.json()
        except:
            pass
        print('data sent')
        return ('success sending data',rjson)
    except Exception as e1:
        check_counter =0
        rjson['return_code'] = 'error connecting to host'
        rjson['return_message'] = str(e1)
        print('exception sending data')
        return ('exception sending data',rjson)


    #print(response.status_code)
    response.encoding = 'utf-8'
    #print(response.text)
    #print(response.content)
    try:
        rjson = response.json()
    except  Exception as e2:
        rjson['return_code'] = 'error parsing response'
        rjson['return_message'] = str(e2)
 
    return (response.status_code,rjson)

def uptime():  
    with open('/proc/uptime', 'r') as f:
        uptime_hours = float(f.readline().split()[0])/3600.0
        return uptime_hours


def get_data():
    global sleep_time, ips, conf_name, connection_lost
    dattmn = datetime.now() 
    tmz = pytz.timezone('EET')
    dattmn = tmz.localize(dattmn)
    dattmn_str = str(dattmn)
    ips = check_output(['hostname', '--all-ip-addresses'])
    ipsu = ips.decode()
    ipsus = ipsu.replace('\n','')
    return_obj = {'command':'data',
                'timestamp':dattmn_str,
                'ids':{
                        'checknode':config['checknode'],
                        'controller':config['controller'],
                        'sensor':config['sensor']
                    },
                #'data_f':[],
                'data_d':[uptime()],
                'data_t':[conf_name, ipsus, connection_lost]
            }
    return return_obj

sync_event = threading.Event()
exit_flag = False
connection_lost = ''
def upload_thread_function():
    global masterhost, check_counter, ch_n, blinking, connection_lost
    while True:
        sync_event.wait()
        sync_event.clear()
        # every 20 seconds 
        if host_is_accessible(masterhost) == 0:
            #there is route to the host
            #gpio.output(ch_n, gpio.HIGH)
            blinking = False
            print('HIGH connected')

            check_counter -= 1
            if check_counter < 0:
                result = upload_data()
                connection_lost = ''
                check_counter = 30
        else:
            #there is no route to host, the led must blink
            check_counter = 0
            if connection_lost == '':
                dattmn = datetime.now()
                tmz = pytz.timezone('EET')
                dattmn = tmz.localize(dattmn)
                connection_lost = str(dattmn)

            print('blinking disconnected')
            blinking = True 
        if exit_flag:
            break;

blinking = True
blink_delay = 0.25
def blinking_thread_function():
    global blinking, blink_delay
    while True:
        if blinking:
            if gpio.input(ch_n):
                gpio.output(ch_n, gpio.LOW)
                #print('LOW blinking ' + str(datetime.now()) + ', sleep_time=' + str(sleep_time))
            else:
                gpio.output(ch_n, gpio.HIGH)
                #print('HIGH blinking ' + str(datetime.now())  + ', sleep_time=' + str(sleep_time))
            sleep(blink_delay)
            
        else:
            gpio.output(ch_n, gpio.HIGH)
            sleep(60*blink_delay)
       


def exit_handler(signal_received, frame):
    # Handle any cleanup here
    #TODO: join the thread
    exit_flag = True
    sync_event.set();
    th.join()
    print('Gracefully finish the counter thread - 2, Ctrl-C')
    exit(0)


if __name__ == '__main__':
    # The configuration of every sensor is located in 'conf' 
    # subdirectory of the script directory.
    # The name of the configuration file can be whatever
    # but it will be a good practice to use '.conf' extension.
    # This name (not the full path) is passed as a first argument
    # to the script.
    signal(SIGINT, exit_handler)
    conf_name = 'alive_sensor.conf'
    log_name = None
    if (len(sys.argv) > 1):
        conf_name = sys.argv[1]
    if (len(sys.argv) > 2):
        log_name = sys.argv[2]

    #print('conf_name=', conf_name)
    #print('log_name=', log_name)
    dattmn = datetime.now() 
    tmz = pytz.timezone('EET')
    dattmn = tmz.localize(dattmn)
    dattmn_str = str(dattmn)
    #print(dattmn_str)
    script_dir = os.path.dirname(os.path.abspath(__file__))
    conf_dir = os.path.join(script_dir, 'conf')
    
    #print('conf_dir=', conf_dir)
    confpath = os.path.join(conf_dir,conf_name)
    #print('confpath ' + confpath)
    config = conf_module.load_conf(confpath)
    if config == None:
        exit(1)

    sss = config['sensor_description']
    print ('sensor_description:', sss)

    if sss == None or len(sss) < 6:
        dev_dir = None
        exit(2) 

    # -------------------- BCM connected--------------------
    search_str = 'BCM:'
    i = sss.find(search_str)
    if i <0 :
        dev_dir = None
        exit(3)
    sss1 = sss[i+len(search_str):]
    i = sss1.find(';')
    if i < 0:
        #dev_dir = None
        exit(4)
    sss1 = sss1[0 : i]
    try:
        ch_n = int(sss1)
    except:
        exit(5)
    print ('BCM: ', ch_n)
    
    parsed_uri = urlparse(config["service_url"])
    masterhost= parsed_uri[1]
    print ('masterhost:', masterhost )
 
    gpio.setmode(gpio.BCM)
    gpio.setup(ch_n, gpio.OUT )
    gpio.output(ch_n, gpio.LOW)    
    #TODO: create and start thread 
    th = threading.Thread(target=upload_thread_function)
 
    # Start thread
    th.start()
    print('Alive thread started')

    th1 = threading.Thread(target=blinking_thread_function)
    th1.start()
    print('Blinking thread started')

    while True:
        sync_event.set();
        sleep(sleep_time)

    #TODO: join the thread
    exit_flag = True
    sync_event.set();
    th.join()
    print('Gracefully finish the counter thread - 1')
    exit(0)
