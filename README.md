"Flamingo tools" is a set of macros that I made to speed up some actions in FreeCAD. Then I collected them in toolbars to make them readily available on the GUI.

The most developed one is CommandsFrame.py: that is one simple toolbox of 12 commands to arrange frames, trusses and similar in FreeCAD with the Arch`s Structure objects. The work flow is the following:
- Draft or Sketch the layout of your frame, or use the edges of a Part or PartDesign solid as the skeleton of your structure
- then create the beams you are going to use in your structure with Arch workbench
- finally switch to Flamingo tools and use the "frame" toolbar to place the beams on the edges or displace them as necessary

While you experiment, remember that the commands may have a different behaviour in case you selected objects before clicking the corresponding button (fillFrame, stretchBeam and levelBeam classes, for instance) or the selection is empty when invoking the command. I tryed to explain that in the command list and it could change during development.

Other toolbars, not fully developed, are: 
    CommandsEagle.py, to import position of objects from a .brd Eagle's file on a PCB based only on their names (that's and addition to the very fine FreeCAD-PCB workbench)
    CommandsPolar.py, to import a set of polar coordinates from a spreadsheet and use them to draw a sketch
    CommandsSpSh.py, just an experiment to manage data from spread sheets
    
TODO.txt  is a partial list of features that I'm looking to add soon, in my spare time. This means it may be not "so soon".

Suggestions and feebacks are welcome.
