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
This module contains the necessary tools to convert from
the svg objects provided from the svg2mod.svg module to
KiCad file formats.
This currently supports both the pretty format and
the legacy mod format.
'''

from __future__ import absolute_import

#from abc import ABC, abstractmethod
#from typing import List, Tuple
import argparse
import datetime
import os
import sys
import re
import io
import time
import logging


import svg2mod.svg as svg
import svg2mod.coloredlogger as coloredlogger

try:
    from shlex import quote
except ImportError:
    from pipes import quote

#----------------------------------------------------------------------------
DEFAULT_DPI = 96 # 96 as of Inkscape 0.92

def main():
    '''This function handles the scripting package calls.
    It is setup to read the arguments from `get_arguments()`
    then parse the target svg file and output all converted
    objects into a kicad footprint module.
    '''

    args,_ = get_arguments()


    # Setup root logger to use terminal colored outputs as well as stdout and stderr
    coloredlogger.split_logger(logging.root)

    if args.verbose_print:
        logging.root.setLevel(logging.INFO)
    elif args.debug_print:
        logging.root.setLevel(logging.DEBUG)
    else:
        logging.root.setLevel(logging.ERROR)

    # Add a second logger that will bypass the log level and output anyway
    # It is a good practice to send only messages level INFO via this logger
    logging.getLogger("unfiltered").setLevel(logging.INFO)

    # This can be used sparingly as follows:
    '''
    logging.getLogger("unfiltered").info("Message Here")
    '''

    if args.list_fonts:
        fonts = svg.Text.load_system_fonts()
        logging.getLogger("unfiltered").info("Font Name: list of supported styles.")
        for font in fonts:
            fnt_text = "  {}:".format(font)
            for styles in fonts[font]:
                fnt_text += " {},".format(styles)
            fnt_text = fnt_text.strip(",")
            logging.getLogger("unfiltered").info(fnt_text)
        sys.exit(0)
    if args.default_font:
        svg.Text.default_font = args.default_font

    pretty = args.format == 'pretty'
    use_mm = args.units == 'mm'

    if pretty:

        if not use_mm:
            logging.critical("Error: decimal units only allowed with legacy output type")
            sys.exit( -1 )

        #if args.include_reverse:
            #print(
                #"Warning: reverse footprint not supported or required for" +
                #" pretty output format"
            #)

    # Import the SVG:
    imported = Svg2ModImport(
        args.input_file_name,
        args.module_name,
        args.module_value,
        args.ignore_hidden_layers,
    )

    # Pick an output file name if none was provided:
    if args.output_file_name is None:

        args.output_file_name = os.path.splitext(
            os.path.basename( args.input_file_name )
        )[ 0 ]

    # Append the correct file name extension if needed:
    if pretty:
        extension = ".kicad_mod"
    else:
        extension = ".mod"
    if args.output_file_name[ - len( extension ) : ] != extension:
        args.output_file_name += extension

    # Create an exporter:
    if pretty:
        exported = Svg2ModExportPretty(
            imported,
            args.output_file_name,
            args.center,
            args.scale_factor,
            args.precision,
            dpi = args.dpi,
            pads = args.convert_to_pads,
        )

    else:

        # If the module file exists, try to read it:
        exported = None
        if os.path.isfile( args.output_file_name ):

            try:
                exported = Svg2ModExportLegacyUpdater(
                    imported,
                    args.output_file_name,
                    args.center,
                    args.scale_factor,
                    args.precision,
                    args.dpi,
                )

            except Exception as e:
                raise e
                #print( e.message )
                #exported = None

        # Write the module file:
        if exported is None:
            exported = Svg2ModExportLegacy(
                imported,
                args.output_file_name,
                args.center,
                args.scale_factor,
                args.precision,
                use_mm = use_mm,
                dpi = args.dpi,
            )

    args = [os.path.basename(sys.argv[0])] + sys.argv[1:]
    cmdline = ' '.join([quote(x) for x in args])

    # Export the footprint:
    exported.write(cmdline)


#----------------------------------------------------------------------------

class LineSegment:
    '''Kicad can only draw straight lines.
    This class can be type-cast from svg.geometry.Segment
    It is designed to have extra functions to help
    calculate intersections.
    '''

    #------------------------------------------------------------------------

    @staticmethod
    def _on_segment( p, q, r ):
        """ Given three collinear points p, q, and r, check if
            point q lies on line segment pr. """

        if (
            q.x <= max( p.x, r.x ) and
            q.x >= min( p.x, r.x ) and
            q.y <= max( p.y, r.y ) and
            q.y >= min( p.y, r.y )
        ):
            return True

        return False


    #------------------------------------------------------------------------

    @staticmethod
    def _orientation( p, q, r ):
        """ Find orientation of ordered triplet (p, q, r).
            Returns following values
            0 --> p, q and r are collinear
            1 --> Clockwise
            2 --> Counterclockwise
        """

        val = (
            ( q.y - p.y ) * ( r.x - q.x ) -
            ( q.x - p.x ) * ( r.y - q.y )
        )

        if val == 0: return 0
        if val > 0: return 1
        return 2


    #------------------------------------------------------------------------

    def __init__( self, p = None, q = None ):

        self.p = p
        self.q = q


    #------------------------------------------------------------------------

    def connects( self, segment):
        ''' Return true if provided segment shares
        endpoints with the current segment else false
        '''

        if self.q == segment.p: return True
        if self.q == segment.q: return True
        if self.p == segment.p: return True
        if self.p == segment.q: return True
        return False


    #------------------------------------------------------------------------

    def intersects( self, segment ):
        """ Return true if line segments 'p1q1' and 'p2q2' intersect.
            Adapted from:
              http://www.geeksforgeeks.org/check-if-two-given-line-segments-intersect/
        """

        # Find the four orientations needed for general and special cases:
        o1 = self._orientation( self.p, self.q, segment.p )
        o2 = self._orientation( self.p, self.q, segment.q )
        o3 = self._orientation( segment.p, segment.q, self.p )
        o4 = self._orientation( segment.p, segment.q, self.q )

        return (

            # General case:
            ( o1 != o2 and o3 != o4 )

            or

            # p1, q1 and p2 are collinear and p2 lies on segment p1q1:
            ( o1 == 0 and self._on_segment( self.p, segment.p, self.q ) )

            or

            # p1, q1 and p2 are collinear and q2 lies on segment p1q1:
            ( o2 == 0 and self._on_segment( self.p, segment.q, self.q ) )

            or

            # p2, q2 and p1 are collinear and p1 lies on segment p2q2:
            ( o3 == 0 and self._on_segment( segment.p, self.p, segment.q ) )

            or

            # p2, q2 and q1 are collinear and q1 lies on segment p2q2:
            ( o4 == 0 and self._on_segment( segment.p, self.q, segment.q ) )
        )


    #------------------------------------------------------------------------

    def q_next( self, q):
        '''Shift segment endpoints so self.q is self.p
        and q is the new self.q
        q is type svg.Point
        '''

        self.p = self.q
        self.q = q

    def __eq__(self, other):
        return (
            isinstance(other, LineSegment) and
            other.p.x == self.p.x and other.p.y == self.p.y and
            other.q.x == self.q.x and other.q.y == self.q.y
        )


    #------------------------------------------------------------------------

#----------------------------------------------------------------------------

class PolygonSegment:
    ''' A polygon should be a collection of segments
    creating an enclosed or manifold shape.
    This class provides functionality to find overlap
    points between a segment and it's self as well as
    identify if another polygon rests inside of the
    closed area of it's self.

    When initializing this class it will round all
    points to the specified number of decimal points,
    default 10, and remove duplicate points in a row.
    '''

    #------------------------------------------------------------------------

    def __init__( self, points, ndigits=10):

        self.points = [points.pop(0).round(ndigits)]

        for point in points:
            p = point.round(ndigits)
            if self.points[-1] != p:
                self.points.append(p)


        if len( points ) < 3:
            logging.warning("Warning: Path segment has only {} points (not a polygon?)".format(len( points )))


    #------------------------------------------------------------------------

    def _find_insertion_point( self, hole, holes, other_insertions ):
        ''' KiCad will not "pick up the pen" when moving between a polygon outline
        and holes within it, so we search for a pair of points connecting the
        outline (self) or other previously inserted points to the hole such
        that the connecting segment will not cross the visible inner space
        within any hole.
        '''

        connected = list( zip(*other_insertions) )
        if len(connected) > 0:
            connected = [self] + list( connected[2] )
        else:
            connected = [self]

        for hp in range( len(hole.points) - 1 ):
            for poly in connected:
                for pp in range( len(poly.points ) - 1 ):
                    hole_point = hole.points[hp]
                    bridge = LineSegment( poly.points[pp], hole_point)
                    trying_new_point = True
                    second_bridge = None
                    # connected_poly = poly
                    while trying_new_point:
                        trying_new_point = False

                        # Check if bridge passes over other bridges that will be created
                        bad_point = False
                        for ip, insertion,_ in other_insertions:
                            insert = LineSegment( ip, insertion[0])
                            if bridge.intersects(insert):
                                bad_point = True
                                break

                        if bad_point:
                            continue

                        # Check for intersection with each other hole:
                        for other_hole in holes:

                            # If the other hole intersects, don't bother checking
                            # remaining holes:
                            res = other_hole.intersects(
                                bridge,
                                check_connects = (
                                    other_hole == hole or connected.count( other_hole ) > 0
                                ),
                                get_points = (
                                    other_hole == hole or connected.count( other_hole ) > 0
                                )
                            )
                            if isinstance(res, bool) and res: break
                            elif isinstance(res, tuple) and len(res) != 0:
                                trying_new_point = True
                                # connected_poly = other_hole
                                if other_hole == hole:
                                    hole_point = res[0]
                                    bridge = LineSegment( bridge.p, res[0] )
                                    second_bridge = LineSegment( bridge.p, res[1] )
                                else:
                                    bridge = LineSegment( res[0], hole_point )
                                    second_bridge = LineSegment( res[1], hole_point )
                                break


                        else:
                            # No other holes intersected, so this insertion point
                            # is acceptable:
                            return ( bridge.p, hole.points_starting_on_index( hole.points.index(hole_point) ), hole )

                        if second_bridge and not trying_new_point:
                            bridge = second_bridge
                            if hole_point != bridge.q:
                                hole_point = bridge.q
                            second_bridge = None
                            trying_new_point = True

        logging.error("Could not insert segment without overlapping other segments")
        exit(1)


    #------------------------------------------------------------------------

    def points_starting_on_index( self, index ):
        ''' Return the list of ordered points starting on the given index, ensuring
        that the first and last points are the same.
        '''

        points = self.points

        if index > 0:

            # Strip off end point, which is a duplicate of the start point:
            points = points[ : -1 ]

            points = points[ index : ] + points[ : index ]

            points.append(
                svg.Point( points[ 0 ].x, points[ 0 ].y )
            )

        return points


    #------------------------------------------------------------------------

    def inline( self, segments ):
        ''' Return a list of points with the given polygon segments (paths) inlined. '''

        if len( segments ) < 1:
            return self.points

        logging.debug( "  Inlining {} segments...".format( len( segments ) ) )

        segments.sort(key=lambda h:
            svg.Segment(self.points[0], h.bbox[0]).length()
        )

        all_segments = segments[ : ] + [ self ]
        insertions = []

        # Find the insertion point for each hole:
        for hole in segments:

            insertion = self._find_insertion_point(
                hole, all_segments, insertions
            )
            if insertion is not None:
                insertions.append( insertion )

        points = self.points[ : ]

        for insertion in insertions:

            ip = points.index(insertion[0])

            if (
                points[ ip ].x == insertion[ 1 ][ 0 ].x and
                points[ ip ].y == insertion[ 1 ][ 0 ].y
            ):
                points = points[:ip+1] + insertion[ 1 ][ 1 : -1 ] + points[ip:]
            else:
                points = points[:ip+1] + insertion[ 1 ] + points[ip:]

        return points


    #------------------------------------------------------------------------

    def intersects( self, line_segment, check_connects, count_intersections=False, get_points=False):
        '''Check to see if line_segment intersects with any
        segments of the polygon. Default return True/False

        If check_connects is True then it will skip intersections
        that share endpoints with line_segment.

        count_intersections will return the number of intersections
        with the polygon.

        get_points returns a tuple of the line that intersects
        with line_segment
        '''

        hole_segment = LineSegment()

        intersections = 0

        # Check each segment of other hole for intersection:
        for point in self.points:

            hole_segment.q_next( point )

            if hole_segment.p is not None:

                if ( check_connects and line_segment.connects( hole_segment )):
                    continue

                if line_segment.intersects( hole_segment ):

                    if count_intersections:
                        # If line_segment passes through a point this prevents a second false positive
                        hole_segment.q = None
                        intersections += 1
                    elif get_points:
                        return hole_segment.p, hole_segment.q
                    else:
                        return True

        if count_intersections:
            return intersections
        if get_points and not check_connects:
            return ()
        return False


    #------------------------------------------------------------------------

    def process( self, transformer, flip, fill ):
        ''' Apply all transformations and rounding, then remove duplicate
        consecutive points along the path.
        '''

        points = []
        for point in self.points:

            point = transformer.transform_point( point, flip )

            if (
                len( points ) < 1 or
                point.x != points[ -1 ].x or
                point.y != points[ -1 ].y
            ):
                points.append( point )

        if (
            points[ 0 ].x != points[ -1 ].x or
            points[ 0 ].y != points[ -1 ].y
        ):
            #print( "Warning: Closing polygon. start=({}, {}) end=({}, {})".format(
                #points[ 0 ].x, points[ 0 ].y,
                #points[ -1 ].x, points[ -1 ].y,
            #) )

            if fill:
                points.append( svg.Point(
                    points[ 0 ].x,
                    points[ 0 ].y,
                ) )

        #else:
            #print( "Polygon closed: start=({}, {}) end=({}, {})".format(
                #points[ 0 ].x, points[ 0 ].y,
                #points[ -1 ].x, points[ -1 ].y,
            #) )

        self.points = points


    #------------------------------------------------------------------------

    def calc_bbox(self):
        '''Calculate bounding box of self'''
        self.bbox =  (
            svg.Point(min(self.points, key=lambda v: v.x).x, min(self.points, key=lambda v: v.y).y),
            svg.Point(max(self.points, key=lambda v: v.x).x, max(self.points, key=lambda v: v.y).y),
        )

    #------------------------------------------------------------------------

    def are_distinct(self, polygon):
        ''' Checks if the supplied polygon either contains or insets our bounding box'''
        distinct = True

        smaller = min([self, polygon], key=lambda p: svg.Segment(p.bbox[0], p.bbox[1]).length())
        larger = self if smaller == polygon else polygon

        if (
            larger.bbox[0].x < smaller.bbox[0].x and
            larger.bbox[0].y < smaller.bbox[0].y and
            larger.bbox[1].x > smaller.bbox[1].x and
            larger.bbox[1].y > smaller.bbox[1].y
        ):
            distinct = False

        # Check number of horizontal intersections. If the number is odd then it the smaller polygon
        # is contained. If the number is even then the polygon is outside of the larger polygon
        if not distinct:
            tline = LineSegment(
                svg.Point(smaller.points[0].x, smaller.points[0].y+0.0000001),
                svg.Point(larger.bbox[1].x,    smaller.points[0].y+0.0000001))
            distinct = bool((larger.intersects(tline, False, True) + 1)%2)

        return distinct
    #------------------------------------------------------------------------


#----------------------------------------------------------------------------

class Svg2ModImport:
    ''' An importer class to read in target svg,
    parse it, and keep only layers on interest.
    '''


    def _prune_hidden( self, items = None ):

        if items is None:

            items = self.svg.items
            self.svg.items = []

        for item in items:

            if not isinstance( item, svg.Group ):
                continue

            if item.hidden :
                logging.warning("Ignoring hidden SVG layer: {}".format( item.name ) )
            elif item.name is not "":
                self.svg.items.append( item )

            if(item.items):
                self._prune_hidden( item.items )

    def __init__( self, file_name=None, module_name="svg2mod", module_value="G***", ignore_hidden_layers=False ):

        self.file_name = file_name
        self.module_name = module_name
        self.module_value = module_value

        if file_name:
            logging.getLogger("unfiltered").info( "Parsing SVG..." )

            self.svg = svg.parse( file_name)
            logging.info("Document scaling: {} units per pixel".format(self.svg.viewport_scale))
        if( ignore_hidden_layers ):
            self._prune_hidden()


    #------------------------------------------------------------------------

#----------------------------------------------------------------------------

class Svg2ModExport(object):
    ''' An abstract class to provide functionality
    to write to kicad module file.
    The abstract methods are the file type specific
    example: pretty, legacy
    '''

    @property
    #@abstractmethod
    def layer_map(self ):
        ''' This should be overwritten by a dictionary object of layer maps '''
        pass

    #@abstractmethod
    def _get_layer_name( self, name, front ):pass

    #@abstractmethod
    def _write_library_intro( self, cmdline ): pass

    #@abstractmethod
    def _get_module_name( self, front = None ): pass

    #@abstractmethod
    def _write_module_header( self, label_size, label_pen, reference_y, value_y, front,): pass

    #@abstractmethod
    def _write_modules( self ): pass

    #@abstractmethod
    def _write_module_footer( self, front ):pass

    #@abstractmethod
    def _write_polygon_header( self, points, layer ):pass

    #@abstractmethod
    def _write_polygon( self, points, layer, fill, stroke, stroke_width ):pass

    #@abstractmethod
    def _write_polygon_footer( self, layer, stroke_width ):pass

    #@abstractmethod
    def _write_polygon_point( self, point ):pass

    #@abstractmethod
    def _write_polygon_segment( self, p, q, layer, stroke_width ):pass

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

        fill = True
        stroke = True
        stroke_width = 0.0

        if item.style is not None and item.style != "":

            for prprty in filter(None, item.style.split( ";" )):

                nv = prprty.split( ":" )
                name = nv[ 0 ].strip()
                value = nv[ 1 ].strip()

                if name == "fill" and value == "none":
                    fill = False

                elif name == "fill-opacity":
                    if float(value) == 0:
                        fill = False

                elif name == "stroke" and value == "none":
                    stroke = False

                elif name == "stroke-width":
                    stroke_width = float( "".join(i for i in value if not i.isalpha()) )

                    # units per pixel converted to output units
                    # TODO: Include all transformations instead of just
                    # the top-level viewport_scale
                    scale = self.imported.svg.viewport_scale / self.scale_factor

                    # remove unnecessary precision to reduce floating point errors
                    stroke_width = round(stroke_width/scale, 6)

                elif name == "stroke-opacity":
                    if float(value) == 0:
                        stroke = False

        if not stroke:
            stroke_width = 0.0
        elif stroke_width is None:
            # Give a default stroke width?
            stroke_width = self._convert_decimal_to_mm( 1 ) if self.use_mm else 1

        return fill, stroke, stroke_width


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

    #------------------------------------------------------------------------

    def add_svg_element(self, elem , layer="F.SilkS"):
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

        if(self.center):
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

        if items is None:

            self.layers = {}
            for name in self.layer_map.keys():
                self.layers[ name ] = None

            items = self.imported.svg.items
            self.imported.svg.items = []

        for item in items:

            if not isinstance( item, svg.Group ):
                continue

            for name in self.layers.keys():
                #if re.search( name, item.name, re.I ):
                if name == item.name and item.name is not "":
                    logging.getLogger("unfiltered").info( "Found SVG layer: {}".format( item.name ) )

                    self.imported.svg.items.append( item )
                    self.layers[ name ] = item
                    break
            else:
                self._prune( item.items )


    #------------------------------------------------------------------------

    def _write_items( self, items, layer, flip = False ):

        for item in items:

            if isinstance( item, svg.Group ):
                self._write_items( item.items, layer, flip )
                continue

            elif isinstance( item, (svg.Path, svg.Ellipse, svg.Rect, svg.Text)):

                segments = [
                    PolygonSegment( segment )
                    for segment in item.segments(
                        precision = self.precision
                    )
                ]

                fill, stroke, stroke_width = self._get_fill_stroke( item )
                fill = (False if layer == "Edge.Cuts" else fill)

                for segment in segments:
                    segment.process( self, flip, fill )

                if len( segments ) > 1:
                    for poly in segments:
                        poly.calc_bbox()
                    segments.sort(key=lambda v: svg.Segment(v.bbox[0], v.bbox[1]).length(), reverse=True)

                    while len(segments) > 0:
                        inlinable = [segments[0]]
                        for seg in segments[1:]:
                            if not inlinable[0].are_distinct(seg):
                                append = True
                                if len(inlinable) > 1:
                                    for hole in inlinable[1:]:
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

                        logging.info( "  Writing {} with {} points".format(item.__class__.__name__, len( points ) ))

                        self._write_polygon(
                            points, layer, fill, stroke, stroke_width
                        )
                    continue

                elif len( segments ) > 0:
                    points = segments[ 0 ].points

                if len ( segments ) == 1:

                    logging.info( "  Writing {} with {} points".format(item.__class__.__name__, len( points ) ))

                    self._write_polygon(
                        points, layer, fill, stroke, stroke_width
                    )
                else:
                    logging.info( "  Skipping {} with 0 points".format(item.__class__.__name__))

            else:
                logging.warning( "Unsupported SVG element: {}".format(item.__class__.__name__))


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

        for name, group in self.layers.items():

            if group is None: continue

            layer = self._get_layer_name( name, front )

            #print( "  Writing layer: {}".format( name ) )
            self._write_items( group.items, layer, not front )

        self._write_module_footer( front )


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
            transformed_point.x = round( transformed_point.x, 12 )
            transformed_point.y = round( transformed_point.y, 12 )
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
            logging.getLogger("unfiltered").info( "Writing module file: {}".format( self.file_name ) )
            self.output_file = open( self.file_name, 'w' )
        else:
            if sys.version_info.major == 2:
                self.output_file = io.BytesIO()
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

    def _get_layer_name( self, name, front ):

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
                self._get_module_name( front ),
                reference_y,
                label_size,
                label_pen,
                self.imported.module_value,
                value_y,
                15, # Seems necessary
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

    def _write_polygon( self, points, layer, fill, stroke, stroke_width ):

        if fill:
            self._write_polygon_filled(
                points, layer
            )

        if stroke:

            self._write_polygon_outline(
                points, layer, stroke_width
            )


    #------------------------------------------------------------------------

    def _write_polygon_footer( self, layer, stroke_width ):

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

        logging.info( "Parsing module file: {}".format( self.file_name ) )
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

        logging.info( "  Reading module {}".format( module_name ) )

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
    newer kicad "pretty" footprint file formats.
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
        'B.Fab' :   "B.Fab"
    }


    #------------------------------------------------------------------------

    def _get_layer_name( self, name, front ):

        return self.layer_map[ name ]


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

    def _write_polygon( self, points, layer, fill, stroke, stroke_width ):

        if fill:
            self._write_polygon_filled(
                points, layer, stroke_width
            )

        # Polygons with a fill and stroke are drawn with the filled polygon
        # above:
        if stroke and not fill:

            self._write_polygon_outline(
                points, layer, stroke_width
            )


    #------------------------------------------------------------------------

    def _write_polygon_footer( self, layer, stroke_width ):

        if self._create_pad:
            self.output_file.write(
                "      )\n    (width {}) )\n  ))".format(
                    stroke_width
                )
            )
        else:
            self.output_file.write(
                "    )\n    (layer {})\n    (width {})\n  )".format(
                    layer, stroke_width
                )
            )


    #------------------------------------------------------------------------

    def _write_polygon_header( self, points, layer, stroke_width):
        self._create_pad = self.convert_pads and layer.find("Cu") == 2
        if stroke_width == 0:
            stroke_width = 1e-5 #This is the smallest a pad can be and still be rendered in kicad

        if self._create_pad:
            self.output_file.write( '''\n  (pad 1 smd custom (at {0} {1}) (size {2:.6f} {2:.6f}) (layers {3})
    (zone_connect 0)
    (options (clearance outline) (anchor circle))
    (primitives\n      (gr_poly (pts \n'''.format(
                    points[0].x, #0
                    points[0].y, #1
                    stroke_width, #2
                    layer, #3
                )
            )
            originx = points[0].x
            originy = points[0].y
            for point in points:
                point.x = point.x-originx
                point.y = point.y-originy
        else:
            self.output_file.write( "\n  (fp_poly\n    (pts \n" )


    #------------------------------------------------------------------------

    def _write_polygon_point( self, point ):

        if self._create_pad:
            self.output_file.write("  ")

        self.output_file.write(
            "      (xy {} {})\n".format( point.x, point.y )
        )


    #------------------------------------------------------------------------

    def _write_polygon_segment( self, p, q, layer, stroke_width ):

        self.output_file.write(
            """\n  (fp_line
    (start {} {})
    (end {} {})
    (layer {})
    (width {})
  )""".format(
                p.x, p.y,
                q.x, q.y,
                layer,
                stroke_width,
            )
        )


    #------------------------------------------------------------------------

#----------------------------------------------------------------------------

def get_arguments():
    ''' Return an instance of pythons argument parser
    with all the command line functionalities arguments
    '''

    parser = argparse.ArgumentParser(
        description = (
            'Convert Inkscape SVG drawings to KiCad footprint modules.'
        )
    )

    mux = parser.add_mutually_exclusive_group(required=True)

    mux.add_argument(
        '-i', '--input-file',
        type = str,
        dest = 'input_file_name',
        metavar = 'FILENAME',
        help = "Name of the SVG file",
    )

    parser.add_argument(
        '-o', '--output-file',
        type = str,
        dest = 'output_file_name',
        metavar = 'FILENAME',
        help = "Name of the module file",
    )

    parser.add_argument(
        '-c', '--center',
        dest = 'center',
        action = 'store_const',
        const = True,
        help = "Center the module to the center of the bounding box",
        default = False,
    )

    parser.add_argument(
        '-P', '--convert-pads',
        dest = 'convert_to_pads',
        action = 'store_const',
        const = True,
        help = "Convert any artwork on Cu layers to pads",
        default = False,
    )

    parser.add_argument(
        '-v', '--verbose',
        dest = 'verbose_print',
        action = 'store_const',
        const = True,
        help = "Print more verbose messages",
        default = False,
    )

    parser.add_argument(
        '--debug',
        dest = 'debug_print',
        action = 'store_const',
        const = True,
        help = "Print debug level messages",
        default = False,
    )

    parser.add_argument(
        '-x', '--exclude-hidden',
        dest = 'ignore_hidden_layers',
        action = 'store_const',
        const = True,
        help = "Do not export hidden layers",
        default = False,
    )

    parser.add_argument(
        '-d', '--dpi',
        type = int,
        dest = 'dpi',
        metavar = 'DPI',
        help = "DPI of the SVG file (int)",
        default = DEFAULT_DPI,
    )

    parser.add_argument(
        '-f', '--factor',
        type = float,
        dest = 'scale_factor',
        metavar = 'FACTOR',
        help = "Scale paths by this factor",
        default = 1.0,
    )

    parser.add_argument(
        '-p', '--precision',
        type = float,
        dest = 'precision',
        metavar = 'PRECISION',
        help = "Smoothness for approximating curves with line segments. Input is the approximate length for each line segment in SVG pixels (float)",
        default = 10.0,
    )
    parser.add_argument(
        '--format',
        type = str,
        dest = 'format',
        metavar = 'FORMAT',
        choices = [ 'legacy', 'pretty' ],
        help = "Output module file format (legacy|pretty)",
        default = 'pretty',
    )

    parser.add_argument(
        '--name', '--module-name',
        type = str,
        dest = 'module_name',
        metavar = 'NAME',
        help = "Base name of the module",
        default = "svg2mod",
    )

    parser.add_argument(
        '--units',
        type = str,
        dest = 'units',
        metavar = 'UNITS',
        choices = [ 'decimal', 'mm' ],
        help = "Output units, if output format is legacy (decimal|mm)",
        default = 'mm',
    )

    parser.add_argument(
        '--value', '--module-value',
        type = str,
        dest = 'module_value',
        metavar = 'VALUE',
        help = "Value of the module",
        default = "G***",
    )

    parser.add_argument(
        '-F', '--default-font',
        type = str,
        dest = 'default_font',
        help = "Default font to use if the target font in a text element cannot be found",
    )

    mux.add_argument(
        '-l', '--list-fonts',
        dest = 'list_fonts',
        const = True,
        default = False,
        action = "store_const",
        help = "List all fonts that can be found in common locations",
    )

    return parser.parse_args(), parser

    #------------------------------------------------------------------------

#----------------------------------------------------------------------------
if __name__ == "__main__":
    main()

logging.root.setLevel(logging.DEBUG)

#----------------------------------------------------------------------------
