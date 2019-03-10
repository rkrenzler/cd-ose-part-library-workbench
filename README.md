# OSE part library

This workbench helps to have fast a access to different FreeCAD files.

**Warning: this code does not work. At this point it is only a proof of conceptcts and a test of available technologies.**

## Problems
* I do not know the magic behind the import function. It seems to work on FreeCAD 0.17 with Assembly 2. But the code curses in red font into the *Report view*.
* The code does not work on FreeCAD 0.18, because it needs *Assembly 2*.


## Installation
See https://www.freecadweb.org/wiki/How_to_install_additional_workbenches .

### Linux
If you do not have ~/.FreeCAD/Mod directory yet, create it.

````
$ mkdir ~/.FreeCAD/Mod
````



Download the workbench.
````
$ mkdir ~/.FreeCAD/Mod
$ cd ~/.FreeCAD/Mod
$ git clone https://github.com/rkrenzler/ose-part-library-workbench.git
````
