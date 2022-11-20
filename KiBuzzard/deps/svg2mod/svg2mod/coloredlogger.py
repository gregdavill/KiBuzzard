# Copyright (C) 2022 -- svg2mod developers < GitHub.com / svg2mod >

# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License along
# with this program; if not, write to the Free Software Foundation, Inc.,
# 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301 USA.
'''
A simple modification to the formatter class in the python logger to allow
ANSI color codes based on the logged message's level
'''

import logging
import sys

#----------------------------------------------------------------------------

#Setup and configure svg2mod and svg2mod-unfiltered loggers

logger = logging.getLogger("svg2mod")
unfiltered_logger = logging.getLogger("svg2mod-unfiltered")
_sh = logging.StreamHandler(sys.stdout)

logger.addHandler(_sh)
unfiltered_logger.addHandler(_sh)

logger.setLevel(logging.DEBUG)

# Add a second logger that will bypass the log level and output anyway
# It is a good practice to send only messages level INFO via this logger
unfiltered_logger.setLevel(logging.INFO)

# This can be used sparingly as follows:
#---------
# unfiltered_logger.info("Message Here")
#---------


#----------------------------------------------------------------------------

class Formatter(logging.Formatter):
    '''Extend formatter to add colored output functionality '''

    # ASCII escape codes for supporting terminals
    color = {
        logging.CRITICAL: "\033[91m\033[7m", #Set red and swap background and foreground
        logging.ERROR: "\033[91m", #Set red
        logging.WARNING: "\033[93m", #Set yellow
        logging.DEBUG: "\033[90m", #Set dark gray/black
        logging.INFO: "" #Do nothing
    }
    reset = "\033[0m" # Reset the terminal back to default color/emphasis

    #------------------------------------------------------------------------

    def __init__(self, fmt="%(message)s", datefmt=None, style="%"):
        super().__init__(fmt, datefmt, style)

    #------------------------------------------------------------------------

    def format(self, record):
        '''Overwrite the format function.
        This saves the original style, overwrites it to support
        color, sends the message to the super.format, and
        finally returns the style to the original format
        '''
        if sys.stdout.isatty():
            fmt_org = self._style._fmt
            self._style._fmt = Formatter.color[record.levelno] + fmt_org + Formatter.reset
        result = logging.Formatter.format(self, record)
        if sys.stdout.isatty():
            self._style._fmt = fmt_org
        return result

    #------------------------------------------------------------------------

#----------------------------------------------------------------------------

def split_logger(logger, formatter=Formatter(), break_point=logging.WARNING):
    '''This will split logging messages at the specified break point. Anything higher
    will be sent to sys.stderr and everything else to sys.stdout
    '''
    for handler in logger.handlers:
        logger.removeHandler(handler)

    handler_error = logging.StreamHandler(sys.stderr)
    handler_error.addFilter(lambda msg: break_point <= msg.levelno)

    handler_out = logging.StreamHandler(sys.stdout)
    handler_out.addFilter(lambda msg: break_point > msg.levelno)

    handler_error.setFormatter(formatter)
    handler_out.setFormatter(formatter)
    logger.addHandler(handler_error)
    logger.addHandler(handler_out)

#----------------------------------------------------------------------------