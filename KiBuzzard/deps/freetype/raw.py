# -*- coding: utf-8 -*-
# -----------------------------------------------------------------------------
#  FreeType high-level python API - Copyright 2011-2015 Nicolas P. Rougier
#  Distributed under the terms of the new BSD license.
# -----------------------------------------------------------------------------
'''
Freetype raw API

This is the raw ctypes freetype binding.
'''
import os
import platform
from ctypes import *
import ctypes.util

import freetype
from freetype.ft_types import *
from freetype.ft_enums import *
from freetype.ft_errors import *
from freetype.ft_structs import *

# First, look for a bundled FreeType shared object on the top-level of the
# installed freetype-py module.
system = platform.system()
if system == 'Windows':
    library_name = 'libfreetype.dll'
elif system == 'Darwin':
    library_name = 'libfreetype.dylib'
else:
    library_name = 'libfreetype.so'

filename = os.path.join(os.path.dirname(freetype.__file__), library_name)

# If no bundled shared object is found, look for a system-wide installed one.
if not os.path.exists(filename):
    # on windows all ctypes does when checking for the library
    # is to append .dll to the end and look for an exact match
    # within any entry in PATH.
    filename = ctypes.util.find_library('freetype')

    if filename is None:
        if platform.system() == 'Windows':
            # Check current working directory for dll as ctypes fails to do so
            filename = os.path.join(os.path.realpath('.'), "freetype.dll")
        else:
            filename = library_name

try:
    _lib = ctypes.CDLL(filename)
except (OSError, TypeError):
    _lib = None
    raise RuntimeError('Freetype library not found')

FT_Init_FreeType       = _lib.FT_Init_FreeType
FT_Done_FreeType       = _lib.FT_Done_FreeType
FT_Library_Version     = _lib.FT_Library_Version

try:
    FT_Library_SetLcdFilter= _lib.FT_Library_SetLcdFilter
except AttributeError:
    def FT_Library_SetLcdFilter (*args, **kwargs):
        return 0
try:
    FT_Library_SetLcdFilterWeights = _lib.FT_Library_SetLcdFilterWeights
except AttributeError:
    pass

FT_New_Face            = _lib.FT_New_Face
FT_New_Memory_Face     = _lib.FT_New_Memory_Face
FT_Open_Face           = _lib.FT_Open_Face
FT_Attach_File         = _lib.FT_Attach_File
FT_Attach_Stream       = _lib.FT_Attach_Stream

try:
    FT_Reference_Face      = _lib.FT_Reference_Face
except AttributeError:
    pass

FT_Done_Face           = _lib.FT_Done_Face
FT_Done_Glyph          = _lib.FT_Done_Glyph
FT_Select_Size         = _lib.FT_Select_Size
FT_Request_Size        = _lib.FT_Request_Size
FT_Set_Char_Size       = _lib.FT_Set_Char_Size
FT_Set_Pixel_Sizes     = _lib.FT_Set_Pixel_Sizes
FT_Load_Glyph          = _lib.FT_Load_Glyph
FT_Load_Char           = _lib.FT_Load_Char
FT_Set_Transform       = _lib.FT_Set_Transform
FT_Render_Glyph        = _lib.FT_Render_Glyph
FT_Get_Kerning         = _lib.FT_Get_Kerning
FT_Get_Track_Kerning   = _lib.FT_Get_Track_Kerning
FT_Get_Glyph_Name      = _lib.FT_Get_Glyph_Name
FT_Get_Glyph           = _lib.FT_Get_Glyph

FT_Glyph_Get_CBox      = _lib.FT_Glyph_Get_CBox

FT_Get_Postscript_Name = _lib.FT_Get_Postscript_Name
FT_Get_Postscript_Name.restype = c_char_p
FT_Select_Charmap      = _lib.FT_Select_Charmap
FT_Set_Charmap         = _lib.FT_Set_Charmap
FT_Get_Charmap_Index   = _lib.FT_Get_Charmap_Index
FT_Get_CMap_Language_ID= _lib.FT_Get_CMap_Language_ID
try:
    #introduced between 2.2.x and 2.3.x
    FT_Get_CMap_Format     = _lib.FT_Get_CMap_Format
except AttributeError:
    pass
FT_Get_Char_Index      = _lib.FT_Get_Char_Index
FT_Get_First_Char      = _lib.FT_Get_First_Char
FT_Get_Next_Char       = _lib.FT_Get_Next_Char
FT_Get_Name_Index      = _lib.FT_Get_Name_Index
FT_Get_SubGlyph_Info   = _lib.FT_Get_SubGlyph_Info

try:
    FT_Get_FSType_Flags    = _lib.FT_Get_FSType_Flags
    FT_Get_FSType_Flags.restype  = c_ushort
except AttributeError:
    pass

FT_Get_X11_Font_Format = _lib.FT_Get_X11_Font_Format
FT_Get_X11_Font_Format.restype = c_char_p

