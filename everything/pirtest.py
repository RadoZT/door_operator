import RPi.GPIO as gpio
from time import sleep
gpio.cleanup()
gpio.setwarnings(False)

gpio.setmode(gpio.BCM)

motor = 21
rr1 = 26

count = 0

gpio.setup(motor, gpio.OUT)
gpio.setup(rr1, gpio.IN, pull_up_down=gpio.PUD_DOWN)

print('start')

while True:
    if gpio.input(rr1) == gpio.HIGH:
        print('1')
        gpio.output(motor, gpio.HIGH)
        sleep(5)

    else :
        print('0')
        gpio.output(motor, gpio.LOW)