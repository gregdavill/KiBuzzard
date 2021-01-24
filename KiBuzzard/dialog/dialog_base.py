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
        wx.Dialog.__init__ ( self, parent, id = wx.ID_ANY, title = u"KiBuzzard", pos = wx.DefaultPosition, size = wx.Size( 420,280 ), style = wx.CLOSE_BOX|wx.DEFAULT_DIALOG_STYLE|wx.RESIZE_BORDER )

        #self.SetSizeHints( wx.Size( 420,280 ), wx.DefaultSize )

        dialogSizer = wx.BoxSizer( wx.VERTICAL )

        self.notebook = wx.Notebook( self, wx.ID_ANY, wx.DefaultPosition, wx.DefaultSize, 0 )
        self.guiPanel = wx.Panel( self.notebook, wx.ID_ANY, wx.DefaultPosition, wx.DefaultSize, wx.TAB_TRAVERSAL )
        guiSizer = wx.BoxSizer( wx.VERTICAL )

        guiFlexSizer = wx.FlexGridSizer( 5, 2, 0, 0 )
        guiFlexSizer.AddGrowableCol( 1 )
        guiFlexSizer.SetFlexibleDirection( wx.BOTH )
        guiFlexSizer.SetNonFlexibleGrowMode( wx.FLEX_GROWMODE_ALL )

        self.labelText = wx.StaticText( self.guiPanel, wx.ID_ANY, u"Label:", wx.DefaultPosition, wx.DefaultSize, 0 )
        self.labelText.Wrap( -1 )

        guiFlexSizer.Add( self.labelText, 0, wx.ALIGN_CENTER_VERTICAL|wx.ALL, 5 )

        labelFlexSizer = wx.FlexGridSizer( 0, 3, 0, 0 )
        labelFlexSizer.AddGrowableCol( 1 )
        labelFlexSizer.SetFlexibleDirection( wx.BOTH )
        labelFlexSizer.SetNonFlexibleGrowMode( wx.FLEX_GROWMODE_SPECIFIED )

        labelStartComboBoxChoices = [ wx.EmptyString, u"[", u"(", u"/", u"<" ]
        self.labelStartComboBox = wx.ComboBox( self.guiPanel, wx.ID_ANY, wx.EmptyString, wx.DefaultPosition, wx.DefaultSize, labelStartComboBoxChoices, wx.CB_READONLY )
        labelFlexSizer.Add( self.labelStartComboBox, 0, wx.ALL, 5 )

        self.labelEdit = wx.TextCtrl( self.guiPanel, wx.ID_ANY, u" ", wx.DefaultPosition, wx.DefaultSize, 0 )
        labelFlexSizer.Add( self.labelEdit, 0, wx.ALL|wx.EXPAND, 5 )

        labelEndComboBoxChoices = [ wx.EmptyString, u"]", u")", u"/", u">" ]
        self.labelEndComboBox = wx.ComboBox( self.guiPanel, wx.ID_ANY, wx.EmptyString, wx.DefaultPosition, wx.DefaultSize, labelEndComboBoxChoices, wx.CB_READONLY )
        labelFlexSizer.Add( self.labelEndComboBox, 0, wx.ALL, 5 )


        guiFlexSizer.Add( labelFlexSizer, 1, wx.EXPAND, 5 )

        self.fontText = wx.StaticText( self.guiPanel, wx.ID_ANY, u"Font:", wx.DefaultPosition, wx.DefaultSize, 0 )
        self.fontText.Wrap( -1 )

        guiFlexSizer.Add( self.fontText, 0, wx.ALIGN_CENTER_VERTICAL|wx.ALL, 5 )

        fontComboBoxChoices = []
        self.fontComboBox = wx.ComboBox( self.guiPanel, wx.ID_ANY, wx.EmptyString, wx.DefaultPosition, wx.DefaultSize, fontComboBoxChoices, wx.CB_READONLY )
        guiFlexSizer.Add( self.fontComboBox, 0, wx.ALL|wx.LEFT|wx.RIGHT, 5 )

        self.scaleText = wx.StaticText( self.guiPanel, wx.ID_ANY, u"Scale:", wx.DefaultPosition, wx.DefaultSize, 0 )
        self.scaleText.Wrap( -1 )

        guiFlexSizer.Add( self.scaleText, 0, wx.ALIGN_CENTER_VERTICAL|wx.ALL, 5 )

        self.scaleSpinCtrl = wx.SpinCtrlDouble( self.guiPanel, wx.ID_ANY, wx.EmptyString, wx.DefaultPosition, wx.DefaultSize, wx.SP_ARROW_KEYS, 0, 1, 0.04, 0.01 )
        self.scaleSpinCtrl.SetDigits( 0 )
        guiFlexSizer.Add( self.scaleSpinCtrl, 0, wx.ALL, 5 )

        self.verticalAlignText = wx.StaticText( self.guiPanel, wx.ID_ANY, u"Vertical Align:", wx.DefaultPosition, wx.DefaultSize, 0 )
        self.verticalAlignText.Wrap( -1 )

        guiFlexSizer.Add( self.verticalAlignText, 0, wx.ALIGN_CENTER_VERTICAL|wx.ALL, 5 )

        verticalAlignComboBoxChoices = [ u"Top", u"Center", u"Bottom" ]
        self.verticalAlignComboBox = wx.ComboBox( self.guiPanel, wx.ID_ANY, u"Center", wx.DefaultPosition, wx.DefaultSize, verticalAlignComboBoxChoices, wx.CB_READONLY )
        guiFlexSizer.Add( self.verticalAlignComboBox, 0, wx.ALL, 5 )

        self.horizontalAlignText = wx.StaticText( self.guiPanel, wx.ID_ANY, u"Horizontal Align:", wx.DefaultPosition, wx.DefaultSize, 0 )
        self.horizontalAlignText.Wrap( -1 )

        guiFlexSizer.Add( self.horizontalAlignText, 0, wx.ALIGN_CENTER_VERTICAL|wx.ALL, 5 )

        horizontalAlignComboBoxChoices = [ u"Left", u"Center", u"Right" ]
        self.horizontalAlignComboBox = wx.ComboBox( self.guiPanel, wx.ID_ANY, u"Center", wx.DefaultPosition, wx.DefaultSize, horizontalAlignComboBoxChoices, wx.CB_READONLY )
        guiFlexSizer.Add( self.horizontalAlignComboBox, 0, wx.ALL, 5 )


        guiSizer.Add( guiFlexSizer, 1, wx.EXPAND, 5 )

        self.createButton = wx.Button( self.guiPanel, wx.ID_ANY, u"Create!", wx.DefaultPosition, wx.DefaultSize, 0 )
        guiSizer.Add( self.createButton, 0, wx.ALL|wx.EXPAND, 5 )


        self.guiPanel.SetSizer( guiSizer )
        self.guiPanel.Layout()
        guiSizer.Fit( self.guiPanel )
        self.notebook.AddPage( self.guiPanel, u"GUI", True )
        self.cmdLinePanel = wx.Panel( self.notebook, wx.ID_ANY, wx.DefaultPosition, wx.DefaultSize, wx.TAB_TRAVERSAL )
        cmdLineSizer = wx.BoxSizer( wx.VERTICAL )

        cmdLineLabelSizer = wx.BoxSizer( wx.HORIZONTAL )

        self.cmdLineLabel = wx.StaticText( self.cmdLinePanel, wx.ID_ANY, u"cmd", wx.DefaultPosition, wx.DefaultSize, 0 )
        self.cmdLineLabel.Wrap( -1 )

        cmdLineLabelSizer.Add( self.cmdLineLabel, 0, wx.ALIGN_CENTER_VERTICAL|wx.ALL, 5 )

        self.cmdLineEdit = wx.TextCtrl( self.cmdLinePanel, wx.ID_ANY, wx.EmptyString, wx.DefaultPosition, wx.DefaultSize, wx.TE_PROCESS_ENTER )
        cmdLineLabelSizer.Add( self.cmdLineEdit, 1, wx.ALL|wx.EXPAND, 5 )


        cmdLineSizer.Add( cmdLineLabelSizer, 1, wx.EXPAND, 5 )

        cmdLineHelpSizer = wx.BoxSizer( wx.VERTICAL )

        self.cmdLineHelpLabel = wx.StaticText( self.cmdLinePanel, wx.ID_ANY, u"Press Enter to Create Label", wx.DefaultPosition, wx.DefaultSize, 0 )
        self.cmdLineHelpLabel.Wrap( -1 )

        cmdLineHelpSizer.Add( self.cmdLineHelpLabel, 1, wx.ALIGN_CENTER|wx.ALL, 5 )


        cmdLineSizer.Add( cmdLineHelpSizer, 1, wx.EXPAND, 5 )


        self.cmdLinePanel.SetSizer( cmdLineSizer )
        self.cmdLinePanel.Layout()
        cmdLineSizer.Fit( self.cmdLinePanel )
        self.notebook.AddPage( self.cmdLinePanel, u"Command Line", False )

        dialogSizer.Add( self.notebook, 1, wx.EXPAND |wx.ALL, 5 )


        self.SetSizer( dialogSizer )
        self.Layout()

        self.Centre( wx.BOTH )

        # Connect Events
        self.labelEdit.Bind( wx.EVT_TEXT_ENTER, self.labelEditOnTextEnter )
        self.createButton.Bind( wx.EVT_BUTTON, self.createButtonOnButtonClick )
        self.cmdLineEdit.Bind( wx.EVT_TEXT_ENTER, self.cmdLineEditOnTextEnter )

    def __del__( self ):
        pass


    # Virtual event handlers, overide them in your derived class
    def labelEditOnTextEnter( self, event ):
        pass

    def createButtonOnButtonClick( self, event ):
        pass

    def cmdLineEditOnTextEnter( self, event ):
        pass


