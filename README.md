"Flamingo tools" is a set of macros that I made to speed up some actions in FreeCAD, collected them in toolbars to make them readily available on the GUI.
To install the workbenches, copy as usual the sub-folders of \data and \Mod in the corresponding folders of FreeCAD installation of your system. 

The most developed workbench is CommandsFrame.py: that is one simple toolbox of 12 commands to arrange frames, trusses and similar in FreeCAD with the Arch`s Structure objects. 
Read tutorialFrame.pdf for more informations.

Other toolbars, not fully developed, are: 
    CommandsEagle.py: that's basically an addition, and shortcut, to the very fine FreeCAD-PCB workbench, to import position of objects from a .brd Eagle's file on a PCB drawn in FreeCAD with the a.m. workbench relating only on their names. -> "If the parts in the group Parts of the .FCStd file have the same name of the parts in the .brd file, they will be moved to the position of the PCB specified in the .brd file."
    CommandsPolar.py, to import a set of polar coordinates from a spreadsheet and use them to draw a sketch
    CommandsSpSh.py, just an experiment to manage data from spread sheets
    
