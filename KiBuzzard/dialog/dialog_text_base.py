# -*- coding: utf-8 -*-

###########################################################################
## Python code generated with wxFormBuilder (version 3.10.1-0-g8feb16b3)
## http://www.wxformbuilder.org/
##
## PLEASE DO *NOT* EDIT THIS FILE!
###########################################################################

from .compat import DialogShim
import wx
import wx.xrc
import wx.stc

import gettext
_ = gettext.gettext

###########################################################################
## Class DIALOG_TEXT_BASE
###########################################################################

class DIALOG_TEXT_BASE ( DialogShim ):

    def __init__( self, parent ):
        DialogShim.__init__ ( self, parent, id = wx.ID_ANY, title = _(u"KiBuzzard Text Properties"), pos = wx.DefaultPosition, size = wx.Size( -1,-1 ), style = wx.DEFAULT_DIALOG_STYLE|wx.RESIZE_BORDER|wx.SYSTEM_MENU )

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

        self.m_FontLabel = wx.StaticText( self, wx.ID_ANY, _(u"Font:"), wx.DefaultPosition, wx.DefaultSize, 0 )
        self.m_FontLabel.Wrap( -1 )

        fgSizerSetup.Add( self.m_FontLabel, 0, wx.ALIGN_CENTER_VERTICAL|wx.LEFT|wx.RIGHT, 5 )

        m_FontComboBoxChoices = []
        self.m_FontComboBox = wx.ComboBox( self, wx.ID_ANY, wx.EmptyString, wx.DefaultPosition, wx.DefaultSize, m_FontComboBoxChoices, wx.CB_READONLY )
        fgSizerSetup.Add( self.m_FontComboBox, 2, wx.ALIGN_CENTER_VERTICAL|wx.EXPAND, 5 )


        fgSizerSetup.Add( ( 0, 0), 0, wx.RIGHT|wx.LEFT, 40 )

        self.m_CapLeftLabel = wx.StaticText( self, wx.ID_ANY, _(u"Cap Left:"), wx.DefaultPosition, wx.DefaultSize, 0 )
        self.m_CapLeftLabel.Wrap( -1 )

        fgSizerSetup.Add( self.m_CapLeftLabel, 0, wx.ALIGN_CENTER_VERTICAL|wx.LEFT|wx.RIGHT, 5 )

        m_CapLeftChoiceChoices = [ wx.EmptyString, _(u"["), _(u"("), _(u"/"), _(u"\\"), _(u"<"), _(u">") ]
        self.m_CapLeftChoice = wx.Choice( self, wx.ID_ANY, wx.DefaultPosition, wx.DefaultSize, m_CapLeftChoiceChoices, 0 )
        self.m_CapLeftChoice.SetSelection( 0 )
        fgSizerSetup.Add( self.m_CapLeftChoice, 1, wx.ALIGN_CENTER_VERTICAL|wx.EXPAND|wx.RIGHT, 3 )

        self.m_HeightLabel = wx.StaticText( self, wx.ID_ANY, _(u"Height:"), wx.DefaultPosition, wx.DefaultSize, 0 )
        self.m_HeightLabel.Wrap( -1 )

        fgSizerSetup.Add( self.m_HeightLabel, 0, wx.ALIGN_CENTER_VERTICAL|wx.RIGHT|wx.LEFT, 5 )

        self.m_HeightCtrl = wx.TextCtrl( self, wx.ID_ANY, wx.EmptyString, wx.DefaultPosition, wx.DefaultSize, wx.TE_PROCESS_ENTER )
        self.m_HeightCtrl.SetMaxLength( 0 )
        fgSizerSetup.Add( self.m_HeightCtrl, 0, wx.ALIGN_CENTER_VERTICAL|wx.EXPAND, 5 )

        self.m_HeightUnits = wx.StaticText( self, wx.ID_ANY, _(u"unit"), wx.DefaultPosition, wx.DefaultSize, 0 )
        self.m_HeightUnits.Wrap( -1 )

        fgSizerSetup.Add( self.m_HeightUnits, 0, wx.ALIGN_CENTER_VERTICAL|wx.RIGHT|wx.LEFT, 5 )

        self.m_CapRightLabel = wx.StaticText( self, wx.ID_ANY, _(u"Cap Right:"), wx.DefaultPosition, wx.DefaultSize, 0 )
        self.m_CapRightLabel.Wrap( -1 )

        fgSizerSetup.Add( self.m_CapRightLabel, 0, wx.ALIGN_CENTER_VERTICAL|wx.RIGHT|wx.LEFT, 5 )

        m_CapRightChoiceChoices = [ wx.EmptyString, _(u"]"), _(u")"), _(u"/"), _(u"\\"), _(u">"), _(u"<") ]
        self.m_CapRightChoice = wx.Choice( self, wx.ID_ANY, wx.DefaultPosition, wx.DefaultSize, m_CapRightChoiceChoices, 0 )
        self.m_CapRightChoice.SetSelection( 0 )
        fgSizerSetup.Add( self.m_CapRightChoice, 0, wx.ALIGN_CENTER_VERTICAL|wx.EXPAND|wx.RIGHT, 3 )

        self.m_WidthLabel = wx.StaticText( self, wx.ID_ANY, _(u"Width:"), wx.DefaultPosition, wx.DefaultSize, 0 )
        self.m_WidthLabel.Wrap( -1 )

        fgSizerSetup.Add( self.m_WidthLabel, 0, wx.ALIGN_CENTER_VERTICAL|wx.LEFT|wx.RIGHT, 5 )

        self.m_WidthCtrl = wx.TextCtrl( self, wx.ID_ANY, wx.EmptyString, wx.DefaultPosition, wx.DefaultSize, wx.TE_PROCESS_ENTER )
        self.m_WidthCtrl.SetMaxLength( 0 )
        fgSizerSetup.Add( self.m_WidthCtrl, 0, wx.ALIGN_CENTER_VERTICAL|wx.EXPAND, 5 )

        self.m_WidthUnits = wx.StaticText( self, wx.ID_ANY, _(u"unit"), wx.DefaultPosition, wx.DefaultSize, 0 )
        self.m_WidthUnits.Wrap( -1 )

        fgSizerSetup.Add( self.m_WidthUnits, 0, wx.ALIGN_CENTER_VERTICAL|wx.LEFT|wx.RIGHT, 5 )

        self.m_AlignmentLabel = wx.StaticText( self, wx.ID_ANY, _(u"Alignment:"), wx.DefaultPosition, wx.DefaultSize, 0 )
        self.m_AlignmentLabel.Wrap( -1 )

        fgSizerSetup.Add( self.m_AlignmentLabel, 0, wx.ALIGN_CENTER_VERTICAL|wx.LEFT|wx.RIGHT, 5 )

        m_AlignmentChoiceChoices = [ _(u"Left"), _(u"Center"), _(u"Right") ]
        self.m_AlignmentChoice = wx.Choice( self, wx.ID_ANY, wx.DefaultPosition, wx.DefaultSize, m_AlignmentChoiceChoices, 0 )
        self.m_AlignmentChoice.SetSelection( 0 )
        fgSizerSetup.Add( self.m_AlignmentChoice, 0, wx.ALIGN_CENTER_VERTICAL|wx.EXPAND|wx.RIGHT, 3 )


        fgSizerSetup.Add( ( 0, 0), 0, wx.EXPAND, 5 )


        fgSizerSetup.Add( ( 0, 0), 1, wx.EXPAND, 5 )


        fgSizerSetup.Add( ( 0, 0), 1, wx.EXPAND, 5 )

        self.m_LayerComboBox1 = wx.StaticText( self, wx.ID_ANY, _(u"Layer:"), wx.DefaultPosition, wx.DefaultSize, 0 )
        self.m_LayerComboBox1.Wrap( -1 )

        fgSizerSetup.Add( self.m_LayerComboBox1, 0, wx.ALIGN_CENTER_VERTICAL|wx.LEFT|wx.RIGHT, 5 )

        m_LayerComboBoxChoices = []
        self.m_LayerComboBox = wx.ComboBox( self, wx.ID_ANY, wx.EmptyString, wx.DefaultPosition, wx.DefaultSize, m_LayerComboBoxChoices, 0 )
        fgSizerSetup.Add( self.m_LayerComboBox, 0, wx.ALIGN_CENTER_VERTICAL|wx.EXPAND, 5 )


        bMainSizer.Add( fgSizerSetup, 0, wx.EXPAND|wx.RIGHT|wx.LEFT, 10 )


        bMainSizer.Add( ( 0, 0), 0, wx.TOP, 5 )

        self.m_staticline1 = wx.StaticLine( self, wx.ID_ANY, wx.DefaultPosition, wx.DefaultSize, wx.LI_HORIZONTAL )
        bMainSizer.Add( self.m_staticline1, 0, wx.BOTTOM|wx.EXPAND|wx.LEFT|wx.RIGHT, 5 )

        fgSizerPadding = wx.FlexGridSizer( 0, 6, 4, 4 )
        fgSizerPadding.AddGrowableCol( 1 )
        fgSizerPadding.AddGrowableCol( 2 )
        fgSizerPadding.AddGrowableCol( 3 )
        fgSizerPadding.AddGrowableCol( 4 )
        fgSizerPadding.SetFlexibleDirection( wx.BOTH )
        fgSizerPadding.SetNonFlexibleGrowMode( wx.FLEX_GROWMODE_SPECIFIED )

        self.m_PaddingLabel = wx.StaticText( self, wx.ID_ANY, _(u"Padding:"), wx.DefaultPosition, wx.DefaultSize, 0 )
        self.m_PaddingLabel.Wrap( -1 )

        fgSizerPadding.Add( self.m_PaddingLabel, 0, wx.ALIGN_CENTER_VERTICAL|wx.LEFT|wx.RIGHT, 5 )

        self.m_PaddingTopLabel = wx.StaticText( self, wx.ID_ANY, _(u"Top"), wx.DefaultPosition, wx.DefaultSize, 0 )
        self.m_PaddingTopLabel.Wrap( -1 )

        fgSizerPadding.Add( self.m_PaddingTopLabel, 1, wx.ALIGN_CENTER, 5 )

        self.m_PaddingLeftLabel = wx.StaticText( self, wx.ID_ANY, _(u"Left"), wx.DefaultPosition, wx.DefaultSize, 0 )
        self.m_PaddingLeftLabel.Wrap( -1 )

        fgSizerPadding.Add( self.m_PaddingLeftLabel, 1, wx.ALIGN_CENTER, 5 )

        self.m_PaddingRightLabel = wx.StaticText( self, wx.ID_ANY, _(u"Right"), wx.DefaultPosition, wx.DefaultSize, 0 )
        self.m_PaddingRightLabel.Wrap( -1 )

        fgSizerPadding.Add( self.m_PaddingRightLabel, 1, wx.ALIGN_CENTER, 5 )

        self.m_PaddingBottomLabel = wx.StaticText( self, wx.ID_ANY, _(u"Bottom"), wx.DefaultPosition, wx.DefaultSize, 0 )
        self.m_PaddingBottomLabel.Wrap( -1 )

        fgSizerPadding.Add( self.m_PaddingBottomLabel, 1, wx.ALIGN_CENTER, 5 )


        fgSizerPadding.Add( ( 0, 0), 1, wx.EXPAND, 5 )


        fgSizerPadding.Add( ( 0, 0), 1, wx.EXPAND, 5 )

        self.m_PaddingTopCtrl = wx.TextCtrl( self, wx.ID_ANY, wx.EmptyString, wx.DefaultPosition, wx.DefaultSize, wx.TE_PROCESS_ENTER )
        self.m_PaddingTopCtrl.SetMaxLength( 0 )
        self.m_PaddingTopCtrl.SetMinSize( wx.Size( 64,-1 ) )

        fgSizerPadding.Add( self.m_PaddingTopCtrl, 1, wx.ALIGN_CENTER_VERTICAL|wx.EXPAND, 5 )

        self.m_PaddingLeftCtrl = wx.TextCtrl( self, wx.ID_ANY, wx.EmptyString, wx.DefaultPosition, wx.DefaultSize, wx.TE_PROCESS_ENTER )
        self.m_PaddingLeftCtrl.SetMaxLength( 0 )
        self.m_PaddingLeftCtrl.SetMinSize( wx.Size( 64,-1 ) )

        fgSizerPadding.Add( self.m_PaddingLeftCtrl, 1, wx.ALIGN_CENTER_VERTICAL|wx.EXPAND, 5 )

        self.m_PaddingRightCtrl = wx.TextCtrl( self, wx.ID_ANY, wx.EmptyString, wx.DefaultPosition, wx.DefaultSize, wx.TE_PROCESS_ENTER )
        self.m_PaddingRightCtrl.SetMaxLength( 0 )
        self.m_PaddingRightCtrl.SetMinSize( wx.Size( 64,-1 ) )

        fgSizerPadding.Add( self.m_PaddingRightCtrl, 1, wx.ALIGN_CENTER_VERTICAL|wx.EXPAND, 5 )

        self.m_PaddingBottomCtrl = wx.TextCtrl( self, wx.ID_ANY, wx.EmptyString, wx.DefaultPosition, wx.DefaultSize, wx.TE_PROCESS_ENTER )
        self.m_PaddingBottomCtrl.SetMaxLength( 0 )
        self.m_PaddingBottomCtrl.SetMinSize( wx.Size( 64,-1 ) )

        fgSizerPadding.Add( self.m_PaddingBottomCtrl, 1, wx.ALIGN_CENTER_VERTICAL|wx.EXPAND, 5 )

        self.m_PaddingUnits = wx.StaticText( self, wx.ID_ANY, _(u"unit"), wx.DefaultPosition, wx.DefaultSize, 0 )
        self.m_PaddingUnits.Wrap( -1 )

        fgSizerPadding.Add( self.m_PaddingUnits, 0, wx.ALIGN_CENTER_VERTICAL|wx.RIGHT|wx.LEFT, 5 )


        bMainSizer.Add( fgSizerPadding, 0, wx.EXPAND|wx.LEFT|wx.RIGHT, 10 )

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
        self.m_MultiLineText.Bind( wx.EVT_CHAR_HOOK, self.OnCharHook )
        self.m_HeightCtrl.Bind( wx.EVT_TEXT_ENTER, self.OnOkClick )
        self.m_WidthCtrl.Bind( wx.EVT_TEXT_ENTER, self.OnOkClick )
        self.m_PaddingTopCtrl.Bind( wx.EVT_TEXT_ENTER, self.OnOkClick )
        self.m_PaddingLeftCtrl.Bind( wx.EVT_TEXT_ENTER, self.OnOkClick )
        self.m_PaddingRightCtrl.Bind( wx.EVT_TEXT_ENTER, self.OnOkClick )
        self.m_PaddingBottomCtrl.Bind( wx.EVT_TEXT_ENTER, self.OnOkClick )
        self.m_sdbSizerOK.Bind( wx.EVT_BUTTON, self.OnOkClick )

    def __del__( self ):
        pass


    # Virtual event handlers, override them in your derived class
    def OnInitDlg( self, event ):
        pass

    def OnCharHook( self, event ):
        pass

    def OnOkClick( self, event ):
        pass








