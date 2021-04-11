# KiBuzzard KiCad Plugin
    Note this plugin is currently a work in progress.
    
    Please ensure project is saved before playing with labels. 
    There may still be some bugs that cause KiCad to crash.

Adaption of Eagle based plugin [Buzzard](https://github.com/sparkfunX/Buzzard) for KiCad

This plugin lets you easily create labels in various fonts, and with inverted backgrounds.

![screenshot](doc/KiBuzzard_screenshot.png)

## Compatibility
This plugin has been designed to work on all platforms (Win, Linux, Mac) and with both Current KiCad 5.1 and Nightly Releases.

    Note: currently in v5 the labels are placed at 0,0 when created. 
    With Nightly they are copied to the clipboard and can be placed interactively.

## Installation
Install the script in your KiCad scripting directory
You can find the location of scripting directories by opening a KiCad scripting terminal and running the following:

```python
import pcbnew; print(pcbnew.PLUGIN_DIRECTORIES_SEARCH)
```

Example on KiCad 5.99 Ubuntu:
```console
>>> import pcbnew; print(pcbnew.PLUGIN_DIRECTORIES_SEARCH)
/usr/share/kicad-nightly/scripting
/usr/share/kicad-nightly/scripting/plugins
/home/__USERNAME__/.config/kicad/5.99/scripting
/home/__USERNAME__/.config/kicad/5.99/scripting/plugins
/home/__USERNAME__/.local/share/kicad/5.99/scripting
/home/__USERNAME__/.local/share/kicad/5.99/scripting/plugins
```

```console
$ git clone https://github.com/gregdavill/KiBuzzard
```

You will also require the FreeType DLLs
This can be done with pip:
```console
$ pip3 install freetype-py --user
```

Alternatively for Windows:
Download FreeType dlls: https://github.com/ubawurinna/freetype-windows-binaries/releases/latest
Copy win64/freetype.dll into C:/Program Files/KiCad/5.99/bin

## Licence and credits

Plugin code licensed under MIT, see `LICENSE` for more info.

 - [Buzzard](https://github.com/sparkfunX/Buzzard) From SparkFun
 - KiCad Plugin/wx Dialog inspiration from [Interactive HTML BOM](https://github.com/openscopeproject/InteractiveHtmlBom/)
