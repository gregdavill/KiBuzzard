# Copyright (C) 2013 -- CJlano < cjlano @ free.fr >
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
A SVG parser with tools to convert an XML svg file
to objects that can be simplified into points.
'''

import copy
import inspect
import itertools
import json
import logging
import math
import operator
import os
import platform
import re
import sys
import xml.etree.ElementTree as etree
from typing import Iterable, List, Tuple

from fontTools.misc import loggingTools
from fontTools.pens.svgPathPen import SVGPathPen
from fontTools.ttLib import ttFont
from svg2mod.coloredlogger import logger

from .geometry import Angle, Bezier, MoveTo, Point, Segment, simplify_segment

svg_ns = '{http://www.w3.org/2000/svg}'

# Regex commonly used
number_re = r'[-+]?(?:\d+(?:\.\d*)?|\.\d+)(?:[eE][-+]?\d+)?'
unit_re = r'em|ex|px|in|cm|mm|pt|pc|%'

# styles of interest and their defaults
svg_defaults = {
        "fill":"black",
        "fill-opacity":"1",
        "stroke":"none",
        "stroke-width":"1px",
        "stroke-opacity":"1",
    }

# Unit converter
unit_convert = {
        None: 1,           # Default unit (same as pixel)
        'px': 1,           # px: pixel. Default SVG unit
        'em': 10,          # 1 em = 10 px FIXME
        'ex': 5,           # 1 ex =  5 px FIXME
        'in': 96,          # 1 in = 96 px
        'cm': 96 / 2.54,   # 1 cm = 1/2.54 in
        'mm': 96 / 25.4,   # 1 mm = 1/25.4 in
        'pt': 96 / 72.0,   # 1 pt = 1/72 in
        'pc': 96 / 6.0,    # 1 pc = 1/6 in
        '%' :  1 / 100.0   # 1 percent
        }

# Logging spammed 'Unable to find font because no font was specified.'
# this allows it to only print the error once before muting it for that run.
_font_warning_sent = False


class Transformable:
    '''Abstract class for objects that can be geometrically drawn & transformed'''

    # This list is all styles that should have the transformation matrix applied
    transformable_styles = ["stroke-width"]

    def __init__(self, elt=None, parent_styles=None):
        # a 'Transformable' is represented as a list of Transformable items
        self.items = []
        self.id = hex(id(self))
        self.name = ""
        self.fill_even_odd = False
        # Unit transformation matrix on init
        self.matrix = Matrix()
        self.xscale = 1
        self.yscale = 1
        self.style = svg_defaults.copy() if not parent_styles and not isinstance(parent_styles, dict) else parent_styles.copy()
        self.rotation = 0
        self.viewport = Point(800, 600) # default viewport is 800x600
        if elt is not None:
            self.id = elt.get('id', self.id)

            # get inkscape:label as self.name
            for ident, value in elt.attrib.items():

                ident = self.parse_name( ident )
                if ident[ "name" ] == "label":
                    self.name = value
                    break
            # self.name isn't set so try setting name to id
            if self.name == '':
                self.name == self.id

            # set fill_even_odd if property set
            self.fill_even_odd = elt.get("fill-rule", '').lower() == 'evenodd'
            if self.fill_even_odd:
                logger.warning(f"Found unsupported attribute: 'fill-rule=evenodd' for {repr(self)}")

            # Find attributes of interest. The are overwritten by styles
            for style_key in svg_defaults:
                self.style[style_key] = elt.get(style_key, self.style[style_key])

            # parse styles and save as dictionary.
            if elt.get('style'):
                for style in elt.get('style').split(";"):
                    if style.find(":") == -1:
                        self.style[name] = None
                    else:
                        nv = style.split(":")
                        name = nv[ 0 ].strip()
                        value = nv[ 1 ].strip()
                        if name in self.transformable_styles:
                            value = list(re.search(r'(\d+\.?\d*)(\D+)?', value).groups())
                            self.style[name] = float(value[0])
                            if value[1] and value[1] not in unit_convert:
                                logger.warning("Style '{}' has an unexpected unit: {}".format(style, value[1]))
                        else:
                            self.style[name] = value

            # Parse transform attribute to update self.matrix
            self.get_transformations(elt)

        if self.style.get("display") == "none":
            self.hidden = True

    @staticmethod
    def parse_name( tag ):
        '''Read and return name from xml data'''
        m = re.match( r'({(.+)})?(.+)', tag )
        return {
            'namespace' : m.group( 2 ),
            'name' : m.group( 3 ),
        }

    def bbox(self):
        '''Bounding box of all points'''
        b_boxes = [x.bbox() for x in self.items]
        if len( b_boxes ) < 1:
            return (Point(0, 0), Point(0, 0))
        xmin = min([b[0].x for b in b_boxes])
        xmax = max([b[1].x for b in b_boxes])
        ymin = min([b[0].y for b in b_boxes])
        ymax = max([b[1].y for b in b_boxes])

        return (Point(xmin,ymin), Point(xmax,ymax))

    # Parse transform field
    def get_transformations(self, elt):
        '''Take an xml element and parse transformation commands
        then apply the matrix and set any needed variables
        '''
        t = elt.get('transform')
        if t is None: return

        svg_transforms = [
                'matrix', 'translate', 'scale', 'rotate', 'skewX', 'skewY']

        # match any SVG transformation with its parameter (until final parenthesis)
        # [^)]*    == anything but a closing parenthesis
        # '|'.join == OR-list of SVG transformations
        transforms = re.findall(
                '|'.join([x + r'[^)]*\)' for x in svg_transforms]), t)

        for t in transforms:
            op, arg = t.split('(')
            op = op.strip()
            # Keep only numbers
            arg = [float(x) for x in re.findall(number_re, arg)]
            logger.debug('transform: ' + op + ' '+ str(arg))

            if op == 'matrix':
                self.matrix *= Matrix(arg)

            if op == 'translate':
                tx = arg[0]
                if len(arg) == 1: ty = 0
                else: ty = arg[1]
                self.matrix *= Matrix([1, 0, 0, 1, tx, ty])

            if op == 'scale':
                sx = arg[0]
                if len(arg) == 1: sy = sx
                else: sy = arg[1]
                self.xscale *= sx
                self.yscale *= sy
                self.matrix *= Matrix([sx, 0, 0, sy, 0, 0])

            if op == 'rotate':
                self.rotation += arg[0]
                cos_a = math.cos(math.radians(arg[0]))
                sin_a = math.sin(math.radians(arg[0]))
                if len(arg) != 1:
                    tx, ty = arg[1:3]
                    self.matrix *= Matrix([1, 0, 0, 1, tx, ty])
                self.matrix *= Matrix([cos_a, sin_a, -sin_a, cos_a, 0, 0])
                if len(arg) != 1:
                    self.matrix *= Matrix([1, 0, 0, 1, -tx, -ty])

            if op == 'skewX':
                tana = math.tan(math.radians(arg[0]))
                self.matrix *= Matrix([1, 0, tana, 1, 0, 0])

            if op == 'skewY':
                tana = math.tan(math.radians(arg[0]))
                self.matrix *= Matrix([1, tana, 0, 1, 0, 0])

    def transform_styles(self, matrix):
        '''Any style in this classes transformable_styles
        will be scaled by the provided matrix.
        If it has a unit type it will convert it to the proper value first.
        '''
        for style in self.transformable_styles:
            if self.style.get(style):
                has_units = re.search(r'\D', self.style[style] if isinstance(self.style[style], str) else '')
                if has_units is None:
                    self.style[style] = float(self.style[style]) * ((matrix.xscale()+matrix.yscale())/2)
                else:
                    unit = has_units.group().lower()
                    self.style[style] = float(re.search(r'\d', self.style[style]).group()) * unit_convert.get(unit, 1) * ((matrix.xscale()+matrix.yscale())/2)


    def transform(self, matrix=None):
        '''Apply the provided matrix. Default (None)
        If no matrix is supplied then recursively apply
        it's already existing matrix to all items.
        '''
        if matrix is None:
            matrix = self.matrix
        else:
            matrix *= self.matrix
        self.transform_styles(matrix)
        for x in self.items:
            x.transform(matrix)

    def length(self, v, mode='xy'):
        '''Return generic 2 dimensional length of svg element'''
        # Handle empty (non-existing) length element
        if v is None:
            return 0

        # Get length value
        m = re.search(number_re, v)
        if m: value = m.group(0)
        else: raise TypeError(v + 'is not a valid length')

        # Get length unit
        m = re.search(unit_re, v)
        if m: unit = m.group(0)
        else: unit = None

        if unit == '%':
            if mode == 'x':
                return float(value) * unit_convert[unit] * self.viewport.x
            if mode == 'y':
                return float(value) * unit_convert[unit] * self.viewport.y
            if mode == 'xy':
                return float(value) * unit_convert[unit] * self.viewport.x # FIXME

        return float(value) * unit_convert[unit]

    def xlength(self, x):
        '''Length of element's x component'''
        return self.length(x, 'x')
    def ylength(self, y):
        '''Length of element's y component'''
        return self.length(y, 'y')

    def flatten(self):
        '''Flatten the SVG objects nested list into a flat (1-D) list,
        removing Groups'''
        # http://rightfootin.blogspot.fr/2006/09/more-on-python-flatten.html
        # Assigning a slice a[i:i+1] with a list actually replaces the a[i]
        # element with the content of the assigned list
        i = 0
        flat = copy.deepcopy(self.items)
        while i < len(flat):
            while isinstance(flat[i], Group):
                flat[i:i+1] = flat[i].items
            i += 1
        return flat

