#Libraries
import RPi.GPIO as gpio
from time import sleep
import os
from utils import timer33

gpio.setwarnings(False)

gpio.cleanup()

#GPIO Mode (BOARD / BCM)
gpio.setmode(gpio.BCM)

motor = 27

rr1 = 22 #test button, reed relay up
rr2 = 17 # reed relay down

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
gpio.setup(pir1, gpio.IN, pull_up_down=gpio.PUD_DOWN)
gpio.setup(pir2, gpio.IN, pull_up_down=gpio.PUD_DOWN)
gpio.setup(pir3, gpio.IN, pull_up_down=gpio.PUD_DOWN)
gpio.setup(pir4, gpio.IN, pull_up_down=gpio.PUD_DOWN)

def pir():
    if gpio.input(pir1) == gpio.LOW and gpio.input(pir2) == gpio.LOW and gpio.input(pir3) == gpio.LOW and gpio.input(pir4) == gpio.LOW:
        rr()
    if gpio.input(pir1) == gpio.HIGH:
        print ('car entring')
        gpio.output(err_horn, gpio.LOW)
    if gpio.input(pir2) == gpio.HIGH:
        print ('human entring from kotelno')
        gpio.output(err_horn, gpio.LOW)
        #piron2 = ', human entring from kotelno,'
    if gpio.input(pir3) == gpio.HIGH:
        print ('human entring from lifter')
        gpio.output(err_horn, gpio.LOW)
        #piron3 = ', human entring from lifter,'
    if gpio.input(pir4) == gpio.HIGH:
        print ('human entring from abonatno')
        gpio.output(err_horn, gpio.LOW)
        #piron3 = ', human entring from abonatno,'
    
def error():
    print('WARNING DOOR IS OPEN')
    gpio.output(err_horn, gpio.HIGH)

def rr():
    timer33.timer_max = 1 # *60
    if gpio.input(rr2) == gpio.HIGH:
        print('everything is ok')
        gpio.output(err_horn, gpio.LOW)
    if gpio.input(rr1) == gpio.HIGH:
        print('have to close the door')
        gpio.output(motor, gpio.HIGH)
    else:
        gpio.output(motor, gpio.LOW)
        
    if gpio.input(rr2) == gpio.LOW:
        timer33.timer_callback = error
        timer33.timer_start()
    

if __name__ == '__main__':
    try:
        
        while True:
            pir()
        # Reset by pressing CTRL + C
            sleep(1)
    except KeyboardInterrupt:
        print("Measurement stopped by User")
        gpio.cleanup()
