# -*- coding: utf-8 -*-
# -----------------------------------------------------------------------------
#
#  FreeType high-level python API - Copyright 2017 Hin-Tak Leung
#  Distributed under the terms of the new BSD license.
#
# -----------------------------------------------------------------------------
"""
An enumeration type that lists the curve tags supported by FreeType 2.

Each point of an outline has a specific tag which indicates whether it
describes a point used to control a line segment or an arc. The tags can take
the following values:

FT_CURVE_TAG_ON

  Used when the point is ‘on’ the curve. This corresponds to start and end
  points of segments and arcs. The other tags specify what is called an ‘off’
  point, i.e., a point which isn't located on the contour itself, but serves
  as a control point for a Bézier arc.

FT_CURVE_TAG_CONIC

  Used for an ‘off’ point used to control a conic Bézier arc.

FT_CURVE_TAG_CUBIC

  Used for an ‘off’ point used to control a cubic Bézier arc.


FT_Curve_Tag_On, FT_Curve_Tag_Conic, FT_Curve_Tag_Cubic are their
correspondning mixed-case aliases.

Use the FT_CURVE_TAG(tag) macro to filter out other, internally used flags.

"""

FT_CURVE_TAGS = {
    'FT_CURVE_TAG_ON'    : 1,
    'FT_CURVE_TAG_CONIC' : 0,
    'FT_CURVE_TAG_CUBIC' : 2}
globals().update(FT_CURVE_TAGS)

FT_Curve_Tag_On     = FT_CURVE_TAG_ON
FT_Curve_Tag_Conic  = FT_CURVE_TAG_CONIC
FT_Curve_Tag_Cubic  = FT_CURVE_TAG_CUBIC

def FT_CURVE_TAG( flag ):
    return ( flag & 3 )

# FreeType itself does not have mixed-case macros
FT_Curve_Tag = FT_CURVE_TAG
