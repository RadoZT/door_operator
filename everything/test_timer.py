from utils import timer33
from time import sleep

def callback ():
    print('timeout')
    timer33.timer_start()

timer33.timer_max = 1

timer33.timer_callback = callback

timer33.timer_start()

while True:
    sleep(1)
    