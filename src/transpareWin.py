#!/usr/bin/python
#-----------------------------------------------------------------------------
# Name:        transparentWin.py
#
# Purpose:     This module is used to create a transparent window. we did some 
#              small changes from the module: https://wiki.wxpython.org/Transparent%20Frames
#              
# Author:      Yuancheng Liu
#
# Created:     2019/07/31
#-----------------------------------------------------------------------------
import wx

class transparentWin(wx.Frame):
    def __init__(self):
        wx.Frame.__init__( self, None, title="Am I transparent?",
                           style=wx.CAPTION | wx.STAY_ON_TOP )
        self.SetClientSize( (300, 300) )
        self.SetBackgroundColour(wx.Colour('WHITE'))
        self.alphaValue = 255
        self.alphaIncrement = -4

        #pnl = rwp.CameraView(self, 0)
        # pnl.setPlay()
        baPanel = wx.Panel(self)
        self.stTxt = wx.StaticText( baPanel, -1, str( self.alphaValue ), (25, 25) )
        self.stTxt.SetFont( wx.Font( 18, wx.SWISS, wx.NORMAL, wx.NORMAL ) )

        self.changeAlpha_timer = wx.Timer( self )
        self.changeAlpha_timer.Start( 50 )       # 20 changes per second
        self.Bind( wx.EVT_TIMER, self.ChangeAlpha )

        self.Bind( wx.EVT_CLOSE, self.OnCloseWindow )

    #end transparentWin class
    #--------------------------------------------------------
    def ChangeAlpha( self, evt )  :
        """ The term "alpha" means variable transparency
              as opposed to a "mask" which is binary transparency.
              alpha == 255 :  fully opaque
              alpha ==   0 :  fully transparent (mouse is ineffective!)

            Only top-level controls can be transparent; no other controls can.
            This is because they are implemented by the OS, not wx.
        """

        self.alphaValue += self.alphaIncrement
        if (self.alphaValue) <= 0 or (self.alphaValue >= 255) :

            # Reverse the increment direction.
            self.alphaIncrement = -self.alphaIncrement

            if self.alphaValue <= 0 :
                self.alphaValue = 0

            if self.alphaValue > 255 :
                self.alphaValue = 255
        #end if

        #self.stTxt.SetLabel( str( self.alphaValue ) )

        # Note that we no longer need to use ctypes or win32api to
        # make transparent windows, however I'm not removing the
        # MakeTransparent code from this sample as it may be helpful
        # to someone for other uses, someday.

        #self.MakeTransparent( self.alphaValue )

        # Instead, just call the SetTransparent() method
        self.SetTransparent( self.alphaValue )      # Easy !

    #end ChangeAlpha def

    #--------------------------------------------------------

    def OnCloseWindow( self, evt ) :

        self.changeAlpha_timer.Stop()
        del self.changeAlpha_timer       # avoid a memory leak
        self.Destroy()

    #-----------------------------------------------------

    def MakeTransparent( self, amount ) :
        """
        This is how the method SetTransparent() is implemented
            on all MS Windows platforms.
        """
        import os
        if os.name == 'nt' :  # could substitute: sys.platform == 'win32'

            hwnd = self.GetHandle()
            try :
                import ctypes   # DLL library interface constants' definitions
                _winlib = ctypes.windll.user32    # create object to access DLL file user32.dll
                style = _winlib.GetWindowLongA( hwnd, '0xffff')
                style |= 0x00080000
                _winlib.SetWindowLongA( hwnd, '0xffff', style )
                _winlib.SetLayeredWindowAttributes( hwnd, 0, amount, 2 )

            except ImportError :

                import win32api, win32con, winxpgui
                _winlib = win32api.LoadLibrary( "user32" )
                pSetLayeredWindowAttributes = win32api.GetProcAddress(
                    _winlib, "SetLayeredWindowAttributes" )
                if pSetLayeredWindowAttributes == None :
                    return
                exstyle = win32api.GetWindowLong( hwnd, win32con.GWL_EXSTYLE )
                if 0 == ( exstyle & 0x80000 ) :
                    win32api.SetWindowLong( hwnd,
                                           win32con.GWL_EXSTYLE,
                                           exstyle | 0x80000 )
                winxpgui.SetLayeredWindowAttributes( hwnd, 0, amount, 2 )
        else :
            print('OS Platform must be MS Windows')
            self.Destroy()
        #end if
    #end MakeTransparent def

#end transparentWin class

#=======================================================

if __name__ == '__main__' :

    app = wx.App( False )
    frm = transparentWin()
    frm.Show()
    app.MainLoop()