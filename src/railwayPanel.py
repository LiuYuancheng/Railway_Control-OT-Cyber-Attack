#!/usr/bin/python
#-----------------------------------------------------------------------------
# Name:        XAKAsensorPanel.py
#
# Purpose:     This module is used to provide differentfunction panels for the 
#              XAKAsensorReader. 
#              
# Author:      Yuancheng Liu
#
# Created:     2019/06/24
# Copyright:   YC
# License:     YC
#-----------------------------------------------------------------------------
import wx
import wx.grid
import time
import random
import firmwGlobal as gv 

PERIODIC = 500  # how many ms the periodic call back

# People counting sensor message labels
DETAIL_LABEL_LIST = [
    'Seonsor ID: ',
    'Parameter Count:',
    'Presence Info:',
    '00: Sequence',
    '01: Idx People count',
    '02: Reserved',
    '03: Reserved',
    '04: Human Presence',
    '05: Program Version',
    '06: ShortTerm avg',
    '07: LongTerm avg',
    '08: EnvMapping rm T',
    '09: Radar Map rm T',
    '10: Idx for radar mapping',
    '11: Num of ppl for radar map',
    '12: Device ID',
    '13: Start Rng',
    '14: End Rng',
    '15: Reserved',
    '16: LED on/off',
    '17: Trans period',
    '18: Calib factor',
    '19: Tiled Angle',
    '20: Radar Height',
    '21: Avg size',
    '22: Presence on/off',
    '23: Reserved',
    '24: Final ppl num',
    '25: Radar MP val',
    '26: Env MP val',
    '27: serial num_1',
    '28: serial num_2',
    '29: serial dist1',
    '30: serial dist2',
    '31: Reserved',
    '32: Reserved',
    '33: Reserved'
]
# Basic information label.
CHART_LABEL_LIST = [
    'Sensor ID:',  # int
    'Connection:',  # str
    'Sequence_N:',  # float
    'People_NUM:',  # float
    'Average_PP:',  # float
    'Final_PNUM:'   # float
]
#-----------------------------------------------------------------------------
#-----------------------------------------------------------------------------
class PanelPlaceHolder(wx.Panel):
    """ Place Holder Panel"""
    def __init__(self, parent):
        wx.Panel.__init__(self, parent)
        self.SetBackgroundColour(wx.Colour(200, 210, 200))
        wx.StaticText(self, -1, "Place Holder: Add more sensor here", (20, 20))


