#!/usr/bin/env python
# -*- coding: utf-8 -*-


from datetime import datetime, date, timezone, timedelta
import time
import pytz

def sleep_to_next_min() -> "Изчакване до следващата цяла минута":
  a = datetime.now()
  c = datetime(a.year,a.month,a.day,a.hour,a.minute,0) + timedelta(minutes=1)
  #print("next_min=", str(c))
  time.sleep((c-a).total_seconds())

def sleep_to_next_5min() -> "Изчакване до следващите кръгли пет минути в часа":
  a = datetime.now()
  x = 5 * (int(a.minute // 5) + 1) 
  c = datetime(a.year,a.month,a.day,a.hour,0,0) + timedelta(minutes=x)
  #print("next_5min",str(c))
  time.sleep((c-a).total_seconds())


def sleep_to_next_15min() -> "Изчакване до следващите кръгли 15 минути в часа":
  a = datetime.now()
  x = 15 * (int(a.minute // 15) + 1) 
  c = datetime(a.year,a.month,a.day,a.hour,0,0) + timedelta(minutes=x)
  #print("next_15min=", str(c))
  time.sleep((c-a).total_seconds())

if __name__ == "__main__":
    while True:
        sleep_to_next_5min()
        print(str(datetime.now()))
