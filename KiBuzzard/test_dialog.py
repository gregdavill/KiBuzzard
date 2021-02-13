#!/usr/bin/env python

#from buzzard import string2paths, renderLabel, drawSVG

from buzzard.buzzard import Buzzard
import argparse

import copy

import wx


class KiBuzzardDialog ( wx.Dialog ):

    def __init__( self, parent ):
        wx.Dialog.__init__ ( self, parent, id = wx.ID_ANY, title = u"KiBuzzard", pos = wx.DefaultPosition, size = wx.Size( 420,352 ), style = wx.CLOSE_BOX|wx.DEFAULT_DIALOG_STYLE|wx.RESIZE_BORDER )

        self.SetSizeHints( wx.Size( 420,280 ), wx.DefaultSize )

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


class Example(KiBuzzardDialog):

    def __init__(self, *args, **kw):
        KiBuzzardDialog.__init__(self, None)
        self.buzzard = Buzzard()

        self.polys = []

        self.InitUI()

        

    def InitUI(self):

        #wx.CallLater(2000, self.DrawLine)

        self.SetTitle("Interactive Label Maker?")
        self.Centre()

        self.Bind(wx.EVT_PAINT, self.OnPaint)

    def labelEditOnText( self, event ):
        ...
        self.polys = []
        
        try:
            self.polys = self.buzzard.generate(self.labelEdit.GetValue())

        except Exception as e:
            print(e)
            # Todo display error messages

        self.Layout()
        self.Refresh()
        self.Update()

    def OnPaint(self, e):

        dc = wx.PaintDC(self)
        dc.SetPen(wx.Pen('#000000', width=2))

        size_x, size_y = self.m_panel3.DoGetSize()
        position_x, position_y = self.m_panel3.DoGetPosition()


        dc.SetDeviceOrigin(int(position_x + size_x/2), int((position_y + size_y)/2))

        dc.SetBrush(wx.Brush('#000000'))


        if len(self.polys):

            min_x = 0
            max_x = 0

            for i in range(len(self.polys)):
                for j in range(len(self.polys[i])):
                    min_x = min(self.polys[i][j][0], min_x)
                    max_x = max(self.polys[i][j][0], max_x)

            print(min_x, max_x)

            print(max_x - min_x)

            size_x, _ = self.m_panel3.DoGetSize()

            scale = (size_x * 0.95) / (max_x - min_x)
            

            polys = copy.deepcopy(self.polys)
            # Scale
            scale = min(60.0, scale)
            print('scale:', scale)
            for i in range(len(polys)):
                for j in range(len(polys[i])):
                    polys[i][j] = (scale*polys[i][j][0],scale*polys[i][j][1])



            dc.DrawPolygonList(polys)
        


def main():

    
    
    app = wx.App()
    ex = Example(None)
    ex.ShowModal()
    app.MainLoop()


if __name__ == '__main__':

    main()