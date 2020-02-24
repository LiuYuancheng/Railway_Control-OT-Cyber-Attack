#-----------------------------------------------------------------------------
# Name:        uiGlobal.py
#
# Purpose:     This module is used as a local config file to set constants, 
#              global parameters which will be used in the other modules.
#              
# Author:      Yuancheng Liu
#
# Created:     2020/01/10
# Copyright:   YC @ Singtel Cyber Security Research & Development Laboratory
# License:     YC
#-----------------------------------------------------------------------------
import os

dirpath = os.getcwd()
print("Current working directory is : %s" % dirpath)
APP_NAME = 'Generator Mgr'

#------<IMAGES PATH>-------------------------------------------------------------
IMG_FD = 'img'
ICO_PATH = os.path.join(dirpath, IMG_FD, "geoIcon.ico")
MOIMG_PATH = os.path.join(dirpath, IMG_FD, "motor.png")
PUIMG_PATH = os.path.join(dirpath, IMG_FD, "pump.png")

#-------<GLOBAL PARAMTERS>-----------------------------------------------------
iMainFrame = None   # MainFrame.
iMotoImgPnl = None  # Image panel.
iPumpImgPnl = None
iCtrlPanel = None   # control panel
iUpdateRate = 0.2     # main frame update rate 1 sec.
iGnMgr = None
