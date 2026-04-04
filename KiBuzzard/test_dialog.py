#!/usr/bin/env python
from dialog.dialog import *
from buzzard.buzzard import Buzzard

from wx import FileConfig

import sys
import subprocess

class MyApp(wx.App):
    def OnInit(self):

        config_file = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'config.ini')
        config = FileConfig(localFilename=config_file)

        print(config_file)

        def text_expander(text) -> str:
            if not text:
                return text
            return text.replace(r'${TEST_EXP}', 'EXPANSION')

        self.frame = frame = Dialog(None, config, Buzzard(), self.run, text_expander)
        if frame.ShowModal() == wx.ID_OK:
            print("Graceful Exit")
        frame.Destroy()
        return True

    def run(self, footprint_string, dlg):

        self.frame.EndModal(wx.ID_OK)


app = MyApp()
app.MainLoop()

print("Done")