FT_Get_Sfnt_Name_Count = _lib.FT_Get_Sfnt_Name_Count
FT_Get_Sfnt_Name       = _lib.FT_Get_Sfnt_Name
try:
    # introduced between 2.2.x and 2.3.x
    FT_Get_Advance         = _lib.FT_Get_Advance
except AttributeError:
    pass


FT_Outline_GetInsideBorder  = _lib.FT_Outline_GetInsideBorder
FT_Outline_GetOutsideBorder = _lib.FT_Outline_GetOutsideBorder
FT_Outline_Get_BBox         = _lib.FT_Outline_Get_BBox
FT_Outline_Get_CBox         = _lib.FT_Outline_Get_CBox
FT_Stroker_New              = _lib.FT_Stroker_New
FT_Stroker_Set              = _lib.FT_Stroker_Set
FT_Stroker_Rewind           = _lib.FT_Stroker_Rewind
FT_Stroker_ParseOutline     = _lib.FT_Stroker_ParseOutline
FT_Stroker_BeginSubPath     = _lib.FT_Stroker_BeginSubPath
FT_Stroker_EndSubPath       = _lib.FT_Stroker_EndSubPath
FT_Stroker_LineTo           = _lib.FT_Stroker_LineTo
FT_Stroker_ConicTo          = _lib.FT_Stroker_ConicTo
FT_Stroker_CubicTo          = _lib.FT_Stroker_CubicTo
FT_Stroker_GetBorderCounts  = _lib.FT_Stroker_GetBorderCounts
FT_Stroker_ExportBorder     = _lib.FT_Stroker_ExportBorder
FT_Stroker_GetCounts        = _lib.FT_Stroker_GetCounts
FT_Stroker_Export           = _lib.FT_Stroker_Export
FT_Stroker_Done             = _lib.FT_Stroker_Done
FT_Glyph_Stroke             = _lib.FT_Glyph_Stroke
FT_Glyph_StrokeBorder       = _lib.FT_Glyph_StrokeBorder
FT_Glyph_To_Bitmap          = _lib.FT_Glyph_To_Bitmap


# FT_Property_Get/FT_Property_Set requires FreeType 2.7.x+
try:
    FT_Property_Get    = _lib.FT_Property_Get
    FT_Property_Set    = _lib.FT_Property_Set
except AttributeError:
    pass

# These two are only found when TT debugger is enabled
try:
    TT_New_Context     = _lib.TT_New_Context
    TT_RunIns          = _lib.TT_RunIns
except AttributeError:
    pass


# Wholesale import of 102 routines which can be reasonably expected
# to be found in freetype 2.2.x onwards. Some of these might need
# to be protected with try:/except AttributeError: in some freetype builds.

FTC_CMapCache_Lookup           = _lib.FTC_CMapCache_Lookup
FTC_CMapCache_New              = _lib.FTC_CMapCache_New
FTC_ImageCache_Lookup          = _lib.FTC_ImageCache_Lookup
FTC_ImageCache_New             = _lib.FTC_ImageCache_New
FTC_Manager_Done               = _lib.FTC_Manager_Done
FTC_Manager_LookupFace         = _lib.FTC_Manager_LookupFace
FTC_Manager_LookupSize         = _lib.FTC_Manager_LookupSize
FTC_Manager_New                = _lib.FTC_Manager_New
FTC_Manager_RemoveFaceID       = _lib.FTC_Manager_RemoveFaceID
FTC_Manager_Reset              = _lib.FTC_Manager_Reset
FTC_Node_Unref                 = _lib.FTC_Node_Unref
FTC_SBitCache_Lookup           = _lib.FTC_SBitCache_Lookup
FTC_SBitCache_New              = _lib.FTC_SBitCache_New

FT_Activate_Size               = _lib.FT_Activate_Size
FT_Add_Default_Modules         = _lib.FT_Add_Default_Modules
FT_Add_Module                  = _lib.FT_Add_Module
FT_Angle_Diff                  = _lib.FT_Angle_Diff
FT_Atan2                       = _lib.FT_Atan2
FT_Bitmap_Convert              = _lib.FT_Bitmap_Convert
FT_Bitmap_Copy                 = _lib.FT_Bitmap_Copy
FT_Bitmap_Done                 = _lib.FT_Bitmap_Done
FT_Bitmap_Embolden             = _lib.FT_Bitmap_Embolden
FT_Bitmap_New                  = _lib.FT_Bitmap_New
FT_CeilFix                     = _lib.FT_CeilFix
FT_ClassicKern_Free            = _lib.FT_ClassicKern_Free
FT_ClassicKern_Validate        = _lib.FT_ClassicKern_Validate
FT_Cos                         = _lib.FT_Cos
FT_DivFix                      = _lib.FT_DivFix
FT_Done_Library                = _lib.FT_Done_Library
FT_Done_Size                   = _lib.FT_Done_Size
FT_FloorFix                    = _lib.FT_FloorFix
try:
    # Not in default windows build of 2.8.x
    FT_Get_BDF_Charset_ID          = _lib.FT_Get_BDF_Charset_ID
    FT_Get_BDF_Property            = _lib.FT_Get_BDF_Property
except AttributeError:
    pass