class Svg(Transformable):
    '''SVG class: use parse to parse a file'''
    # class Svg handles the <svg> tag
    # tag = 'svg'

    def __init__(self, filename=None):
        self.viewport_scale = 1
        Transformable.__init__(self)
        if filename:
            self.parse(filename)

    def parse(self, filename:str):
        '''Read provided svg xml file and
        append all svg element to items list
        '''
        self.filename = filename
        tree = etree.parse(filename)
        self.root = tree.getroot()
        if self.root.tag != svg_ns + 'svg':
            raise TypeError('file %s does not seem to be a valid SVG file', filename)

        # Create a top Group to group all other items (useful for viewBox elt)
        top_group = Group()
        self.items.append(top_group)

        # SVG dimension
        width = self.xlength(self.root.get('width'))
        height = self.ylength(self.root.get('height'))

        # update viewport
        top_group.viewport = Point(width, height)

        # viewBox
        if self.root.get('viewBox') is not None:
            view_box = re.findall(number_re, self.root.get('viewBox'))

            # If the document somehow doesn't have dimensions get if from viewBox
            if self.root.get('width') is None or self.root.get('height') is None:
                width = float(view_box[2]) - float(view_box[0])
                height = float(view_box[3]) - float(view_box[1])
                logger.debug("Unable to find width or height properties. Using viewBox.")

            sx = width / (float(view_box[2]) - float(view_box[0]))
            sy = height / (float(view_box[3]) - float(view_box[1]))
            tx = -float(view_box[0])
            ty = -float(view_box[1])
            self.viewport_scale = round((float(view_box[2]) - float(view_box[0]))/width, 6)
            top_group.matrix = Matrix([sx, 0, 0, sy, tx, ty])
        if ( self.root.get("width") is None or self.root.get("height") is None ) \
                and self.root.get("viewBox") is None:
            logger.critical("Fatal Error: Unable to find SVG dimensions. Exiting.")
            sys.exit(-1)

        # Parse XML elements hierarchically with groups <g>
        top_group.append(self.root)

        self.transform()

    def title(self):
        '''Returns svg title if exists. Otherwise try to return filename'''
        t = self.root.find(svg_ns + 'title')
        if t is not None:
            return t
        return os.path.splitext(os.path.basename(self.filename))[0]

    def json(self):
        '''Return a dictionary of children items'''
        return self.items


