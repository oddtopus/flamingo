# FreeCAD EagleTools module  
# (c) 2016 Riccardo Treu LGPL

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
# Riccardo Treu - LGPL

class bareImport:
  def Activated (self):
    from eagleCmd import *
    print "- module eagleCmd.py imported -"
  def GetResources(self):
    return{'Pixmap':'Std_Tool1','MenuText':'Import Eagle tools','ToolTip':'Use this to import function brdIn() and brdCompare()'}

class doBrdImport:
  def Activated (self):
    import eagleCmd
    global brdPos
    brdPos=eagleCmd.brdIn()
    print "*** created global variable 'brdPos' ***\n"
  def GetResources(self):
    return{'Pixmap':'Std_Tool2','MenuText':'Import .brd positions','ToolTip':'Use this to execute function brdIn()'}

class doBrdDispose:
  def Activated (self):
    import eagleCmd
    if (brdPos):
      eagleCmd.brdCompare(brdPos)
      print "*** components moved to the specified position ***\n"
    else:
      print "*** global variable 'brdPos' not defined ***\n"
  def GetResources(self):
    return{'Pixmap':'Std_Tool3','MenuText':'Dispose components on PCB','ToolTip':'Use this to dispose components after imported the .brd'}

#---------------------------------------------------------------------------
# Adds the commands to the FreeCAD command manager
#---------------------------------------------------------------------------
addCommand('bareImport',bareImport()) 
addCommand('doBrdImport',doBrdImport())
addCommand('doBrdDispose',doBrdDispose())

