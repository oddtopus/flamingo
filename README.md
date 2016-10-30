"Flamingo tools" is a set of macros that I made to speed up some actions in FreeCAD, collected them in toolbars to make them readily available on the GUI.
To install the workbenches, you may copy as usual the files of this repository in a subfolder of \Mod in you FreeCAD installation of your system. It is also available among the add-ons official list.

The most developed toolbar is CommandsFrame.py: that is one simple toolbox of 12 commands to arrange frames, trusses and similar in FreeCAD with the Arch`s Structure objects. 
Read tutorialFrame.pdf for more informations.

Other toolbars, not fully developed, are:
 
CommandsEagle.py: that's basically an addition, and shortcut, to the very fine FreeCAD-PCB workbench, to import position of objects from a .brd Eagle's file on a PCB drawn in FreeCAD with the a.m. workbench relating only on their names. -> "If the parts in the group Parts of the .FCStd file have the same name of the parts in the .brd file, they will be moved to the position of the PCB specified in the .brd file."
Read tutorialEagle.pdf for more informations

CommandsPolar.py: to import a set of polar coordinates from a spreadsheet and use them to draw a sketch. That is for future development of a project that includes also a prototype electronic board and a ultrasonic range finder...

CommandsSpSh.py: removed from workbench but code is still available. It was just an experiment to manage data from spread sheets
    
CommandsPipe.py: new toolbar under development from September '16. 
Read tutorialPype.pdf for some anticipations.
Read automatic documentation of Python modules for details and latest updates.