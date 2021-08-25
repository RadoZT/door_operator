#Libraries
import RPi.GPIO as gpio
from time import sleep
import time
import os

gpio.setwarnings(False)

gpio.cleanup()

#GPIO Mode (BOARD / BCM)
gpio.setmode(gpio.BCM)

#set GPIO Pins
trig = 18
echo = 24

motor = 27

rr1 = 25 #test button, reed relay up
rr2 = 23 # reed relay down

pir1 = 16 # in front of garage door
pir2 = 20 # next to kotelno door
pir3 = 21 # next to human door
pir4 = 26 # next to last door, in the bottom ap.4/5

distance_last = 0
#hysteresis zone = 5 /2  =>  +-2.5cm triger 
hyst = 2.5
dd = 0 #distane


#set GPIO direction (IN / OUT)
gpio.setup(trig, gpio.OUT)
gpio.setup(echo, gpio.IN)
gpio.setup(rr1, gpio.IN, pull_up_down=gpio.PUD_DOWN)
gpio.setup(rr2, gpio.IN, pull_up_down=gpio.PUD_DOWN)
gpio.setup(motor, gpio.OUT)
gpio.setup(pir1, gpio.IN, pull_up_down=gpio.PUD_DOWN)
gpio.setup(pir2, gpio.IN, pull_up_down=gpio.PUD_DOWN)
gpio.setup(pir3, gpio.IN, pull_up_down=gpio.PUD_DOWN)
gpio.setup(pir4, gpio.IN, pull_up_down=gpio.PUD_DOWN)






def distance():
    # set Trigger to HIGH
    gpio.output(trig, True)

    # set Trigger after 0.01ms to LOW
    time.sleep(0.00001)
    gpio.output(trig, False)

    StartTime = time.time()
    StopTime = time.time()

    # save StartTime
    while gpio.input(echo) == 0:
        StartTime = time.time()

    # save time of arrival
    while gpio.input(echo) == 1:
        StopTime = time.time()

    # time difference between start and arrival
    TimeElapsed = StopTime - StartTime
    # multiply with the sonic speed (34300 cm/s)
    # and divide by 2, because there and back
    distance = (TimeElapsed * 34300) / 2
    
    return distance


def pir():
    if gpio.input(pir1) == gpio.LOW and gpio.input(pir2) == gpio.LOW and gpio.input(pir3) == gpio.LOW and gpio.input(pir4) == gpio.LOW:
        rr()
    if gpio.input(rr2) == gpio.LOW and gpio.input(pir1) == gpio.HIGH:
        print ('car entring')
    if gpio.input(pir2) == gpio.HIGH or gpio.input(pir3) == gpio.HIGH or gpio.input(pir4) == gpio.HIGH:
        print ('human entring')
    

def rr():
    while gpio.input(rr1) == gpio.LOW and gpio.input(rr2) == gpio.LOW:
        avrm()
        
def avrm():
    
    distance_last = distance()
    print ("Measured LAST Distance = %.1f cm" % distance_last )
	
    time.sleep(1) # period  
			
    distance_now  = distance()
    print ("Measured NOW Distance = %.1f cm" % distance_now )

    distance_change = distance_last - distance_now 
    print ("Changes = %.1f cm" % distance_change )


    #distance_now > distance_last   =>  return door closing
    if distance_now > (distance_last + hyst):
        print ("TRIGGER - door closing ")
      

    #distance_now < distance_last   =>  return door opening
    if distance_now < (distance_last - hyst):
        print ("TRIGGER - door opening ")
   
    #distance_now = distance_last   =>  return nothing - no changes;
    if distance_now <= (distance_last + hyst) and distance_now >= (distance_last - hyst):
        print ("TRIGGER - Nothing. not changes. ")
  
  
       
                
    distance_last = distance_now
    
    


if __name__ == '__main__':

    #gpio.add_event_detect(25, gpio.RISING, callback=button)
    #gpio.add_event_detect(17, gpio.OUT, gpio.FALLING, callback=door)
    
    try:
        
        while True:
            avrm()
        # Reset by pressing CTRL + C
            time.sleep(1)
    except KeyboardInterrupt:
        print("Measurement stopped by User")
        gpio.cleanup()