FT_Get_MM_Var                  = _lib.FT_Get_MM_Var
FT_Get_Module                  = _lib.FT_Get_Module
FT_Get_Multi_Master            = _lib.FT_Get_Multi_Master
FT_Get_PFR_Advance             = _lib.FT_Get_PFR_Advance
FT_Get_PFR_Kerning             = _lib.FT_Get_PFR_Kerning
FT_Get_PFR_Metrics             = _lib.FT_Get_PFR_Metrics
FT_Get_PS_Font_Info            = _lib.FT_Get_PS_Font_Info
FT_Get_PS_Font_Private         = _lib.FT_Get_PS_Font_Private
FT_Get_Renderer                = _lib.FT_Get_Renderer
FT_Get_Sfnt_Table              = _lib.FT_Get_Sfnt_Table
FT_Get_TrueType_Engine_Type    = _lib.FT_Get_TrueType_Engine_Type
FT_Get_WinFNT_Header           = _lib.FT_Get_WinFNT_Header
FT_Glyph_Copy                  = _lib.FT_Glyph_Copy
FT_GlyphSlot_Embolden          = _lib.FT_GlyphSlot_Embolden
FT_GlyphSlot_Oblique           = _lib.FT_GlyphSlot_Oblique
FT_GlyphSlot_Own_Bitmap        = _lib.FT_GlyphSlot_Own_Bitmap
FT_Glyph_Transform             = _lib.FT_Glyph_Transform
FT_Has_PS_Glyph_Names          = _lib.FT_Has_PS_Glyph_Names
FT_List_Add                    = _lib.FT_List_Add
FT_List_Finalize               = _lib.FT_List_Finalize
FT_List_Find                   = _lib.FT_List_Find
FT_List_Insert                 = _lib.FT_List_Insert
FT_List_Iterate                = _lib.FT_List_Iterate
FT_List_Remove                 = _lib.FT_List_Remove
FT_List_Up                     = _lib.FT_List_Up
FT_Load_Sfnt_Table             = _lib.FT_Load_Sfnt_Table
FT_Matrix_Invert               = _lib.FT_Matrix_Invert
FT_Matrix_Multiply             = _lib.FT_Matrix_Multiply
FT_MulDiv                      = _lib.FT_MulDiv
FT_MulFix                      = _lib.FT_MulFix
FT_New_Library                 = _lib.FT_New_Library
FT_New_Size                    = _lib.FT_New_Size
FT_OpenType_Free               = _lib.FT_OpenType_Free
FT_OpenType_Validate           = _lib.FT_OpenType_Validate
FT_Outline_Check               = _lib.FT_Outline_Check
FT_Outline_Copy                = _lib.FT_Outline_Copy
FT_Outline_Decompose           = _lib.FT_Outline_Decompose
FT_Outline_Done                = _lib.FT_Outline_Done
FT_Outline_Embolden            = _lib.FT_Outline_Embolden
FT_Outline_Get_Bitmap          = _lib.FT_Outline_Get_Bitmap
FT_Outline_Get_Orientation     = _lib.FT_Outline_Get_Orientation
FT_Outline_New                 = _lib.FT_Outline_New
FT_Outline_Render              = _lib.FT_Outline_Render
FT_Outline_Reverse             = _lib.FT_Outline_Reverse
FT_Outline_Transform           = _lib.FT_Outline_Transform
FT_Outline_Translate           = _lib.FT_Outline_Translate
FT_Remove_Module               = _lib.FT_Remove_Module
FT_RoundFix                    = _lib.FT_RoundFix
FT_Set_Debug_Hook              = _lib.FT_Set_Debug_Hook
FT_Set_MM_Blend_Coordinates    = _lib.FT_Set_MM_Blend_Coordinates
FT_Set_MM_Design_Coordinates   = _lib.FT_Set_MM_Design_Coordinates
FT_Set_Renderer                = _lib.FT_Set_Renderer
FT_Set_Var_Blend_Coordinates   = _lib.FT_Set_Var_Blend_Coordinates
FT_Set_Var_Design_Coordinates  = _lib.FT_Set_Var_Design_Coordinates
FT_Sfnt_Table_Info             = _lib.FT_Sfnt_Table_Info
FT_Sin                         = _lib.FT_Sin
FT_Stream_OpenGzip             = _lib.FT_Stream_OpenGzip
FT_Stream_OpenLZW              = _lib.FT_Stream_OpenLZW
FT_Tan                         = _lib.FT_Tan
FT_TrueTypeGX_Free             = _lib.FT_TrueTypeGX_Free
FT_TrueTypeGX_Validate         = _lib.FT_TrueTypeGX_Validate
FT_Vector_From_Polar           = _lib.FT_Vector_From_Polar
FT_Vector_Length               = _lib.FT_Vector_Length
FT_Vector_Polarize             = _lib.FT_Vector_Polarize
FT_Vector_Rotate               = _lib.FT_Vector_Rotate
FT_Vector_Transform            = _lib.FT_Vector_Transform
FT_Vector_Unit                 = _lib.FT_Vector_Unit

# Wholesale import ends
