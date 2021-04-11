#!/usr/bin/env python
from dialog.dialog import *
from buzzard.buzzard import Buzzard

from wx import FileConfig

import sys
import subprocess

class MyApp(wx.App):
    def OnInit(self):

        config_file = os.path.join(os.path.dirname(__file__), '..', 'config.ini')
        config = FileConfig(localFilename=config_file)

        self.frame = frame = Dialog(None, config, Buzzard(), self.run)
        if frame.ShowModal() == wx.ID_OK:
            print("Graceful Exit")
        frame.Destroy()
        return True

    def run(self, footprint_string):
        # Copy footprint into clipboard
        if sys.platform.startswith('linux'):
            clip_args = ['xclip', '-sel', 'clip', '-noutf8']
        elif sys.platform == 'darwin':
            clip_args = ['pbcopy']
        else:
            clip_args = ['clip.exe']

        process = subprocess.Popen(clip_args, stdin=subprocess.PIPE)
        process.communicate(footprint_string.encode('ascii'))
        
        self.frame.EndModal(wx.ID_OK)


app = MyApp()
app.MainLoop()

print("Done")
