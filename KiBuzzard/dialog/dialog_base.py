# -*- coding: utf-8 -*-

###########################################################################
## Python code generated with wxFormBuilder (version 3.9.0 Jan 11 2021)
## http://www.wxformbuilder.org/
##
## PLEASE DO *NOT* EDIT THIS FILE!
###########################################################################

import wx
import wx.xrc

###########################################################################
## Class KiBuzzardDialog
###########################################################################

class KiBuzzardDialog ( wx.Dialog ):

    def __init__( self, parent ):
        wx.Dialog.__init__ ( self, parent, id = wx.ID_ANY, title = u"KiBuzzard", pos = wx.DefaultPosition, size = wx.Size( 309,76 ), style = wx.DEFAULT_DIALOG_STYLE )

        self.SetSizeHints( wx.DefaultSize, wx.DefaultSize )

        bSizer28 = wx.BoxSizer( wx.VERTICAL )

        bSizer12 = wx.BoxSizer( wx.HORIZONTAL )

        self.m_staticText13 = wx.StaticText( self, wx.ID_ANY, u"cmd", wx.DefaultPosition, wx.DefaultSize, 0 )
        self.m_staticText13.Wrap( -1 )

        bSizer12.Add( self.m_staticText13, 0, wx.ALIGN_CENTER_VERTICAL|wx.ALL, 5 )

        self.m_textCtrl4 = wx.TextCtrl( self, wx.ID_ANY, wx.EmptyString, wx.DefaultPosition, wx.DefaultSize, wx.TE_PROCESS_ENTER )
        bSizer12.Add( self.m_textCtrl4, 1, wx.ALL|wx.EXPAND, 5 )


        bSizer28.Add( bSizer12, 1, wx.ALL|wx.EXPAND, 5 )


        self.SetSizer( bSizer28 )
        self.Layout()

        self.Centre( wx.BOTH )

        # Connect Events
        self.m_textCtrl4.Bind( wx.EVT_TEXT_ENTER, self.OnTextEnter )

    def __del__( self ):
        pass


    # Virtual event handlers, overide them in your derived class
    def OnTextEnter( self, event ):
        event.Skip()


