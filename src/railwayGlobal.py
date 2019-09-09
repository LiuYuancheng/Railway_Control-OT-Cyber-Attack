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
#   M0  -> Q0.0 Airport LED
#   M10 -> Q0.1 Power Plant
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
TTICO_PATH = "".join([dirpath, "\\img\\title.ico"])

# Panel background path:
BGPNG_PATH = "".join([dirpath, "\\img\\Trainbg1.png"])      # map panel.
RAJPG_PATH = "".join([dirpath, "\\img\\ransomwareAtt.jpg"]) # ransomeare attack panel.
TAGIF_PATH = "".join([dirpath, "\\img\\trojanAtt.gif"])     # tronjan attack panel.

# Pedestrian cross signal at the gate: 
WKJPG_PATH = "".join([dirpath, "\\img\\walk.jpg"])          # Pedestrian pass.
HTPNG_PATH = "".join([dirpath, "\\img\\hitPPl.png"])        # Pedestrian accident.
PPPNG_PATH = "".join([dirpath, "\\img\\passS18.png"])       # signal for people pass 
PSPNG_PATH = "".join([dirpath, "\\img\\stopS18.png"])       # signal for people stop 
CPPNG_PATH = "".join([dirpath, "\\img\\gateCarP18.png"])    # signal for cars pass    
CSPNG_PATH = "".join([dirpath, "\\img\\gateCarS18.png"])    # signal for cars stop.

# Train setting panel path:
LDSET_PATH = "".join([dirpath, "\\img\\loadSet32.png"])     # load setting.    
EMGST_PATH = "".join([dirpath, "\\img\\emgStop32.png"])     # emergency stop.
RECOV_PATH = "".join([dirpath, "\\img\\reset32.png"])       # train station recover.

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

# Camera signal and the camera panel view:
CAMPNG_PATH = "".join([dirpath, "\\img\\cameraUp.png"])   # station light on.
TPSGIP_PATH = "".join([dirpath, "\\img\\trailPass.gif"])   # station light on.

# Train clash image:
CLPNG_PATH = "".join([dirpath, "\\img\\clash.png"]) 

#-------<GLOBAL PARAMTERS>-----------------------------------------------------
# Set the global reference here.
iAgentMgr = None
iAttackCtrlPanel = None
iCtrlCount = 0      # device PLC control count.
iDataPanel = None   # display panel
iDetailPanel = None # detail panel to show the component's information.
iEmgStop = False    # emergency stop
iMainFrame = None   # Main frame 
iMapMgr = None      # map manager
iMapPanel = None    # History chart panel.
iPlcSimulation = False   # Flag to identify whether connect to real PLC
iPlcPanelList = []  # Plc panel list. 
iPlcMgr = None      # Plc manager 
iPowCtrlPanel = None  # Power control panel.   
iSensorCount = 0    # number of sensors. 
iTrainAPanel = None # Train A control panel. 
iTrainBPanel = None # Train B control panel.
iSensorAttack = False # Flag of sensor attack situation active.





