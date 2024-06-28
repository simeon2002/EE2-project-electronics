import requests
import json
import random
from datetime import datetime
import time
from gpiozero import MCP3008
import time
import math
thermistor = MCP3008(channel=0, port=0, device=0)



thermistor = MCP3008(channel=0, device=0, port=0, max_voltage=3.3)

while True:
    V_in = 3.3
    adc_value = thermistor.value # value between o and 1
    V_fixed = (adc_value) * V_in
    R_fixed =  1e3



    #print(V_fixed, " V")
    # print(R_t, ' ohms')
    #print(adc_value, "adc_value")
    V_t = (V_in - V_fixed)
    temp = 1 / 10e-3 * V_t
    temp_in_c = temp - 273
   # print(temp, " kelvin")
    print(temp_in_c, " degrees")
    time.sleep(1)
    unit = 'C'  # send for generality. if one day F is used, it will still be okay.
    hi = 1
   # print(str(temp_in_c) + str(hi))
    url = "https://studev.groept.be/api/a23ib2d03/insert_temperature/" + str(temp_in_c) + "/" + str(hi)
    response = requests.get(url)
   
