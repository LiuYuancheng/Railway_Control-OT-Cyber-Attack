import socket
import sys


# function code: 
# https://www.schneider-electric.com/en/faqs/FA308725/
# https://www.schneider-electric.com/en/faqs/FA295250/
# https://www.schneider-electric.com/en/faqs/FA249614/

TID = '0000'
PROTOCOL_ID = '0000'
UID = '01'
BIT_COUNT = '0001'
BYTE_COUNT = '01'
FC = '0f' # Write Multiple Registers
LENGTH = '0008'
DATA_0 = '00'
DATA_1 = '01'

M0 = '0000'
M1 = '0001'
M2 = '0002'
M3 = '0003'
M4 = '0004'
M5 = '0005'
M6 = '0006'
M10 = '000a'
M20 = '0014'
M30 = '001e'
M40 = '0028'
M50 = '0032'
M60 = '003c'

ADDRESS = {'M0': M0,
           'M1': M1,
           'M2': M2,
           'M3': M3,
           'M4': M4,
           'M5': M5,
           'M6': M6,
           'M10': M10,
           'M20': M20,
           'M30': M30,
           'M40': M40,
           'M50': M50,
           'M60': M60
           }

VALUES = {'0': DATA_0, '1': DATA_1}

def send_write_modbus_packet(controler_ip, ref_number, data):
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.connect((controler_ip, 502))

    modbus_payload = TID + PROTOCOL_ID + LENGTH + UID + FC + ref_number + BIT_COUNT + BYTE_COUNT + data

    # print modbus_payload
    s.send(modbus_payload.decode('hex'))
    r = s.recv(1024)
    r = r.encode('hex')
    print(r)
    s.close()


#Usage: python send_modbus_cmd.py <control IP> <address> <value to set> \
#Control IP: in the format x.x.x.x\
#Address: M0,M10,M20,M30,M40,M50,M60\
#Value to Set: 0,1 \
#Example: python send_modbus_cmd.py 192.168.1.86 M10 0\
#
#")

if len(sys.argv)< 3:
    print('parameter missing')

else:
    if not len(str(sys.argv[1]).split('.'))==4 :
        print("ERROR: Control IP must be in the format x.x.x.x")
        exit()

    if sys.argv[2] not in ADDRESS.keys():
        print("ERROR: Address should be one of the following:  M0,M10,M20,M30,M40,M50,M60")
        exit()

    if sys.argv[3] not in ['0','1']:
        print("ERROR: Value to Set should be one of the following:  0,1")
        exit()


    send_write_modbus_packet(controler_ip=sys.argv[1], ref_number = ADDRESS[sys.argv[2]] ,data=VALUES[sys.argv[3]])
