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

from .modules.svgstring2path import string2paths

# Takes an x/y tuple and returns a complex number
def tuple_to_imag(t):
    return t[0] + t[1] * 1j

# The freetype library doesn't reliably report the
# bounding box size of a glyph, so instead we figure
# it out and store it here
class boundingBox:
    def __init__(self, xMax, yMax, xMin, yMin):
        self.xMax = xMax
        self.yMax = yMax
        self.xMin = xMin
        self.yMin = yMin

# Global variables (most of these are rewritten by CLI self later)
SCALE = 1 / 90
SUBSAMPLING = 1
SIMPLIFY = 0.1 * SCALE
SIMPLIFYHQ = False
TRACEWIDTH = '0.1'


class Buzzard():
    def __init__(self):
        #self.fontName = 'mplus-1mn-medium'
        #self.fontName = 'UbuntuMono-B'
        self.fontName = 'mplus-1c-light'
        self.verbose = True
        self.scaleFactor = 0.04
        self.originPos = 'cc'
        self.subSampling = 0.1
        self.traceWidth = 0.1
        self.exportHeight = 0

    
    def generate(self, inString):
        paths, attributes, svg_attributes = string2paths(self.renderLabel(inString).tostring())
        return self.drawSVG(svg_attributes, attributes, paths)


    # ******************************************************************************
    #
    # Create SVG Document containing properly formatted inString
    #
    #
    def renderLabel(self, inString):
        dwg = svgwrite.Drawing()    # SVG drawing in memory
        strIdx = 0                  # Used to iterate over inString
        xOffset = 100               # Cumulative character placement offset
        yOffset = 0                 # Cumulative character placement offset
        charSizeX = 8               # Character size constant 
        charSizeY = 8               # Character size constant 
        baseline = 170              # Y value of text baseline
        leftCap = ''                # Used to store cap shape for left side of tag
        rightCap = ''               # Used to store cap shape for right side of tag
        removeTag = False           # Track whether characters need to be removed from string ends
        glyphBounds = []            # List of boundingBox objects to track rendered character size
        finalSegments = []          # List of output paths 
        escaped = False             # Track whether the current character was preceded by a '\'
        lineover = False            # Track whether the current character needs to be lined over
        lineoverList = []

        # If we can't find the typeface that the user requested, we have to quit
        try:
            face = Face(os.path.dirname(os.path.abspath(__file__)) + '/typeface/' + self.fontName + '.ttf')
            face.set_char_size(charSizeX,charSizeY,200,200)
        except Exception as e:
            print(e)
            print("WARN: No Typeface found with the name " + self.fontName + ".ttf")
            sys.exit(0)  # quit Python

        # If the typeface that the user requested exists, but there's no position table for it, we'll continue with a warning
        try: 
            table = __import__('KiBuzzard.KiBuzzard.buzzard.typeface.' + self.fontName, globals(), locals(), ['glyphPos'])
            glyphPos = table.glyphPos
            spaceDistance = table.spaceDistance
        except:
            glyphPos = 0
            spaceDistance = 60
            print("WARN: No Position Table found for this typeface. Composition will be haphazard at best.")

        # If there's lineover text, drop the text down to make room for the line
        dropBaseline = False
        a = False
        x = 0
        while x < len(inString):
            if x > 0 and inString[x] == '\\':
                a = True
                if x != len(inString)-1:
                    x += 1
            if inString[x] == '!' and not a:
                dropBaseline = True
            a = False
            x += 1
        if dropBaseline:
            baseline = 190

        # Detect and Remove tag style indicators
        if inString[0] == '(':
            leftCap = 'round'
            removeTag = True
        elif inString[0] == '[':
            leftCap = 'square'
            removeTag = True
        elif inString[0] == '<':
            leftCap = 'pointer'
            removeTag = True
        elif inString[0] == '>':
            leftCap = 'flagtail'
            removeTag = True
        elif inString[0] == '/':
            leftCap = 'fslash'
            removeTag = True
        elif inString[0] == '\\':
            leftCap = 'bslash'
            removeTag = True

        if removeTag:
            inString = inString[1:]

        removeTag = False

        if inString[-1] == ')':
            rightCap = 'round'
            removeTag = True
        elif inString[-1] == ']':
            rightCap = 'square'
            removeTag = True
        elif inString[-1] == '>':
            rightCap = 'pointer'
            removeTag = True
        elif inString[-1] == '<':
            rightCap = 'flagtail'
            removeTag = True
        elif inString[-1] == '/':
            rightCap = 'fslash'
            removeTag = True
        elif inString[-1] == '\\':
            rightCap = 'bslash'
            removeTag = True    

        if removeTag:
            inString = inString[:len(inString)-1]

        # Draw and compose the glyph portion of the tag 
        for charIdx in range(len(inString)):
            # Check whether this character is a space
            if inString[charIdx] == ' ':
                glyphBounds.append(boundingBox(0,0,0,0)) 
                xOffset += spaceDistance
                continue
            # Check whether this character is a backslash that isn't escaped 
            # and isn't the first character (denoting a backslash-shaped tag)
            if inString[charIdx] == '\\' and charIdx > 0 and not escaped:
                glyphBounds.append(boundingBox(0,0,0,0))
                escaped = True
                continue
            # If this is a non-escaped '!' mark the beginning of lineover
            if inString[charIdx] == '!' and not escaped:
                glyphBounds.append(boundingBox(0,0,0,0))
                lineover = True
                # If we've hit the end of the string but not the end of the lineover
                # go ahead and finish it out
                if charIdx == len(inString)-1 and len(lineoverList) > 0:
                    linePaths = []
                    linePaths.append(Line(start=complex(lineoverList[0], 10), end=complex(xOffset,10)))
                    linePaths.append(Line(start=complex(xOffset,10), end=complex(xOffset,30)))
                    linePaths.append(Line(start=complex(xOffset,30), end=complex(lineoverList[0], 30)))
                    linePaths.append(Line(start=complex(lineoverList[0], 30), end=complex(lineoverList[0], 10)))
                    linepath = Path(*linePaths)
                    linepath = elPath(linepath.d())
                    finalSegments.append(linepath)
                    lineover = False
                    lineoverList.clear()
                continue
            # All special cases end in 'continue' so if we've gotten here we can clear our flags      
            if escaped:
                escaped = False

            face.load_char(inString[charIdx])   # Load character curves from font
            outline = face.glyph.outline        # Save character curves to var
            y = [t[1] for t in outline.points]
            # flip the points
            outline_points = [(p[0], max(y) - p[1]) for p in outline.points]
            start, end = 0, 0
            paths = []
            box = 0
            yOffset = 0

            for i in range(len(outline.contours)):
                end = outline.contours[i]
                points = outline_points[start:end + 1]
                points.append(points[0])
                tags = outline.tags[start:end + 1]
                tags.append(tags[0])
                segments = [[points[0], ], ]
                box = boundingBox(points[0][0],points[0][1],points[0][0],points[0][1])
                for j in range(1, len(points)):
                    if not tags[j]: # if this point is off-path
                        if tags[j-1]: # and the last point was on-path
                            segments[-1].append(points[j]) # toss this point onto the segment
                        elif not tags[j-1]: # and the last point was off-path
                            # get center point of two
                            newPoint = ((points[j][0] + points[j-1][0]) / 2.0,
                                        (points[j][1] + points[j-1][1]) / 2.0)
                            segments[-1].append(newPoint) # toss this new point onto the segment
                            segments.append([newPoint, points[j], ]) # and start a new segment with the new point and this one
                    elif tags[j]: # if this point is on-path
                        segments[-1].append(points[j]) # toss this point onto the segment
                        if  j < (len(points) - 1):
                            segments.append([points[j], ]) # and start a new segment with this point if we're not at the end    

                for segment in segments:
                    if len(segment) == 2:
                        paths.append(Line(start=tuple_to_imag(segment[0]),
                                        end=tuple_to_imag(segment[1])))

                    elif len(segment) == 3:
                        paths.append(QuadraticBezier(start=tuple_to_imag(segment[0]),
                                                    control=tuple_to_imag(segment[1]),
                                                    end=tuple_to_imag(segment[2])))
                start = end + 1

            # Derive bounding box of character
            for segment in paths:
                i = 0
                while i < 10:
                    point = segment.point(0.1*i)
                    if point.real > box.xMax:
                        box.xMax = point.real
                    if point.imag > box.yMax:
                        box.yMax = point.imag
                    if point.real < box.xMin:
                        box.xMin = point.real
                    if point.imag < box.yMin:
                        box.yMin = point.imag
                    i += 1

            glyphBounds.append(box)
            path = Path(*paths)
            if glyphPos != 0:
                try:
                    xOffset += glyphPos[inString[charIdx]].real
                    yOffset = glyphPos[inString[charIdx]].imag
                except: 
                    pass
            if lineover and len(lineoverList) == 0:
                lineoverList.append(xOffset)
                lineover = False
                
            if (lineover and len(lineoverList) > 0):
                linePaths = []
                linePaths.append(Line(start=complex(lineoverList[0], 10), end=complex(xOffset,10)))
                linePaths.append(Line(start=complex(xOffset,10), end=complex(xOffset,30)))
                linePaths.append(Line(start=complex(xOffset,30), end=complex(lineoverList[0], 30)))
                linePaths.append(Line(start=complex(lineoverList[0], 30), end=complex(lineoverList[0], 10)))
                linepath = Path(*linePaths)
                linepath = elPath(linepath.d())
                finalSegments.append(linepath)
                lineover = False
                lineoverList.clear()
                
            pathTransform = Matrix.translate(xOffset, baseline+yOffset-box.yMax)
            path = elPath(path.d()) * pathTransform
            path = elPath(path.d())
            finalSegments.append(path)
            xOffset += 30
            if glyphPos != 0:
                try:
                    xOffset -= glyphPos[inString[charIdx]].real
                except:
                    pass
            xOffset += (glyphBounds[charIdx].xMax - glyphBounds[charIdx].xMin)
            strIdx += 1

        if leftCap == '' and rightCap == '':
            for i in range(len(finalSegments)):
                svgObj = dwg.add(dwg.path(finalSegments[i].d()))
                svgObj['fill'] = "#000000"
        else:
            #draw the outline of the label as a filled shape and 
            #subtract each latter from it
            tagPaths = []
            if rightCap == 'round':
                tagPaths.append(Line(start=complex(100,0), end=complex(xOffset,0)))
                tagPaths.append(Arc(start=complex(xOffset,0), radius=complex(100,100), rotation=180, large_arc=1, sweep=1, end=complex(xOffset,200)))
            elif rightCap == 'square':
                tagPaths.append(Line(start=complex(100,0), end=complex(xOffset,0)))
                tagPaths.append(Line(start=complex(xOffset,0), end=complex(xOffset+50,0)))
                tagPaths.append(Line(start=complex(xOffset+50,0), end=complex(xOffset+50,200)))
                tagPaths.append(Line(start=complex(xOffset+50,200), end=complex(xOffset,200)))        
            elif rightCap == 'pointer':
                tagPaths.append(Line(start=complex(100,0), end=complex(xOffset,0)))
                tagPaths.append(Line(start=complex(xOffset,0), end=complex(xOffset+50,0)))
                tagPaths.append(Line(start=complex(xOffset+50,0), end=complex(xOffset+100,100)))
                tagPaths.append(Line(start=complex(xOffset+100,100), end=complex(xOffset+50,200)))
                tagPaths.append(Line(start=complex(xOffset+50,200), end=complex(xOffset,200)))
            elif rightCap == 'flagtail':
                tagPaths.append(Line(start=complex(100,0), end=complex(xOffset,0)))
                tagPaths.append(Line(start=complex(xOffset,0), end=complex(xOffset+100,0)))
                tagPaths.append(Line(start=complex(xOffset+100,0), end=complex(xOffset+50,100)))
                tagPaths.append(Line(start=complex(xOffset+50,100), end=complex(xOffset+100,200)))        
                tagPaths.append(Line(start=complex(xOffset+100,200), end=complex(xOffset,200))) 
            elif rightCap == 'fslash':
                tagPaths.append(Line(start=complex(100,0), end=complex(xOffset,0)))
                tagPaths.append(Line(start=complex(xOffset,0), end=complex(xOffset+50,0)))        
                tagPaths.append(Line(start=complex(xOffset+50,0), end=complex(xOffset,200))) 
            elif rightCap == 'bslash':
                tagPaths.append(Line(start=complex(100,0), end=complex(xOffset,0)))
                tagPaths.append(Line(start=complex(xOffset,0), end=complex(xOffset+50,200)))        
                tagPaths.append(Line(start=complex(xOffset+50,200), end=complex(xOffset,200))) 
            elif rightCap == '' and leftCap != '':
                tagPaths.append(Line(start=complex(100,0), end=complex(xOffset,0)))
                tagPaths.append(Line(start=complex(xOffset,0), end=complex(xOffset,200)))

            if leftCap == 'round':
                tagPaths.append(Line(start=complex(xOffset,200), end=complex(100,200)))
                tagPaths.append(Arc(start=complex(100,200), radius=complex(100,100), rotation=180, large_arc=0, sweep=1, end=complex(100,0)))
            elif leftCap == 'square':
                tagPaths.append(Line(start=complex(xOffset,200), end=complex(100,200)))
                tagPaths.append(Line(start=complex(100,200), end=complex(50,200)))
                tagPaths.append(Line(start=complex(50,200), end=complex(50,0)))
                tagPaths.append(Line(start=complex(50,0), end=complex(100,0)))     
            elif leftCap == 'pointer':
                tagPaths.append(Line(start=complex(xOffset,200), end=complex(100,200)))
                tagPaths.append(Line(start=complex(100,200), end=complex(50,200)))
                tagPaths.append(Line(start=complex(50,200), end=complex(0,100)))
                tagPaths.append(Line(start=complex(0,100), end=complex(50,0)))
                tagPaths.append(Line(start=complex(50,0), end=complex(100,0)))
            elif leftCap == 'flagtail':
                tagPaths.append(Line(start=complex(xOffset,200), end=complex(100,200)))
                tagPaths.append(Line(start=complex(100,200), end=complex(0,200)))
                tagPaths.append(Line(start=complex(0,200), end=complex(50,100)))
                tagPaths.append(Line(start=complex(50,100), end=complex(0,0)))
                tagPaths.append(Line(start=complex(0,0), end=complex(100,0)))
            elif leftCap == 'fslash':
                tagPaths.append(Line(start=complex(xOffset,200), end=complex(100,200)))
                tagPaths.append(Line(start=complex(100,200), end=complex(50,200)))
                tagPaths.append(Line(start=complex(50,200), end=complex(100,0)))
            elif leftCap == 'bslash':
                tagPaths.append(Line(start=complex(xOffset,200), end=complex(100,200)))
                tagPaths.append(Line(start=complex(100,200), end=complex(50,0)))
                tagPaths.append(Line(start=complex(50,0), end=complex(100,0)))
            elif leftCap == '' and rightCap != '':
                tagPaths.append(Line(start=complex(xOffset,200), end=complex(100,200)))
                tagPaths.append(Line(start=complex(100,200), end=complex(100,0)))

            path = Path(*tagPaths)
            for i in range(len(finalSegments)):
                path = elPath(path.d()+" "+finalSegments[i].reverse())
            tagObj = dwg.add(dwg.path(path.d()))
            tagObj['fill'] = "#000000"

        dwg['width'] = xOffset+100
        dwg['height'] = 250

        #dwg.saveas('out.svg')

        print('create svg')

        return dwg
    #
    #
    # ******************************************************************************
    #
    #   Convert SVG paths to various EAGLE polygon formats
    #
    #
    def drawSVG(self, svg_attributes, attributes, paths):

        global SCALE
        global SUBSAMPLING
        global SIMPLIFY
        global SIMPLIFYHQ
        global TRACEWIDTH

        out = ''
        svgWidth = 0
        svgHeight = 0

        if 'viewBox' in svg_attributes.keys():
            if svg_attributes['viewBox'].split()[2] != '0':
                svgWidth = str(
                    round(float(svg_attributes['viewBox'].split()[2]), 2))
                svgHeight = str(
                    round(float(svg_attributes['viewBox'].split()[3]), 2))
            else:
                svgWidth = svg_attributes['width']
                svgHeight = svg_attributes['height']
        else:
            svgWidth = svg_attributes['width']
            svgHeight = svg_attributes['height']

        specifiedWidth = svg_attributes['width']
        if 'mm' in specifiedWidth:
            specifiedWidth = float(specifiedWidth.replace('mm', ''))
            SCALE = specifiedWidth / float(svgWidth)
            if self.verbose:
                print("SVG width detected in mm \\o/")
        elif 'in' in specifiedWidth:
            specifiedWidth = float(specifiedWidth.replace('in', '')) * 25.4
            SCALE = specifiedWidth / float(svgWidth)
            if self.verbose:
                print("SVG width detected in inches")
        else:
            SCALE = (self.scaleFactor * 25.4) / 150
            if self.verbose:
                print("SVG width not found, guessing based on scale factor")

        self.exportHeight = float(svgHeight) * SCALE

        if len(paths) == 0:
            print("No paths found. Did you use 'Object to path' in Inkscape?")

        i = 0
        out = []
        while i < len(paths):

            if self.verbose:
                print('Translating Path ' + str(i+1) + ' of ' + str(len(paths)))

            # Apply the tranform from this svg object to actually transform the points
            # We need the Matrix object from svgelements but we can only matrix multiply with
            # svgelements' version of the Path object so we're gonna do some dumb stuff
            # to launder the Path object from svgpathtools through a d-string into 
            # svgelements' version of Path. Luckily, the Path object from svgelements has 
            # backwards compatible .point methods
            pathTransform = Matrix('')
            if 'transform' in attributes[i].keys():
                pathTransform = Matrix(attributes[i]['transform'])
                if self.verbose:
                    print('...Applying Transforms')
            path = elPath(paths[i].d()) * pathTransform
            path = elPath(path.d())

            # Another stage of transforms that gets applied to all paths
            # in order to shift the label around the origin

            tx = {
                'l':0,
                'c':0-(float(svgWidth)/2),
                'r':0-float(svgWidth)
            }
            ty = {
                't':250,
                'c':150,
                'b':50
            }
            path = elPath(paths[i].d()) * Matrix.translate(tx[self.originPos[1]],ty[self.originPos[0]])
            path = elPath(path.d())

            style = 0

            if 'style' in attributes[i].keys():
                style = styleParse(attributes[i]['style'])

            if 'fill' in attributes[i].keys():
                filled = attributes[i]['fill'] != 'none' and attributes[i]['fill'] != ''
            elif 'style' in attributes[i].keys():
                filled = style['fill'] != 'none' and style['fill'] != ''
            else:
                filled = False

            if 'stroke' in attributes[i].keys():
                stroked = attributes[i]['stroke'] != 'none' and attributes[i]['stroke'] != ''
            elif 'style' in attributes[i].keys():
                stroked = style['stroke'] != 'none' and style['stroke'] != ''
            else:
                stroked = False

            if not filled and not stroked:
                i += 1
                continue  # not drawable (clip path?)

            SUBSAMPLING = self.subSampling
            TRACEWIDTH = str(self.traceWidth)
            l = path.length()
            divs = round(l * SUBSAMPLING)
            if divs < 3:
                divs = 3
            maxLen = l * 2 * SCALE / divs
            p = path.point(0)
            p = complex(p.real * SCALE, p.imag * SCALE)
            last = p
            polys = []
            points = []
            s = 0
            while s <= divs:
                p = path.point(s * 1 / divs)
                p = complex(p.real * SCALE, p.imag * SCALE)
                if dist(p, last) > maxLen:
                    if len(points) > 1:
                        points = simplify(points, SIMPLIFY, SIMPLIFYHQ)
                        polys.append(points)
                    points = [p]
                else:
                    points.append(p)

                last = p
                s += 1

            if len(points) > 1:
                points = simplify(points, SIMPLIFY, SIMPLIFYHQ)          
                polys.append(points)

            if filled:
                polys = unpackPoly(polys)

            for points in polys:

                if len(points) < 2:
                    return
                    
                _points = []
                if filled:
                    points.append(points[0]) # re-add final point so we loop around

                for p in points:
                    precisionX = round(p.real, 8)
                    precisionY = round(p.imag - self.exportHeight, 8)
                    _points += [(precisionX, precisionY)]

                out += [_points]
            
            i += 1

        self.polys = out

        return out


    def create_footprint(self):
        
        out = "(footprint \"buzzardLabel\"\n" + \
            " (layer \"F.Cu\")\n" + \
            " (attr board_only exclude_from_pos_files exclude_from_bom)\n"

        for poly in self.polys:

            if len(poly) < 2:
                return
                
            scriptLine = " (fp_poly (pts"
            for points in poly:
                scriptLine += " (xy {0:.4f} {1:.4f})".format(points[0],points[1])
            scriptLine += ") (layer \"F.SilkS\") (width 0.01) (fill solid))\n"
        
            out += scriptLine + '\n'
    
        out += ')\n'
        return out

