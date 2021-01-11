import os
import sys
import subprocess
import threading
import time

import wx
import wx.aui

import pcbnew
from .dialog.dialog import Dialog

import pyperclip

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

    def __init__(self):
        super(KiBuzzardPlugin, self).__init__()
        self.name = "Create Labels"
        self.category = "Read PCB"
        self.pcbnew_icon_support = hasattr(self, "show_toolbar_button")
        self.show_toolbar_button = True
        icon_dir = os.path.dirname(os.path.dirname(__file__))
        self.icon_file_name = os.path.join(icon_dir, 'icon.png')
        self.description = "Create Labels"

    def defaults(self):
        pass

    def Run(self):
        board = pcbnew.GetBoard()
        pcb_file_name = board.GetFileName()
        
        dlg = Dialog()
        try:
            if dlg.ShowModal() == wx.ID_OK:
                #print(dlg.GetValue())
                arg = dlg.GetValue()

                subprocess.run(['python', '/home/greg/Projects/sparkfunx/Buzzard/buzzard.py', arg])

                txt = open('/home/greg/Projects/sparkfunx/Buzzard/output.scr').read()

                pcb_io = pcbnew.PCB_IO()
                footprint = pcbnew.Cast_to_FOOTPRINT(pcb_io.Parse(txt))


                footprint.SetParent(board)
                board.Add(footprint)
                footprint.SetPosition(pcbnew.wxPoint(0,0))
                #footprint.SetNeedsPlaced(True)
                #pcbnew.Refresh()
                wx.CallAfter(pcbnew.Refresh)
                #pyperclip.copy_gtk(txt)

                #subprocess.run(['xclip', '-sel', 'clip', '/home/greg/Projects/sparkfunx/Buzzard/output.scr'])
                


                ...
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
