from utils import timer33 as start
from utils import timer33 as stop
import RPi.GPIO as gpio
from time import sleep
gpio.cleanup()
gpio.setwarnings(False)

gpio.setmode(gpio.BCM)

motor = 17
rr1 = 23

gpio.setup(motor, gpio.OUT)
gpio.setup(rr1, gpio.IN, pull_up_down=gpio.PUD_DOWN)
print('start timer test')

def gg():
    start.timer_max = 1 # *30
    if gpio.input(rr1) == gpio.LOW:
        start.timer_callback = fan_s
        start.timer_start()
    else:
        gpio.output(motor, gpio.LOW)

def fan_s():
    stop.timer_max = 1 # *30
    gpio.output(motor, gpio.HIGH)
    stop.timer_callback = fan_st
    stop.timer_start()
    
def fan_st():
    start.timer_max = 1 # *30
    gpio.output(motor, gpio.LOW)
    start.timer_callback = fan_s
    start.timer_start()
    
    
while True:
    gg()
    