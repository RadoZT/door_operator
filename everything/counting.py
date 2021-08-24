#!/usr/local/bin/python
import RPi.GPIO as gpio
import time

gpio.setwarnings(False)

gpio.cleanup()

#GPIO Mode (BOARD / BCM)
gpio.setmode(gpio.BCM)

counter = 0

ledout2 = 22

ledin2 = 10

gpio.setup(ledout2, gpio.OUT)
gpio.setup(ledin2, gpio.IN, pull_up_down=gpio.PUD_DOWN)
gpio.output(ledout2, True)
li2 = gpio.input(ledin2)

try :
    while True:

        if li2 == gpio.LOW:
            counter += 1
        
        print (counter)
    #time.sleep(0.1)
except KeyboardInterrupt :
    gpio.cleanup() # Clean up