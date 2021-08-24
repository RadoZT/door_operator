import sys
import os
from utils import conf_module
from utils import timer33
from signal import signal, SIGINT
import requests
import json
from collections import namedtuple
from datetime import datetime, date, time, timezone
import pytz
import RPi.GPIO as gpio
from time import sleep
import threading


#set GPIO Pins
trig = None
echo = None

motor = None

rr1 = None #test button, reed relay up
rr2 = None # reed relay down

pir1 = None # in front of garage door
pir2 = None # next to kotelno door
pir3 = None # next to human door
pir4 = None # next to last door, in the bottom ap.4/5



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
    global deltaedges_u
    global lock_c, old_timestamp, time_delay, printflag
    global bad_situation_message, upload_sensor_data_timestamp

    read_gpio()
    dattmn = datetime.now()
    dattmn = tmz.localize(dattmn)
    dattmn_str = str(dattmn)

    deltaedge1_total_seconds = None
    if deltaedges_u[0] != None:
        deltaedge1_total_seconds = deltaedges_u[0].total_seconds()

    deltaedge2_total_seconds = None
    if deltaedges_u[1] != None:
        deltaedge2_total_seconds = deltaedges_u[1].total_seconds()

    deltaedge3_total_seconds = None
    if deltaedges_u[2] != None:
        deltaedge3_total_seconds = deltaedges_u[2].total_seconds()

    deltaedge4_total_seconds = None
    if deltaedges_u[3] != None:
        deltaedge4_total_seconds = deltaedges_u[3].total_seconds()

    deltaedge5_total_seconds = None
    if deltaedges_u[4] != None:
        deltaedge5_total_seconds = deltaedges_u[4].total_seconds()

    return_obj = {'command':'data',
                'timestamp':dattmn_str,
                'ids':{
                        'checknode':config['checknode'],
                        'controller':config['controller'],
                        'sensor':config['sensor']
                    },
                'data_f':[],
                #'data_d':[uptime()],
                #'data_t':[conf_name, ipsus, connection_lost]
            }
    #if bad_situation_message != "":
    return_obj["data_t"] = [bad_situation_message, "last upload:" + str(tmz.localize(upload_sensor_data_timestamp))]

    return return_obj

sync_event = threading.Event()
exit_flag = False

def upload_thread_function():
    global sync_event, exit_flag, printflag
    global bad_situation_message
    global upload_sensor_data_timestamp, exit_flag
    global bad_situation_message
    global lock_c, old_timestamp, time_delay, printflag
    global deltaedges_u

    while True:
        sync_event.wait()
        sync_event.clear()
        #print('tred, printflag : ', printflag)
        '''
        flow_curr_timestamp = datetime.now()
        flow_delta = (flow_curr_timestamp - flow_old_timestamp).total_seconds()
        #print (flow_curr_timestamp, flow_old_timestamp, flow_delta)
        flow_old_timestamp = flow_curr_timestamp

        #upload_data()     #in production must be uncommented
        #print(get_data())  #in production must be commented
        '''
        if printflag == 1:
            #lock_c.acquire()
            #print('loop')
            printflag = 0
            upload_data()
            upload_sensor_data_timestamp = datetime.now()

            xdeltaedge1 = deltaedges_u[0]

            xdeltaedge2 = deltaedges_u[1]

            xdeltaedge3 =deltaedges_u[2]

            xdeltaedge4 = deltaedges_u[3]

            xdeltaedge5 = deltaedges_u[4]

        if exit_flag:
            break

def exit_handler(signal_recieved, frame):
    global exit_flag
    exit_flag = True
    sync_event.set()
    sleep(2)
    sync_event.set()
    #print('gracefully finish counter thread - 2, Ctrl - C')
    exit(0)


if __name__=='__main__':
    global conf_module
    signal(SIGINT, exit_handler)
    gpio.setmode(gpio.BCM)

    conf_name = 'sensors.conf'
    log_name = None
    
    if (len(sys.argv) > 1):
        conf_name = sys.argv[1]
    if (len(sys.argv) > 2):
        log_name = sys.argv[2]

    script_dir = os.path.dirname(os.path.abspath(__file__))
    conf_dir = os.path.join(script_dir, 'conf')

    #print('conf_dir=', conf_dir)
    confpath = os.path.join(conf_dir,conf_name)
    #print('confpath ' + confpath)
    config = conf_module.load_conf(confpath)
    if config == None:
        exit(1)

#---------------------------------------------------------
    sss = config['sensor_description']
    i = sss.find('BCM:')
    if i <0 :
        dev_dir = None
        exit(3)

    sss1 = sss[i+4:]
    i = sss1.find(';')
    if i < 0:
        #dev_dir = None
        exit(4)

    sss1 = sss1[0 : i]
    sss = sss1.split(',')

    for ss in sss:
        try:
            ch_n = int(ss)
            channels.append(ch_n)
        except:
            exit(5)

    if len( channels) == 0:
        exit(6)

    #print ('BCM: ', str(channels))
    trig = channels[0]
    echo = channels[1]
    motor = channels[2]
    rr1 = channels[3]
    rr2 = channels[4]
    pir1 = channels[5]
    pir2 = channels[6]
    pir3 = channels[7]
    pir4 = channels[8]
    gpio.setmode(gpio.BCM)
#---------------------------------------------------------


    init_gpio()
    reset_levels()

    gpio.add_event_detect(trig, gpio.BOTH, callback=)
    gpio.add_event_detect(echo, gpio.BOTH, callback=)
    gpio.add_event_detect(motor, gpio.BOTH, callback=)
    gpio.add_event_detect(rr1, gpio.BOTH, callback=)
    gpio.add_event_detect(rr2, gpio.BOTH, callback=)
    gpio.add_event_detect(pir1, gpio.BOTH, callback=)
    gpio.add_event_detect(pir2, gpio.BOTH, callback=)
    gpio.add_event_detect(pir3, gpio.BOTH, callback=)
    gpio.add_event_detect(pir4, gpio.BOTH, callback=)
    

    th = threading.Thread(target=upload_thread_function)
    th.start()
    #print('Counter thread started')
    

    #print('conf_name=', conf_name)
    #print('log_name=', log_name)
    dattmn = datetime.now()
    #tmz = pytz.timezone('EET')
    dattmn = tmz.localize(dattmn)
    dattmn_str = str(dattmn)
    #print(dattmn_str)

    while True:
        sleep(60)

        #print ("RPM is {0}".format(master_counter - master_counter_old))
        #revcount_old = revcount
        #revcount = 0
        #print('while loop ', gpio.input(channels[0]), gpio.input(channels[1]), gpio.input(channels[2]), gpio.input(channels[3]), gpio.input(channels[4]))
        #sync_event.set()
        if exit_flag:
            break

    #TODO: join the thread
    exit_flag = True
    sync_event.set()
    th.join()
    #print('Gracefully finish the counter thread - 1')
    exit(0)
