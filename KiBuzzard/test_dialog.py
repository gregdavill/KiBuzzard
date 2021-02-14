#!/usr/bin/env python
from dialog.dialog import *
from buzzard.buzzard import Buzzard

from wx import FileConfig

class MyApp(wx.App):
    def OnInit(self):

        config_file = os.path.join(os.path.dirname(__file__), '..', 'config.ini')
        config = FileConfig(localFilename=config_file)

        self.frame = frame = Dialog(None, config, Buzzard(), self.run)
        if frame.ShowModal() == wx.ID_OK:
            print("Graceful Exit")
        frame.Destroy()
        return True

    def run(self, str):
        print(str)
        self.frame.EndModal(wx.ID_OK)


app = MyApp()
app.MainLoop()

print("Done")
