import os
import sys
import time
import tempfile
import logging
import wx
import wx.aui
from wx import FileConfig

import pcbnew
import base64
import json
from .dialog import Dialog

from .buzzard.buzzard import Buzzard


class KiBuzzardPlugin(pcbnew.ActionPlugin, object):

    def __init__(self):
        super(KiBuzzardPlugin, self).__init__()

        self.config_file = os.path.join(os.path.dirname(__file__), 'config.json')
        self.InitLogger()
        self.logger = logging.getLogger(__name__)

        self.name = "Create Labels"
        self.category = "Modify PCB"
        self.pcbnew_icon_support = hasattr(self, "show_toolbar_button")
        self.show_toolbar_button = True
        icon_dir = os.path.dirname(__file__)
        self.icon_file_name = os.path.join(icon_dir, 'icon.png')
        self.description = "Create Labels"
        
        self._pcbnew_frame = None

        self.kicad_build_version = pcbnew.GetBuildVersion()

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
                dlg.EndModal(wx.ID_OK)
                return

            if self.IsVersion(['5.99','6.0', '6.99']):
                json_str = json.dumps(dlg.label_params, sort_keys=True)
                encoded_str = base64.b64encode(json_str.encode('utf-8')).decode('ascii')
                footprint_string = p_buzzard.create_v6_footprint(parm_text=encoded_str)

                if dlg.updateFootprint is None:
                    # New footprint
                    clipboard = wx.Clipboard.Get()
                    if clipboard.Open():
                        clipboard.SetData(wx.TextDataObject(footprint_string))
                        clipboard.Close()
                else:
                    # Create new footprint, and replace old ones place
                    try:
                        b = pcbnew.GetBoard()
                        
                        pos = dlg.updateFootprint.GetPosition()
                        orient = dlg.updateFootprint.GetOrientation()
                        wasOnBackLayer = ("B." in dlg.updateFootprint.GetLayerName())
                        
                        io = pcbnew.PCB_PLUGIN()
                        new_fp = pcbnew.Cast_to_FOOTPRINT(io.Parse(footprint_string))
                        b.Add(new_fp)
                        new_fp.SetPosition(pos)
                        # Flip before setting orientation
                        if wasOnBackLayer:
                            new_fp.Flip(pos, True)
                        new_fp.SetOrientation(orient)

                        b.Remove(dlg.updateFootprint)
                    except:
                        import traceback
                        wx.LogError(traceback.format_exc())
                    
            dlg.EndModal(wx.ID_OK)

        dlg = Dialog(self._pcbnew_frame, self.config_file, Buzzard(), run_buzzard)
    
        try:
            if dlg.ShowModal() == wx.ID_OK:
                if len(dlg.polys) == 0:
                    return 
                # Don't try to paste if we've updated a footprint
                if dlg.updateFootprint is not None:
                    return
                
                if self.IsVersion(['5.99','6.0', '6.99']):
                    if self._pcbnew_frame is not None:
                        # Set focus to main window and attempt to execute a Paste operation 
                        try:
                            evt = wx.KeyEvent(wx.wxEVT_CHAR_HOOK)
                            evt.SetKeyCode(ord('V'))
                            #evt.SetUnicodeKey(ord('V'))
                            evt.SetControlDown(True)
                    
                            wnd = [i for i in self._pcbnew_frame.Children if i.ClassName == 'wxWindow'][0]
                            #print(wnd)
                            #print(evt)
                            wx.PostEvent(wnd, evt)
                        except:
                            # Likely on Linux with old wx python support :(
                            keyinput = wx.UIActionSimulator()
                            self._pcbnew_frame.Raise()
                            self._pcbnew_frame.SetFocus()
                            wx.MilliSleep(100)
                            wx.Yield()
                            # Press and release CTRL + V
                            keyinput.Char(ord("V"), wx.MOD_CONTROL)
                            wx.MilliSleep(100)
        finally:
            dlg.Destroy()
                        
                    
    def InitLogger(self):
        root = logging.getLogger()
        root.setLevel(logging.DEBUG)

        # Log to stderr
        handler1 = logging.StreamHandler(sys.stderr)
        handler1.setLevel(logging.DEBUG)


        log_path = os.path.dirname(__file__)
        log_file = os.path.join(log_path, "kibuzzard.log")

        # and to our error file
        # Check logging file permissions, if fails, move log file to tmp folder
        handler2 = None
        try:
            handler2 = logging.FileHandler(log_file)
        except PermissionError:
            log_path = os.path.join(tempfile.mkdtemp()) 
            try: # Use try/except here because python 2.7 doesn't support exist_ok
                os.makedirs(log_path)

            except:
                pass
            log_file = os.path.join(log_path, "kibuzzard.log")
            handler2 = logging.FileHandler(log_file)

            # Also move config file
            self.config_file = os.path.join(log_path, 'config.json')
        
        handler2.setLevel(logging.DEBUG)
        formatter = logging.Formatter(
            "%(asctime)s %(name)s %(lineno)d:%(message)s", datefmt="%m-%d %H:%M:%S"
        )
        handler1.setFormatter(formatter)
        handler2.setFormatter(formatter)
        root.addHandler(handler1)
        root.addHandler(handler2)
       

    