
import wx

class DialogShim(wx.Dialog):
    def __init__(self, parent, **kwargs):
        wx.Dialog.__init__(self, parent, **kwargs)

    def SetSizeHints(self, a, b, c=None):
        if c is not None:
            super().SetSizeHints(a,b,c)
        else:
            super().SetSizeHintsSz( a,b)
        