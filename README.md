# svg2mod

[![Build Status](https://travis-ci.com/svg2mod/svg2mod.svg?branch=main)](https://travis-ci.com/svg2mod/svg2mod)
[![GitHub last commit](https://img.shields.io/github/last-commit/svg2mod/svg2mod)](https://github.com/svg2mod/svg2mod/commits/main)

[![PyPI - License](https://img.shields.io/pypi/l/svg2mod?color=black)](https://pypi.org/project/svg2mod/)
[![PyPI - Python Version](https://img.shields.io/pypi/pyversions/svg2mod)](https://pypi.org/project/svg2mod/)
[![PyPI](https://img.shields.io/pypi/v/svg2mod?color=informational&label=version)](https://pypi.org/project/svg2mod/)

This is a program / library to convert SVG drawings to KiCad footprint module files.

It includes a modified version of [cjlano's python SVG parser and drawing module](https://github.com/cjlano/svg) to interpret drawings and approximate curves using straight line segments.  Module files can be output in KiCad's legacy or s-expression (i.e., pretty) formats.

## Requirements

* Python 3
* [fonttools](https://pypi.org/project/fonttools/)

## Installation

```pip install svg2mod```

## Example

```svg2mod -i input.svg```

## Usage

```text
usage: svg2mod [-h] [-i FILENAME] [-o FILENAME] [-c] [-P] [-v] [--debug] [-x]
               [-d DPI] [-f FACTOR] [-p PRECISION] [--format FORMAT]
               [--name NAME] [--units UNITS] [--value VALUE] [-F DEFAULT_FONT]
               [-l]

Convert Inkscape SVG drawings to KiCad footprint modules.

optional arguments:
  -h, --help            show this help message and exit
  -i FILENAME, --input-file FILENAME
                        Name of the SVG file
  -o FILENAME, --output-file FILENAME
                        Name of the module file
  -c, --center          Center the module to the center of the bounding box
  -P, --convert-pads    Convert any artwork on Cu layers to pads
  -v, --verbose         Print more verbose messages
  --debug               Print debug level messages
  -x, --exclude-hidden  Do not export hidden layers
  -d DPI, --dpi DPI     DPI of the SVG file (int)
  -f FACTOR, --factor FACTOR
                        Scale paths by this factor
  -p PRECISION, --precision PRECISION
                        Smoothness for approximating curves with line
                        segments. Input is the approximate length for each
                        line segment in SVG pixels (float)
  --format FORMAT       Output module file format (legacy|pretty)
  --name NAME, --module-name NAME
                        Base name of the module
  --units UNITS         Output units, if output format is legacy (decimal|mm)
  --value VALUE, --module-value VALUE
                        Value of the module
  -F DEFAULT_FONT, --default-font DEFAULT_FONT
                        Default font to use if the target font in a text
                        element cannot be found
  -l, --list-fonts      List all fonts that can be found in common locations```
```

## SVG Files

svg2mod expects images saved in the uncompressed Inkscape SVG (i.e., not "plain SVG") format. This is so it can associate inkscape layers with kicad layers

* Drawings should be to scale (1 mm in Inscape will be 1 mm in KiCad).  Use the --factor option to resize the resulting module(s) up or down from there.
* Paths are fully supported Rect are partially supported.
  * A path may have an outline and a fill.  (Colors will be ignored.)
  * A path may have holes, defined by interior segments within the path (see included examples).
  * 100% Transparent fills and strokes with be ignored.
  * Rect supports rotations, but not corner radii.
  * Text Elements are partially supported
* Groups may be used.  However, styles applied to groups (e.g., stroke-width) are not applied to contained drawing elements.  In these cases, it may be necessary to ungroup (and perhaps regroup) the elements.
* Layers must be named to match the target in kicad. The supported layers are listed below. They will be ignored otherwise.
* __If there is an issue parsing an inkscape object or stroke convert it to a path.__
  * __Use Inkscape's "Path->Object To Path" and "Path->Stroke To Path" menu options to convert these elements into paths that will work.__

### Layers

This supports the layers listed below. They are the same in inkscape and kicad:

| KiCad layer(s)   | KiCad legacy | KiCad pretty |
|:----------------:|:------------:|:------------:|
| F.Cu             | Yes          | Yes          |
| B.Cu             | Yes          | Yes          |
| F.Adhes          | Yes          | Yes          |
| B.Adhes          | Yes          | Yes          |
| F.Paste          | Yes          | Yes          |
| B.Paste          | Yes          | Yes          |
| F.SilkS          | Yes          | Yes          |
| B.SilkS          | Yes          | Yes          |
| F.Mask           | Yes          | Yes          |
| B.Mask           | Yes          | Yes          |
| Dwgs.User        | Yes          | Yes          |
| Cmts.User        | Yes          | Yes          |
| Eco1.User        | Yes          | Yes          |
| Eco2.User        | Yes          | Yes          |
| Edge.Cuts        | Yes          | Yes          |
| F.Fab            | --           | Yes          |
| B.Fab            | --           | Yes          |
| F.CrtYd          | --           | Yes          |
| B.CrtYd          | --           | Yes          |

Note: If you have a layer "F.Cu", all of its sub-layers will be treated as "F.Cu" regardless of their names.
