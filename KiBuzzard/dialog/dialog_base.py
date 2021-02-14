# -*- coding: utf-8 -*-

###########################################################################
## Python code generated with wxFormBuilder (version Oct 26 2018)
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
        wx.Dialog.__init__ ( self, parent, id = wx.ID_ANY, title = u"KiBuzzard", pos = wx.DefaultPosition, size = wx.Size( 420,352 ), style = wx.CLOSE_BOX|wx.DEFAULT_DIALOG_STYLE|wx.RESIZE_BORDER )

        # For some reason SetSizeHints is different on Windows?
        self.SetSizeHintsSz( wx.Size( 420,280 ), wx.DefaultSize )

        dialogSizer = wx.BoxSizer( wx.VERTICAL )

        guiSizer = wx.BoxSizer( wx.VERTICAL )

        guiFlexSizer = wx.FlexGridSizer( 5, 2, 0, 0 )
        guiFlexSizer.AddGrowableCol( 1 )
        guiFlexSizer.SetFlexibleDirection( wx.BOTH )
        guiFlexSizer.SetNonFlexibleGrowMode( wx.FLEX_GROWMODE_ALL )

        self.labelText = wx.StaticText( self, wx.ID_ANY, u"Label:", wx.DefaultPosition, wx.DefaultSize, 0 )
        self.labelText.Wrap( -1 )

        guiFlexSizer.Add( self.labelText, 0, wx.ALIGN_CENTER_VERTICAL|wx.ALL, 5 )

        self.labelEdit = wx.TextCtrl( self, wx.ID_ANY, wx.EmptyString, wx.DefaultPosition, wx.DefaultSize, 0 )
        guiFlexSizer.Add( self.labelEdit, 0, wx.ALL|wx.EXPAND, 5 )


        guiSizer.Add( guiFlexSizer, 1, wx.EXPAND, 5 )

        self.m_panel3 = wx.Panel( self, wx.ID_ANY, wx.DefaultPosition, wx.DefaultSize, wx.TAB_TRAVERSAL )
        guiSizer.Add( self.m_panel3, 1, wx.EXPAND |wx.ALL, 5 )

        self.createButton = wx.Button( self, wx.ID_ANY, u"Create!", wx.DefaultPosition, wx.DefaultSize, 0 )
        guiSizer.Add( self.createButton, 0, wx.ALL|wx.EXPAND, 5 )


        dialogSizer.Add( guiSizer, 1, wx.EXPAND, 5 )


        self.SetSizer( dialogSizer )
        self.Layout()

        self.Centre( wx.BOTH )

        # Connect Events
        self.labelEdit.Bind( wx.EVT_TEXT, self.labelEditOnText )
        self.labelEdit.Bind( wx.EVT_TEXT_ENTER, self.labelEditOnTextEnter )
        self.createButton.Bind( wx.EVT_BUTTON, self.createButtonOnButtonClick )

    def __del__( self ):
        pass


    # Virtual event handlers, overide them in your derived class
    def labelEditOnText( self, event ):
        pass

    def labelEditOnTextEnter( self, event ):
        pass

    def createButtonOnButtonClick( self, event ):
        pass
