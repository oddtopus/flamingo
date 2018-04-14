## Flamingo Workbench
"Flamingo tools" is a set of customized FreeCAD commands and objects that help to speed-up the drawing of frames and pipelines, mainly.

![screenshot1](https://www.freecadweb.org/wiki/images/8/85/FlamingoBlob.png)

## Installation
* preferably, use the FreeCAD-Addons-Installer https://github.com/FreeCAD/FreeCAD-addons as long as it's included in FreeCAD's official add-ons.
* otherwise copy the files of this repository in a subfolder of Mod/ in the FreeCAD installation folder

## Usage
For convenience Flamingo tools are grouped in three toolbars/menus + one utility set.

### FrameTools toolbar
![screenshot1](https://www.freecadweb.org/wiki/images/9/9e/Flamingos_frame2.jpg)

It's a simple toolbox of 12 commands to arrange frames, trusses and similar to using the Structure objects in FreeCAD's Arch module. 
Read [tutorialFrame.pdf](https://github.com/oddtopus/flamingo/blob/master/tutorials/tutorialFrame.pdf) for more informations. Code is in `CommandsFrame.py`

### PypeTools toolbar
![screenshot1](https://www.freecadweb.org/wiki/images/0/06/Flamingos_pype2.jpg)

The logical continuation of the frame tool since it deals with creating pipelines and tubular structures. It also features its own Python classes to create the piping objects, such as tubes, elbows, flanges etc. 
Read [tutorialPype2.pdf](https://github.com/oddtopus/flamingo/blob/master/tutorials/tutorialPype2.pdf) for more specific features. Code is in `CommandsPipe.py`

### EagleTools toolbar
This toolbar is mantained only for historical reasons. "Eagle tools": are basically an addition and shortcut to the very fine [FreeCAD-PCB workbench](https://github.com/marmni/FreeCAD-PCB) (available via the [FreeCAD addon manager](https://github.com/FreeCAD/FreeCAD-addons)) to import position of objects from a .brd Eagle's file on a PCB drawn in FreeCAD with the a.m. workbench relating only on their names. It's also the origin, by extension, of the name of the entire workbench.

> "If the parts in the group Parts of the .FCStd file have the same name of the parts in the .brd file, they will be moved to the position of the PCB specified in the .brd file."  

Read [tutorialEagle.pdf](https://github.com/oddtopus/flamingo/blob/master/tutorials/tutorialEagle.pdf) for more informations. Code is in `CommandsEagle.py`

### Utils toolbar
![screenshot1](https://www.freecadweb.org/wiki/images/d/d2/Flamingos_utils.jpg)

Finally the "Utils" toolbar provides some functionality to query the objects in the model and their distance, to move/rotate the work plane and a little hack of the DWire creation dialog of Draft module, which allow to change the WP position on-the-fly.

## Documentation
Commands are documented within the code: use the "Automatic documentation from python modules" of the Help menu.

There is also a FreeCAD [wiki](https://www.freecadweb.org/wiki/Flamingo_Workbench) page dedicated to Flamingo that is in ongoing progress. 

Also, for more info on the overall FreeCAD project:

* [FreeCAD Site main page](https://www.freecadweb.org/)

* [FreeCAD Wiki main page](https://www.freecadweb.org/wiki)

* [FreeCAD Repository](https://github.com/FreeCAD/FreeCAD)

## Feedback
To provide feedback please post to the FreeCAD [forum ](https://forum.freecadweb.org) thread dedicated to Flamingo tools.

For bug reports and feature requests please use the "Issues" queue in flamingo's github repository.

If you wish to use, modify or merge in your code the contents of this repository, the appropriate credit is

    contribution from flamingo (2016-2018, LGPL3) by oddtopus
    https://github.com/oddtopus/flamingo


