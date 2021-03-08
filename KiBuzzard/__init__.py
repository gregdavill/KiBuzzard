import os
import sys
import subprocess
import threading
import time

import wx
import wx.aui
from wx import FileConfig

import pcbnew
from .dialog import Dialog

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
        self.config = FileConfig(localFilename=self.config_file)
        self._pcbnew_frame = None


    def defaults(self):
        pass

    def find_python3(self):

        # try to see if python3 is already in PATH
        try:
            process = subprocess.Popen('python3')
            return 'python3'
        except:
            pass

        # official python installer doesn't add python3 by default to PATH
        # also even if added to PATH python3 on windows is actually called python
        # however it will install py launcher https://docs.python.org/3.8/using/windows.html?#launcher
        # use that to get python3 executable on windows
        try:
            process = subprocess.Popen(['py', '-3', '-c', 'import sys; print(sys.executable)'], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            python3_path, _ = process.communicate()
            return python3_path.decode().strip()

        except:
            pass

        return ''

    def Run(self):
        buzzard_script = os.path.join(self.buzzard_path, 'buzzard.py')

        # check for python3
        # try getting it from config
        python3_path = self.config.Read('/python3/path', defaultVal='')

        # if no defined, try to search for it
        if not python3_path:
            python3_path = self.find_python3()

            # we found a path, lets save it!
            if python3_path:
                wx.MessageBox('python3 path set to `%s`\nIf this is not the correct python3, please update the path in config.ini' % python3_path, 'python3', wx.OK | wx.ICON_INFORMATION)
                self.config.Write('/python3/path', python3_path)
                self.config.Flush()

        # if python3 is not found let the user know!
        if not python3_path:
            wx.MessageBox(
                'Buzzard needs python3 to run.\n'
                + 'Please make sure python3 is installed on your machine!\n'
                + 'If python3 is installed on the machine please update the python3 path in config.ini.\n'
                + 'Eg:\n'
                + '[python3]\n'
                + 'path=\\path\\to\\python3\n'
                + '*On Windows machines slashes (\\) need to be escaped (\\\\).',
                'Can\'t find python3',
                wx.OK | wx.ICON_ERROR,
            )
            return

        if self._pcbnew_frame is None:
            try:
                self._pcbnew_frame = [x for x in wx.GetTopLevelWindows() if ('pcbnew' in x.GetTitle().lower() and not 'python' in x.GetTitle().lower()) or ('pcb editor' in x.GetTitle().lower())][0]
            except:
                pass

        def run_buzzard(str):
            import re

            str = str + ' -stdout -o ki' + ('5' if '5.1' in pcbnew.GetBuildVersion() else '')
            args = [a.strip('"') for a in re.findall('".+?"|\S+', str)]
            if sys.platform.startswith('win'):
                args = [re.sub('([<>])', r'^\1', a) for a in args] # escape '<' or '>' with a caret, '^<'

            # Execute Buzzard
            process = None
            process = subprocess.Popen([python3_path, buzzard_script] + args, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            stdout, stderr = process.communicate()
            if stderr:
                wx.MessageBox(stderr, 'Error', wx.OK | wx.ICON_ERROR)

            # check for errors
            error_line = [s for s in stderr.decode('utf8').split('\n') if 'error' in s]
            if len(error_line) > 0:
                wx.MessageBox(error_line[0], 'Error', wx.OK | wx.ICON_ERROR)

            else:
                # Copy footprint into clipboard
                if sys.platform.startswith('linux'):
                    clip_args = ['xclip', '-sel', 'clip', '-noutf8']
                elif sys.platform == 'darwin':
                    clip_args = ['pbcopy']
                else:
                    clip_args = ['clip.exe']

                process = subprocess.Popen(clip_args, stdin=subprocess.PIPE)
                process.communicate(stdout)

                dlg.EndModal(wx.ID_OK)

        dlg = Dialog(self._pcbnew_frame, self.config, self.buzzard_path, run_buzzard)
        try:
            if dlg.ShowModal() == wx.ID_OK:
                # Set focus to main window and execute a Paste operation
                if self._pcbnew_frame is not None:
                    self._pcbnew_frame.Raise()
                    wx.Yield()
                    keyinput = wx.UIActionSimulator()
                    keyinput.Char(ord("V"), wx.MOD_CONTROL)
        finally:
            self.config.Flush()
            dlg.Destroy()


plugin = KiBuzzardPlugin()
plugin.register()


# Add a button the hacky way if plugin button is not supported
# in pcbnew, unless this is linux.
if not plugin.pcbnew_icon_support and not sys.platform.startswith('linux'):
    t = threading.Thread(target=check_for_bom_button)
    t.daemon = True
    t.start()
