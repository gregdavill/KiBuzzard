import base64
import json
import logging
import os
import sys
import tempfile

import kipy
import wx
import wx.aui
from buzzard.buzzard import Buzzard
from dialog import Dialog


class KiBuzzardPlugin:
    def __init__(self):
        self.config_file = os.path.join(os.path.dirname(__file__), "config.json")
        self.InitLogger()
        self.logger = logging.getLogger(__name__)

        self.kicad = kipy.KiCad()

        self.name = "Create Labels"
        self.category = "Modify PCB"
        self.pcbnew_icon_support = hasattr(self, "show_toolbar_button")
        self.show_toolbar_button = True
        icon_dir = os.path.dirname(__file__)
        self.icon_file_name = os.path.join(icon_dir, "icon.png")
        self.description = "Create Labels"

        self.kicad_build_version = self.kicad.get_version()

    def Run(self):
        def run_buzzard(dlg, p_buzzard):
            self.logger.log(logging.DEBUG, "Running KiBuzzard")

            if len(dlg.polys) == 0:
                self.logger.log(logging.DEBUG, "No polygons to render")
                dlg.EndModal(wx.ID_OK)
                return

            json_str = json.dumps(dlg.label_params, sort_keys=True)
            encoded_str = base64.b64encode(json_str.encode("utf-8")).decode("ascii")
            footprint_string = p_buzzard.create_v6_footprint(parm_text=encoded_str)

            if dlg.updateFootprint is None:
                # New footprint
                self.logger.log(logging.DEBUG, "Loading label onto clipboard")
                clipboard = wx.Clipboard.Get()
                if clipboard.Open():
                    clipboard.SetData(wx.TextDataObject(footprint_string))
                    clipboard.Close()
                else:
                    self.logger.log(logging.DEBUG, "Clipboard error")

            else:
                # Create a replacement footprint and also place it in the clipboard
                self.logger.log(
                    logging.DEBUG,
                    "Updating selected footprint {}".format(dlg.updateFootprint),
                )
                try:
                    board = self.kicad.get_board()

                    # FIXME: Once supported by the IDC API, parse the sexpr
                    # into a footprint object and update the footprint

                    clipboard = wx.Clipboard.Get()
                    if clipboard.Open():
                        clipboard.SetData(wx.TextDataObject(footprint_string))
                        clipboard.Close()
                    else:
                        self.logger.log(logging.DEBUG, "Clipboard error")

                    # Remove the old footprint
                    board.remove_items([dlg.updateFootprint])

                except:
                    import traceback

                    wx.LogError(traceback.format_exc())
            dlg.EndModal(wx.ID_OK)

        dlg = Dialog(None, self.config_file, Buzzard(), run_buzzard)

        try:
            if dlg.ShowModal() == wx.ID_OK:
                if len(dlg.polys) == 0:
                    return
                # Don't try to paste if we've updated a footprint
                if dlg.updateFootprint is not None:
                    return

                # FIXME: Start a new place operation once the IDC API supports it

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
            try:  # Use try/except here because python 2.7 doesn't support exist_ok
                os.makedirs(log_path)

            except:
                pass
            log_file = os.path.join(log_path, "kibuzzard.log")
            handler2 = logging.FileHandler(log_file)

            # Also move config file
            self.config_file = os.path.join(log_path, "config.json")

        handler2.setLevel(logging.DEBUG)
        formatter = logging.Formatter(
            "%(asctime)s %(name)s %(lineno)d:%(message)s", datefmt="%m-%d %H:%M:%S"
        )
        handler1.setFormatter(formatter)
        handler2.setFormatter(formatter)
        root.addHandler(handler1)
        root.addHandler(handler2)


def main():
    app = wx.App()
    kbzz = KiBuzzardPlugin()
    kbzz.Run()


if __name__ == "__main__":
    main()
