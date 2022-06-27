#!/usr/bin/env python

import os
from util import add_paths
dir_path = os.path.dirname(os.path.realpath(__file__))
paths = [
    os.path.join(dir_path, 'deps'), 
    os.path.join(dir_path, 'deps', 'fonttools', 'Lib'), 
    os.path.join(dir_path, 'deps', 'svg2mod')
]


with add_paths(paths):
    from dialog.dialog import *
    from buzzard.buzzard import Buzzard


from wx import FileConfig

import sys
import subprocess


class MyApp(wx.App):
    def OnInit(self):

        config_file = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'config.json')
        
        self.frame = frame = Dialog(None, config_file, Buzzard(), self.run)
        if frame.ShowModal() == wx.ID_OK:
            print("Graceful Exit")
        frame.Destroy()
        return True

    def run(self, footprint_string, dlg):

        self.frame.EndModal(wx.ID_OK)


app = MyApp()
app.MainLoop()

print("Done")