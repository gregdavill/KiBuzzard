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
The command line interface for using svg2mod
as a tool in a terminal.
'''

import argparse
import logging
import os
import shlex
import sys
import traceback

import svg2mod.coloredlogger as coloredlogger
from svg2mod.coloredlogger import logger, unfiltered_logger
from svg2mod import svg
from svg2mod.exporter import (DEFAULT_DPI, Svg2ModExportLatest,
                              Svg2ModExportLegacy, Svg2ModExportLegacyUpdater,
                              Svg2ModExportPretty)
from svg2mod.importer import Svg2ModImport

#----------------------------------------------------------------------------

def main():
    '''This function handles the scripting package calls.
    It is setup to read the arguments from `get_arguments()`
    then parse the target svg file and output all converted
    objects into a kicad footprint module.
    '''

    args,_ = get_arguments()


    # Setup root logger to use terminal colored outputs as well as stdout and stderr
    coloredlogger.split_logger(logger)

    if args.debug_print:
        logger.setLevel(logging.DEBUG)
    elif args.verbose_print:
        logger.setLevel(logging.INFO)
    else:
        logger.setLevel(logging.WARNING)

    if args.input_file_name_flag and not args.input_file_name:
        args.input_file_name = args.input_file_name_flag

    if args.list_fonts:
        fonts = svg.Text.load_system_fonts()
        unfiltered_logger.info("Font Name: list of supported styles.")
        for font in fonts:
            fnt_text = f"  {font}:"
            for styles in fonts[font]:
                fnt_text += f" {styles},"
            fnt_text = fnt_text.strip(",")
            unfiltered_logger.info(fnt_text)
        sys.exit(0)
    if args.default_font:
        svg.Text.default_font = args.default_font

    pretty = args.format in ['pretty','latest']
    use_mm = args.units == 'mm'

    if pretty:

        if not use_mm:
            logger.critical("Error: decimal units only allowed with legacy output type")
            sys.exit( -1 )

    try:
        # Import the SVG:
        imported = Svg2ModImport(
            args.input_file_name,
            args.module_name,
            args.module_value,
            args.ignore_hidden,
            args.force_layer
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
            exported = (Svg2ModExportPretty if args.format == "pretty" else Svg2ModExportLatest)(
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

        cmd_args = [os.path.basename(sys.argv[0])] + sys.argv[1:]
        cmdline = ' '.join(shlex.quote(x) for x in cmd_args)

        # Export the footprint:
        exported.write(cmdline)
    except Exception as e:
        if args.debug_print:
            traceback.print_exc()
        else:
            logger.critical(f'Unhandled exception (Exiting)\n {type(e).__name__}: {e} ')
        exit(-1)

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
        nargs="?",
        type = str,
        dest = 'input_file_name',
        metavar = 'IN_FILENAME',
        help = "Name of the SVG file",
    )

    mux.add_argument(
        '-i', '--input-file',
        type = str,
        dest = 'input_file_name_flag',
        metavar = 'FILENAME',
        help = "Name of the SVG file, but specified with a flag.",
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
        dest = 'ignore_hidden',
        action = 'store_const',
        const = True,
        help = "Do not export hidden objects",
        default = False,
    )

    parser.add_argument(
        '--force', '--force-layer',
        type = str,
        dest = 'force_layer',
        metavar = 'LAYER',
        help = "Force everything into the single provided layer",
        default = None,
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
        default = 5.0,
    )
    parser.add_argument(
        '--format',
        type = str,
        dest = 'format',
        metavar = 'FORMAT',
        choices = [ 'legacy', 'pretty', 'latest'],
        help = "Output module file format (legacy|pretty|latest). 'latest' introduces features used in kicad >= 6",
        default = 'latest',
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

#----------------------------------------------------------------------------

if __name__ == "__main__":
    main()

#----------------------------------------------------------------------------
