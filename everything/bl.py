#Libraries
import RPi.GPIO as GPIO
from time import sleep
#Set warnings off (optional)
GPIO.setwarnings(False)
GPIO.setmode(GPIO.BCM)
#Set Button and LED pins
Button = 17
LED = 22
#Setup Button and LED
GPIO.setup(Button,GPIO.IN,pull_up_down=GPIO.PUD_UP)
GPIO.setup(LED,GPIO.OUT)
flag = 0
count = 0

try :
    while True:
        button_state = GPIO.input(Button)
        print('button state:', button_state)
        print ('counter : ', count)
        bs_last = button_state
        sleep(0.1)
        bs_now = button_state
        
        if button_state == 1:
            GPIO.output(LED,GPIO.HIGH)
            count += 1
        if button_state == 0:
            GPIO.output(LED,GPIO.LOW)
            flag += 1
        if bs_last == bs_now


except KeyboardInterrupt :
    GPIO.cleanup() # Clean up