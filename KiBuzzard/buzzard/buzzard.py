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
        self.rightCap = ''               # Used to store cap shape for right side of tag-

        self.svgText = None

#        svg.Text.load_system_fonts()
        fnt_lib = svg.Text._system_fonts
        if fnt_lib is None:
            fnt_lib = {}

        # Load included fonts 
        typeface_path = os.path.join(os.path.dirname(os.path.realpath(__file__)), 'typeface')
        for entry in os.listdir(typeface_path):
            entry_path = os.path.join(typeface_path, entry)
            
            if not entry_path.endswith('.ttf'):
                continue

            fnt_lib[os.path.splitext(os.path.basename(entry_path))[0]] = {'Path':entry_path}
      
    def generate(self, inString):
        self.svgText = self.renderLabel(inString)
        
        mod = Svg2Points(svg2mod.Svg2ModImport(), precision=1.0, scale_factor=self.scaleFactor, center=True)
        mod.add_svg_element(self.svgText)
        mod.write()

        return mod.polys




    # ******************************************************************************
    #
    # Create SVG Document containing properly formatted inString
    #
    #
    def renderLabel(self, inString):
        # t is an svg Text element
        t = svg.Text()

        #t.set_font(font="DejaVu Sans", italic=False, bold=True)
        t.set_font(self.fontName)
        # Add multiline text
        
        for i,s in enumerate(inString.split('\n')):
            t.add_text(s, origin=svg.Point(0, 15*i))
        
        # This needs to be called to convert raw text to useable path elements
        t.convert_to_path()
    
        bbox = t.bbox()
        height = bbox[1].y - bbox[0].y
        buff = t.size/5
        height += buff*2
        width = bbox[1].x - bbox[0].x

        # Create outline around text 
        if (self.leftCap != '') & (self.rightCap != ''):
            pstr = f'M {bbox[0].x},{bbox[0].y-buff} '
            
            if self.leftCap == 'round':
                pstr += f'a {height/2},{height/2} 0 0 0 0,{height} '
            if self.leftCap == 'square':
                pstr += f'l {-buff},0 l 0,{height} l {buff},0 '
            if self.leftCap == 'fslash':
                pstr += f'l {-buff},0 l {-2*buff},{height} l {3*buff},0 '
            if self.leftCap == 'bslash':
                pstr += f'l {-3*buff},0 l {2*buff},{height} l {buff},0 '
            if self.leftCap == 'pointer':
                pstr += f'l {height/-2},{height/2} l {height/2},{height/2} '
            if self.leftCap == 'flagtail':
                pstr += f'l {-1*buff - height/2},0 l {height/2},{height/2} l {height/-2},{height/2} l {buff + height/2},0'
                
            pstr += f'h {width} '
            
            if self.rightCap == 'round':
                pstr += f'a {height/2},{height/2} 0 0 0 0,{-height} '
            if self.rightCap == 'square':
                pstr += f'l {buff},0 l 0,{-height} l {-buff},0 '
            if self.rightCap == 'fslash':
                pstr += f'l {buff},0 l {2*buff},{-height} l {-3*buff},0 '
            if self.rightCap == 'bslash':
                pstr += f'l {3*buff},0 l {-2*buff},{-height} l {-buff},0 '
            if self.rightCap == 'pointer':
                pstr += f'l {height/2},{height/-2} l {height/-2},{height/-2} '
            if self.rightCap == 'flagtail':
                pstr += f'l {1*buff + height/2},0 l {height/-2},{height/-2} l {height/2},{height/-2} l {-buff -height/2},0'

            pstr += f'h {-1*width} z'

            p = svg.Path()
            p.parse(pstr)
            t.paths.append([p])

        return t

    def create_v6_footprint(self):
        mod = svg2mod.Svg2ModExportPretty(precision=1.0, scale_factor=self.scaleFactor, center=True)
        mod.add_svg_element(self.svgText)
        mod.write()
        return mod.raw_file_data

    def create_v5_footprint(self):
        return ""

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

