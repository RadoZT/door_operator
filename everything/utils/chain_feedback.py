import time
import threading
import timer33
import RPi.GPIO as gpio


lo1 = 17   # leds output
lo2 = 22
lo3 = 27

li1 = 16   # leds input
li2 = 20
li3 = 21

gpio.setup(lo1, gpio.OUT)
gpio.setup(lo2, gpio.OUT)
gpio.setup(lo3, gpio.OUT)

gpio.setup(li1, gpio.IN)
gpio.setup(li2, gpio.IN)
gpio.setup(li3, gpio.IN)


led_state = 0



def led_opening():
    led_state = 1
def led_closing():
    led_state = -1