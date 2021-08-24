import time
import threading

timer_callback = None
timerstate = 0
timer_counter = 0
timer_max = 18


def timer_start():
    global timer_counter, timerstate
    timerstate = 1
    timer_counter = timer_max
def timer_reset():
    global timer_counter, timerstate
    timerstate = 0
    timer_counter = 0
def timer_expired():
    global timer_counter, timerstate
    timerstate = 0
    timer_counter = 0
    if (timer_callback is not None):
        timer_callback()
def timer_thread_function():
    global timer_counter, timerstate
    while True:
        if timerstate == 1:
            time.sleep(10)
            timer_counter -= 1
            if timer_counter <= 0:
                timer_expired()

timer_thread = threading.Thread(target=timer_thread_function)
timer_thread.start()