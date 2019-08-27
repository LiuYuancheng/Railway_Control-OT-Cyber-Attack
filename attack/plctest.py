import S7PLC1200
from time import sleep
import snap7
from snap7.util import *
import struct

plc = S7PLC1200.S7PLC1200("192.168.10.73")
plc.writeMem('QX0.1',True) # write Q0.0 to be true, which will only turn on the output if it isn't connected to any rung in your ladder code
print(plc.getMem('MX0.1')) # read memory bit M0.1
print(plc.getMem('IX0.1')) # read input bit I0.0
#print(plc.getMem("FREAL100"))# read real from MD100
#print(plc.getMem("MW20"))# read int word from MW20
#print(plc.getMem("MB24",254))# write to MB24 the value 254
plc.plc.disconnect()