class Group(Transformable):
    '''Handle svg <g> elements
    The name and hidden attributes are stored in self.name
    and self.hidden respectively. These can be manually set
    if object is not initialized with an xml element.
    '''
    # class Group handles the <g> tag
    tag = 'g'

    def __init__(self, elt=None, *args, **kwargs):
        Transformable.__init__(self, elt, *args, **kwargs)

    def append(self, element):
        '''Convert and append xml element(s) to items list
        element is expected to be iterable.
        If an svg non xml object needs to be appended
        then interface directly with the items list:
                group.items.append(svg_object)
        '''
        for elt in element:
            elt_class = svgClass.get(elt.tag, None)
            if elt_class is None:
                logger.debug('No handler for element %s' % elt.tag)
                continue
            # instantiate elt associated class (e.g. <path>: item = Path(elt)
            item = elt_class(elt, parent_styles=self.style)
            # Apply group matrix to the newly created object
            # Actually, this is effectively done in Svg.__init__() through call to
            # self.transform(), so doing it here will result in the transformations
            # being applied twice.
            #item.matrix = self.matrix * item.matrix
            item.viewport = self.viewport

            self.items.append(item)
            # Recursively append if elt is a <g> (group)
            if elt.tag == svg_ns + 'g':
                item.append(elt)

    def __repr__(self):
        return '<Group ' + self.id + " ({})".format( self.name ) + '>: ' + repr(self.items)

    def json(self):
        '''Return json formatted dictionary of group'''
        return {'Group ' + self.id + " ({})".format( self.name ) : self.items}

class Matrix:
    ''' SVG transformation matrix and its operations
    a SVG matrix is represented as a list of 6 values [a, b, c, d, e, f]
    (named vect hereafter) which represent the 3x3 matrix
    ((a, c, e)
     (b, d, f)
     (0, 0, 1))
    see http://www.w3.org/TR/SVG/coords.html#EstablishingANewUserSpace '''

    def __init__(self, vect=None):
        # Unit transformation vect by default
        if vect is None:
            vect = [1, 0, 0, 1, 0, 0]
        if len(vect) != 6:
            raise ValueError("Bad vect size %d" % len(vect))
        self.vect = list(vect)

    def __mul__(self, other):
        '''Matrix multiplication'''
        if isinstance(other, Matrix):
            a = self.vect[0] * other.vect[0] + self.vect[2] * other.vect[1]
            b = self.vect[1] * other.vect[0] + self.vect[3] * other.vect[1]
            c = self.vect[0] * other.vect[2] + self.vect[2] * other.vect[3]
            d = self.vect[1] * other.vect[2] + self.vect[3] * other.vect[3]
            e = self.vect[0] * other.vect[4] + self.vect[2] * other.vect[5] \
                    + self.vect[4]
            f = self.vect[1] * other.vect[4] + self.vect[3] * other.vect[5] \
                    + self.vect[5]
            return Matrix([a, b, c, d, e, f])

        if isinstance(other, Point):
            x = other.x * self.vect[0] + other.y * self.vect[2] + self.vect[4]
            y = other.x * self.vect[1] + other.y * self.vect[3] + self.vect[5]
            return Point(x,y)

        return NotImplemented

    def __str__(self):
        return str(self.vect)

    def xscale(self):
        '''Return the rotated x scalar value'''
        return self.vect[0]/abs(self.vect[0]) * math.sqrt(self.vect[0]**2 + self.vect[2]**2)
    def yscale(self):
        '''Return the rotated x scalar value'''
        return self.vect[3]/abs(self.vect[3]) * math.sqrt(self.vect[1]**2 + self.vect[3]**2)
    def rot(self):
        '''Return the angle of rotation from the matrix.

        https://math.stackexchange.com/questions/13150/extracting-rotation-scale-values-from-2d-transformation-matrix
        '''
        if self.vect[0] != 0:
            return Angle(math.atan2(-self.vect[2], self.vect[0]))
        if self.vect[3] != 0:
            return Angle(math.atan2(self.vect[1], self.vect[3]))
        return 0



class Path(Transformable):
    '''SVG <path> tag handler
    self.items contains all objects for path instructions.
    Calling .parse(...) will append new path instruction
    objects to items list.
    '''
    # class Path handles the <path> tag
    tag = 'path'
    COMMANDS = 'MmZzLlHhVvCcSsQqTtAa'

    def __init__(self, elt=None, *args, **kwargs):
        Transformable.__init__(self, elt, *args, **kwargs)
        if elt is not None:
            self.parse(elt.get('d'))

    def parse(self, path_str:str):
        """Parse svg path string and build elements list"""

        path_list = re.findall(number_re + r"|\ *[%s]\ *" % Path.COMMANDS, path_str)

        path_list.reverse()

        command = None
        current_pt = Point(0,0)
        start_pt = None

        while path_list:
            if path_list[-1].strip() in Path.COMMANDS:
                last_command = command
                command = path_list.pop().strip()
                absolute = (command == command.upper())
                command = command.upper()
            else:
                if command is None:
                    raise ValueError("No command found at %d" % len(path_list))

            if command == 'M':
            # MoveTo
                x = path_list.pop()
                y = path_list.pop()
                pt = Point(x, y)
                if absolute:
                    current_pt = pt
                else:
                    current_pt += pt
                start_pt = current_pt

                self.items.append(MoveTo(current_pt))

                # MoveTo with multiple coordinates means LineTo
                command = 'L'

            elif command == 'Z':
            # Close Path
                l = Segment(current_pt, start_pt)
                self.items.append(l)
                current_pt = start_pt

            elif command in 'LHV':
            # LineTo, Horizontal & Vertical line
                # extra coord for H,V
                if absolute:
                    x,y = current_pt.coord()
                else:
                    x,y = (0,0)

                if command in 'LH':
                    x = path_list.pop()
                if command in 'LV':
                    y = path_list.pop()

                pt = Point(x, y)
                if not absolute:
                    pt += current_pt

                self.items.append(Segment(current_pt, pt))
                current_pt = pt

            elif command in 'CQ':
                dimension = {'Q':3, 'C':4}
                bezier_pts = []
                bezier_pts.append(current_pt)
                for _ in range(1,dimension[command]):
                    x = path_list.pop()
                    y = path_list.pop()
                    pt = Point(x, y)
                    if not absolute:
                        pt += current_pt
                    bezier_pts.append(pt)

                self.items.append(Bezier(bezier_pts))
                current_pt = pt

            elif command in 'TS':
                # number of points to read
                num_pts = {'T':1, 'S':2}
                # the control point, from previous Bezier to mirror
                ctrl_pt = {'T':1, 'S':2}
                # last command control
                last = {'T': 'QT', 'S':'CS'}

                bezier_pts = []
                bezier_pts.append(current_pt)

                if last_command in last[command]:
                    pt0 = self.items[-1].control_point(ctrl_pt[command])
                else:
                    pt0 = current_pt
                pt1 = current_pt
                # Symmetrical of pt1 against pt0
                bezier_pts.append(pt1 + pt1 - pt0)

                for _ in range(0,num_pts[command]):
                    x = path_list.pop()
                    y = path_list.pop()
                    pt = Point(x, y)
                    if not absolute:
                        pt += current_pt
                    bezier_pts.append(pt)

                self.items.append(Bezier(bezier_pts))
                current_pt = pt

            elif command == 'A':
                rx = path_list.pop()
                ry = path_list.pop()
                x_rotation = path_list.pop()
                # Arc flags are not necessarily separated numbers
                flags = path_list.pop().strip()
                large_arc_flag = flags[0]
                if large_arc_flag not in '01':
                    logger.error("Arc parsing failure")
                    break

                if len(flags) > 1:  flags = flags[1:].strip()
                else:               flags = path_list.pop().strip()
                sweep_flag = flags[0]
                if sweep_flag not in '01':
                    logger.error("Arc parsing failure")
                    break

                if len(flags) > 1:  x = flags[1:]
                else:               x = path_list.pop()
                y = path_list.pop()
                end_pt = Point(x, y)
                if not absolute: end_pt += current_pt
                self.items.append(
                    Arc(current_pt, rx, ry, x_rotation, large_arc_flag, sweep_flag, end_pt))
                current_pt = end_pt

            else:
                path_list.pop()

    def __str__(self):
        return '\n'.join(str(x) for x in self.items)

    def __repr__(self):
        return '<Path ' + self.id + '>'

    def segments(self, precision=0) -> List[Segment]:
        '''Return a list of segments, each segment is ended by a MoveTo.
           A segment is a list of Points'''
        ret = []
        # group items separated by MoveTo
        for moveTo, group in itertools.groupby(self.items,
                lambda x: isinstance(x, MoveTo)):
            # Use only non MoveTo item
            if not moveTo:
                # Generate segments for each relevant item
                seg = [x.segments(precision) for x in group]
                # Merge all segments into one
                ret.append(list(itertools.chain.from_iterable(seg)))

        return ret

    def simplify(self, precision:float) -> List[Segment]:
        '''Simplify segment with precision:
           Remove any point which are ~aligned'''
        ret = []
        for seg in self.segments(precision):
            ret.append(simplify_segment(seg, precision))

        return ret

