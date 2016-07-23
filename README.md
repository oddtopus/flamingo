"Flamingo tools" is a set of macros that I made to speed up some actions in FreeCAD. Then I collected them in workbenches to make them readily available on the GUI.
The main part is the CommandsFrame.py workbench: one simple toolbox of 12 commands to arrange frames, trusses and similar in FreeCAD with the Arch`s Structure objects. I did not documented these functions yet: while you experiment, remember that the commands may have a different behaviour in case you selected objects before clicking the corresponding button (fillFrame, stretchBeam and levelBeam classes, for instance).

Other workbenches, not fully developed, are: 
    CommandsEagle.py, to import position of objects from a .brd Eagle's file based only on their names (that's and addition to the very fine FreeCAD-PCB workbench)
    CommandsPolar.py, to import a set of polar coordinates from a spreadsheet
    CommandsSpSh.py, just an experiment to manage data from spread sheets
    
TODO.txt  is a partial list of features that I'm looking to add soon, in my spare time. This means it may be not "so soon".

Suggestions and feebacks are welcome.
