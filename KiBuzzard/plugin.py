import os
import sys
import time
import tempfile
import logging
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

        self.InitLogger()
        self.logger = logging.getLogger(__name__)

        self.name = "Create Labels"
        self.category = "Modify PCB"
        self.pcbnew_icon_support = hasattr(self, "show_toolbar_button")
        self.show_toolbar_button = True
        icon_dir = os.path.dirname(os.path.dirname(__file__))
        self.icon_file_name = os.path.join(icon_dir, 'icon.png')
        self.description = "Create Labels"
        self.config = FileConfig(localFilename=self.config_file)
        
        self._pcbnew_frame = None

        self.kicad_build_version = pcbnew.GetBuildVersion()
        if self.IsVersion(['5.0','5.1']):
            # Library location for KiCad 5.1
            self.filepath = os.path.join(tempfile.mkdtemp(), 'buzzard_labels.pretty', 'label.kicad_mod') 
            try: # Use try/except here because python 2.7 doesn't support exist_ok
                os.makedirs(os.path.dirname(self.filepath))
            except:
                pass

    def IsVersion(self, VersionStr):
        for v in VersionStr:
            if v in self.kicad_build_version:
                return True
        return False

    def Run(self):
        if self._pcbnew_frame is None:
            try:
                self._pcbnew_frame = [x for x in wx.GetTopLevelWindows() if ('pcbnew' in x.GetTitle().lower() and not 'python' in x.GetTitle().lower()) or ('pcb editor' in x.GetTitle().lower())]
                if len(self._pcbnew_frame) == 1:
                    self._pcbnew_frame = self._pcbnew_frame[0]
                else:
                    self._pcbnew_frame = None
            except:
                pass

        def run_buzzard(dlg, p_buzzard): 

            if len(dlg.polys) == 0:
                dlg.EndModal(wx.ID_CANCEL)
                return

            if self.IsVersion(['5.1','5.0']):
                # Handle KiCad 5.1
                filepath = self.filepath

                with open(filepath, 'w+') as f:
                    f.write(p_buzzard.create_v5_footprint())

                print(os.path.dirname(filepath))

                board = pcbnew.GetBoard()
                footprint = pcbnew.FootprintLoad(os.path.dirname(filepath), 'label')

                footprint.SetPosition(pcbnew.wxPoint(0, 0))
                board.Add(footprint)
                pcbnew.Refresh()

                # Zoom doesn't seem to work.
                #b = footprint.GetBoundingBox()
                #pcbnew.WindowZoom(b.GetX(), b.GetY(), b.GetWidth(), b.GetHeight())

            elif self.IsVersion(['5.99','6.0', '6.99']):
                footprint_string = p_buzzard.create_v6_footprint()

                clipboard = wx.Clipboard.Get()
                if clipboard.Open():
                    clipboard.SetData(wx.TextDataObject(footprint_string))
                    clipboard.Close()
                    
            dlg.EndModal(wx.ID_OK)

        dlg = Dialog(self._pcbnew_frame, self.config, Buzzard(), run_buzzard)
    
        if dlg.ShowModal() == wx.ID_OK:
            
            if self.IsVersion(['5.99','6.0', '6.99']):
                if self._pcbnew_frame is not None:
                    # Set focus to main window and attempt to execute a Paste operation
                    self._pcbnew_frame.Raise()
                    wx.Yield()
                    keyinput = wx.UIActionSimulator()
                    
                    # Press and release CTRL + V
                    keyinput.KeyDown(ord("V"), wx.MOD_CONTROL)
                    time.sleep(0.2)
                    keyinput.KeyUp(ord("V"), wx.MOD_CONTROL) 

    def InitLogger(self):
        root = logging.getLogger()
        root.setLevel(logging.DEBUG)

        # Log to stderr
        handler1 = logging.StreamHandler(sys.stderr)
        handler1.setLevel(logging.DEBUG)

        log_file = os.path.join(os.path.dirname(__file__), "..", "kibuzzard.log")

        # and to our error file
        handler2 = logging.FileHandler(log_file)
        handler2.setLevel(logging.DEBUG)
        formatter = logging.Formatter(
            "%(asctime)s %(name)s %(lineno)d:%(message)s", datefmt="%m-%d %H:%M:%S"
        )
        handler1.setFormatter(formatter)
        handler2.setFormatter(formatter)
        root.addHandler(handler1)
        root.addHandler(handler2)
