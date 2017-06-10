"Flamingo tools" is a set of customized FreeCAD commands and objects that help to speed-up the drawing of frames and pipelines, mainly.

To install the workbench:
* preferably, use the FreeCAD-Addons-Installer https://github.com/FreeCAD/FreeCAD-addons as long as it's included in FreeCAD's official add-ons.
* otherwise copy the files of this repository in a subfolder of \Mod in the FreeCAD installation folder 

Commands are documented within the code: use the "Automatic documentation from python modules" of the Help menu.
Temporarily there is also a wiki-sandbox at https://www.freecadweb.org/wiki/Sandbox:Flamingo. The part on frame-tools is almost complete.
Also, for more info on the overall FreeCAD project:
* https://www.freecadweb.org/
* https://www.freecadweb.org/wiki
* https://github.com/FreeCAD/FreeCAD

For convenience Flamingo tools are grouped in three toolbars/menus + one utility set.
* The 1st toolbar is "Frame tools": that is aimed to arrange frames, trusses and similar in FreeCAD using the Structure objects of Arch module. 
.../flamingo/tutorials/tutorialFrame.pdf
* The 2nd toolbar is "Pype tools": that's the logical continuation of frame tool since it deals with creating pipelines and tubular structures. It also features its own Python classes to create the piping objects, such as tubes, elbows, flanges etc.
.../flamingo/tutorials/tutorialPype2.pdf
* The 3rd toolbar, mantanined only for historical reasons, is "Eagle tools": that's basically an addition, and shortcut, to the very fine FreeCAD-PCB workbench (also available in the FreeCAD's add-on repository) to import position of objects from a .brd Eagle's file on a PCB drawn in FreeCAD with the a.m. workbench relating only on their names. It's also the origin, by extension, of the name of the entire workbench.
.../flamingo/tutorials/tutorialEagle.pdf
* Finally the "Utils" toolbar provides some functionality to query the objects in the model and their distance, to move/rotate the work plane and a little hack of the DWire creation dialog of Draft module, which allow to change the WP position on-the-fly.

