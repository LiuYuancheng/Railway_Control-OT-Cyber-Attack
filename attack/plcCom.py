import os 
from time import sleep
import snap7
from snap7.util import *
from snap7.snap7types import S7AreaPA
import struct
print("Try to connect to Plc")
plc = snap7.client.Client()
plc.connect("192.168.10.73",0,1)

area = 0x83    # area for Q memory
area = S7AreaPA   # area for Q memory
start = 0      # location we are going to start the read
length = 1     # length in bytes of the read
bit = 0        # which bit in the Q memory byte we are reading

byte = plc.read_area(area,0,start,length)
print("Q0.0:"+str(get_bool(byte,0,bit)))
plc.disconnect()