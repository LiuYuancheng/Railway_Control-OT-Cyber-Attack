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
GATE_TYPE   = 'GT'
ATTPT_TYPE  = 'AP'
SIGNAL_TYPE = 'SL'
FORK_TYPE   = 'FK'

# Title icon path.
TTICO_PATH = "".join([dirpath, "\\img\\title.ico"])

# Map background path.
BGPNG_PATH = "".join([dirpath, "\\img\\Trainbg1.png"])
RAJPG_PATH = "".join([dirpath, "\\img\\ransomwareAtt.jpg"])
TAGIF_PATH = "".join([dirpath, "\\img\\trojanAtt.gif"])

WKJPG_PATH = "".join([dirpath, "\\img\\walk.jpg"])
HTPNG_PATH = "".join([dirpath, "\\img\\hitPPl.png"])
LTPNG_PATH = "".join([dirpath, "\\img\\left.png"])

# Train setting panel path:
LDSET_PATH = "".join([dirpath, "\\img\\loadSet32.png"])     # load setting.    
EMGST_PATH = "".join([dirpath, "\\img\\emgStop32.png"])     # emergency stop.
RECOV_PATH = "".join([dirpath, "\\img\\reset32.png"])       # train station recover.


LPJPG_PATH = "".join([dirpath, "\\img\\Ppass.jpg"])   # light for people pass 
LSJPG_PATH = "".join([dirpath, "\\img\\Pstop.jpg"])

# Cross signal: 
PPPNG_PATH = "".join([dirpath, "\\img\\passS18.png"])       # signal for people pass 
PSPNG_PATH = "".join([dirpath, "\\img\\stopS18.png"])       # signal for people stop 
CPPNG_PATH = "".join([dirpath, "\\img\\gateCarP18.png"])    # signal for cars pass    
CSPNG_PATH = "".join([dirpath, "\\img\\gateCarS18.png"])    # signal for cars stop.

# Railway fork signal:
FSPNG_PATH = "".join([dirpath, "\\img\\forkOnS18.png"])     # fork go straight signal. 
FAPNG_PATH = "".join([dirpath, "\\img\\forkAoffS18.png"])   # railway A fork on signal.
FBPNG_PATH = "".join([dirpath, "\\img\\forkBoffS18.png"])   # railway B fork on signal.

# Station signal light: 
SOPNG_PATH = "".join([dirpath, "\\img\\stationOn18.png"])   # station signal on.
SFPNG_PATH = "".join([dirpath, "\\img\\stationOff18.png"])  # station signal off.

# Power plant light:
POPNG_PATH = "".join([dirpath, "\\img\\powerPlantOn.png"])  # powerplant light on.
PFPNG_PATH = "".join([dirpath, "\\img\\powerPlantOff.png"]) # powerplant light off.

# Industrial Area. 
INOPNG_PATH = "".join([dirpath, "\\img\\industrOn.png"])    # industrial area light on.
INFPNG_PATH = "".join([dirpath, "\\img\\industrOff.png"])   # industrial area light off.

# City area light
CTOPNG_PATH = "".join([dirpath, "\\img\\cityOn.png"])       # city area light on.
CTFPNG_PATH = "".join([dirpath, "\\img\\cityOff.png"])      # city area light off.

# Residential area light
RDOPNG_PATH = "".join([dirpath, "\\img\\residentialOn.png"]) # Residential area light on.     
RDFPNG_PATH = "".join([dirpath, "\\img\\residentialOff.png"])# Residential area light off.   

# AirPort area light
APOPNG_PATH = "".join([dirpath, "\\img\\AirportOn.png"])    # AirPort area light on.     
APFPNG_PATH = "".join([dirpath, "\\img\\AirportOff.png"])   # AirPort area light off.     

# Station signal light: 
STONPNG_PATH = "".join([dirpath, "\\img\\stationOn.png"])   # station light on.
STOFPNG_PATH = "".join([dirpath, "\\img\\stationOff.png"])  # station light off.

# Camera:
CAMPNG_PATH = "".join([dirpath, "\\img\\cameraUp.png"])   # station light on.
TPSGIP_PATH = "".join([dirpath, "\\img\\trailPass.gif"])   # station light on.








CLPNG_PATH = "".join([dirpath, "\\img\\clash.png"]) 

# PLC basic config: (type, IP address, port, input_#, output_#)
PLC_CFG = {
    'PLC0'  : ('[m221]',    "192.168.0.101", '4343', 8, 8), 
    'PLC1'  : ('[m221]',    "192.168.0.102", '4343', 8, 8), 
    'PLC2'  : ('[S7-1200]', "192.168.0.103", '4343', 8, 8)
}

#-------<GLOBAL PARAMTERS>-----------------------------------------------------
# Set the global reference here.
iAgentMgr = None
iAttackCtrlPanel = None
iCtrlCount = 0      # device PLC control count.
iDataPanel = None   # display panel
iDetailPanel = None

iEmgStop = False    # emergency stop
iMainFrame = None   # Main frame. 
iMapMgr = None
iMapPanel = None    # History chart panel.
iPlcPanelList = []  # Plc panel list. 
iPlcMgr = None
iPowCtrlPanel = None
iRailWay = None
iSensorCount = 0    # number of sensors. 
iTrainAPanel = None # Train A control panel. 
iTrainBPanel = None # Train B control panel.






