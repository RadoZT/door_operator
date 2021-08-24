import RPi.GPIO as gpio
import time

gpio.setwarnings(False)

gpio.setmode(gpio.BCM)

motor = 26


gpio.setup(motor, gpio.OUT)

print('start')

while True:
    gpio.output(motor, gpio.HIGH)
    print('1')
    time.sleep(5)
    gpio.output(motor, gpio.LOW)
    print('0')
    time.sleep(5)
