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
Tools to convert data from Svg2ModImport to
the file information  used in kicad module files.
'''


import copy
import datetime
import io
import json
import os
import re
import time
from abc import ABC, abstractmethod

from svg2mod import svg
from svg2mod.coloredlogger import logger, unfiltered_logger
from svg2mod.importer import Svg2ModImport
from svg2mod.svg2mod import PolygonSegment

#----------------------------------------------------------------------------

DEFAULT_DPI = 96 # 96 as of Inkscape 0.92
MINIMUM_SIZE = 1e-5 # Minimum size kicad will render

#----------------------------------------------------------------------------

class Svg2ModExport(ABC):
    ''' An abstract class to provide functionality
    to write to kicad module file.
    The abstract methods are the file type specific
    example: pretty, legacy
    '''

    #------------------------------------------------------------------------

    @property
    @abstractmethod
    def layer_map(self ):
        ''' This should be overwritten by a dictionary object of layer maps '''
        pass

    @abstractmethod
    def _get_layer_name( self, item_name, name, front ):pass

    @abstractmethod
    def _write_library_intro( self, cmdline ): pass

    @abstractmethod
    def _get_module_name( self, front = None ): pass

    @abstractmethod
    def _write_module_header( self, label_size, label_pen, reference_y, value_y, front,): pass

    @abstractmethod
    def _write_modules( self ): pass

    @abstractmethod
    def _write_module_footer( self, front ):pass

    @abstractmethod
    def _write_polygon_header( self, points, layer ):pass

    @abstractmethod
    def _write_polygon_footer( self, layer, stroke_width, fill=True):pass

    @abstractmethod
    def _write_polygon_point( self, point ):pass

    @abstractmethod
    def _write_polygon_segment( self, p, q, layer, stroke_width ):pass

    @abstractmethod
    def _write_thru_hole( self, circle, layer ):pass

    #------------------------------------------------------------------------

    @staticmethod
    def _convert_decimal_to_mm( decimal ):
        return float( decimal ) * 0.00254


    #------------------------------------------------------------------------

    @staticmethod
    def _convert_mm_to_decimal( mm ):
        return int( round( mm * 393.700787 ) )


    #------------------------------------------------------------------------

    def _get_fill_stroke( self, item ):

        s = item.style

        fill = False if not s.get('fill') or s["fill"] == "none" else True
        fill = fill if not s.get('fill-opacity') or float(s['fill-opacity']) != 0 else False

        stroke = False if not s.get('stroke') or s["stroke"] == "none" else True
        stroke = stroke if not s.get('stroke-opacity') or float(s['stroke-opacity']) != 0 else False

        stroke_width = s["stroke-width"] * self.scale_factor if s.get('stroke-width') else MINIMUM_SIZE

        if stroke_width is None:
            stroke_width = 0

        # This should display something.
        if not self.imported.ignore_hidden and not fill and not stroke:
            stroke = True
            stroke_width = stroke_width if stroke_width else MINIMUM_SIZE

        # There should be no stroke_width if no stroke
        return fill, stroke, stroke_width if stroke else 0


    #------------------------------------------------------------------------

    def __init__(
        self,
        svg2mod_import = Svg2ModImport(),
        file_name = None,
        center = False,
        scale_factor = 1.0,
        precision = 20.0,
        use_mm = True,
        dpi = DEFAULT_DPI,
        pads = False,
    ):
        if use_mm:
            # 25.4 mm/in;
            scale_factor *= 25.4 / float(dpi)
            use_mm = True
        else:
            # PCBNew uses decimal (10K DPI);
            scale_factor *= 10000.0 / float(dpi)

        self.imported = svg2mod_import
        self.file_name = file_name
        self.center = center
        self.scale_factor = scale_factor
        self.precision = precision
        self.use_mm = use_mm
        self.dpi = dpi
        self.convert_pads = pads

        # Local instance variables
        self.translation = None
        self.layers = {}
        self.output_file = None
        self.raw_file_data = None


    #------------------------------------------------------------------------

    def add_svg_element(self, elem : svg.Transformable, layer="F.SilkS"):
        ''' This can be used to add a svg element
        to a specific layer.
        If the importer doesn't have a svg element
        it will also create an empty Svg object.
        '''
        grp = svg.Group()
        grp.name = layer
        grp.items.append(elem)
        try:
            self.imported.svg.items.append(grp)
        except AttributeError:
            self.imported.svg = svg.Svg()
            self.imported.svg.items.append(grp)

    #------------------------------------------------------------------------


    def _calculate_translation( self ):

        min_point, max_point = self.imported.svg.bbox()

        if self.center:
            # Center the drawing:
            adjust_x = min_point.x + ( max_point.x - min_point.x ) / 2.0
            adjust_y = min_point.y + ( max_point.y - min_point.y ) / 2.0

            self.translation = svg.Point(
                0.0 - adjust_x,
                0.0 - adjust_y,
            )

        else:
            self.translation = svg.Point(
                0.0,
                0.0,
            )

    #------------------------------------------------------------------------

    def _prune( self, items = None ):
        '''Find and keep only the layers of interest.'''

        empty_group_exception = items is None

        if items is None:

            self.layers = {}
            for name in self.layer_map.keys():
                self.layers[ name ] = []


            items = self.imported.svg.items
            self.imported.svg.items = []

        kept_layers = {}

        for item in items:

            if not hasattr(item, 'name'):
                continue

            i_name = item.name.split(":", 1)

            for name in self.layers.keys():
                # if name == i_name[0] and i_name[0] != "":
                if re.match( '^{}$'.format(name), i_name[0]):
                    # Don't add empty groups to the list of valid items
                    if isinstance(item, svg.Group) and not item.items:
                        break

                    if kept_layers.get(i_name[0]):
                        kept_layers[i_name[0]].append(item.name)
                    else:
                        kept_layers[i_name[0]] = [item.name]

                    # Item isn't a group so make it one
                    if not isinstance(item, svg.Group):
                        grp = svg.Group()
                        grp.name = item.name
                        grp.items.append( item )
                        item = grp

                    # save valid groups
                    self.imported.svg.items.append( item )
                    self.layers[name].append((i_name, item))
                    break
            else:
                self._prune( item.items )

        for kept in sorted(kept_layers.keys()):
            unfiltered_logger.info( "Found SVG layer: {}".format( kept ) )
            logger.debug( "  Detailed names: [{}]".format( ", ".join(kept_layers[kept]) ) )

        # There are no elements to write so don't write
        if empty_group_exception:
            for name in self.layers:
                if self.layers[name]:
                    break
            else:
                logger.warning("No valid items found. Maybe try --force Layer.Name")
                raise Exception("Not writing empty file. No valid items found.")

    #------------------------------------------------------------------------

    def _write_items( self, items, layer, flip = False ):

        for item in items:

            if isinstance( item, svg.Group ):
                self._write_items( item.items, layer, flip )
                continue

            if re.match(r"^Drill\.\w+", str(layer)):
                if isinstance(item, (svg.Circle, svg.Ellipse)):
                    self._write_thru_hole(item, layer)
                else:
                    logger.warning( "Non Circle SVG element in drill layer: {}".format(item.__class__.__name__))

            elif isinstance( item, (svg.Path, svg.Ellipse, svg.Rect, svg.Text, svg.Polygon)):

                segments = [
                    PolygonSegment( segment )
                    for segment in item.segments(
                        precision = self.precision
                    )
                ]

                fill, stroke, stroke_width = self._get_fill_stroke( item )
                if layer == "Edge.Cuts":
                    fill = False
                    stroke = True
                    stroke_width = MINIMUM_SIZE if stroke_width < MINIMUM_SIZE else stroke_width


                fill = (True if re.match("^Keepout", str(layer)) else fill)
                stroke_width = (0.508 if re.match("^Keepout", str(layer)) else stroke_width)

                for segment in segments:
                    segment.process( self, flip, fill )

                if len( segments ) > 1:
                    # Sort segments in order of size
                    segments.sort(key=lambda v: svg.Segment(v.bbox[0], v.bbox[1]).length(), reverse=True)

                    # Write all segments
                    while len(segments) > 0:
                        inlinable = [segments[0]]

                        # Search to see if any paths are contained in the current shape
                        for seg in segments[1:]:
                            # Contained in parent shape
                            if fill and not inlinable[0].are_distinct(seg):
                                append = True
                                if len(inlinable) > 1:
                                    for hole in inlinable[1:]:
                                        # Contained in a hole. It is separate
                                        if not hole.are_distinct(seg):
                                            append = False
                                            break
                                if append: inlinable.append(seg)
                        for poly in inlinable:
                            segments.pop(segments.index(poly))
                        if len(inlinable) > 1:
                            points = inlinable[ 0 ].inline( inlinable[ 1 : ] )
                        elif len(inlinable) > 0:
                            points = inlinable[ 0 ].points

                        logger.info( "  Writing {} with {} points".format(item.__class__.__name__, len( points ) ))

                        self._write_polygon(
                            points, layer, fill, stroke, stroke_width
                        )
                    continue

                if len( segments ) > 0:
                    points = segments[ 0 ].points

                if len ( segments ) == 1:

                    logger.info( "  Writing {} with {} points".format(item.__class__.__name__, len( points ) ))

                    self._write_polygon(
                        points, layer, fill, stroke, stroke_width
                    )
                else:
                    logger.info( "  Skipping {} with 0 points".format(item.__class__.__name__))

            else:
                logger.warning( "Unsupported SVG element: {}".format(item.__class__.__name__))


    #------------------------------------------------------------------------

    def _write_module( self, front ):

        module_name = self._get_module_name( front )

        min_point, max_point = self.imported.svg.bbox()
        min_point = self.transform_point( min_point, flip = False )
        max_point = self.transform_point( max_point, flip = False )

        label_offset = 1200
        label_size = 600
        label_pen = 120

        if self.use_mm:
            label_size = self._convert_decimal_to_mm( label_size )
            label_pen = self._convert_decimal_to_mm( label_pen )
            reference_y = min_point.y - self._convert_decimal_to_mm( label_offset )
            value_y = max_point.y + self._convert_decimal_to_mm( label_offset )
        else:
            reference_y = min_point.y - label_offset
            value_y = max_point.y + label_offset

        self._write_module_header(
            label_size, label_pen,
            reference_y, value_y,
            front,
        )

        for name, groups in self.layers.items():
            for i_name, group in groups:

                if group is None: continue

                layer = self._get_layer_name( i_name, name, front )

                self._write_items( group.items, layer, not front )

        self._write_module_footer( front )


    #------------------------------------------------------------------------

    def _write_polygon( self, points, layer, fill, stroke, stroke_width ):

        if fill and len(points) > 2:
            self._write_polygon_filled(
                points, layer, stroke_width
            )
            return

        # Polygons with a fill and stroke are drawn with the filled polygon above
        if stroke:
            if len(points) == 1:
                points.append(copy.copy(points[0]))

            self._write_polygon_outline(
                points, layer, stroke_width
            )
            return

        if len(points) < 3:
            logger.debug("  Not writing non-polygon with no stroke.")
        else:
            logger.debug("  Polygon has no stroke or fill. Skipping.")


    #------------------------------------------------------------------------


    def _write_polygon_filled( self, points, layer, stroke_width = 0.0 ):

        self._write_polygon_header( points, layer )

        for point in points:
            self._write_polygon_point( point )

        self._write_polygon_footer( layer, stroke_width )


    #------------------------------------------------------------------------

    def _write_polygon_outline( self, points, layer, stroke_width ):

        prior_point = None
        for point in points:

            if prior_point is not None:

                self._write_polygon_segment(
                    prior_point, point, layer, stroke_width
                )

            prior_point = point


    #------------------------------------------------------------------------

    def transform_point( self, point, flip = False ):
        ''' Transform provided point by this
        classes scale factor.
        '''

        transformed_point = svg.Point(
            ( point.x + self.translation.x ) * self.scale_factor,
            ( point.y + self.translation.y ) * self.scale_factor,
        )

        if flip:
            transformed_point.x *= -1

        if self.use_mm:
            transformed_point.x = transformed_point.x
            transformed_point.y = transformed_point.y
        else:
            transformed_point.x = int( round( transformed_point.x ) )
            transformed_point.y = int( round( transformed_point.y ) )

        return transformed_point


    #------------------------------------------------------------------------

    def write( self, cmdline="scripting" ):
        '''Write the kicad footprint file.
        The value from the command line argument
        is set in a comment in the header of the file.

        If self.file_name is not null then this will
        overwrite the target file with the data provided.
        However if it is null then all data is written
        to the string IO class (for same API as writing)
        then dumped into self.raw_file_data before the
        writer is closed.
        '''

        self._prune()

        # Must come after pruning:
        self._calculate_translation()

        if self.file_name:
            unfiltered_logger.info( "Writing module file: {}".format( self.file_name ) )
            self.output_file = open( self.file_name, 'w' )
        else:
            self.output_file = io.StringIO()

        self._write_library_intro(cmdline)

        self._write_modules()

        if self.file_name is None:
            self.raw_file_data = self.output_file.getvalue()

        self.output_file.close()
        self.output_file = None


    #------------------------------------------------------------------------

#----------------------------------------------------------------------------

class Svg2ModExportLegacy( Svg2ModExport ):
    ''' A child of Svg2ModExport that implements
    specific functionality for kicad legacy file types
    '''

    layer_map = {
        #'inkscape-name' : [ kicad-front, kicad-back ],
        'F.Cu' : [ 15, 15 ],
        'B.Cu' : [ 0, 0 ],
        'F.Adhes' : [ 17, 17 ],
        'B.Adhes' : [ 16, 16 ],
        'F.Paste' : [ 19, 19 ],
        'B.Paste' : [ 18, 18 ],
        'F.SilkS' : [ 21, 21 ],
        'B.SilkS' : [ 20, 20 ],
        'F.Mask' : [ 23, 23 ],
        'B.Mask' : [ 22, 22 ],
        'Dwgs.User' : [ 24, 24 ],
        'Cmts.User' : [ 25, 25 ],
        'Eco1.User' : [ 26, 26 ],
        'Eco2.User' : [ 27, 27 ],
        'Edge.Cuts' : [ 28, 28 ],
    }


    #------------------------------------------------------------------------

    def __init__(
        self,
        svg2mod_import,
        file_name,
        center,
        scale_factor = 1.0,
        precision = 20.0,
        use_mm = True,
        dpi = DEFAULT_DPI,
    ):
        super( Svg2ModExportLegacy, self ).__init__(
            svg2mod_import,
            file_name,
            center,
            scale_factor,
            precision,
            use_mm,
            dpi,
            pads = False,
        )

        self.include_reverse = True


    #------------------------------------------------------------------------

    def _get_layer_name( self, item_name, name, front ):

        layer_info = self.layer_map[ name ]
        layer = layer_info[ 0 ]
        if not front and layer_info[ 1 ] is not None:
            layer = layer_info[ 1 ]

        return layer


    #------------------------------------------------------------------------

    def _get_module_name( self, front = None ):

        if self.include_reverse and not front:
            return self.imported.module_name + "-rev"

        return self.imported.module_name


    #------------------------------------------------------------------------

    def _write_library_intro( self, cmdline ):

        modules_list = self._get_module_name( front = True )
        if self.include_reverse:
            modules_list += (
                "\n" +
                self._get_module_name( front = False )
            )

        units = ""
        if self.use_mm:
            units = "\nUnits mm"

        self.output_file.write( """PCBNEW-LibModule-V1  {0}{1}
$INDEX
{2}
$EndINDEX
#
# Converted using: {3}
#
""".format(
                datetime.datetime.now().strftime( "%a %d %b %Y %I:%M:%S %p %Z" ),
                units,
                modules_list,
                cmdline.replace("\\","\\\\")
            )
        )


    #------------------------------------------------------------------------

    def _write_module_header(
        self, label_size, label_pen,
        reference_y, value_y, front,
    ):

        self.output_file.write( """$MODULE {0}
Po 0 0 0 {6} 00000000 00000000 ~~
Li {0}
T0 0 {1} {2} {2} 0 {3} N I 21 "{0}"
T1 0 {5} {2} {2} 0 {3} N I 21 "{4}"
""".format(
                self._get_module_name( front ), #0
                reference_y, #1
                label_size, #2
                label_pen, #3
                self.imported.module_value, #4
                value_y, #5
                15, # Seems necessary #6
            )
        )


    #------------------------------------------------------------------------

    def _write_module_footer( self, front ):

        self.output_file.write(
            "$EndMODULE {0}\n".format( self._get_module_name( front ) )
        )


    #------------------------------------------------------------------------

    def _write_modules( self ):

        self._write_module( front = True )

        if self.include_reverse:
            self._write_module( front = False )

        self.output_file.write( "$EndLIBRARY" )


    #------------------------------------------------------------------------

    def _write_polygon_footer( self, layer, stroke_width, fill=True ):

        pass


    #------------------------------------------------------------------------

    def _write_polygon_header( self, points, layer ):

        pen = 1
        if self.use_mm:
            pen = self._convert_decimal_to_mm( pen )

        self.output_file.write( "DP 0 0 0 0 {} {} {}\n".format(
            len( points ),
            pen,
            layer
        ) )


    #------------------------------------------------------------------------

    def _write_polygon_point( self, point ):

        self.output_file.write(
            "Dl {} {}\n".format( point.x, point.y )
        )


    #------------------------------------------------------------------------

    def _write_polygon_segment( self, p, q, layer, stroke_width ):

        self.output_file.write( "DS {} {} {} {} {} {}\n".format(
            p.x, p.y,
            q.x, q.y,
            stroke_width,
            layer
        ) )


    #------------------------------------------------------------------------

    def _write_thru_hole( self, circle, layer ):

        pass

    #------------------------------------------------------------------------

#----------------------------------------------------------------------------

class Svg2ModExportLegacyUpdater( Svg2ModExportLegacy ):
    ''' A Svg2Mod exporter class that reads some settings
    from an already existing module and will append its
    changes to the file.
    '''

    #------------------------------------------------------------------------

    def __init__(
        self,
        svg2mod_import,
        file_name,
        center,
        scale_factor = 1.0,
        precision = 20.0,
        dpi = DEFAULT_DPI,
        include_reverse = True,
    ):
        self.file_name = file_name
        use_mm = self._parse_output_file()

        super( Svg2ModExportLegacyUpdater, self ).__init__(
            svg2mod_import,
            file_name,
            center,
            scale_factor,
            precision,
            use_mm,
            dpi,
        )


    #------------------------------------------------------------------------

    def _parse_output_file( self ):

        logger.info( "Parsing module file: {}".format( self.file_name ) )
        module_file = open( self.file_name, 'r' )
        lines = module_file.readlines()
        module_file.close()

        self.loaded_modules = {}
        self.post_index = []
        self.pre_index = []
        use_mm = False

        index = 0

        # Find the start of the index:
        while index < len( lines ):

            line = lines[ index ]
            index += 1
            self.pre_index.append( line )
            if line[ : 6 ] == "$INDEX":
                break

            m = re.match( r"Units[\s]+mm[\s]*", line )
            if m is not None:
                use_mm = True

        # Read the index:
        while index < len( lines ):

            line = lines[ index ]
            if line[ : 9 ] == "$EndINDEX":
                break
            index += 1
            self.loaded_modules[ line.strip() ] = []

        # Read up until the first module:
        while index < len( lines ):

            line = lines[ index ]
            if line[ : 7 ] == "$MODULE":
                break
            index += 1
            self.post_index.append( line )

        # Read modules:
        while index < len( lines ):

            line = lines[ index ]
            if line[ : 7 ] == "$MODULE":
                module_name, module_lines, index = self._read_module( lines, index )
                if module_name is not None:
                    self.loaded_modules[ module_name ] = module_lines

            elif line[ : 11 ] == "$EndLIBRARY":
                break

            else:
                raise Exception(
                    "Expected $EndLIBRARY: [{}]".format( line )
                )

        return use_mm


    #------------------------------------------------------------------------

    def _read_module( self, lines, index ):

        # Read module name:
        m = re.match( r'\$MODULE[\s]+([^\s]+)[\s]*', lines[ index ] )
        module_name = m.group( 1 )

        logger.info( "  Reading module {}".format( module_name ) )

        index += 1
        module_lines = []
        while index < len( lines ):

            line = lines[ index ]
            index += 1

            m = re.match(
                r'\$EndMODULE[\s]+' + module_name + r'[\s]*', line
            )
            if m is not None:
                return module_name, module_lines, index

            module_lines.append( line )

        raise Exception(
            "Could not find end of module '{}'".format( module_name )
        )


    #------------------------------------------------------------------------

    def _write_library_intro( self, cmdline ):

        # Write pre-index:
        self.output_file.writelines( self.pre_index )

        self.loaded_modules[ self._get_module_name( front = True ) ] = None
        if self.include_reverse:
            self.loaded_modules[
                self._get_module_name( front = False )
            ] = None

        # Write index:
        for module_name in sorted(
            self.loaded_modules.keys(),
            key = str.lower
        ):
            self.output_file.write( module_name + "\n" )

        # Write post-index:
        self.output_file.writelines( self.post_index )


    #------------------------------------------------------------------------

    def _write_preserved_modules( self, up_to = None ):

        if up_to is not None:
            up_to = up_to.lower()

        for module_name in sorted(
            self.loaded_modules.keys(),
            key = str.lower
        ):
            if up_to is not None and module_name.lower() >= up_to:
                continue

            module_lines = self.loaded_modules[ module_name ]

            if module_lines is not None:

                self.output_file.write(
                    "$MODULE {}\n".format( module_name )
                )
                self.output_file.writelines( module_lines )
                self.output_file.write(
                    "$EndMODULE {}\n".format( module_name )
                )

                self.loaded_modules[ module_name ] = None


    #------------------------------------------------------------------------

    def _write_module_footer( self, front ):

        super( Svg2ModExportLegacyUpdater, self )._write_module_footer(
            front,
        )

        # Write remaining modules:
        if not front:
            self._write_preserved_modules()


    #------------------------------------------------------------------------

    def _write_module_header(
        self,
        label_size,
        label_pen,
        reference_y,
        value_y,
        front,
    ):
        self._write_preserved_modules(
            up_to = self._get_module_name( front )
        )

        super( Svg2ModExportLegacyUpdater, self )._write_module_header(
            label_size,
            label_pen,
            reference_y,
            value_y,
            front,
        )


    #------------------------------------------------------------------------

#----------------------------------------------------------------------------

class Svg2ModExportPretty( Svg2ModExport ):
    ''' This provides functionality for the
    older kicad "pretty" footprint file formats.
    It is a child of Svg2ModExport.
    '''

    layer_map = {
        #'inkscape-name' : kicad-name,
        'F.Cu' :    "F.Cu",
        'B.Cu' :    "B.Cu",
        'F.Adhes' : "F.Adhes",
        'B.Adhes' : "B.Adhes",
        'F.Paste' : "F.Paste",
        'B.Paste' : "B.Paste",
        'F.SilkS' : "F.SilkS",
        'B.SilkS' : "B.SilkS",
        'F.Mask' :  "F.Mask",
        'B.Mask' :  "B.Mask",
        'Dwgs.User' : "Dwgs.User",
        'Cmts.User' : "Cmts.User",
        'Eco1.User' : "Eco1.User",
        'Eco2.User' : "Eco2.User",
        'Edge.Cuts' : "Edge.Cuts",
        'F.CrtYd' : "F.CrtYd",
        'B.CrtYd' : "B.CrtYd",
        'F.Fab' :   "F.Fab",
        'B.Fab' :   "B.Fab",
        'Drill.Cu': "Drill.Cu",
        'Drill.Mech': "Drill.Mech",
    }

    keepout_allowed = ['tracks','vias','pads','copperpour','footprints']


    # Breaking changes where introduced in kicad v6
    # This variable disables the drill breaking changes for v5 support
    _drill_inner_layers = False


    #------------------------------------------------------------------------

    def __init__(self, *args, **kwargs):
        super(Svg2ModExportPretty, self).__init__(*args, **kwargs)
        self._special_footer = ""
        self._extra_indent = 0

    #------------------------------------------------------------------------

    def _get_layer_name( self, item_name, name, front ):

        name = self.layer_map[ name ]

        # For pretty format layers can have attributes in the svg name
        # This validates all the layers and converts them to a json string
        # which is attached to the returned value with `:`
        attrs = {}

        # Keepout layer validation and expansion
        if name == "Keepout":
            attrs["layers"] = []
            layers = re.match(r'^(.*)\.Keepout', item_name[0]).groups()[0]
            if len(layers) == 1 and layers not in "BFI*":
                raise Exception("Unexpected keepout layer: {} in {}".format(layers, item_name[0]))
            if len(layers) == 1:
                if layers == '*':
                    attrs['layers'] = ['F','B','I']
                else:
                    attrs['layers'] = [layers]
            else:
                for layer in layers:
                    if layer not in "FBI":
                        raise Exception("Unexpected keepout layer: {} in {}".format(layer, item_name[0]))
                    if layer != '&':
                        attrs['layers'].append(layer)

        # All attributes with the exception of keepout layers is validated
        if len(item_name) == 2 and item_name[1]:
            for arg in item_name[1].split(';'):
                arg = arg.strip(' ,:')

                # This is used in Svg2ModExportLatest as it is a breaking change
                # Keepout allowed items
                if name == "Keepout" and re.match(r'^allowed:\w+', arg, re.I):
                    attrs["allowed"] = []
                    for allowed in arg.lower().split(":", 1)[1].split(','):
                        if allowed in self.keepout_allowed:
                            attrs["allowed"].append(allowed)
                        else:
                            logger.warning("Invalid allowed option in keepout: {} in {}".format(allowed, arg))
                # Zone hatch patterns
                elif name == "Keepout" and re.match(r'^hatch:(none|edge|full)$', arg, re.I):
                    attrs["hatch"] = arg.split(":", 1)[1]

                #Copper pad attributes
                elif re.match(r'^\w+\.Cu', name) and re.match(r'^pad(:(\d+|mask|paste))?', arg, re.I):
                    if arg.lower() == "pad":
                        attrs["copper_pad"] = True
                    else:
                        ops = arg.split(":", 1)[1]
                        for opt in ops.split(','):
                            if re.match(r'^\d+$', opt):
                                attrs["copper_pad"] = int(opt)
                            elif opt.lower() == "mask" and name != "Drill.Cu":
                                attrs["pad_mask"] = True
                                if not attrs.get("copper_pad"):
                                    attrs["copper_pad"] = True
                            elif opt.lower() == "paste" and name != "Drill.Cu":
                                attrs["pad_paste"] = True
                                if not attrs.get("copper_pad"):
                                    attrs["copper_pad"] = True
                            else:
                                logger.warning("Invalid pad option '{}' for layer {}".format(opt, name))
                else:
                    logger.warning("Unexpected option: {} for {}".format(arg, item_name[0]))
        if attrs:
            return name+":"+json.dumps(attrs)
        return name


    #------------------------------------------------------------------------

    def _get_module_name( self, front = None ):

        return self.imported.module_name


    #------------------------------------------------------------------------

    def _write_library_intro( self, cmdline ):

        self.output_file.write( """(module {0} (layer F.Cu) (tedit {1:8X})
  (attr virtual)
  (descr "{2}")
  (tags {3})
""".format(
                self.imported.module_name, #0
                int( round( #1
                    os.path.getctime( self.imported.file_name ) if self.imported.file_name else time.time()
                ) ),
                "Converted using: {}".format( cmdline.replace("\\", "\\\\") ), #2
                "svg2mod", #3
            )
        )


    #------------------------------------------------------------------------

    def _write_module_footer( self, front ):

        self.output_file.write( "\n)" )


    #------------------------------------------------------------------------

    def _write_module_header(
        self, label_size, label_pen,
        reference_y, value_y, front,
    ):
        if front:
            side = "F"
        else:
            side = "B"

        self.output_file.write(
"""  (fp_text reference {0} (at 0 {1}) (layer {2}.SilkS) hide
    (effects (font (size {3} {3}) (thickness {4})))
  )
  (fp_text value {5} (at 0 {6}) (layer {2}.SilkS) hide
    (effects (font (size {3} {3}) (thickness {4})))
  )""".format(

                self._get_module_name(), #0
                reference_y, #1
                side, #2
                label_size, #3
                label_pen, #4
                self.imported.module_value, #5
                value_y, #6
            )
        )


    #------------------------------------------------------------------------

    def _write_modules( self ):

        self._write_module( front = True )


    #------------------------------------------------------------------------

    def _write_polygon_filled( self, points, layer, stroke_width = 0):
        self._write_polygon_header( points, layer, stroke_width)

        for point in points:
            self._write_polygon_point( point )

        self._write_polygon_footer( layer, stroke_width )

    #------------------------------------------------------------------------

    def _write_polygon_footer( self, layer, stroke_width, fill=True ):

        #Format option #2 is expected, but only used in Svg2ModExportLatest
        if self._special_footer:
            self.output_file.write(self._special_footer.format(
                layer.split(":", 1)[0], stroke_width, "" #2
            ))
        else:
            self.output_file.write(
                "    )\n    (layer {})\n    (width {}){}\n  )".format(
                    layer.split(":", 1)[0], stroke_width, "" #3
                )
            )
        self._special_footer = ""
        self._extra_indent = 0


    #------------------------------------------------------------------------

    def _write_polygon_header( self, points, layer, stroke_width):

        l_name = layer
        options = {}
        try:
            l_name, options = layer.split(":", 1)
            options = json.loads(options)
        except ValueError:pass

        create_pad = (self.convert_pads and l_name.find("Cu") == 2) or options.get("copper_pad")

        if stroke_width == 0:
            stroke_width = MINIMUM_SIZE

        if l_name == "Keepout":
            self._extra_indent = 1
            layers = ["*"]
            if len(options["layers"]) == 3:
                layers = ["*"]
            elif "I" not in options["layers"]:
                layers = ["&".join(options["layers"])]
            else:
                options["layers"].remove("I")
                layers = options["layers"][:] + ['In{}'.format(i) for i in range(1,31)]


            self.output_file.write( '''\n  (zone (net 0) (net_name "") (layers "{0}.Cu") (hatch {1} {2:.6f})
    (connect_pads (clearance 0))
    (min_thickness {3:.6f})
    (keepout ({4}allowed))
    (fill (thermal_gap {2:.6f}) (thermal_bridge_width {2:.6f}))
    (polygon
      (pts\n'''.format(
                    '.Cu" "'.join(layers), #0
                    options["hatch"] if options.get("hatch") else "full", #1
                    stroke_width, #2
                    stroke_width/2, #3
                    "allowed) (".join(
                        [i+" "+(
                            "not_" if not options.get("allowed") or i not in options["allowed"] else ""
                        ) for i in self.keepout_allowed]
                    ), #4
                )
            )
            self._special_footer = "      )\n    )\n  )"
        elif create_pad:
            pad_number = "" if not options.get("copper_pad") or isinstance(options["copper_pad"], bool) else str(options.get("copper_pad"))
            layer = l_name
            if options.get("pad_mask"):
                layer += " {}.Mask".format(l_name.split(".", 1)[0])
            if options.get("pad_paste"):
                layer += " {}.Paste".format(l_name.split(".", 1)[0])
            self._extra_indent = 1

            self._special_footer = "\n  )"

            self.output_file.write( '''\n  (pad "{0}" smd custom (at {1} {2}) (size {3:.6f} {3:.6f}) (layers {4})
    (zone_connect 0)
    (options (clearance outline) (anchor circle))'''.format(
                    pad_number, #0
                    points[0].x, #1
                    points[0].y, #2
                    stroke_width, #3
                    layer, #4
                )
            )
            # Pads primitives with 2 or less points crash kicad
            if len(points) >= 2:
                self.output_file.write('''\n    (primitives\n      (gr_poly (pts \n''')
                self._special_footer = "      )\n    (width {}){{2}})\n  ))".format(stroke_width)

                origin_x = points[0].x
                origin_y = points[0].y
                for point in points:
                    point.x = point.x-origin_x
                    point.y = point.y-origin_y
            else:
                for point in points[:]:
                    points.remove(point)
        else:
            self.output_file.write( "\n  (fp_poly\n    (pts \n" )


    #------------------------------------------------------------------------

    def _write_polygon_point( self, point ):

        if self._extra_indent:
            self.output_file.write("  "*self._extra_indent)

        self.output_file.write(
            "      (xy {} {})\n".format( point.x, point.y )
        )


    #------------------------------------------------------------------------

    def _write_polygon_segment( self, p, q, layer, stroke_width ):
        l_name = layer
        options = {}
        try:
            l_name, options = layer.split(":", 1)
            options = json.loads(options)
        except ValueError:pass

        create_pad = (self.convert_pads and l_name.find("Cu") == 2) or options.get("copper_pad")

        if stroke_width == 0:
            stroke_width = MINIMUM_SIZE

        if create_pad:
            pad_number = "" if not options.get("copper_pad") or isinstance(options["copper_pad"], bool) else str(options.get("copper_pad"))
            layer = l_name
            if options.get("pad_mask"):
                layer += " {}.Mask".format(l_name.split(".", 1)[0])
            if options.get("pad_paste"):
                layer += " {}.Paste".format(l_name.split(".", 1)[0])

            # There are major performance issues when multiple line primitives are in the same pad
            self.output_file.write( '''\n  (pad "{0}" smd custom (at {1} {2}) (size {3:.6f} {3:.6f}) (layers {4})
    (zone_connect 0)
    (options (clearance outline) (anchor circle))
    (primitives\n      (gr_line (start 0 0) (end {5} {6}) (width {3}))
  ))'''.format(
                    pad_number, #0
                    p.x, #1
                    p.y, #2
                    stroke_width, #3
                    layer, #4
                    q.x - p.x, #5
                    q.y - p.y, #6
                )
            )
        else:

            self.output_file.write(
                """\n  (fp_line
        (start {} {}) (end {} {})
        (layer {}) (width {})
    )""".format(
                    p.x, p.y,
                    q.x, q.y,
                    layer.split(':',1)[0],
                    stroke_width,
                )
            )

    #------------------------------------------------------------------------

    def _write_thru_hole( self, circle, layer ):

        if not isinstance(circle, svg.Circle):
            logger.info("Found an ellipse in Drill layer. Using an average of rx and ry.")
            circle.rx = (circle.rx + circle.ry ) / 2

        l_name = layer
        options = {}
        try:
            l_name, options = layer.split(":", 1)
            options = json.loads(options)
        except ValueError:pass

        plated = l_name == "Drill.Cu"
        pad_number = ""
        if plated and options.get("copper_pad") and not isinstance(options["copper_pad"], bool):
            pad_number = str(options.get("copper_pad"))

        rad = circle.rx * self.scale_factor
        drill = rad * 2

        size = circle.style.get("stroke-width") * self.scale_factor
        if size and plated:
            drill -= size
            size = size + ( rad * 2 )
        elif size:
            size = size + ( rad * 2 )
            drill = size
        else:
            size = rad

        center = self.transform_point(circle.center)

        self.output_file.write(
            '\n  (pad "{0}" {1}thru_hole circle (at {2} {3}) (size {4} {4}) (drill {5}) (layers *.Mask{6}) {7})'.format(
                pad_number, #0
                "" if plated else "np_", #1
                center.x, #2
                center.y, #3
                size, #4
                drill, #5
                " *.Cu" if plated else "", #6
                "(remove_unused_layers) (keep_end_layers)" if plated and self._drill_inner_layers else "", #7
            )
        )

    #------------------------------------------------------------------------

#----------------------------------------------------------------------------


class Svg2ModExportLatest(Svg2ModExportPretty):
    ''' This provides functionality for the newer kicad
    "pretty" footprint file formats introduced in kicad v6.
    It is a child of Svg2ModExport.
    '''

    layer_map = {
        #'inkscape-name' : kicad-name,
        'F.Cu' :    "F.Cu",
        'B.Cu' :    "B.Cu",
        'F.Adhes' : "F.Adhes",
        'B.Adhes' : "B.Adhes",
        'F.Paste' : "F.Paste",
        'B.Paste' : "B.Paste",
        'F.SilkS' : "F.SilkS",
        'B.SilkS' : "B.SilkS",
        'F.Mask' :  "F.Mask",
        'B.Mask' :  "B.Mask",
        'Dwgs.User' : "Dwgs.User",
        'Cmts.User' : "Cmts.User",
        'Eco1.User' : "Eco1.User",
        'Eco2.User' : "Eco2.User",
        'Edge.Cuts' : "Edge.Cuts",
        'F.CrtYd' : "F.CrtYd",
        'B.CrtYd' : "B.CrtYd",
        'F.Fab' :   "F.Fab",
        'B.Fab' :   "B.Fab",
        'Drill.Cu': "Drill.Cu",
        'Drill.Mech': "Drill.Mech",
        r'\S+\.Keepout': "Keepout"
    }

    # Breaking changes where introduced in kicad v6
    # This variable enables the drill breaking changes for v5 support
    _drill_inner_layers = True

    #------------------------------------------------------------------------

    def _write_polygon_outline( self, points, layer, stroke_width = 0):
        self._write_polygon_header( points, layer, stroke_width)

        for point in points:
            self._write_polygon_point( point )

        self._write_polygon_footer( layer, stroke_width, fill=False )

    #------------------------------------------------------------------------

    def _write_polygon_footer( self, layer, stroke_width, fill=True ):

        if self._special_footer:
            self.output_file.write(self._special_footer.format(
                layer.split(":", 1)[0], stroke_width,
                " (fill none)" if not fill else ""
            ))
        else:
            self.output_file.write(
                "    )\n    (layer {})\n    (width {}){}\n  )".format(
                    layer.split(":", 1)[0], stroke_width,
                    " (fill none)" if not fill else ""
                )
            )
        self._special_footer = ""
        self._extra_indent = 0



    #------------------------------------------------------------------------

#----------------------------------------------------------------------------