class Polygon(Path):
    '''SVG <polygon> tag handler
    A polygon has a space separated list of points in format x,y.
    '''

    # class Polygon handles the <polygon> tag
    tag = 'polygon'

    def __init__(self, elt, *args, **kwargs):
        self.path_len = -1
        Transformable.__init__(self, elt, *args, **kwargs)
        if elt is not None:
            if elt.get('pathLength'):
                self.path_len = int(elt.get('pathLength'))
            self.parse(elt.get('points'))

    def parse(self, point_str):
        '''Split the points from point_str and create a list of segments'''
        start_pt = None
        current_pt = None

        points = re.findall(number_re, point_str)
        points.reverse()
        while points:
            start_pt = current_pt
            current_pt = Point(points.pop(), points.pop())

            if start_pt and current_pt:
                self.items.append(Segment(start_pt, current_pt))

    def __repr__(self) -> str:
        return '<Polygon ' + self.id + '>'

    def segments(self, precision=0) -> List[Segment]:
        ''' Return list of segments '''

        seg = [x.segments(precision) for x in self.items]

        return [list(itertools.chain.from_iterable(seg))]


class Ellipse(Transformable):
    '''SVG <ellipse> tag handler
    An ellipse is created by the center point (center)
    the x radius (rx) and the y radius (ry).
    Setting these values will change the ellipse
    regardless if it was created by an xml element.

    If provided xml has a 'd' attribute or path
    then this will also parse that.
        (This is for support of inkscape arc objects)
    '''
    # class Ellipse handles the <ellipse> tag
    tag = 'ellipse'

    def __init__(self, elt=None, *args, **kwargs):
        Transformable.__init__(self, elt, *args, **kwargs)
        self.arc = False
        if elt is not None:
            self.center = Point(self.xlength(elt.get('cx')),
                                self.ylength(elt.get('cy')))
            self.rx = self.length(elt.get('rx'))
            self.ry = self.length(elt.get('ry'))
            if elt.get('d') is not None:
                self.arc = True
                self.path = Path(elt)
                self.path_str = elt.get('d')
        else:
            self.center = Point(0,0)
            self.rx = 0
            self.ry = 0

    def __repr__(self):
        return '<Ellipse ' + self.id + '>'

    def bbox(self) -> Tuple[Point, Point]:
        '''Approximate the bounding box for the given ellipse by
        decomposing the ellipse into a small number of segments.

        While there may be better ways of computing this
        it is much easier to compute the bounding box of segments.
        '''
        if self.arc:
            return Transformable.bbox(self)

        points = self.segments((self.rx+self.ry) / 8)
        if isinstance(points[0], Iterable):
            points = list(itertools.chain.from_iterable(points))

        xmin = min([p.x for p in points])
        xmax = max([p.x for p in points])
        ymin = min([p.y for p in points])
        ymax = max([p.y for p in points])

        return (Point(xmin,ymin),Point(xmax,ymax))

    def transform(self, matrix=None):
        '''Apply the provided matrix. Default (None)
        If no matrix is supplied then recursively apply
        it's already existing matrix to all items.
        Also apply to center, rx, and ry
        '''
        if matrix is None:
            matrix = self.matrix
        else:
            matrix *= self.matrix
        self.transform_styles(matrix)

        self.center = matrix * self.center
        self.rx = matrix.xscale()*self.rx
        self.ry = matrix.yscale()*self.ry
        self.rotation += math.degrees(matrix.rot().angle)
        self.matrix= matrix

    def P(self, t) -> Point:
        '''Return a Point on the Ellipse for t in [0..1] or % from angle 0 to the full circle.
        Rotation is not handled in this function.
        '''
        x = self.center.x + self.rx * math.cos(2 * math.pi * t)
        y = self.center.y + self.ry * math.sin(2 * math.pi * t)
        return Point(x,y)

    def segments(self, precision=0) -> List[Segment]:
        '''Flatten all curves to segments with target length of precision'''
        if self.arc:
            segments = self.path.segments(precision)
            return segments
        if max(self.rx, self.ry) < precision:
            return [[self.center]]

        p = [(0,self.P(0)), (1, self.P(1))]
        d = 2 * max(self.rx, self.ry)

        while d > precision:
            for (t1,_),(t2,_) in zip(p[:-1],p[1:]):
                t = t1 + (t2 - t1)/2.
                p.append((t, self.P(t)))
            p.sort(key=operator.itemgetter(0))
            d = Segment(p[0][1],p[1][1]).length()

        ret = [x.rot(math.radians(self.rotation), x=self.center.x, y=self.center.y) for __,x in p]
        return [ret]

    def simplify(self, __):
        '''Return self because a 3 point representation is already simple'''
        return self

