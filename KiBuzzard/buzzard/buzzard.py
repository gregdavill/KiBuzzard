# Original code from: https://github.com/sparkfunX/Buzzard
import os
import time
import copy

from fontTools.ttLib import ttFont
from fontTools.pens.recordingPen import RecordingPen
from fontTools.pens.basePen import decomposeQuadraticSegment

from svg2mod import svg, svg2mod
from svg2mod.exporter import Svg2ModExport, Svg2ModExportLatest, DEFAULT_DPI
from svg2mod.importer import Svg2ModImport

class Padding():
    def __init__(self):
        self.left = 0.001
        self.right = 0.001
        self.top = 0.001
        self.bottom = 0.001        


class Buzzard():
    def __init__(self):
        self.fontName = 'FredokaOne'
        self.layer = 'F.Cu'
        self.verbose = True
        self.scaleFactor = 0.04
        self.subSampling = 0.1
        self.traceWidth = 0.1
        self.padding = Padding()
        self.width = 0
        self.alignment = ''
        self.leftCap = ''                # Used to store cap shape for left side of tag
        self.rightCap = ''               # Used to store cap shape for right side of tag-
        self.svgText = None
        #self.SystemFonts = svg.Text._system_fonts

        #svg.Text.load_system_fonts()

        fnt_lib = svg.Text._system_fonts
        if fnt_lib is None:
            fnt_lib = {}

        # Load included fonts 
        typeface_path = os.path.join(os.path.dirname(os.path.realpath(__file__)), 'typeface')
        for entry in os.listdir(typeface_path):
            entry_path = os.path.join(typeface_path, entry)
            
            if not (entry_path.endswith('.ttf') or entry_path.endswith('.otf')):
                continue

            fnt_lib[os.path.splitext(os.path.basename(entry_path))[0]] = {'Path':entry_path}

    def generate(self, inString):
        self.svgText = self.renderLabel(inString)
        self.svgText.style['fill'] = True
        
        mod = Svg2Points(Svg2ModImport(), precision=1.0, scale_factor=1.0, center=True)
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

        t.set_font(self.fontName)
        
        for i,s in enumerate(inString.split('\n')):
            t.add_text(s, origin=svg.Point(0, 15*i))
        
        # This needs to be called to convert raw text to useable path elements
        t.convert_to_path()
    
        # bounds check padding
        padding = self.padding
        for attr in ['left', 'right', 'top', 'bottom']:
            if getattr(padding,attr) <= 0: setattr(padding, attr, 0.001)

        bbox = t.bbox()
        height = bbox[1].y - bbox[0].y
        
        height += padding.top + padding.bottom
        width = bbox[1].x - bbox[0].x
        textWidth = (width + (self.padding.left + self.padding.right))


        fixedWidth = max(0, self.width - (self.padding.left + self.padding.right))
        width = max(width, fixedWidth)

        alignmentOffset = 0
        if self.alignment == 'Left' or fixedWidth != width:
            alignmentOffset = 0
        elif self.alignment == 'Center':
            alignmentOffset = (self.width - textWidth)/2
        elif self.alignment == 'Right':
            alignmentOffset = (self.width - textWidth)
            
        # Create outline around text 
        if (self.leftCap != '') & (self.rightCap != ''):
            pstr = "M {},{} ".format(bbox[0].x - alignmentOffset, bbox[0].y-padding.top)
            pstr += "h {} ".format(-padding.left)
            
            if self.leftCap == 'round':
                pstr += "a {},{} 0 0 0 0,{} ".format(height/2,height/2,height)
            if self.leftCap == 'square':
                pstr += "v {} ".format(height)
            if self.leftCap == 'fslash':
                pstr += "l {},{} h {} ".format(-0.3*height, height, 0.3*height)
            if self.leftCap == 'bslash':
                pstr += "h {} l {},{} ".format(-0.3*height, 0.3*height, height)
            if self.leftCap == 'pointer':
                pstr += "l {},{} l {},{} ".format(height/-3, height/2, height/3, height/2)
            if self.leftCap == 'flagtail':
                pstr += "h {} l {},{} l {},{} h {}".format(height/-3, height/3, height/2, height/-3, height/2, height/3)

            pstr += "h {} ".format(padding.left)        
            pstr += "h {} ".format(width)
            pstr += "h {} ".format(padding.right)
            
            if self.rightCap == 'round':
                pstr += "a {},{} 0 0 0 0,{} ".format(height/2, height/2,-height)
            if self.rightCap == 'square':
                pstr += "v {} ".format(-height)
            if self.rightCap == 'fslash':
                pstr += "l {},{} h {} ".format(0.3*height, -height, -0.3*height)
            if self.rightCap == 'bslash':
                pstr += "h {} l {},{} ".format(0.3*height, -0.3*height, -height)
            if self.rightCap == 'pointer':
                pstr += "l {},{} l {},{} ".format(height/3, height/-2, height/-3, height/-2)
            if self.rightCap == 'flagtail':
                pstr += "h {} l {},{} l {},{} h {}".format(height/3, height/-3, height/-2, height/3, height/-2, height/-3)
            
            pstr += "h {} ".format(-padding.right)
            pstr += "h {} z".format(-1*width)

            p = svg.Path()
            p.parse(pstr)
            t.paths.append([p])

        return t

    def create_v6_footprint(self, parm_text=None):
        name = "kibuzzard-{:8X}".format(int(round(time.time())))
        mod = Svg2ModExportLatestCustom(Svg2ModImport(module_name=name, module_value="G***"), precision=1.0, scale_factor=self.scaleFactor, center=True, params=parm_text)
        if self.layer == "F.Cu/F.Mask":
            print(self.svgText)
            mod.add_svg_element(self.svgText, layer="F.Cu")
            offset_text = copy.copy(self.svgText)
            offset_text.style["stroke-width"] = 0.2
            mod.add_svg_element(offset_text, layer="F.Mask")
        else:
            mod.add_svg_element(self.svgText, layer=self.layer)
        mod.write()
        return mod.raw_file_data


