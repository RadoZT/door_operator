import RPi.GPIO as gpio
from time import sleep
gpio.cleanup()
gpio.setwarnings(False)

gpio.setmode(gpio.BCM)

motor = 17
rr1 = 20

gpio.setup(motor, gpio.OUT)
gpio.setup(rr1, gpio.IN, pull_up_down=gpio.PUD_DOWN)

print('start')

while True:
    if gpio.input(rr1) == gpio.HIGH:
        gpio.output(motor, gpio.HIGH)
        print('1')
    else:
        gpio.output(motor, gpio.LOW)
        #print('0')

gpio.cleanup()