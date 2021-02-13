#!/usr/bin/env python

#from buzzard import string2paths, renderLabel, drawSVG

from buzzard.buzzard import Buzzard
from dialog.dialog_base import KiBuzzardDialog
import argparse

import copy

import wx

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


            size_x, _ = self.m_panel3.DoGetSize()

            scale = (size_x * 0.95) / (max_x - min_x)
            

            # Create copy of poly list for scaling preview
            polys = copy.deepcopy(self.polys)

            # Scale
            scale = min(60.0, scale)


            #print(min_x, max_x)
            #print(max_x - min_x)
            #print('scale:', scale)
            
            
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