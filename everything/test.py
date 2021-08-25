import RPi.GPIO as GPIO

channel = 10
GPIO.setmode(GPIO.BCM)  
# Setup your channel
GPIO.setup(channel, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
#GPIO.output(channel, GPIO.LOW)

# To test the value of a pin use the .input method
channel_is_on = GPIO.input(channel)  # Returns 0 if OFF or 1 if ON

if channel_is_on:
    # Do something here
    print('gg')
    
