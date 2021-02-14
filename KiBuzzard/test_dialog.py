#!/usr/bin/env python
from dialog.dialog import *
from buzzard.buzzard import Buzzard

from wx import FileConfig

class MyApp(wx.App):
    def OnInit(self):

        config_file = os.path.join(os.path.dirname(__file__), '..', 'config.ini')
        config = FileConfig(localFilename=config_file)

        frame = Dialog(None, config, Buzzard(), lambda: None)
        if frame.ShowModal() == wx.ID_OK:
            print("Should generate bom")
        frame.Destroy()
        return True


app = MyApp()
app.MainLoop()

print("Done")