#-----------------------------------------------------------------------------
#-----------------------------------------------------------------------------
class PanelBaseInfo(wx.Panel):
    """ Panel to display the basic sensor information and pop up the detail sensor
        information window if the user clicked the detail button.
    """
    def __init__(self, parent):
        wx.Panel.__init__(self, parent, size=(100, 300))
        self.SetBackgroundColour(wx.Colour(200, 210, 200))
        self.valueDispList = []
        self.infoWindow = None  # window to show the detail information.
        flagsR = wx.RIGHT | wx.ALIGN_CENTER_VERTICAL
        sizer = wx.BoxSizer(wx.VERTICAL)
        sizer.AddSpacer(20)
        # Information rows
        for item in CHART_LABEL_LIST:
            sizer.Add(wx.StaticText(self, -1, item))
            datalabel = wx.StaticText(self, -1, '--')
            self.valueDispList.append(datalabel)
            sizer.Add(datalabel, flag=flagsR, border=2)
        # Control button rows.
        self.pauseBt = wx.Button(self, label='Pause ||'.rjust(10), size=(80, 23))
        self.pauseBt.Bind(wx.EVT_BUTTON, self.pauseUpdate)
        sizer.Add(self.pauseBt, flag=flagsR, border=2)
        self.detailBt = wx.Button(self, label='Detail >>'.rjust(10), size=(80, 23))
        self.detailBt.Bind(wx.EVT_BUTTON, self.showDetail)
        sizer.Add(self.detailBt, flag=flagsR, border=2)
        self.SetSizer(sizer)
        self.Show(True)

    #-----------------------------------------------------------------------------
    def displayTargetClose(self, event):
        """ Close display target info window and clear the tracked target."""
        if self.infoWindow:
            self.infoWindow.Destroy()
            self.infoWindow = None
            gv.iDetailPanel = None

    #-----------------------------------------------------------------------------
    def pauseUpdate(self, event):
        """ Start/Pause the update of the chart display."""
        buttonLb = event.GetEventObject().GetLabel()
        if 'Pause' in buttonLb:
            self.pauseBt.SetLabel('Start >'.rjust(10))
            if gv.iChartPanel: gv.iChartPanel.updateDisplay(updateFlag=False)
        elif 'Start' in buttonLb:
            self.pauseBt.SetLabel('Pause ||'.rjust(10))
            if gv.iChartPanel: gv.iChartPanel.updateDisplay(updateFlag=True)

    #-----------------------------------------------------------------------------
    def showDetail(self, event):
        """ pop up the detail window to show all the sensor parameters value."""
        if self.infoWindow is None and gv.iDetailPanel is None:
            #posF =[ n+600 for n in gv.iMainFrame.GetClientAreaOrigin()]
            posF = gv.iMainFrame.GetPosition()
            self.infoWindow = wx.MiniFrame(gv.iMainFrame, -1,
                'Detail Sensor Info', pos=(posF[0]+486, posF[1]),
                size=(350, 700),
                style=wx.DEFAULT_FRAME_STYLE)
            gv.iDetailPanel = PanelDetailInfo(self.infoWindow)
            self.infoWindow.Bind(wx.EVT_CLOSE, self.displayTargetClose)
            self.infoWindow.Show()

   #-----------------------------------------------------------------------------
    def updateData(self, dataList):
        """ Update the data display on the panel. Input parameter sequence and 
            type follow <LABEL_LIST2>. 
        """
        if len(dataList) != len(CHART_LABEL_LIST):
            print("PanelBaseInfo: input dataList element missing.")
            return
        for i, value in enumerate(dataList):
            dataStr = "{0:.2f}".format(value) if isinstance(
                value, float) else str(value)
            self.valueDispList[i].SetLabel("> "+dataStr)

#-----------------------------------------------------------------------------
#-----------------------------------------------------------------------------
class PanelChart(wx.Panel):
    """ This function is used to provide lineChart wxPanel to show the history 
        of the people counting sensor's data.
        example: http://manwhocodes.blogspot.com/2013/04/graphics-device-interface-in-wxpython.html
    """
    def __init__(self, parent, recNum):
        """ Init the panel."""
        wx.Panel.__init__(self, parent, size=(350, 300))
        self.SetBackgroundColour(wx.Colour(200, 210, 200))
        self.recNum = 60
        self.updateFlag = True  # flag whether we update the diaplay area
        # [(current num, average num, final num)]*60
        self.data = [(0, 0, 0)] * self.recNum
        self.times = ('-30s', '-25s', '-20s', '-15s', '-10s', '-5s', '0s')
        self.Bind(wx.EVT_PAINT, self.OnPaint)

    #-----------------------------------------------------------------------------
    def appendData(self, numsList):
        """ Append the data into the data hist list.
            numsList Fmt: [(current num, average num, final num)]
        """
        for i, value in enumerate(numsList):
            if value> 20: numsList[i] = 20
        self.data.append(numsList)
        self.data.pop(0) # remove the first oldest recode in the list.
    
    #-----------------------------------------------------------------------------
    def drawBG(self, dc):
        """ Draw the line chart background."""
        dc.SetPen(wx.Pen('WHITE'))
        dc.DrawRectangle(1, 1, 300, 200)
        # Draw Axis and Grids:
        dc.SetPen(wx.Pen('#D5D5D5')) #dc.SetPen(wx.Pen('#0AB1FF'))
        font = dc.GetFont()
        font.SetPointSize(8)
        dc.SetFont(font)
        dc.DrawLine(1, 1, 300, 1)
        dc.DrawLine(1, 1, 1, 201)
        for i in range(2, 22, 2): 
            dc.DrawLine(2, i*10, 300, i*10) # Y-Grid
            dc.DrawLine(2, i*10, -5, i*10)  # Y-Axis
            dc.DrawText(str(i).zfill(2), -25, i*10+5) # format to ## int  
        for i in range(len(self.times)): 
            dc.DrawLine(i*50, 2, i*50, 200) # X-Grid
            dc.DrawLine(i*50, 2, i*50, -5)  # X-Axis
            dc.DrawText(self.times[i], i*50-10, -5)
        # DrawTitle:
        font = dc.GetFont()
        #font.SetWeight(wx.FONTWEIGHT_BOLD)
        dc.SetFont(font)
        dc.DrawText('XAKA sensor data', 2, 235)

    #-----------------------------------------------------------------------------
    def drawFG(self, dc):
        """ Draw the front ground data chart line."""
        color = ('#0AB1FF', '#CE8349', '#A5CDAA')
        label = ("Cur_N", "Avg_N", "Fnl_N")
        for idx in range(3):
            # Draw the line sample.
            dc.SetPen(wx.Pen(color[idx], width=2, style=wx.PENSTYLE_SOLID))
            dc.DrawLine(100+idx*60, 212, 100+idx*60+8, 212)
            dc.DrawText(label[idx], idx*60+115, 220)
            # Create the point list and draw.
            dc.DrawSpline([(i*5, self.data[i][idx]*10)for i in range(len(self.data))])

    #-----------------------------------------------------------------------------
    def updateDisplay(self, updateFlag=None):
        """ Set/Update the display: if called as updateDisplay() the function will 
            update the panel, if called as updateDisplay(updateFlag=?) the function will 
            set the self update flag.
        """
        if updateFlag is None and self.updateFlag: 
            self.Refresh(True)
            self.Update()
        else:
            self.updateFlag = updateFlag

    #-----------------------------------------------------------------------------
    def OnPaint(self, event):
        """ Main panel drawing function."""
        dc = wx.PaintDC(self)
        # set the axis Orientation area and fmt to up+right direction.
        dc.SetDeviceOrigin(40, 240)
        dc.SetAxisOrientation(True, True)
        self.drawBG(dc)
        self.drawFG(dc)

