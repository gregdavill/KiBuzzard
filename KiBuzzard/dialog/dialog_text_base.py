# -*- coding: utf-8 -*-

###########################################################################
## Python code generated with wxFormBuilder (version 3.9.0 Jan 11 2021)
## http://www.wxformbuilder.org/
##
## PLEASE DO *NOT* EDIT THIS FILE!
###########################################################################

import wx
import wx.xrc
import wx.stc

import gettext
_ = gettext.gettext

###########################################################################
## Class DIALOG_TEXT_BASE
###########################################################################

class DIALOG_TEXT_BASE ( wx.Dialog ):

    def __init__( self, parent ):
        wx.Dialog.__init__ ( self, parent, id = wx.ID_ANY, title = _(u"KiBuzzard Text Properties"), pos = wx.DefaultPosition, size = wx.Size( -1,-1 ), style = wx.DEFAULT_DIALOG_STYLE|wx.RESIZE_BORDER|wx.SYSTEM_MENU )

        self.SetSizeHints( wx.Size( -1,-1 ), wx.DefaultSize )

        bMainSizer = wx.BoxSizer( wx.VERTICAL )

        m_MultiLineSizer = wx.BoxSizer( wx.VERTICAL )

        self.textLabel = wx.StaticText( self, wx.ID_ANY, _(u"Text:"), wx.DefaultPosition, wx.DefaultSize, 0 )
        self.textLabel.Wrap( -1 )

        m_MultiLineSizer.Add( self.textLabel, 0, wx.RIGHT|wx.LEFT, 5 )

        self.m_MultiLineText = wx.stc.StyledTextCtrl( self, wx.ID_ANY, wx.DefaultPosition, wx.DefaultSize, 0)
        self.m_MultiLineText.SetUseTabs ( True )
        self.m_MultiLineText.SetTabWidth ( 4 )
        self.m_MultiLineText.SetIndent ( 4 )
        self.m_MultiLineText.SetTabIndents( False )
        self.m_MultiLineText.SetBackSpaceUnIndents( False )
        self.m_MultiLineText.SetViewEOL( False )
        self.m_MultiLineText.SetViewWhiteSpace( False )
        self.m_MultiLineText.SetMarginWidth( 2, 0 )
        self.m_MultiLineText.SetIndentationGuides( True )
        self.m_MultiLineText.SetReadOnly( False );
        self.m_MultiLineText.SetMarginWidth( 1, 0 )
        self.m_MultiLineText.SetMarginWidth ( 0, 0 )
        self.m_MultiLineText.MarkerDefine( wx.stc.STC_MARKNUM_FOLDER, wx.stc.STC_MARK_BOXPLUS )
        self.m_MultiLineText.MarkerSetBackground( wx.stc.STC_MARKNUM_FOLDER, wx.BLACK)
        self.m_MultiLineText.MarkerSetForeground( wx.stc.STC_MARKNUM_FOLDER, wx.WHITE)
        self.m_MultiLineText.MarkerDefine( wx.stc.STC_MARKNUM_FOLDEROPEN, wx.stc.STC_MARK_BOXMINUS )
        self.m_MultiLineText.MarkerSetBackground( wx.stc.STC_MARKNUM_FOLDEROPEN, wx.BLACK )
        self.m_MultiLineText.MarkerSetForeground( wx.stc.STC_MARKNUM_FOLDEROPEN, wx.WHITE )
        self.m_MultiLineText.MarkerDefine( wx.stc.STC_MARKNUM_FOLDERSUB, wx.stc.STC_MARK_EMPTY )
        self.m_MultiLineText.MarkerDefine( wx.stc.STC_MARKNUM_FOLDEREND, wx.stc.STC_MARK_BOXPLUS )
        self.m_MultiLineText.MarkerSetBackground( wx.stc.STC_MARKNUM_FOLDEREND, wx.BLACK )
        self.m_MultiLineText.MarkerSetForeground( wx.stc.STC_MARKNUM_FOLDEREND, wx.WHITE )
        self.m_MultiLineText.MarkerDefine( wx.stc.STC_MARKNUM_FOLDEROPENMID, wx.stc.STC_MARK_BOXMINUS )
        self.m_MultiLineText.MarkerSetBackground( wx.stc.STC_MARKNUM_FOLDEROPENMID, wx.BLACK)
        self.m_MultiLineText.MarkerSetForeground( wx.stc.STC_MARKNUM_FOLDEROPENMID, wx.WHITE)
        self.m_MultiLineText.MarkerDefine( wx.stc.STC_MARKNUM_FOLDERMIDTAIL, wx.stc.STC_MARK_EMPTY )
        self.m_MultiLineText.MarkerDefine( wx.stc.STC_MARKNUM_FOLDERTAIL, wx.stc.STC_MARK_EMPTY )
        self.m_MultiLineText.SetSelBackground( True, wx.SystemSettings.GetColour(wx.SYS_COLOUR_HIGHLIGHT ) )
        self.m_MultiLineText.SetSelForeground( True, wx.SystemSettings.GetColour(wx.SYS_COLOUR_HIGHLIGHTTEXT ) )
        self.m_MultiLineText.SetToolTip( _(u"Enter the text placed on selected layer.") )

        m_MultiLineSizer.Add( self.m_MultiLineText, 1, wx.EXPAND|wx.BOTTOM|wx.RIGHT|wx.LEFT, 5 )


        bMainSizer.Add( m_MultiLineSizer, 20, wx.EXPAND|wx.ALL, 10 )

        m_SingleLineSizer = wx.BoxSizer( wx.VERTICAL )

        self.m_PreviewLabel = wx.StaticText( self, wx.ID_ANY, _(u"Preview:"), wx.DefaultPosition, wx.DefaultSize, 0 )
        self.m_PreviewLabel.Wrap( -1 )

        m_SingleLineSizer.Add( self.m_PreviewLabel, 0, wx.LEFT|wx.RIGHT, 5 )

        self.m_PreviewPanel = wx.Panel( self, wx.ID_ANY, wx.DefaultPosition, wx.DefaultSize, wx.TAB_TRAVERSAL )
        m_SingleLineSizer.Add( self.m_PreviewPanel, 1, wx.ALL|wx.EXPAND, 5 )


        bMainSizer.Add( m_SingleLineSizer, 20, wx.EXPAND|wx.BOTTOM|wx.RIGHT|wx.LEFT, 10 )

        fgSizerSetup = wx.FlexGridSizer( 0, 5, 4, 0 )
        fgSizerSetup.AddGrowableCol( 1 )
        fgSizerSetup.AddGrowableCol( 4 )
        fgSizerSetup.SetFlexibleDirection( wx.BOTH )
        fgSizerSetup.SetNonFlexibleGrowMode( wx.FLEX_GROWMODE_SPECIFIED )

        self.m_LayerLabel = wx.StaticText( self, wx.ID_ANY, _(u"Font:"), wx.DefaultPosition, wx.DefaultSize, 0 )
        self.m_LayerLabel.Wrap( -1 )

        fgSizerSetup.Add( self.m_LayerLabel, 0, wx.ALIGN_CENTER_VERTICAL|wx.LEFT|wx.RIGHT, 5 )

        m_FontComboBoxChoices = []
        self.m_FontComboBox = wx.ComboBox( self, wx.ID_ANY, wx.EmptyString, wx.DefaultPosition, wx.DefaultSize, m_FontComboBoxChoices, wx.CB_READONLY )
        fgSizerSetup.Add( self.m_FontComboBox, 0, wx.ALIGN_CENTER_VERTICAL|wx.EXPAND, 5 )


        fgSizerSetup.Add( ( 0, 0), 0, wx.RIGHT|wx.LEFT, 40 )

        self.m_CapLeftLabel = wx.StaticText( self, wx.ID_ANY, _(u"Cap Left:"), wx.DefaultPosition, wx.DefaultSize, 0 )
        self.m_CapLeftLabel.Wrap( -1 )

        fgSizerSetup.Add( self.m_CapLeftLabel, 0, wx.ALIGN_CENTER_VERTICAL|wx.LEFT|wx.RIGHT, 5 )

        m_JustifyChoice1Choices = [ wx.EmptyString, _(u"["), _(u"("), _(u"/"), _(u"\\"), _(u"<"), _(u">") ]
        self.m_JustifyChoice1 = wx.Choice( self, wx.ID_ANY, wx.DefaultPosition, wx.DefaultSize, m_JustifyChoice1Choices, 0 )
        self.m_JustifyChoice1.SetSelection( 0 )
        fgSizerSetup.Add( self.m_JustifyChoice1, 0, wx.ALIGN_CENTER_VERTICAL|wx.EXPAND|wx.RIGHT, 3 )

        self.m_SizeYLabel = wx.StaticText( self, wx.ID_ANY, _(u"Height:"), wx.DefaultPosition, wx.DefaultSize, 0 )
        self.m_SizeYLabel.Wrap( -1 )

        self.m_SizeYLabel.SetToolTip( _(u"Text height") )

        fgSizerSetup.Add( self.m_SizeYLabel, 0, wx.ALIGN_CENTER_VERTICAL|wx.RIGHT|wx.LEFT, 5 )

        self.m_SizeYCtrl = wx.TextCtrl( self, wx.ID_ANY, wx.EmptyString, wx.DefaultPosition, wx.DefaultSize, wx.TE_PROCESS_ENTER )
        self.m_SizeYCtrl.SetMaxLength( 0 )
        fgSizerSetup.Add( self.m_SizeYCtrl, 0, wx.ALIGN_CENTER_VERTICAL|wx.EXPAND, 5 )

        self.m_SizeYUnits = wx.StaticText( self, wx.ID_ANY, _(u"unit"), wx.DefaultPosition, wx.DefaultSize, 0 )
        self.m_SizeYUnits.Wrap( -1 )

        fgSizerSetup.Add( self.m_SizeYUnits, 0, wx.ALIGN_CENTER_VERTICAL|wx.RIGHT|wx.LEFT, 5 )

        self.m_staticText11 = wx.StaticText( self, wx.ID_ANY, _(u"Cap Right:"), wx.DefaultPosition, wx.DefaultSize, 0 )
        self.m_staticText11.Wrap( -1 )

        fgSizerSetup.Add( self.m_staticText11, 0, wx.ALIGN_CENTER_VERTICAL|wx.RIGHT|wx.LEFT, 5 )

        m_JustifyChoiceChoices = [ wx.EmptyString, _(u"]"), _(u")"), _(u"/"), _(u"\\"), _(u">"), _(u"<") ]
        self.m_JustifyChoice = wx.Choice( self, wx.ID_ANY, wx.DefaultPosition, wx.DefaultSize, m_JustifyChoiceChoices, 0 )
        self.m_JustifyChoice.SetSelection( 0 )
        fgSizerSetup.Add( self.m_JustifyChoice, 0, wx.ALIGN_CENTER_VERTICAL|wx.EXPAND|wx.RIGHT, 3 )

        self.m_ThicknessLabel = wx.StaticText( self, wx.ID_ANY, _(u"Thickness:"), wx.DefaultPosition, wx.DefaultSize, 0 )
        self.m_ThicknessLabel.Wrap( -1 )

        self.m_ThicknessLabel.SetToolTip( _(u"Text thickness") )

        fgSizerSetup.Add( self.m_ThicknessLabel, 0, wx.ALIGN_CENTER_VERTICAL|wx.RIGHT|wx.LEFT, 5 )

        self.m_ThicknessCtrl = wx.TextCtrl( self, wx.ID_ANY, wx.EmptyString, wx.DefaultPosition, wx.DefaultSize, wx.TE_PROCESS_ENTER )
        self.m_ThicknessCtrl.SetMaxLength( 0 )
        self.m_ThicknessCtrl.Enable( False )

        fgSizerSetup.Add( self.m_ThicknessCtrl, 0, wx.ALIGN_CENTER_VERTICAL|wx.EXPAND, 2 )

        self.m_ThicknessUnits = wx.StaticText( self, wx.ID_ANY, _(u"unit"), wx.DefaultPosition, wx.DefaultSize, 0 )
        self.m_ThicknessUnits.Wrap( -1 )

        fgSizerSetup.Add( self.m_ThicknessUnits, 0, wx.ALIGN_CENTER_VERTICAL|wx.RIGHT|wx.LEFT, 5 )


        fgSizerSetup.Add( ( 0, 0), 1, wx.EXPAND, 5 )


        fgSizerSetup.Add( ( 0, 0), 1, wx.EXPAND, 5 )


        bMainSizer.Add( fgSizerSetup, 0, wx.EXPAND|wx.RIGHT|wx.LEFT, 10 )


        bMainSizer.Add( ( 0, 0), 0, wx.TOP, 5 )

        self.m_staticline = wx.StaticLine( self, wx.ID_ANY, wx.DefaultPosition, wx.DefaultSize, wx.LI_HORIZONTAL )
        bMainSizer.Add( self.m_staticline, 0, wx.EXPAND|wx.TOP|wx.RIGHT|wx.LEFT, 10 )

        lowerSizer = wx.BoxSizer( wx.HORIZONTAL )


        lowerSizer.Add( ( 0, 0), 1, wx.EXPAND, 5 )

        m_sdbSizer = wx.StdDialogButtonSizer()
        self.m_sdbSizerOK = wx.Button( self, wx.ID_OK )
        m_sdbSizer.AddButton( self.m_sdbSizerOK )
        self.m_sdbSizerCancel = wx.Button( self, wx.ID_CANCEL )
        m_sdbSizer.AddButton( self.m_sdbSizerCancel )
        m_sdbSizer.Realize();

        lowerSizer.Add( m_sdbSizer, 0, wx.ALL, 5 )


        bMainSizer.Add( lowerSizer, 0, wx.EXPAND, 5 )


        self.SetSizer( bMainSizer )
        self.Layout()
        bMainSizer.Fit( self )

        self.Centre( wx.BOTH )

        # Connect Events
        self.Bind( wx.EVT_INIT_DIALOG, self.OnInitDlg )
        self.m_SizeYCtrl.Bind( wx.EVT_TEXT_ENTER, self.OnOkClick )
        self.m_ThicknessCtrl.Bind( wx.EVT_TEXT_ENTER, self.OnOkClick )
        self.m_sdbSizerOK.Bind( wx.EVT_BUTTON, self.OnOkClick )

    def __del__( self ):
        pass


    # Virtual event handlers, overide them in your derived class
    def OnInitDlg( self, event ):
        pass

    def OnOkClick( self, event ):
        pass