# An arc is an ellipse with a beginning and an end point instead of an entire circumference
class Arc(Ellipse):
    '''This inherits from Ellipse but does not have a svg tag
    Because there are no arc tags this class converts the
    path data for an arc into an object that can be flattened.
    '''

    def __init__(self, start_pt, rx, ry, x_rotation, large_arc_flag, sweep_flag, end_pt):
        Ellipse.__init__(self, None)
        try:
            self.rx = float(rx)
            self.ry = float(ry)
            self.rotation = float(x_rotation)
            self.large_arc_flag = large_arc_flag=='1'
            self.sweep_flag = sweep_flag=='1'
        except:
            pass
        self.end_pts = [start_pt, end_pt]
        self.angles = []

        self.calculate_center()

    def __repr__(self):
        return '<Arc ' + self.id + '>'

    def calculate_center(self):
        '''Calculate the center point of the arc from the
        non-intuitively provided data in an svg path.

        This is done by creating rotated ellipses around
        the start and end point. Then choosing the correct
        intersection point based on the two arc choosing flags.
        If there is no intersection then the center is the midpoint
        between the beginning and end points.
        '''
        angle = Angle(math.radians(self.rotation))

        # set some variables that are used often to decrease size of final equations
        pts = self.end_pts
        cs2 = 2*angle.cos*angle.sin*(math.pow(self.ry, 2) - math.pow(self.rx, 2))
        rs = (math.pow(self.ry*angle.sin, 2) + math.pow(self.rx*angle.cos, 2))
        rc = (math.pow(self.ry*angle.cos, 2) + math.pow(self.rx*angle.sin, 2))


        # Create a line that passes through both intersection points
        y = -pts[0].x*(cs2) + pts[1].x*cs2 - 2*pts[0].y*rs + 2*pts[1].y*rs
        # Round to prevent floating point errors
        y = round(y, 10)
        # A vertical line will break the program so we cannot calculate with these equations
        if y != 0:
            # Finish calculating the line
            m = ( -2*pts[0].x*rc + 2*pts[1].x*rc - pts[0].y*cs2 + pts[1].y*cs2 ) / -y
            b = (
                math.pow(pts[0].x,2)*rc - math.pow(pts[1].x,2)*rc + pts[0].x*pts[0].y*cs2 -
                pts[1].x*pts[1].y*cs2 + math.pow(pts[0].y,2)*(rs) - math.pow(pts[1].y,2)*rs
            ) / -y

            # Now that we have a line we can setup a quadratic equation to solve for all intersection points
            qa = rc + m*cs2 + math.pow(m,2)*rs
            qb = -2*pts[0].x*rc + b*cs2 - pts[0].y*cs2 - m*pts[0].x*cs2 + 2*m*b*rs - 2*pts[0].y*m*rs
            qc = (
                math.pow(pts[0].x,2)*rc - b*pts[0].x*cs2 + pts[0].x*pts[0].y*cs2 + math.pow(b,2)*rs -
                2*b*pts[0].y*rs + math.pow(pts[0].y,2)*rs - math.pow(self.rx*self.ry, 2)
            )

        else:
            # When the slope is vertical we need to calculate with x instead of y
            x = (pts[0].x+pts[1].x)/2
            m=0
            b=x

            # The quadratic formula but solving for y instead of x and only when the slope is vertical
            qa = rs
            qb =  x*cs2 - pts[0].x*cs2 - 2*pts[0].y*rs
            qc = (
                math.pow(x,2)*rc - 2*x*pts[0].x*rc + math.pow(pts[0].x,2)*rc - x*pts[0].y*cs2 +
                pts[0].x*pts[0].y*cs2 + math.pow(pts[0].y,2)*rs - math.pow(self.rx*self.ry, 2)
            )

        # This is the value to see how many real solutions the quadratic equation has.
        # if root is negative then there are only imaginary solutions or no real solutions
        # if the root is 0 then there is one solution
        # otherwise there are two solutions
        root = math.pow(qb, 2) - 4*qa*qc

        # If there are no roots then we need to scale the arc to fit the points
        if root < 0:
            # Center point
            point = Point((pts[0].x + pts[1].x)/2,(pts[0].y + pts[1].y)/2)
            # Angle between center and one of the end points adjusted to remove rotation from original data
            ptAng = math.atan2(self.end_pts[0].y-point.y, self.end_pts[0].x-point.x) - angle.angle
            # Adjust the angle to compensate for ellipse irregularity
            ptAng = math.atan((self.rx/self.ry) * math.tan(ptAng))
            # Calculate scaling factor between provided ellipse and actual end points
            radius = math.sqrt(math.pow(self.rx*math.cos(ptAng),2) + math.pow(self.ry*math.sin(ptAng),2))
            dist = math.sqrt( math.pow(self.end_pts[0].x-point.x, 2)+math.pow(self.end_pts[0].y-point.y, 2))
            factor = dist/radius
            self.rx *= factor
            self.ry *= factor


        # finish solving the quadratic equation and find the corresponding points on the intersection line
        elif root == 0:
            x_root = (-qb+math.sqrt(root))/(2*qa)
            point = Point(x_root, x_root*m + b)
        # Using the provided large_arc and sweep flags to choose the correct root
        else:
            x_roots = [(-qb+math.sqrt(root))/(2*qa), (-qb-math.sqrt(root))/(2*qa)]
            points = [Point(x_roots[0], x_roots[0]*m + b), Point(x_roots[1], x_roots[1]*m + b)]
            # Calculate the angle of the beginning point to the end point

            # If counterclockwise the two angles are the angle is within 180 degrees of each other:
            #   and no flags are set use the first center
            #   and the sweep flag is set use the second
            #   the large arc flag is set invert the previous selection

            # Don't save the angles because they are calculated from the first possible center.
            # This may change so we'll just recalculate the angles later on
            angles = []
            for pt in pts:
                pt = Point(pt.x-points[0].x, pt.y-points[0].y)
                pt.rot(math.radians(-self.rotation))
                pt = Point(pt.x/self.rx, pt.y/self.ry)
                angles.append(math.atan2(pt.y,pt.x)%(math.pi*2))
            target = 0
            if self.sweep_flag:
                target = 0 if (angles[0] - angles[1]) < 0 or (angles[0] - angles[1]) > math.pi else 1
            else:
                target = 1 if (angles[0] - angles[1]) < 0 or (angles[0] - angles[1]) > math.pi else 0

            point = points[target if not self.large_arc_flag else target ^ 1 ]


        # Swap the x and y results from when the intersection line is vertical because we solved for y instead of x
        # Also remove any insignificant floating point errors
        if y == 0:
            point = Point(round(point.y, 10), round(point.x, 10))
        else:
            point = Point(round(point.x, 10), round(point.y, 10))
        self.center = point

        # Calculate start and end angle of the un-rotated arc
        if len(self.angles) < 2:
            self.angles = []
            for pt in self.end_pts:
                pt = Point(pt.x-self.center.x, pt.y-self.center.y)
                pt = pt.rot(math.radians(-self.rotation))
                pt = Point(pt.x/self.rx, pt.y/self.ry)
                self.angles.append(math.atan2(pt.y,pt.x))

        if not self.sweep_flag and self.angles[0] < self.angles[1]:
            self.angles[0] += 2*math.pi
        elif self.sweep_flag and self.angles[1] < self.angles[0]:
            self.angles[1] += 2*math.pi

    def transform(self, matrix=None):
        super().transform(matrix)
        self.end_pts[0] = self.matrix * self.end_pts[0]
        self.end_pts[1] = self.matrix * self.end_pts[1]

    def segments(self, precision=0) -> List[Segment]:
        '''This returns segments as expected by the
        Path object. (A list of points. Not a list of lists of points)
        '''
        if max(self.rx, self.ry) < precision:
            return self.end_pts
        return Ellipse.segments(self, precision)[0]

    def P(self, t) -> Point:
        '''Return a Point on the Arc for t in [0..1] where t is the % from
        the start angle to the end angle.

        Final angle transformation is handled in Ellipse.segments
        '''
        x = self.center.x + self.rx * math.cos(((self.angles[1] - self.angles[0]) * t) + self.angles[0])
        y = self.center.y + self.ry * math.sin(((self.angles[1] - self.angles[0]) * t) + self.angles[0])
        return Point(x,y)