#-----------------------------------------------------------------------------
#-----------------------------------------------------------------------------
class PanelDetailInfo(wx.Panel):
    """ Panel to show the all 35 detail parameters' value read from the sensor."""
    def __init__(self, parent):
        """ Init the panel."""
        wx.Panel.__init__(self, parent, size=(350, 300))
        self.parent = parent
        self.valueDispList = []     # Label list will display on UI.
        self.SetBackgroundColour(wx.Colour(200, 200, 200))
        sizer = self.buildUISizer()
        self.SetSizer(sizer)

    #-----------------------------------------------------------------------------
    def buildUISizer(self):
        """ build the UI sizer for the background panel."""
        sizer = wx.GridSizer(len(DETAIL_LABEL_LIST)+2, 2, 4, 4)
        # Add the title line.
        sizer.Add(wx.Button(self, label='ParameterName ',
                            size=(170, 18), style=wx.BU_LEFT, name='ParameterName'))
        sizer.Add(wx.Button(self, label='FeedbackValue ', size=(
            170, 18), style=wx.BU_LEFT, name='Value'))
        # Add the display area.
        for item in DETAIL_LABEL_LIST:
            sizer.Add(wx.StaticText(self, -1, item))
            datalabel = wx.StaticText(self, -1, '--')
            self.valueDispList.append(datalabel)
            sizer.Add(datalabel)
        return sizer

    #-----------------------------------------------------------------------------
    def updateDisplay(self, dataList):
        """ Update the panel display. The input data list follow the sequence in 
            <DETAIL_LABEL_LIST>
        """
        if len(dataList) != len(DETAIL_LABEL_LIST):
            print("PanelDetailInfo: The input data list element missing %d", len(dataList))
            return
        for i in range(len(dataList)): 
            self.valueDispList[i].SetLabel(str(dataList[i]))

