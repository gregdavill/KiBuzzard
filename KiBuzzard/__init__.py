import os
import sys
import subprocess
import threading
import time

import wx
import wx.aui
from wx import FileConfig

import os
from .util import add_paths
dir_path = os.path.dirname(os.path.realpath(__file__))
paths = [
    os.path.join(dir_path, 'deps'), 
    os.path.join(dir_path, 'deps', 'fonttools', 'Lib'), 
    os.path.join(dir_path, 'deps', 'svg2mod')
]

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

    while not wx.GetApp():
        time.sleep(1)
    bm = wx.Bitmap(os.path.join(os.path.dirname(__file__),'icon.png'), wx.BITMAP_TYPE_PNG)
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


try:
    with add_paths(paths):
        from .plugin import KiBuzzardPlugin
    plugin = KiBuzzardPlugin()
    plugin.register()
except Exception as e:
    print(e)
    import logging    
    root = logging.getLogger()
    root.debug(repr(e))

# Add a button the hacky way if plugin button is not supported
# in pcbnew, unless this is linux.
if not plugin.pcbnew_icon_support and not sys.platform.startswith('linux'):
    t = threading.Thread(target=check_for_bom_button)
    t.daemon = True
    t.start()

