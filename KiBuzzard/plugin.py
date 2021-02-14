import os
import sys
import subprocess
import tempfile
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

        self.kicad_build_version = pcbnew.GetBuildVersion()
        if '5.1' in self.kicad_build_version or '5.0' in self.kicad_build_version:
            # Library location for KiCad 5.1
            self.filepath = os.path.join(tempfile.mkdtemp(), 'buzzard_labels.pretty', 'label.kicad_mod') 
            os.makedirs(os.path.dirname(self.filepath), exist_ok=True)

    def defaults(self):
        pass

    def Run(self):
        if self._pcbnew_frame is None:
            self._pcbnew_frame = [x for x in wx.GetTopLevelWindows() if 'pcbnew' in x.GetTitle().lower() and not 'python' in x.GetTitle().lower()][0]

        def run_buzzard(p_buzzard): 

            if '5.1' in self.kicad_build_version or '5.0' in self.kicad_build_version:
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

            elif '5.99' in self.kicad_build_version or '6.0' in self.kicad_build_version:
                footprint_string = p_buzzard.create_v6_footprint()

                # Copy footprint into clipboard
                if sys.platform.startswith('linux'):
                    clip_args = ['xclip', '-sel', 'clip', '-noutf8']
                elif sys.platform == 'darwin':
                    clip_args = ['pbcopy']
                else:
                    clip_args = ['clip.exe']

                process = subprocess.Popen(clip_args, stdin=subprocess.PIPE)
                process.communicate(footprint_string.encode('ascii'))

            dlg.EndModal(wx.ID_OK)

        dlg = Dialog(None, self.config, Buzzard(), run_buzzard)
        try:
            if dlg.ShowModal() == wx.ID_OK:
                
                if '5.99' in self.kicad_build_version:
                    # Set focus to main window and attempt to execute a Paste operation
                    self._pcbnew_frame.Raise()
                    wx.Yield()
                    keyinput = wx.UIActionSimulator()
                    keyinput.Char(ord("V"), wx.MOD_CONTROL)    
        except Exception as e:
            print(e)
        
        finally:
            self.config.Flush()
            dlg.Destroy()