#-----------------------------------------------------------------------------
#-----------------------------------------------------------------------------
class PanelMap(wx.Panel):
    """ Draw the office top view map with the data. The background Image setting 
        example may be useful in the future: 
        http://www.blog.pythonlibrary.org/2010/03/18/wxpython-putting-a-background-image-on-a-panel/
    """
    def __init__(self, parent):
        """ Init the panel."""
        wx.Panel.__init__(self, parent, size=(240, 275))
        self.SetBackgroundColour(wx.Colour(200, 210, 200))
        self.bitmap = wx.Bitmap(gv.BGPNG_PATH)
        self.bitmapSZ = self.bitmap.GetSize()
        self.toggle = True      # Display toggle flag.     
        self.pplNum = 0         # Number of peopel.
        self.highLightIdx = 0   # High light area. 
        self.Bind(wx.EVT_PAINT, self.OnPaint)
        self.Bind(wx.EVT_LEFT_DOWN, self.OnClick)
        
    #-----------------------------------------------------------------------------
    def OnPaint(self, event):
        """ Draw the whole panel. """
        dc = wx.PaintDC(self)
        dc.DrawBitmap(self.bitmap, 1, 1)
        # Dc Draw the detection area.
        penColor = 'BLUE' if self.toggle else 'RED'
        dc.SetPen(wx.Pen(penColor, width=2, style=wx.PENSTYLE_LONG_DASH))
        w, h = self.bitmapSZ[0]//2, self.bitmapSZ[1]//2
        # High Light the user selected area.
        self.DrawHighLight(dc, w, h)
        # draw the sensor as a flag rectangle:
        dc.SetPen(wx.Pen('blue', width=1, style=wx.PENSTYLE_SOLID))
        dc.SetBrush(wx.Brush(wx.Colour(penColor)))
        dc.DrawRectangle(112, 60, 11, 11)
        # Draw the transparent rectangle to represent how many people in the area.
        gdc = wx.GCDC(dc)
        r = g = b = 120
        r = r+self.pplNum*7 if r+self.pplNum*7 < 255 else 254
        brushclr = wx.Colour(r, g, b, 128)   # half transparent
        gdc.SetBrush(wx.Brush(brushclr))
        gdc.DrawRectangle(1, 1, w, h)
        self.toggle = not self.toggle # set the toggle display flag.

    #-----------------------------------------------------------------------------
    def DrawHighLight(self, dc, w, h):
        """ High light the area user clicked"""
        # set the position: l-left t-top r-right b-bottum x_offset y_offset.
        l, t, r, b, x_offset, y_offset = 1, 1, w, h, 0, 0 
        
        if self.highLightIdx == 1:
            x_offset = w
        elif self.highLightIdx == 2:
            y_offset = h
        elif self.highLightIdx == 3:
            x_offset = w
            y_offset = h
        # Hight list area by draw a rectangle.
        dc.DrawLine(l+x_offset, t+y_offset, r+x_offset, t+y_offset)
        dc.DrawLine(l+x_offset, t+y_offset, l+x_offset, b+y_offset)
        dc.DrawLine(r+x_offset, t+y_offset, r+x_offset, b+y_offset)
        dc.DrawLine(l+x_offset, b+y_offset, r+x_offset, b+y_offset)

    #-----------------------------------------------------------------------------
    def OnClick(self, event):
        """ High light the user clicked area."""
        x, y = event.GetPosition()
        w, h = self.bitmapSZ[0]//2, self.bitmapSZ[1]//2
        if x < w and y < h:
            self.highLightIdx = 0
        elif x >= w and y < h:
            self.highLightIdx = 1
        elif x < w and y >= h:
            self.highLightIdx = 2
        else:
            self.highLightIdx = 3
        self.updateDisplay()
        # mark the line in the sensor information grid.
        self.Parent.markSensorRow(self.highLightIdx)

    #-----------------------------------------------------------------------------
    def updateNum(self, number):
        """ Udpate the self people number."""
        self.pplNum = int(number)

    #-----------------------------------------------------------------------------
    def updateDisplay(self, updateFlag=None):
        """ Set/Update the display: if called as updateDisplay() the function will 
            update the panel, if called as updateDisplay(updateFlag=?) the function will 
            set the self update flag.
        """
        self.Refresh(True)
        self.Update()

