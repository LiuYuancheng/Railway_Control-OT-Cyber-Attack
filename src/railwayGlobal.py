#-----------------------------------------------------------------------------
# Name:        firmwGlobal.py
#
# Purpose:     This module is used set the Local config file as global value 
#              which will be used in the other modules.
# Author:      Yuancheng Liu
#
# Created:     2019/05/17
# Copyright:   YC
# License:     YC
#-----------------------------------------------------------------------------
import os

dirpath = os.getcwd()
print("Current working directory is : %s" %dirpath)

# Server ip and port for connection: 
LOCAL_IP = '127.0.0.1'
SITCP_PORT = 5005   # port for firmware sign request.
RGTCP_PORT = 5006   # port for sensor registration request.

# Firmware sign server choice:
SI_SERVER_CHOICE = {
    "LocalDefault [127.0.0.1]"  : ('127.0.0.1', SITCP_PORT),
    "Server_1 [192.168.0.100]"  : ('192.168.0.100', SITCP_PORT),
    "Server_2 [192.168.0.101]"  : ('192.168.0.101', SITCP_PORT)
}

# Sensor registration server choice:
RG_SERVER_CHOICE = {
    "LocalDefault [127.0.0.1]"  : ('127.0.0.1', RGTCP_PORT),
    "Server_1 [192.168.0.100]"  : ('192.168.0.100', RGTCP_PORT),
}

#UI window ICON.
ICON_PATH = "".join([dirpath, "\\firmwSign\\singtelIcon.ico"])

BGPNG_PATH = "".join([dirpath, "\\firmwSign\\TopView.png"])

# Data received buffer size:
BUFFER_SIZE = 1024  # Normally 1024, but we want fast response

# Defualt firmware path
DEFUALT_FW = "".join([dirpath, "\\firmwSign\\firmwareSample"])

# Data message dump and load tag
CMD_TYPE = 'C'.encode('utf-8')  # cmd type message used for contorl.
FILE_TYPE = 'F'.encode('utf-8') # file(bytes) type.

# Random bytes setting:
RAN_LEN = 4 # The random number/bytes length.

# RSA encryp/decrypt setting:
RSA_ENCODE_MODE = 'base64'# or 'hex' Sign encode mode.
RSA_UNLOCK  = "Anything for 30-day trial" # RSA unblock periodic
RSA_CERT_PATH = "".join([dirpath, "\\firmwSign\\publickey.cer"])
RSA_PRI_PATH = "".join( [dirpath, "\\firmwSign\\privatekey.pem"]) # RSA pricate key

# SWA_TT setting:
SWATT_ITER  = 300 # Swatt calculation iteration count.

# Recieved private key/sert from the server.
RECV_CERT_PATH = "".join([dirpath, "\\firmwSign\\receivered.cer"])
RECV_PRIK_PATH = "".join([dirpath, "\\firmwSign\\receivered.pem"]) 


# sqlite database file.
DB_PATH = "".join([dirpath, "\\firmwSign\\firmwDB.db"])

# TSL/SSL communication setting:
CA_PATH = "".join([dirpath, "\\firmwSign\\testCert\\CA.cert"])
# Client SSL private key and certificate.    
CSSL_PRIK_PATH = "".join([dirpath, "\\firmwSign\\testCert\\client.pkey"])
CSSL_CERT_PATH = "".join([dirpath, "\\firmwSign\\testCert\\client.cert"])
# Server SSL pricate key and certificate
SSSL_PRIK_PATH = "".join([dirpath, "\\firmwSign\\testCert\\server.pkey"])
SSSL_CERT_PATH = "".join([dirpath, "\\firmwSign\\testCert\\server.cert"])

# firmware sign pricate key and certificate
SIGN_CERT_PATH = "".join([dirpath, "\\firmwSign\\testCert\\certificate.pem"])
SIGN_PRIV_PATH = "".join([dirpath, "\\firmwSign\\testCert\\private_key.pem"])

#-----------------------------------------------------------------------------
# Set the global reference here.

iChartPanel = None      # History chart panel
iMapPanel = None        # Monitor area map panel
iDetailPanel = None     # Detail informaiton display panel
iMainFrame = None       # Program main frame
