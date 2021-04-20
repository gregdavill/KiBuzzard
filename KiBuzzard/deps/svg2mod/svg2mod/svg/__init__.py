'''
A SVG parser with tools to convert an XML svg file
to objects that can be simplified into points.
'''
#__all__ = ['geometry', 'svg']

from .svg import *

def parse(filename):
    '''Take in a filename and return a SVG object of parsed file'''
    return Svg(filename)