# Use Pythagoras to find the distance between two points
def dist(a, b):
    dx = a.real - b.real
    dy = a.imag - b.imag
    return math.sqrt(dx * dx + dy * dy)

# Parse a style tag into a dictionary
def styleParse(attr):
    out = dict()
    i = 0
    for tag in attr.split(';'):
        out[tag.split(':')[0]] = tag.split(':')[1]
        i += 1
    return out

# ray-casting algorithm based on
# http://www.ecse.rpi.edu/Homepages/wrf/Research/Short_Notes/pnpoly.html
def isInside(point, poly):
    x = point.real
    y = point.imag
    inside = False
    i = 0
    j = len(poly) - 1
    while i < len(poly):
        xi = poly[i].real
        yi = poly[i].imag
        xj = poly[j].real
        yj = poly[j].imag
        intersect = ((yi > y) != (yj > y)) and (x < ((xj - xi) * (y - yi) / (yj - yi) + xi))
        if intersect:
            inside = not inside
        j = i
        i += 1
    return inside


# Shoelace Formula without absolute value which returns negative if points are CCW
# https://stackoverflow.com/questions/14505565/detect-if-a-set-of-points-in-an-array-that-are-the-vertices-of-a-complex-polygon
def polygonArea(poly):
    area = 0
    i = 0
    while i < len(poly):
        j = (i + 1) % len(poly)
        area += poly[i].real * poly[j].imag
        area -= poly[j].real * poly[i].imag
        i += 1
    return area / 2


