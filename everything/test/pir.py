import RPi.GPIO as GPIO
import time
 
GPIO.setmode(GPIO.BCM)
GPIO.setwarnings(False)
PIR_PIN = 26
led = 17
GPIO.setup(PIR_PIN, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
GPIO.setup(led, GPIO.OUT)



print('Starting up the PIR Module (click on STOP to exit)')
time.sleep(1)
print ('Ready')

while True:
    GPIO.setup(PIR_PIN, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
    if GPIO.input(PIR_PIN) == GPIO.HIGH:
        print('Motion Detected')
        GPIO.output(led, True)
    else:
        print('Motion no')
        GPIO.output(led, False)
    time.sleep(1)