#-----------------------------------------------------------------------------
#-----------------------------------------------------------------------------
class PanelMultInfo(wx.Panel):
    """ Mutli-information panel used to show all sensor's detection situation on the 
        office topview map, sensor connection status and show a Grid to show all the 
        sensor's detection data.
    """
    def __init__(self, parent):
        """ Init the panel."""
        wx.Panel.__init__(self, parent, size=(350, 300))
        self.SetBackgroundColour(wx.Colour(200, 210, 200))
        self.mapPanel = None
        self.sensorCount = 1    # total sensor count.
        self.totPllNum = 0      # total current number of people detected
        self.totPllAvg = 0      # total avg number of people detected 
        self.senIndList = []    # sensor indicator list.
        mainUISizer = self.buidUISizer()
        self.SetSizer(mainUISizer)

    #-----------------------------------------------------------------------------
    def buidUISizer(self):
        """ Build the UI with 2 columns.left: Map, right: sensor data Grid."""
        sizer = wx.BoxSizer(wx.HORIZONTAL)
        flagsT = wx.RIGHT
        flagsR = wx.RIGHT | wx.ALIGN_CENTER_VERTICAL
        sizer.AddSpacer(5)
        # Column idx = 1 Map panel.
        gv.iMapPanel = self.mapPanel = PanelMap(self)
        # Column idx =2 Data display part:
        sizer.Add(self.mapPanel, flag=flagsR, border=2)
        vsizer = wx.BoxSizer(wx.VERTICAL)
        vsizer.Add(wx.StaticText(self, label='Sensor Connection Status:'),
                   flag=flagsT, border=2)
        vsizer.AddSpacer(10)
        # Column dix =2, row idx = 1: All the sensor connection indicators: 
        hbox = wx.BoxSizer(wx.HORIZONTAL)
        for i in range(4):
            sen1S = wx.StaticText(self, label=str('Sensor '+str(i)).center(10))
            self.senIndList.append(sen1S)
            sen1S.SetBackgroundColour(wx.Colour(120, 120, 120))
            hbox.Add(sen1S, flag=flagsR, border=2)
            hbox.AddSpacer(5)
        self.updateSensorIndicator(0, 1)
        vsizer.Add(hbox, flag=flagsR, border=2)
        vsizer.AddSpacer(10)
        # Column dix =2, row idx = 2: Sensor information display Grid.
        vsizer.Add(wx.StaticText(self, label='Sensors FeedBack Data:'),
            flag=flagsT, border=2)
        vsizer.AddSpacer(10)
        self.grid = wx.grid.Grid(self, -1)
        self.grid.CreateGrid(5, 3)
        # Set the Grid size.
        self.grid.SetRowLabelSize(40)
        self.grid.SetColSize(0, 50)
        self.grid.SetColSize(1, 65)
        self.grid.SetColSize(2, 65)
        # Set the Grid's labels.
        self.grid.SetColLabelValue(0, 'Sen ID')
        self.grid.SetColLabelValue(1, 'Crt NUM')
        self.grid.SetColLabelValue(2, 'Avg NUM')
        self.grid.SetRowLabelValue(4, 'Tot')
        self.grid.Bind(wx.grid.EVT_GRID_LABEL_LEFT_CLICK, self.highLightMap)
        vsizer.Add(self.grid, flag=flagsR, border=2)
        sizer.Add(vsizer, flag=flagsT, border=2)
        return sizer

    #-----------------------------------------------------------------------------
    def updateSensorIndicator(self, idx, state):
        """ Update the sensor indictor's status Green:online, Gray:Offline."""
        color = wx.Colour("Green") if state else wx.Colour(120, 120, 120)
        self.senIndList[idx].SetBackgroundColour(color)

    #-----------------------------------------------------------------------------
    def updateSensorGrid(self, idx, dataList):
        """ Update the sensor Grid's display based on the sensor index. """
        if len(dataList) != 3:
            print("PanelMultInfo: Sensor Grid fill in data element missing.")
            return
        # Udpate the grid cells' data. 
        for i, item in enumerate(dataList):
            dataStr = "{0:.4f}".format(item) if isinstance(
                item, float) else str(item)
            self.grid.SetCellValue(idx, i, dataStr)
            if i == 1: self.totPllNum += item
            if i == 2: self.totPllAvg += item
        # update the total numbers. 
        self.grid.SetCellValue(4, 0, str(self.sensorCount))
        self.grid.SetCellValue(4, 1, "{0:.4f}".format(self.totPllNum))
        self.grid.SetCellValue(4, 2, "{0:.4f}".format(self.totPllAvg))
        self.grid.ForceRefresh()  # refresh all the grid's cell at one time ?
        self.totPllNum = self.totPllAvg = 0

    #-----------------------------------------------------------------------------
    def markSensorRow(self, idx):
        """ Mark(highlight)the selected row."""
        self.grid.SelectRow(idx)

    #-----------------------------------------------------------------------------
    def highLightMap(self, event):
        """ High light the sensor covered area on the topview map."""
        row_index = event.GetRow()
        self.grid.SelectRow(row_index)
        self.mapPanel.highLightIdx = row_index 

