#-----------------------------------------------------------------------------
# Name:        railwayGlobal.py
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

BGPNG_PATH = "".join([dirpath, "\\img\\Trainbg.png"])
WKPNG_PATH = "".join([dirpath, "\\img\\walk.jpg"])

#-----------------------------------------------------------------------------
# Set the global reference here.
iPlcPanelList = []  # Plc panel list. 
iMapPanel = None    # History chart panel
