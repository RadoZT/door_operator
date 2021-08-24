#Libraries
import RPi.GPIO as GPIO
import time
GPIO.setwarnings(False)


#GPIO Mode (BOARD / BCM)
GPIO.setmode(GPIO.BCM)
 
#set GPIO Pins
GPIO_TRIGGER = 18
GPIO_ECHO    = 24
 
#set GPIO direction (IN / OUT)
GPIO.setup(GPIO_TRIGGER, GPIO.OUT)
GPIO.setup(GPIO_ECHO, GPIO.IN)
distance_last = 0
#hysteresis zone = 5 /2  =>  +-2.5cm triger 
hyst = 2.5
 
def distance():
    # set Trigger to HIGH
    GPIO.output(GPIO_TRIGGER, True)
 
    # set Trigger after 0.01ms to LOW
    time.sleep(0.00001)
    GPIO.output(GPIO_TRIGGER, False)
 
    StartTime = time.time()
    StopTime = time.time()
 
    # save StartTime
    while GPIO.input(GPIO_ECHO) == 0:
        StartTime = time.time()
 
    # save time of arrival
    while GPIO.input(GPIO_ECHO) == 1:
        StopTime = time.time()
 
    # time difference between start and arrival
    TimeElapsed = StopTime - StartTime
	
    # multiply with the sonic speed (34300 cm/s)
    # and divide by 2, because there and back
    distance = (TimeElapsed * 34300) / 2
 
    return distance
 
if __name__ == '__main__':
    try:

        while True:
            distance_last = distance()
            print ("Measured LAST Distance = %.1f cm" % distance_last )
	
            time.sleep(1) # period  
			
            distance_now  = distance()
            print ("Measured NOW Distance = %.1f cm" % distance_now )

            distance_change = distance_last - distance_now 
            print ("Changes = %.1f cm" % distance_change )


            #distance_now > distance_last   =>  return door close
            if( distance_now > (distance_last + hyst) ):
                print ("TRIGGER - door close ")
            

            #distance_now < distance_last   =>  return door opening 
            if( distance_now < (distance_last - hyst) ):
                print ("TRIGGER - door opening ")
            
 
            #distance_now = distance_last   =>  return nothing - no changes;
            if( distance_now <= (distance_last + hyst)  and distance_now >= (distance_last - hyst)):
                print ("TRIGGER - Nothing. not changes. ")
                
            distance_last = distance_now
 
        # Reset by pressing CTRL + C
    except KeyboardInterrupt:
        print("Measurement stopped by User")
        GPIO.cleanup()