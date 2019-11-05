#-----------------------------------------------------------------------------
# Name:        railwayGlobal.py
#
# Purpose:     This module is used as the Local config file to set constants, 
#              global parameters which will be used in the other modules.
#              
# Author:      Yuancheng Liu
#
# Created:     2019/05/17
# Copyright:   YC @ Singtel Cyber Security Research & Development Laboratory
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

# PLC basic config: (type, IP address, port, input_#, output_#)
PLC_CFG = {
    'PLC0'  : ('[m221]',    "192.168.10.72", 'M', 8, 8),
    'PLC2'  : ('[m221]',    "192.168.10.71", 'M', 8, 8),
    'PLC1'  : ('[S7-1200]', "192.168.10.73", 'C', 8, 8)
}
# PLC output connection map table:
# PLC 0 [schneider M221]: 
#   M10 -> Q0.0 Airport LED
#   M0 -> Q0.1 Power Plant
#   M60 -> Q0.2 Industrial LED
# PLC 1 [seimens S7-1200]
#   Qx0.0-> Q0.0 station + sensor
#   Qx0.1-> Q0.1 level crossing pwr
#   Qx0.2-> Q0.2 Resident LED
# PLC 2 [schneider M221]:
#   M0  -> Q0.0 fork turnout
#   M10 -> Q0.1 track A pwr
#   M20 -> Q0.2 track B pwr
#   M60 -> Q0.3 city LED

#------<IMAGES PATH>-------------------------------------------------------------
# Title icon path:
IMG_FD = 'img'
TTICO_PATH = os.path.join(dirpath, IMG_FD, "title.ico")

# Panel background path:
BGPNG_PATH = os.path.join(dirpath, IMG_FD, "Trainbg1.png")      # map panel.
RAJPG_PATH = os.path.join(dirpath, IMG_FD, "ransomwareAtt.jpg") # ransomeare attack panel.
TAGIF_PATH = os.path.join(dirpath, IMG_FD, "trojanAtt.gif")     # tronjan attack panel.

# Pedestrian cross signal at the gate: 
WKJPG_PATH = os.path.join(dirpath, IMG_FD, "walk.jpg")          # Pedestrian pass.
HTPNG_PATH = os.path.join(dirpath, IMG_FD, "hitPPl.png")        # Pedestrian accident.
PPPNG_PATH = os.path.join(dirpath, IMG_FD, "passS18.png")       # signal for people pass 
PSPNG_PATH = os.path.join(dirpath, IMG_FD, "stopS18.png")       # signal for people stop 
CPPNG_PATH = os.path.join(dirpath, IMG_FD, "gateCarP18.png")    # signal for cars pass    
CSPNG_PATH = os.path.join(dirpath, IMG_FD, "gateCarS18.png")    # signal for cars stop.

# Train setting panel path:
LDSET_PATH = os.path.join(dirpath, IMG_FD, "loadSet32.png")     # load setting.    
EMGST_PATH = os.path.join(dirpath, IMG_FD, "emgStop32.png")     # emergency stop.
RECOV_PATH = os.path.join(dirpath, IMG_FD, "reset32.png")       # train station recover.

# Railway fork signal:
FSPNG_PATH = os.path.join(dirpath, IMG_FD, "forkOnS18.png")     # fork go straight signal. 
FAPNG_PATH = os.path.join(dirpath, IMG_FD, "forkAoffS18.png")   # railway A fork on signal.
FBPNG_PATH = os.path.join(dirpath, IMG_FD, "forkBoffS18.png")   # railway B fork on signal.

# Station signal light: 
SOPNG_PATH = os.path.join(dirpath, IMG_FD, "stationOn18.png")   # station signal on.
SFPNG_PATH = os.path.join(dirpath, IMG_FD, "stationOff18.png")  # station signal off.

# Power plant light:
POPNG_PATH = os.path.join(dirpath, IMG_FD, "powerPlantOn.png")  # powerplant light on.
PFPNG_PATH = os.path.join(dirpath, IMG_FD, "powerPlantOff.png") # powerplant light off.

# Industrial Area. 
INOPNG_PATH = os.path.join(dirpath, IMG_FD, "industrOn.png")    # industrial area light on.
INFPNG_PATH = os.path.join(dirpath, IMG_FD, "industrOff.png")   # industrial area light off.

# City area light
CTOPNG_PATH = os.path.join(dirpath, IMG_FD, "cityOn.png")       # city area light on.
CTFPNG_PATH = os.path.join(dirpath, IMG_FD, "cityOff.png")      # city area light off.

# Residential area light
RDOPNG_PATH = os.path.join(dirpath, IMG_FD, "residentialOn.png") # Residential area light on.     
RDFPNG_PATH = os.path.join(dirpath, IMG_FD, "residentialOff.png")# Residential area light off.   

# AirPort area light
APOPNG_PATH = os.path.join(dirpath, IMG_FD, "AirportOn.png")    # AirPort area light on.     
APFPNG_PATH = os.path.join(dirpath, IMG_FD, "AirportOff.png")   # AirPort area light off.     

# Station signal light: 
STONPNG_PATH = os.path.join(dirpath, IMG_FD, "stationOn.png")   # station light on.
STOFPNG_PATH = os.path.join(dirpath, IMG_FD, "stationOff.png")  # station light off.

# Camera signal and the camera panel view:
CAMPNG_PATH = os.path.join(dirpath, IMG_FD, "cameraUp.png")   # station light on.
TPSGIP_PATH = os.path.join(dirpath, IMG_FD, "trailPass.gif")   # station light on.

# Train clash image:
CLPNG_PATH = os.path.join(dirpath, IMG_FD, "clash.png") 

#-------<GLOBAL PARAMTERS>-----------------------------------------------------
# Set the global reference here.
iAgentMgr = None
iAttackCtrlPanel = None
iCtrlCount = 0      # device PLC control count.
iDataPanel = None   # display panel
iDetailPanel = None # detail panel to show the component's information.
iDisplayMode = 1    # 0 - notbook display, 1 - one panel display.
iEmgStop = False    # emergency stop
iMainFrame = None   # Main frame 
iMapMgr = None      # map manager
iMapPanel = None    # History chart panel.
iPlcSimulation = True   # Flag to identify whether connect to real PLC
iPlcPanelList = []  # Plc panel list. 
iPlcMgr = None      # Plc manager 
iPowCtrlPanel = None  # Power control panel.   
iSensorCount = 0    # number of sensors. 
iTrainAPanel = None # Train A control panel. 
iTrainBPanel = None # Train B control panel.
iSensorAttack = False # Flag of sensor attack situation active.





