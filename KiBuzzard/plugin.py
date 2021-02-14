import os

import wx
import wx.aui
from wx import FileConfig

import pcbnew
from .dialog import Dialog

from .buzzard.buzzard import Buzzard

class KiBuzzardPlugin(pcbnew.ActionPlugin, object):
    config_file = os.path.join(os.path.dirname(__file__), '..', 'config.ini')

    def __init__(self):
        super(KiBuzzardPlugin, self).__init__()
        self.name = "Create Labels"
        self.category = "Modify PCB"
        self.pcbnew_icon_support = hasattr(self, "show_toolbar_button")
        self.show_toolbar_button = True
        icon_dir = os.path.dirname(os.path.dirname(__file__))
        self.icon_file_name = os.path.join(icon_dir, 'icon.png')
        self.description = "Create Labels"
        self.config = FileConfig(localFilename=self.config_file)
        self._pcbnew_frame = None


    def defaults(self):
        pass

    def Run(self):
        if self._pcbnew_frame is None:
            self._pcbnew_frame = [x for x in wx.GetTopLevelWindows() if 'pcbnew' in x.GetTitle().lower() and not 'python' in x.GetTitle().lower()][0]

        def run_buzzard(str):
                
                dlg.EndModal(wx.ID_OK)

        dlg = Dialog(self._pcbnew_frame, self.config, Buzzard(), run_buzzard)
        try:
            if dlg.ShowModal() == wx.ID_OK:
                # Set focus to main window and execute a Paste operation
                self._pcbnew_frame.Raise()
                wx.Yield()
                keyinput = wx.UIActionSimulator()
                keyinput.Char(ord("V"), wx.MOD_CONTROL)    
        finally:
            self.config.Flush()
            dlg.Destroy()
