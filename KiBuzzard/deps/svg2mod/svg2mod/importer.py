# Copyright (C) 2021 -- svg2mod developers < GitHub.com / svg2mod >

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
Svg2ModImport is responsible for basic parsing
of svg layers to be used with an instance of
Svg2ModExport.
'''


from svg2mod import svg
from svg2mod.coloredlogger import logger, unfiltered_logger

#----------------------------------------------------------------------------

class Svg2ModImport:
    ''' An importer class to read in target svg,
    parse it, and keep only layers on interest.
    '''

    #------------------------------------------------------------------------

    def _prune_hidden( self, items = None ):

        if items is None:

            items = self.svg.items

        for item in items[:]:

            if hasattr(item, "hidden") and item.hidden:
                if hasattr(item, "name") and item.name:
                    logger.warning("Ignoring hidden SVG item: {}".format( item.name ) )
                items.remove(item)

            if hasattr(item, "items") and item.items:
                self._prune_hidden( item.items )

    #------------------------------------------------------------------------

    def __init__( self, file_name=None, module_name="svg2mod", module_value="G***", ignore_hidden=False, force_layer=None):

        self.file_name = file_name
        self.module_name = module_name
        self.module_value = module_value
        self.ignore_hidden = ignore_hidden

        if file_name:
            unfiltered_logger.info( "Parsing SVG..." )

            self.svg = svg.parse( file_name )
            logger.info("Document scaling: {} units per pixel".format(self.svg.viewport_scale))
        if force_layer:
            new_layer = svg.Group()
            new_layer.name = force_layer
            new_layer.items = self.svg.items[:]
            self.svg.items = [new_layer]
        if self.ignore_hidden:
            self._prune_hidden()


    #------------------------------------------------------------------------

#----------------------------------------------------------------------------