# Move a small distance away from path[idxa] towards path[idxb]
def interpPt(path, idxa, idxb):
    # a fraction of the trace width so we don't get much of a notch in the line

    amt = float(TRACEWIDTH) / 8

    # wrap index
    if idxb < 0:
        idxb += len(path)
    if idxb >= len(path):
        idxb -= len(path)
          
    # get 2 pts
    a = path[idxa]
    b = path[idxb]
    dx = b.real - a.real
    dy = b.imag - a.imag
    d = math.sqrt(dx * dx + dy * dy)
    if amt > d:
        return  # return nothing - will just end up using the last point
    return complex(a.real + (dx * amt / d), a.imag + (dy * amt / d))


# Some svg paths conatin multiple nested polygons. We need to open them and splice them together.
def unpackPoly(poly):
    # ensure all polys are the right way around
    #if self.verbose:
    #    print('...Unpacking ' + str(len(poly)) + ' Polygons')
    p = 0
    while p < len(poly):
        if polygonArea(poly[p]) > 0:
            poly[p].reverse()
            #if self.verbose:
            #    print('...Polygon #'+str(p)+' was backwards, reversed')
        p += 1

    # check for polys that are within more than 1 other poly,
    # extract them now, then we append them later
    # This isn't a perfect solution and only handles a single nesting
    extraPolys = []
    polyTmp    = []
    for j in range(len(poly)):
        c = 0
        for k in range(len(poly)):
            if j == k:
                continue
            if isInside(poly[j][0], poly[k]):
                c += 1
        if c > 1:
            extraPolys.append(poly[j])
        else:
            polyTmp.append(poly[j])

    poly = polyTmp
    finalPolys = [poly[0]]

    p = 1
    while p < len(poly):
        path = poly[p]
        outerPolyIndex = 'undefined'
        i = 0
        while i < len(finalPolys):
            if isInside(path[0], finalPolys[i]):
                outerPolyIndex = i
                break
            elif isInside(finalPolys[i][0], path):
                # polys in wrong order - old one is inside new one
                t = path
                path = finalPolys[i]
                finalPolys[i] = t
                outerPolyIndex = i
                break
            i += 1

        if outerPolyIndex != 'undefined':
            path.reverse()  # reverse poly
            outerPoly = finalPolys[outerPolyIndex]
            minDist = 10000000000
            minOuter = 0
            minPath = 0
            a = 0
            while a < len(outerPoly):
                b = 0
                while b < len(path):
                    l = dist(outerPoly[a], path[b])
                    if l < minDist:
                        minDist = l
                        minOuter = a
                        minPath = b
                    b += 1
                a += 1

                # splice the inner poly into the outer poly
                # but we have to recess the two joins a little
                # otherwise Eagle reports Invalid poly when filling
                # the top layer
            finalPolys[outerPolyIndex] = outerPoly[0:minOuter]
            stub = interpPt(outerPoly, minOuter, minOuter - 1)
            (finalPolys[outerPolyIndex].append(stub) if stub is not None else None)
            stub = interpPt(path, minPath, minPath + 1)
            (finalPolys[outerPolyIndex].append(stub) if stub is not None else None)
            finalPolys[outerPolyIndex].extend(path[minPath + 1:])
            finalPolys[outerPolyIndex].extend(path[:minPath])
            stub = interpPt(path, minPath, minPath - 1)
            (finalPolys[outerPolyIndex].append(stub) if stub is not None else None)
            stub = interpPt(outerPoly, minOuter, minOuter + 1)
            (finalPolys[outerPolyIndex].append(stub) if stub is not None else None)  
            finalPolys[outerPolyIndex].extend(outerPoly[minOuter + 1:])     
            
        else:
            # not inside, just add this poly
            finalPolys.append(path)

        p += 1

    #print(finalPolys)
    return finalPolys + extraPolys


