#(c) 2016 R. T. LGPL: part of Flamingo tools w.b. for FreeCAD

__title__="eagleTools toolbar"
__author__="oddtopus"
__url__="github.com/oddtopus/flamingo"
__license__="LGPL 3"

# import FreeCAD modules
import FreeCAD, FreeCADGui,inspect

# helper -------------------------------------------------------------------

def addCommand(name,cmdObject):
	(list,num) = inspect.getsourcelines(cmdObject.Activated)
	pos = 0
	# check for indentation
	while(list[1][pos] == ' ' or list[1][pos] == '\t'):
		pos += 1
	source = ""
	for i in range(len(list)-1):
		source += list[i+1][pos:]
	FreeCADGui.addCommand(name,cmdObject,source)

#---------------------------------------------------------------------------
# The command classes
#---------------------------------------------------------------------------

# Eagle import tool
# Riccardo Treu - LGPL  2016

class importPos:
  def Activated (self):
    import eagleForms
    eagleForm=eagleForms.eagleForm()
  def GetResources(self):
    return{'Pixmap':'Std_Tool1','MenuText':'Dispose components on PCB','ToolTip':'Use this to import positions from a .brd file and dispose components'}

#---------------------------------------------------------------------------
# Adds the commands to the FreeCAD command manager
#---------------------------------------------------------------------------
addCommand('importPos',importPos())

