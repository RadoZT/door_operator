import RPi.GPIO as GPIO
import time

GPIO.cleanup()
GPIO.setwarnings(False)

GPIO.setmode(GPIO.BCM)



GPIO.setmode(GPIO.BCM)
GPIO.setup(20, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
GPIO.setup(17, GPIO.OUT)   # fan



# state
# 0 start up.  LEDs off.
# 1 button pressed.  Red LED on
# 2 button not pressed.  Red LED on
# 3 button pressed.  Red LED off
# 4 button not pressed.  Red LED on

state = 0

while True:
    button = GPIO.input(20)

    if state==0:
        GPIO.output(17,False)
        print('Start program')
        if button:
            state=1
            
    elif state==1:
        GPIO.output(17,True)
        print('State 1 work')
        if not(button):
            state=2
            
    elif state==2:
        GPIO.output(17,True)
        print('State 2 work')
        if button:
            state=3
            
    elif state==3:
        GPIO.output(17,False)
        print('State 3 don"t work')
        if not(button):
            state=4
                
    elif state==4:
        GPIO.output(17,False)
        print('State 4 don"t work')
        if button:
            state=1

    time.sleep(0.1)

GPIO.cleanup()
