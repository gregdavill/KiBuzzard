import os
import sys
import subprocess
import threading
import time

import wx
import wx.aui
from wx import FileConfig

import pyperclip

import pcbnew
from .dialog.dialog import Dialog

def check_for_bom_button():
    # From Miles McCoo's blog
    # https://kicad.mmccoo.com/2017/03/05/adding-your-own-command-buttons-to-the-pcbnew-gui/
    def find_pcbnew_window():
        windows = wx.GetTopLevelWindows()
        pcbneww = [w for w in windows if "pcbnew" in w.GetTitle().lower()]
        if len(pcbneww) != 1:
            return None
        return pcbneww[0]

    def callback(_):
        plugin.Run()

    path = os.path.dirname(__file__)
    while not wx.GetApp():
        time.sleep(1)
    bm = wx.Bitmap(path + '/icon.png', wx.BITMAP_TYPE_PNG)
    button_wx_item_id = 0

    from pcbnew import ID_H_TOOLBAR
    while True:
        time.sleep(1)
        pcbnew_window = find_pcbnew_window()
        if not pcbnew_window:
            continue

        top_tb = pcbnew_window.FindWindowById(ID_H_TOOLBAR)
        if button_wx_item_id == 0 or not top_tb.FindTool(button_wx_item_id):
            top_tb.AddSeparator()
            button_wx_item_id = wx.NewId()
            top_tb.AddTool(button_wx_item_id, "KiBuzzard", bm,
                           "Execute Buzzard script", wx.ITEM_NORMAL)
            top_tb.Bind(wx.EVT_TOOL, callback, id=button_wx_item_id)
            top_tb.Realize()

class KiBuzzardPlugin(pcbnew.ActionPlugin, object):
    config_file = os.path.join(os.path.dirname(__file__), '..', 'config.ini')
    buzzard_path = os.path.join(os.path.dirname(__file__), '..', 'deps', 'buzzard')

    def __init__(self):
        super(KiBuzzardPlugin, self).__init__()
        self.name = "Create Labels"
        self.category = "Modify PCB"
        self.pcbnew_icon_support = hasattr(self, "show_toolbar_button")
        self.show_toolbar_button = True
        icon_dir = os.path.dirname(os.path.dirname(__file__))
        self.icon_file_name = os.path.join(icon_dir, 'icon.png')
        self.description = "Create Labels"
        self.last_str = ""
        self.load_from_ini()
        self._pcbnew_frame = None


    def defaults(self):
        pass

    def load_from_ini(self):
        """Init from config file if it exists."""
        if not os.path.isfile(self.config_file):
            return
        f = FileConfig(localFilename=self.config_file)
        f.SetPath('/general')
        self.last_str = f.Read('last_str', self.last_str)


    def save(self):
        f = FileConfig(localFilename=self.config_file)
        f.SetPath('/general')
        f.Write('last_str', self.last_str)
        f.Flush()


    def Run(self):
        buzzard_script = os.path.join(self.buzzard_path, 'buzzard.py')

        if self._pcbnew_frame is None:
            self._pcbnew_frame = [x for x in wx.GetTopLevelWindows() if 'pcbnew' in x.GetTitle().lower() and not 'python' in x.GetTitle().lower()][0]

        
        def run_buzzard(str):
            import re

            self.last_str = str

            str = str + ' -o ki -stdout'
            args = [a.strip('"') for a in re.findall('".+?"|\S+', str)]

            # Execute Buzzard
            process = subprocess.Popen(['python', buzzard_script] + args, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            stdout, stderr = process.communicate()

            # check for errors
            error_line = [s for s in stderr.decode('utf8').split('\n') if 'error' in s]
            if len(error_line) > 0:
                wx.MessageBox(error_line[0], 'Error', wx.OK | wx.ICON_ERROR)

            else:        
                # Copy footprint into clipboard
                process = subprocess.Popen(['xclip', '-sel', 'clip', '-noutf8'], stdin=subprocess.PIPE)
                process.communicate(stdout)

                # Save copy of string
                self.save()

                dlg.EndModal(wx.ID_OK)

                 

        
        dlg = Dialog(self._pcbnew_frame, self.last_str, run_buzzard)
        try:
            if dlg.ShowModal() == wx.ID_OK:
                # Set focus to main window and execute a Paste operation
                self._pcbnew_frame.Raise()
                wx.Yield()
                keyinput = wx.UIActionSimulator()
                keyinput.Char(ord("V"), wx.MOD_CONTROL)    
        finally:
            dlg.Destroy()



plugin = KiBuzzardPlugin()
plugin.register()


# Add a button the hacky way if plugin button is not supported
# in pcbnew, unless this is linux.
if not plugin.pcbnew_icon_support and not sys.platform.startswith('linux'):
    t = threading.Thread(target=check_for_bom_button)
    t.daemon = True
    t.start()
