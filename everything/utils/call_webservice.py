# -*- coding: utf-8 -*-
import sys
import os
import codecs
import requests
import json
from collections import namedtuple

def upload_data(data):
  print('start upload data')
  print(data)
  response = requests.post('http://localhost:8080/ControllerOperations/process_sensor_data.ashx',
                     json = data)
  print(response.status_code)


if __name__ == "__main__":
    data = '{"ha_node_name":"kotelno", "sensor":"garden_temperature_humidity", "measurments":["temperature","humidity"], "units":["celsius","percent"],"values":[25.3,73]}'
    data1 = {'ha_node_name':'kotelno','sensor':'garden_temperature_humidity','measurments':['temperature','humidity'], 'units':['celsius','percent'], 'values':[25.3,73]
    }
    upload_data(data1)