#-----------------------------------------------------------------------------
#-----------------------------------------------------------------------------
class PanelSetup(wx.Panel):
    """ Panel to handle the program setup."""
    def __init__(self, parent):
        """ Init the panel."""
        wx.Panel.__init__(self, parent, size=(350, 300))
        self.SetBackgroundColour(wx.Colour(200, 210, 200))
        flagsT = wx.RIGHT
        flagsR = wx.RIGHT | wx.ALIGN_CENTER_VERTICAL

        vsizer = wx.BoxSizer(wx.VERTICAL)
        vsizer.AddSpacer(10)
        # Row idx = 1: Sensor firmware registration part:
        vsizer.Add(wx.StaticText(self, label='Sensor Registration Setting:'),
                   flag=flagsT, border=2)
        vsizer.AddSpacer(10)
        hbox1 = wx.BoxSizer(wx.HORIZONTAL)
        self.serverchoice = wx.Choice(
            self, -1, size=(150, 23), choices=list(gv.RG_SERVER_CHOICE.keys()), name='Server')
        self.serverchoice.SetSelection(0)
        hbox1.Add(self.serverchoice, flag=flagsR, border=2)
        hbox1.AddSpacer(5)
        self.regBt = wx.Button(
            self, label='Sensor registration.', size=(150, 23))
        self.regBt.Bind(wx.EVT_BUTTON, self.logtoServer)
        hbox1.Add(self.regBt, flag=flagsR, border=2)
        hbox1.AddSpacer(5)
        self.sgSimuBt = wx.Button(
            self, label='Sigature Simulation.', size=(150, 23))
        self.sgSimuBt.Bind(wx.EVT_BUTTON, self.sigaSimuInput)
        hbox1.Add(self.sgSimuBt, flag=flagsR, border=2)
        vsizer.Add(hbox1, flag=flagsR, border=2)
        # Row idx =2: Sensor setting/sensor data send back to server part.
        pass 
        self.SetSizer(vsizer)

#-----------------------------------------------------------------------------
    def logtoServer(self, event):
        """ Call the mainFrame's <logtoServer> to establish SSL connection."""
        ServerName = self.serverchoice.GetString(self.serverchoice.GetSelection())
        if gv.iMainFrame: gv.iMainFrame.logtoServer(ServerName)

#-----------------------------------------------------------------------------
    def sigaSimuInput(self, event):
        """Call the mainFrame's <sigaSimuInput> fill in the simulation siguature."""
        if gv.iMainFrame: gv.iMainFrame.sigaSimuInput(event)

#-----------------------------------------------------------------------------
#-----------------------------------------------------------------------------
class LineChartExample(wx.Frame):
    def __init__(self, parent, id, title):
        """ Frame the test the Line Chart(Currently not used.)"""
        wx.Frame.__init__(self, parent, id, title, size=(390, 300))
        panel = wx.Panel(self, -1)
        panel.SetBackgroundColour('WHITE')
        hbox = wx.BoxSizer(wx.HORIZONTAL)
        self.linechart = PanelChart(panel, 100)
        hbox.Add(self.linechart)
        panel.SetSizer(hbox)
        self.Centre()
        self.Show(True)
        self.timer = wx.Timer(self)
        self.Bind(wx.EVT_TIMER, self.periodic)
        self.timer.Start(PERIODIC)  # every 500 ms

    def periodic(self, event):
        num = random.randint(0, 20)
        self.linechart.addData(
            (random.randint(0, 20), random.randint(0, 20), random.randint(0, 20)))
        self.linechart.Refresh(True)

#app = wx.App()
#LineChartExample(None, -1, 'A line chart')
#app.MainLoop()
