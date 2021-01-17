# Buzzard plugin for KiCad
    Note this plugin currently only works on KiCad 5.99

Basic plugin wrapper for [Buzzard](https://github.com/sparkfunX/Buzzard). 

This plugin lets you easily create nice "Inverted" block text boxes.

![screenshot](doc/KiBuzzard_screenshot.png)

## Installation
Ensure you also get the submodules with KiBuzzard
```console
$ git clone https://github.com/gregdavill/KiBuzzard --recursive
$ pip3 install -r requirements.txt --user
```
Install in your KiCad scripting directory

## Licence and credits

Plugin code licensed under MIT, see `LICENSE` for more info.

 - [Buzzard](https://github.com/sparkfunX/Buzzard) From SparkFun
 - KiCad Plugin/Dilog inspiration from [Interactive HTML BOM](https://github.com/openscopeproject/InteractiveHtmlBom/)