# A circle is a special type of ellipse where rx = ry = radius
class Circle(Ellipse):
    '''SVG <circle> tag handler
    This is an ellipse by rx and ry are equal.
    '''
    # class Circle handles the <circle> tag
    tag = 'circle'

    def __init__(self, elt=None, *args, **kwargs):
        if elt is not None:
            elt.set('rx', elt.get('r'))
            elt.set('ry', elt.get('r'))
        Ellipse.__init__(self, elt, *args, **kwargs)

    def __repr__(self):
        return '<Circle ' + self.id + '>'

class Rect(Path):
    '''SVG <rect> tag handler
    This decompiles a rectangle svg xml element into
    essentially a path with 4 segments.

    P1 and P2 are the opposing corner points.

    As of now corner radii are not supported.
    '''
    # class Rect handles the <rect> tag
    tag = 'rect'

    def __init__(self, elt=None, *args, **kwargs):
        Transformable.__init__(self, elt, *args, **kwargs)
        if elt is not None:
            p = Point(self.xlength(elt.get('x')),
                            self.ylength(elt.get('y')))
            width = self.xlength(elt.get("width"))
            height = self.xlength(elt.get("height"))

            rx = self.xlength(elt.get('rx'))
            ry = self.xlength(elt.get('ry'))
            if not rx: rx = ry if ry else 0
            if not ry: ry = rx if rx else 0
            if rx > width/2: rx = width/2
            if ry > height/2: ry = width/2
            if rx or ry:
                cmd = f'''M{p.x+rx} {p.y} a{rx} {ry} 0 0 0 {-rx} {ry} v{height-(ry*2)}
                a{rx} {ry} 0 0 0 {rx} {ry}   h{width-(rx*2)}
                a{rx} {ry} 0 0 0 {rx} {-ry}  v{-(height-(ry*2))}
                a{rx} {ry} 0 0 0 {-rx} {-ry} h{-(width-(rx*2))} z'''
            else:
                cmd = f'M{p.x},{p.y}v{height}h{width}v{-height}h{-width}'

            self.p = p
            self.width = width
            self.height = height
            self.rx = rx
            self.ry = ry

            self.parse(cmd)

    def __repr__(self):
        return '<Rect ' + self.id + '>'

class Line(Transformable):
    '''SVG <line> tag handler

    This is essentially a wrapper around the Segment class
    '''
    # class Line handles the <line> tag
    tag = 'line'

    def __init__(self, elt=None, *args, **kwargs):
        Transformable.__init__(self, elt, *args, **kwargs)
        if elt is not None:
            self.P1 = Point(self.xlength(elt.get('x1')),
                            self.ylength(elt.get('y1')))
            self.P2 = Point(self.xlength(elt.get('x2')),
                            self.ylength(elt.get('y2')))
            self.segment = Segment(self.P1, self.P2)

    def __repr__(self):
        return '<Line ' + self.id + '>'

    def bbox(self) -> Tuple[Point, Point]:
        '''Bounding box'''
        xmin = min([p.x for p in (self.P1, self.P2)])
        xmax = max([p.x for p in (self.P1, self.P2)])
        ymin = min([p.y for p in (self.P1, self.P2)])
        ymax = max([p.y for p in (self.P1, self.P2)])

        return (Point(xmin,ymin), Point(xmax,ymax))

    def transform(self, matrix=None):
        '''Apply the provided matrix. Default (None)
        If no matrix is supplied then recursively apply
        it's already existing matrix to all items.
        '''
        if matrix is None:
            matrix = self.matrix
        else:
            matrix *= self.matrix
        self.transform_styles(matrix)

        self.P1 = matrix * self.P1
        self.P2 = matrix * self.P2
        self.segment = Segment(self.P1, self.P2)

    def segments(self, __=0) -> List[Segment]:
        '''Return the segment of the line'''
        return [self.segment.segments()]


