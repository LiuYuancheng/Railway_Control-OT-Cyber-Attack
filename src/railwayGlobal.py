#-----------------------------------------------------------------------------
# Name:        railwayGlobal.py
#
# Purpose:     This module is used as the Local config file to set constants, 
#              global parameters which will be used in the other modules.
#              
# Author:      Yuancheng Liu
#
# Created:     2019/05/17
# Copyright:   YC
# License:     YC
#-----------------------------------------------------------------------------
import os

dirpath = os.getcwd()
print("Current working directory is : %s" %dirpath)

APP_NAME = 'RailWay PLC Control Hub V1.0'

#------<CONSTANTS>-------------------------------------------------------------

# Agent type 
RAYWAY_TYPE = 'RW'
SENSOR_TYPE = 'SS'
GATE_TYPE = 'GT'
ATTPT_TYPE = 'AP'
SIGNAL_TYPE = 'SL'

TTICO_PATH = "".join([dirpath, "\\img\\title.ico"])


BGPNG_PATH = "".join([dirpath, "\\img\\Trainbg1.png"])
WKJPG_PATH = "".join([dirpath, "\\img\\walk.jpg"])
HTPNG_PATH = "".join([dirpath, "\\img\\hitPPl.png"])
LTPNG_PATH = "".join([dirpath, "\\img\\left.png"])


LDSET_PATH = "".join([dirpath, "\\img\\loadSet32.png"])    
EMGST_PATH = "".join([dirpath, "\\img\\emgStop32.png"])
RECOV_PATH = "".join([dirpath, "\\img\\reset32.png"])



LPJPG_PATH = "".join([dirpath, "\\img\\Ppass.jpg"])   # light for people pass 
LSJPG_PATH = "".join([dirpath, "\\img\\Pstop.jpg"])



PPPNG_PATH = "".join([dirpath, "\\img\\passS18.png"])   # light for people pass 
PSPNG_PATH = "".join([dirpath, "\\img\\stopS18.png"])

CPPNG_PATH = "".join([dirpath, "\\img\\gateCarP18.png"])
CSPNG_PATH = "".join([dirpath, "\\img\\gateCarS18.png"])

FSPNG_PATH = "".join([dirpath, "\\img\\forkOnS18.png"])
FAPNG_PATH = "".join([dirpath, "\\img\\forkAoffS18.png"])
FBPNG_PATH = "".join([dirpath, "\\img\\forkBoffS18.png"])

SOPNG_PATH = "".join([dirpath, "\\img\\stationOn18.png"])
SFPNG_PATH = "".join([dirpath, "\\img\\stationOff18.png"])


POPNG_PATH = "".join([dirpath, "\\img\\powerPlantOn.png"])
PFPNG_PATH = "".join([dirpath, "\\img\\powerPlantOff.png"])

INOPNG_PATH = "".join([dirpath, "\\img\\industrOn.png"])
INFPNG_PATH = "".join([dirpath, "\\img\\industrOff.png"])

CTOPNG_PATH = "".join([dirpath, "\\img\\cityOn.png"])
CTFPNG_PATH = "".join([dirpath, "\\img\\cityOff.png"])

RDOPNG_PATH = "".join([dirpath, "\\img\\residentialOn.png"])
RDFPNG_PATH = "".join([dirpath, "\\img\\residentialOff.png"])

APOPNG_PATH = "".join([dirpath, "\\img\\AirportOn.png"])
APFPNG_PATH = "".join([dirpath, "\\img\\AirportOff.png"])

FRJPG_PATH = "".join([dirpath, "\\img\\forkAoffS18.png"]) 

CLPNG_PATH = "".join([dirpath, "\\img\\clash.png"]) 

# PLC basic config: (type, IP address, port, input_#, output_#)
PLC_CFG = {
    'PLC0'  : ('[m221]',    "192.168.0.101", '4343', 8, 8), 
    'PLC1'  : ('[m221]',    "192.168.0.102", '4343', 8, 8), 
    'PLC2'  : ('[S7-1200]', "192.168.0.103", '4343', 8, 8)
}

#-------<GLOBAL PARAMTERS>-----------------------------------------------------
# Set the global reference here.
iRailWay = None
iPlcPanelList = []  # Plc panel list. 
iMapPanel = None    # History chart panel.
iTrainPanel = None  # Train control panel. 
iMainFrame = None   # Main frame. 
iSensorCount = 0    # number of sensors. 
iEmgStop = False    # emergency stop 
iDetailPanel = None
iAttackCtrlPanel = None 