class Svg2ModExportLatestCustom( Svg2ModExportLatest ):
    
    def __init__(
        self,
        svg2mod_import = Svg2ModImport(),
        file_name = None,
        center = True,
        scale_factor = 1.0,
        precision = 20.0,
        use_mm = True,
        dpi = DEFAULT_DPI,
        params = None
    ):
        self.params = params
        super( Svg2ModExportLatestCustom, self ).__init__(
            svg2mod_import,
            file_name,
            center,
            scale_factor,
            precision,
            use_mm,
            dpi,
            pads = False,
        )


    def _write_library_intro( self, cmdline ):
        self.output_file.write( """(footprint {0} (layer F.Cu) (tedit {1:8X}) (generator kibuzzard)
    (attr board_only exclude_from_pos_files exclude_from_bom)
    (descr "{2}")
    (tags "kb_params={3}")
    """.format(
                self.imported.module_name, #0
                int( round( #1
                    os.path.getctime( self.imported.file_name ) if self.imported.file_name else time.time()
                ) ),
                "Generated with KiBuzzard", #2
                self.params, #3
            )
        )
    
    def _write_module_header(
        self, label_size, label_pen,
        reference_y, value_y, front,
    ):
        super()._write_module_header(0, 0, reference_y, value_y, front)

    


class Svg2Points( Svg2ModExport ):
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
        svg2mod_import = Svg2ModImport(),
        file_name = None,
        center = True,
        scale_factor = 1.0,
        precision = 20.0,
        use_mm = True,
        dpi = DEFAULT_DPI,
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

        if len(points) > 2:
            self._write_polygon_filled(
                points, layer
            )
            return
 
        if len(points) < 3:
            print("  Not writing non-polygon with no stroke.")
        else:
            print("  Polygon has no stroke or fill. Skipping.")


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


    def _write_thru_hole( self, circle, layer ):
        pass

