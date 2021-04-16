# Original code from: https://github.com/sparkfunX/Buzzard
import sys
import os
from svgpathtools import Line, QuadraticBezier, Path, Arc
from freetype import Face
from svgelements import Path as elPath, Matrix
import svgwrite
import math
import subprocess
import re
import xml.etree.ElementTree as XMLET
import shlex

from fontTools.ttLib import ttFont
from fontTools.pens.recordingPen import RecordingPen
from fontTools.pens.basePen import decomposeQuadraticSegment


from svg2mod import svg2mod, svg


class Buzzard():
    def __init__(self):
        self.fontName = 'FredokaOne'
        self.verbose = True
        self.scaleFactor = 0.04
        self.subSampling = 0.1
        self.traceWidth = 0.1
        self.leftCap = ''                # Used to store cap shape for left side of tag
        self.rightCap = ''               # Used to store cap shape for right side of tag
        
    
    def generate(self, inString):
        t = self.renderLabel(inString)
        
        mod = Svg2Points(precision=1.0)
        mod.add_svg_element(t)
        mod.write()

        return mod.polys




    # ******************************************************************************
    #
    # Create SVG Document containing properly formatted inString
    #
    #
    def renderLabel(self, inString):
        

        # mod is the kicad footprint writer class
        # t is an svg Text element
        t = svg.Text()
        
        
        t.set_font(font="DejaVu Sans", italic=False, bold=True)
        # Add multiline text
        
        t.add_text(inString)
        #t.add_text("Hello,")
        #t.add_text("World", origin=svg.Point(0,15))
        
        # This needs to be called to convert raw text to useable path elements
        t.convert_to_path()

        bbox = t.bbox()
        height = bbox[1].y - bbox[0].y
        buff = t.size/5
        height += buff*2
        width = bbox[1].x - bbox[0].x

        # Create outline around text with one side being an arc and the other a point
        # these are svg path commands lowercase letters mean relative moves and uppercase are absolute moves
        pstr = f"M {bbox[0].x},{bbox[0].y-buff} a {height/2},{height/2} 0 0 0 0,{height} h {width} l {height/2},{height/-2} l {height/-2},{height/-2} h {-1*width} z"

        p = svg.Path()
        p.parse(pstr)
        t.paths.append([p])


        # Print kicad footprint text created by running mod.write()
        #print(mod.raw_file_data)

        return t

    def create_v6_footprint(self):
        
        out = "(footprint \"buzzardLabel\"\n" + \
            " (layer \"F.Cu\")\n" + \
            " (attr board_only exclude_from_pos_files exclude_from_bom)\n"

        for poly in self.polys:

            if len(poly) < 2:
                return

            scriptLine = " (fp_poly (pts"
            for points in poly:
                scriptLine += " (xy {0:.4f} {1:.4f})".format(points[0],points[1])
            scriptLine += ") (layer \"F.SilkS\") (width 0.05) (fill solid))\n"
        
            out += scriptLine + '\n'
    
        out += ')\n'
        return out

    def create_v5_footprint(self):
        
        out = "(module Symbol:buzzardLabel (layer F.Cu) (tedit 0)\n" + \
              " (attr virtual)\n"

        for poly in self.polys:

            if len(poly) < 2:
                return

            scriptLine = " (fp_poly (pts"
            for points in poly:
                scriptLine += " (xy {0:.4f} {1:.4f})".format(points[0],points[1])
            out += scriptLine + ") (layer F.SilkS) (width 0.05))\n"
        
            
        out += ')\n'
        return out

class Svg2Points( svg2mod.Svg2ModExport ):
    ''' A child of Svg2ModExport that implements
    specific functionality for creating points to render
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
        svg2mod_import = svg2mod.Svg2ModImport(),
        file_name = None,
        center = True,
        scale_factor = 1.0,
        precision = 20.0,
        use_mm = True,
        dpi = svg2mod.DEFAULT_DPI,
    ):
        super( Svg2Points, self ).__init__(
            svg2mod_import,
            file_name,
            center,
            scale_factor,
            precision,
            use_mm,
            dpi,
            pads = False,
        )

        self.include_reverse = False
        self.polys = []


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
        pass
    
    #------------------------------------------------------------------------

    def _write_module_header(
        self, label_size, label_pen,
        reference_y, value_y, front,
    ):
        pass


    #------------------------------------------------------------------------

    def _write_module_footer( self, front ):
        pass


    #------------------------------------------------------------------------

    def _write_modules( self ):
        self._write_module( front = True )

        if self.include_reverse:
            self._write_module( front = False )



    #------------------------------------------------------------------------

    def _write_polygon( self, points, layer, fill, stroke, stroke_width ):
        self._write_polygon_filled(
            points, layer
        )


    #------------------------------------------------------------------------

    def _write_polygon_footer( self, layer, stroke_width ):
        pass


    #------------------------------------------------------------------------

    def _write_polygon_header( self, points, layer ):
        self.polys.append([])
        pass


    #------------------------------------------------------------------------

    def _write_polygon_point( self, point ):
        self.polys[-1].append(point)


    #------------------------------------------------------------------------

    def _write_polygon_segment( self, p, q, layer, stroke_width ):
        self._write_polygon_point(p)
        self._write_polygon_point(q)

