import time
import threading
import timer33
import RPi.GPIO as gpio

gpio.setwarnings(False)

gpio.cleanup()

#GPIO Mode (BOARD / BCM)
gpio.setmode(gpio.BCM)

rrc = 25     # reed relay close
rro = 23     # reed relay open


reedrelay_callback = None
reedrelay_state = 0
reedrelay_counter = 0
#reedrelay_max = 18


gpio.setup(rrc, gpio.IN, pull_up_down=gpio.PUD_DOWN)
gpio.setup(rro, gpio.IN, pull_up_down=gpio.PUD_DOWN)



              # |====================================|
              # |0|Неопределено състояние            |
              # |1|Вратата е затворена               | 
              # |2|Вратата се отваря                 |
              # |3|Вратата е отворена                |
              # |4|Вратата се затваря                |
              # |5|Вратата е в неопределено състояние| 
              # |6|Авария в датчиците                |
              # |====================================|
              
              
              
def reedrelay_up():
    #global reedrelay_counter, reedrelay_state
    reedrelay_state = 3
    reedrelay_closing()
    timer33.timer_max = 3
    reedrelay_stop()

    
def reedrelay_down():
    reedrelay_state = 1
    reedrelay_opening()
    timer33.timer_max = 2.5
    reedrelay_stop()
    
     
def reedrelay_opening():
    reedrelay_state = 2
    #if (reedrelay_callback is not None):
        #reedrelay_callback()
        
def reedrelay_closing():
    reedrelay_state = 4
    
def reedrelay_stop():
    reedrelay_state = 5
    
def reedrelay_trouble():
    reedrelay_state = 6
    
def reedrelay_thread_function():
    global reedrelay_counter, reedrelay_state
    while True:
        if gpio.input(rro) == gpio.LOW and gpio.input(rrc) == gpio.HIGH :
            reedrelay_down()
        elif gpio.input(rrc) == gpio.LOW and gpio.input(rro) == gpio.HIGH :
            reedrelay_up()
        elif gpio.input(rrc) == gpio.LOW and gpio.input(rro) == gpio.LOW :
            reedrelay_stop()
        elif gpio.input(rrc) == gpio.HIGH and gpio.input(rro) == gpio.HIGH :
            reedrelay_trouble()


reedrelay_thread = threading.Thread(target=reedrelay_thread_function)
reedrelay_thread.start()