class Text(Transformable):
    '''SVG <text> tag handler
    Take provided xml text element and convert using ttf and otf fonts
    into path element that can be used.

    setting Text.default_font is important. If the listed font
    cannot be found this is the fall back value.

    A list of fonts installed on the system can be found by calling
        Text.load_system_fonts(...)
    this keeps all found font in memory after first time call to
    improve performance.

    All distinct text element, those that have different start locations
    or fonts, are stored in text in a list.

    Adding new strings can be done by calling add_text(...)
    and removing strings is done by removing the item from the text list

    Once all strings are properly configured in the text list running
    convert_to_path will append a list of path elements to the paths variable

    The bounding box will not report a valid size until convert_to_path has been ran.
    '''
    # class Text handles the <text> tag
    tag = 'text'

    default_font = None
    _system_fonts = {}
    _os_font_paths = {
        "Darwin": ["/Library/Fonts", "~/Library/Fonts"],
        "Linux": ["/usr/share/fonts","/usr/local/share/fonts","~/.local/share/fonts"],
        "Windows": ["C:/Windows/Fonts", "~/AppData/Local/Microsoft/Windows/Fonts"]
    }

    def __init__(self, elt=None, parent=None, *args, **kwargs):
        Transformable.__init__(self, elt, *args, **kwargs)

        self.bbox_points = [Point(0,0), Point(0,0)]
        self.paths = []

        if elt is not None:
            self.parse(elt, parent)
            if parent is None:
                self.convert_to_path(auto_transform=False)
        else:
            self.origin = Point(0,0)
            self.font_family = Text.default_font
            self.size = 12
            self.bold = "normal"
            self.italic = "normal"
            if self.font_family:
                self.font_file = self.find_font_file()
            self.text = []

    def set_font(self, font=None, bold=None, italic=None, size=None):
        '''Set the font of the current text element.
        font is expected to be a string of the font family name.
        bold is expected Boolean
        italic is expected Boolean
        size is expected int, but can work with string ending in px
        '''
        font = font if font else self.font_family
        bold = bold if bold else (self.bold.lower() != "normal")
        italic = italic if italic else (self.italic.lower() != "normal")
        size = size if size else self.size
        if isinstance(size, str):
            size = float(size.strip("px"))

        self.font_family = font
        self.size = size
        self.bold = "normal" if not bold else "bold"
        self.italic = "normal" if not italic else "italic"
        self.font_file = self.find_font_file()


    def add_text(self, text, origin=Point(0,0), inherit=True):
        '''Add text the list of text objects
        if the origin is not different then the parents origin or
        inherit is set to False then a new text element will
        be created an added to the strings tuple in the text list.
        '''
        if origin == self.origin and inherit:
            self.text.append((text, self))
        else:
            new_line = Text()
            new_line.set_font(
                font=self.font_family,
                bold=(self.bold != "normal"),
                italic=(self.italic != "normal"),
                size=self.size
            )

            new_line.origin = origin
            self.text.append((text, new_line))


    def parse(self, elt, parent):
        '''Read the useful data from the xml element.
        Since text tags can have nested text tags
        parse can be called multiple times for one text tag.
        However all nested tags should have parent set so
        they can inherit and append the proper values
        from their immediate parent
        '''
        x = elt.get('x')
        y = elt.get('y')

        # It seems that any values in style that override these values take precedence
        self.font_configs = {
            "font-family": elt.get('font-family'),
            "font-size": elt.get('font-size'),
            "font-weight": elt.get('font-weight'),
            "font-style": elt.get('font-style'),
        }
        for style in self.style:
            if style in self.font_configs.keys() and self.style[style]:
                self.font_configs[style] = self.style[style]

        if isinstance(self.font_configs["font-size"], str):
            self.font_configs["font-size"] = float(self.font_configs["font-size"].strip("px"))

        for config in self.font_configs:
            if self.font_configs[config] is None and parent is not None:
                self.font_configs[config] = parent.font_configs[config]

        self.font_family = self.font_configs["font-family"]
        self.size = self.font_configs["font-size"]
        self.bold = self.font_configs["font-weight"]
        self.italic = self.font_configs["font-style"]

        self.font_file = self.find_font_file()

        if parent is not None:
            x = parent.origin.x if x is None else float(x)
            y = parent.origin.y if y is None else float(y)
        x = 0 if x is None else float(x)
        y = 0 if y is None else float(y)
        self.origin = Point(x,y)

        self.text = [] if elt.text is None else [(elt.text, self)]
        for child in list(elt):
            Text(child, self)
        if parent is not None:
            parent.text.extend(self.text)
            if elt.tail is not None:
                parent.text.append((elt.tail, parent))

        del self.font_configs


    def find_font_file(self):
        '''This will look through the indexed fonts and
        attempt to find one with a matching font name and text style.

        -- Faux font styles are not supported ==

        If the styling cannot be found it will fall back to either
        italic or bold if both were asked for and there wasn't a style
        with both or regular if italic or bold are set but not found.

        If the target font cannot be found then the default is used if set and found.
        '''
        if self.font_family is None:
            if Text.default_font is None:
                global _font_warning_sent
                if not _font_warning_sent:
                    logger.error("Unable to find font because no font was specified.")
                    _font_warning_sent = True
                return None
            self.font_family = Text.default_font
        fonts = [fnt.strip().strip("'") for fnt in self.font_family.split(",")]
        if Text.default_font is not None: fonts.append(Text.default_font)

        font_files = None
        target_font = None
        for fnt in fonts:
            if Text.load_system_fonts().get(fnt) is not None:
                target_font = fnt
                font_files = Text.load_system_fonts().get(fnt)
                break
        if font_files is None:
            # We are unable to find a font and since there is no default font stop building font data
            logger.error("Unable to find font(s) \"{}\"{}".format(
                self.font_family,
                " and no default font specified" if Text.default_font is None else f" or default font \"{Text.default_font}\""
            ))
            self.paths = []
            return

        bold = self.bold is not None and self.bold.lower() != "normal"
        italic = self.italic is not None and self.italic.lower() != "normal"

        reg = ["Regular", "Book"]
        bol = ["Bold", "Demibold"]
        ita = ["Italic", "Oblique"]

        search = reg
        if bold and not italic:
            search = bol
        elif italic and not bold:
            search = ita
        elif italic and bold:
            search = [f"{b} {i}" if n == 0 else f"{i} {b}" for b in bol for i in ita for n in range(2)]
        tar_font = list(filter(None, [font_files.get(style) for style in search]))
        if len(tar_font) == 0 and len(font_files.keys()) == 1:
            tar_font = [font_files[list(font_files.keys())[0]]]
            logger.warning("Font \"{}\" does not natively support style \"{}\" using \"{}\" instead".format(
                target_font, search[0], list(font_files.keys())[0]))
        elif len(tar_font) == 0 and italic and bold:
            orig_search = search[0]
            search = []
            search.extend(ita)
            search.extend(bol)
            search.extend(reg)
            search.extend(list(font_files.keys()))
            for style in search:
                if font_files.get(style) is not None:
                    tar_font = [font_files[style]]
                    logger.warning("Font \"{}\" does not natively support style \"{}\" using \"{}\" instead".format(
                        target_font, orig_search, style))
                    break
        return tar_font[0]


    def convert_to_path(self, auto_transform=True):
        ''' Read the vector data from the ttf/otf file and
        convert it into a path string for each letter and
        parse the path string by a Path instance.

        if auto_transform is True then this calls self.transform()
        at the end to apply all transformations on the paths.

        This should only be called once so double check transform()
        is never called elsewhere.
        '''
        self.paths = []
        if not self.text: return
        prev_origin = self.text[0][1].origin

        offset = Point(prev_origin.x, prev_origin.y)
        for text, attrib in self.text:

            if attrib.font_file is None or attrib.font_family is None:
                continue
            size = attrib.size
            ttf = ttFont.TTFont(attrib.font_file)
            offset.y = attrib.origin.y + ttf["head"].unitsPerEm
            scale = size/ttf["head"].unitsPerEm

            if prev_origin != attrib.origin:
                prev_origin = attrib.origin
                offset.x = attrib.origin.x

            path = []
            for char in text:

                path_buff = ""
                try: glf = ttf.getGlyphSet()[ttf.getBestCmap()[ord(char)]]
                except KeyError:
                    logger.warning('Unsupported character in <text> element "{}"'.format(char))
                    #txt = txt.replace(char, "")
                    continue

                pen = SVGPathPen(ttf.getGlyphSet())
                glf.draw(pen)

                for cmd in pen._commands:
                    path_buff += cmd + ' '

                if len(path_buff) > 0:
                    path.append(Path())
                    path[-1].parse(path_buff)
                    # Apply the scaling then the translation
                    translate = Matrix([1,0,0,-1,offset.x,attrib.origin.y]) * Matrix([scale,0,0,scale,0,0])
                    # This queues the translations until .transform() is called
                    path[-1].matrix =  translate * path[-1].matrix

                offset.x += (scale*glf.width)

            self.paths.append(path)
        if auto_transform:
            self.transform()

    def bbox(self) -> Tuple[Point, Point]:
        '''Find the bounding box of all the paths that make
        each letter.
        This will only work if there are available paths.
        '''
        if self.paths is None or len(self.paths) == 0:
            return [Point(0,0),Point(0,0)]

        b_boxes = [path.bbox() for paths in self.paths for path in paths]

        return (
            Point(min(b_boxes, key=lambda v: v[0].x)[0].x, min(b_boxes, key=lambda v: v[0].y)[0].y),
            Point(max(b_boxes, key=lambda v: v[1].x)[1].x, max(b_boxes, key=lambda v: v[1].y)[1].y),
        )

    def transform(self, matrix=None):
        '''Apply the provided matrix. Default (None)
        If no matrix is supplied then recursively apply
        it's already existing matrix to all items.
        '''
        if matrix is None:
            matrix = self.matrix
        else:
            matrix *= self.matrix
        self.transform_styles(matrix)

        self.origin = matrix * self.origin
        for paths in self.paths:
            for path in paths:
                path.transform(matrix)

    def segments(self, precision=0) -> List[Segment]:
        '''Get a list of all points in all paths
        with provide precision.
        This will only work if there are available paths.
        '''
        segments = []
        for paths in self.paths:
            for path in paths:
                segments.extend(path.segments(precision))
        return segments

    @staticmethod
    def load_system_fonts(reload:bool=False) -> List[dict]:
        '''Find all fonts in common locations on the file system
        To properly read all fonts they need to be parsed so this
        is inherently slow on systems with many fonts.
        To prevent long parsing time all the results are cached
        and the cached results are returned next time this function
        is called.
        If a force reload of all indexed fonts is desirable setting
        reload to True will clear the cache and re-index the system.
        '''
        if reload:
            Text._system_fonts = {}
        if len(Text._system_fonts.keys()) < 1:
            fonts_files = []
            logger.info("Loading system fonts.")
            for path in Text._os_font_paths[platform.system()]:
                try:
                    fonts_files.extend([os.path.join(dp, f) for dp, dn, fn in os.walk(os.path.expanduser(path)) for f in fn])
                except:
                    pass

            for font_file in fonts_files:
                try:
                    font = ttFont.TTFont(font_file)
                    name = font["name"].getName(1,1,0).toStr()
                    style = font["name"].getName(2,1,0).toStr()
                    if Text._system_fonts.get(name) is None:
                        Text._system_fonts[name] = {style:font_file}
                    elif Text._system_fonts[name].get(style) is None:
                        Text._system_fonts[name][style] = font_file
                except:
                    pass
            logger.debug(f"  Found {len(Text._system_fonts.keys())} fonts in system")
        return Text._system_fonts


class JSONEncoder(json.JSONEncoder):
    ''' overwrite JSONEncoder for svg classes which have defined a .json() method '''
    def default(self, obj):
        ''' overwrite default function to handle svg classes '''
        if not isinstance(obj, tuple(svgClass.values() + [Svg])):
            return json.JSONEncoder.default(self, obj)

        if not hasattr(obj, 'json'):
            return repr(obj)

        return obj.json()

## Code executed on module load ##

# Make fontTools more quiet
loggingTools.configLogger(level=logging.INFO)


# SVG tag handler classes are initialized here
# (classes must be defined before)

svgClass = {}
# Register all classes with attribute 'tag' in svgClass dictionary
for name, cls in inspect.getmembers(sys.modules[__name__], inspect.isclass):
    tag = getattr(cls, 'tag', None)
    if tag:
        svgClass[svg_ns + tag] = cls