#
#
# ******************************************************************************
#
#   Python port of:
#   Simplify.js, a high-performance JS polyline simplification library
#   Vladimir Agafonkin, 2013
#   mourner.github.io/simplify-js
#

# square distance from a point to a segment
def getSqSegDist(p, p1, p2):

    x = p1.real
    y = p1.imag
    dx = p2.real - x
    dy = p2.imag - y

    if dx != 0 or dy != 0:

        t = ((p.real - x) * dx + (p.imag - y) * dy) / (dx * dx + dy * dy)

        if (t > 1):
            x = p2.real
            y = p2.imag

        elif (t > 0):
            x += dx * t
            y += dy * t

    dx = p.real - x
    dy = p.imag - y

    return dx * dx + dy * dy

# basic distance-based simplification
def simplifyRadialDist(points, sqTolerance):

    prevPoint = points[0]
    newPoints = [prevPoint]

    i = 1
    leng = len(points)

    while i < leng:
        point = points[i]

        if dist(point, prevPoint) > sqTolerance:
            newPoints.append(point)
            prevPoint = point

        i += 1

    if prevPoint != point:
        newPoints.append(point)

    return newPoints

# simplification using optimized Douglas-Peucker algorithm with recursion elimination
def simplifyDouglasPeucker(points, sqTolerance):

    leng = len(points)
    markers = [''] * leng
    first = 0
    last = leng - 1
    stack = []
    newPoints = []

    markers[first] = markers[last] = 1

    while last:

        maxSqDist = 0

        i = first + 1
        while i < last:
            sqDist = getSqSegDist(points[i], points[first], points[last])

            if sqDist > maxSqDist:
                index = i
                maxSqDist = sqDist

            i += 1

        if maxSqDist > sqTolerance:
            markers[index] = 1
            stack.extend([first, index, index, last])

        if stack:
            last = stack.pop()
            first = stack.pop()
        else:
            break

    i = 0
    while i < leng:
        if markers[i]:
            newPoints.append(points[i])
        i += 1

    return newPoints

# both algorithms combined for awesome performance
def simplify(points, tolerance, highestQuality):

    sqTolerance = tolerance * tolerance if tolerance != '' else 1

    points = points if highestQuality else simplifyRadialDist(
        points, sqTolerance)

    points = simplifyDouglasPeucker(points, sqTolerance)

    return points
