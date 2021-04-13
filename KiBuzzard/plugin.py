import os
import sys
import subprocess
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
        if '5.1' in self.kicad_build_version or '5.0' in self.kicad_build_version:
            # Library location for KiCad 5.1
            self.filepath = os.path.join(tempfile.mkdtemp(), 'buzzard_labels.pretty', 'label.kicad_mod') 
            try: # Use try/except here because python 2.7 doesn't support exist_ok
                os.makedirs(os.path.dirname(self.filepath))
            except:
                pass

    def defaults(self):
        pass

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


                if wx.TheClipboard.Open():
                    wx.TheClipboard.SetData(wx.TextDataObject(footprint_string))
                    wx.TheClipboard.Close()
                    
            dlg.EndModal(wx.ID_OK)

        dlg = Dialog(self._pcbnew_frame, self.config, Buzzard(), run_buzzard)
    
        if dlg.ShowModal() == wx.ID_OK:
            
            if '5.99' in self.kicad_build_version:
                if self._pcbnew_frame is not None:
                    # Set focus to main window and attempt to execute a Paste operation
                    self._pcbnew_frame.Raise()
                    wx.Yield()
                    keyinput = wx.UIActionSimulator()
                    keyinput.Char(ord("V"), wx.MOD_CONTROL)    

    def InitLogger(self):
        # Remove all handlers associated with the root logger object.
        for handler in logging.root.handlers[:]:
            logging.root.removeHandler(handler)

        log_file = os.path.join(os.path.dirname(__file__), '..', 'kibuzzard.log')

        # set up logger
        logging.basicConfig(level=logging.DEBUG,
                            filename=log_file,
                            filemode='w',
                            format='%(asctime)s %(name)s %(lineno)d:%(message)s',
                            datefmt='%m-%d %H:%M:%S')

        stdout_logger = logging.getLogger('STDOUT')
        sl_out = StreamToLogger(stdout_logger, logging.INFO)
        sys.stdout = sl_out

        stderr_logger = logging.getLogger('STDERR')
        sl_err = StreamToLogger(stderr_logger, logging.ERROR)
        sys.stderr = sl_err


class StreamToLogger(object):
    """
    Fake file-like stream object that redirects writes to a logger instance.
    """
    def __init__(self, logger, log_level=logging.INFO):
        self.logger = logger
        self.log_level = log_level
        self.linebuf = ''

    def write(self, buf):
        for line in buf.rstrip().splitlines():
            self.logger.log(self.log_level, line.rstrip())

    def flush(self, *args, **kwargs):
        """No-op for wrapper"""
        pass