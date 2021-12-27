# KiBuzzard KiCad Plugin
    Note this plugin is currently a work in progress.
    
    Please ensure project is saved before playing with labels. 
    There may still be some bugs that cause KiCad to crash.

Adaption of Eagle based plugin [Buzzard](https://github.com/sparkfunX/Buzzard) for KiCad

This plugin lets you easily create labels in various fonts, and with inverted backgrounds.

![screenshot](doc/KiBuzzard_screenshot.png)

## Compatibility
This plugin has been designed to work on all platforms (Win, Linux, Mac) and with both Current KiCad 5.1, 6.0 and Nightly Releases.

    Note: currently in v5 the labels are placed at 0,0 when created. 
    With Nightly they are copied to the clipboard and can be placed interactively.

## Installation
Install the script in your KiCad scripting directory
You can find the location of scripting directories by opening a KiCad scripting terminal and running the following:

```python
import pcbnew; print(pcbnew.PLUGIN_DIRECTORIES_SEARCH)
```

Example on KiCad 6.00 Ubuntu (from KiCad-Nightly package):
```console
>>> import pcbnew; print(pcbnew.PLUGIN_DIRECTORIES_SEARCH)
/usr/share/kicad-nightly/scripting
/usr/share/kicad-nightly/scripting/plugins
/home/__USERNAME__/.config/kicad/6.00/scripting
/home/__USERNAME__/.config/kicad/6.00/scripting/plugins
/home/__USERNAME__/.local/share/kicad/6.00/scripting
/home/__USERNAME__/.local/share/kicad/6.00/scripting/plugins
```

You can either use git to download the plugin, or directly download as Zip.
```console
$ cd /home/__USERNAME__/.config/kicad/6.00
$ mkdir scripting
$ cd scripting
$ git clone https://github.com/gregdavill/KiBuzzard
```

    Note: `KiBuzzard` should be the root folder of the plugin, with this README in it, when downloading as a zip KiBuzzard may have been put into a subfolder.
```console
~/.config/kicad/6.00/scripting$ ls -l KiBuzzard/ 
total 728
drwxrwxr-x 2 greg greg   4096 Apr 19  2021 doc
drwxrwxr-x 2 greg greg   4096 Jan 15  2021 icons
drwxrwxr-x 6 greg greg   4096 Jul 16 09:47 KiBuzzard
-rw-rw-r-- 1 greg greg     29 Apr 14  2021 __init__.py
-rw-rw-r-- 1 greg greg    126 Dec 28 08:01 config.ini
-rw-rw-r-- 1 greg greg   3275 Jan 15  2021 icon.png
-rw-rw-r-- 1 greg greg   1092 Nov 21  2020 LICENCE
-rw-rw-r-- 1 greg greg   2179 Dec 28 08:12 README.md
-rw-rw-r-- 1 greg greg 144967 Apr 23  2021 text_dialog.fbp
```

For Arch Linux users is already a [kicad-kibuzzard-git](https://aur.archlinux.org/packages/kicad-kibuzzard-git/) package in the AUR.

## Custom fonts

You should be able to load in extra TrueType fonts into `KiBuzzard/buzzard/typeface`. 
You may need to reopen KiCad, and then the extra fonts should be visible in the font selection dropdown.

    Note: be sure to understand your PCB fabs capability when it comes to silkscreen resolution when selecting a custom font.

![Screenshot showing extra fonts](doc/KiBuzzard_fonts.png)

## Licence and credits

Plugin code licensed under MIT, see `LICENSE` for more info.

 - [Buzzard](https://github.com/sparkfunX/Buzzard) From SparkFun
 - KiCad Plugin/wx Dialog inspiration from [Interactive HTML BOM](https://github.com/openscopeproject/InteractiveHtmlBom/)
