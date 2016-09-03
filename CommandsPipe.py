"""
pipeTools workbench
(c) 2016 Riccardo Treu LGPL
"""

# import FreeCAD modules
import FreeCAD, FreeCADGui,inspect

# helper -------------------------------------------------------------------
# FreeCAD TemplatePyMod module  
# (c) 2007 Juergen Riegel LGPL

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

class insertPipe:
  def Activated (self):
    import pipeForms
    pipeFormObj=pipeForms.insertPipeForm()
  def GetResources(self):
    return{'Pixmap':'Std_Tool1','MenuText':'Insert a tube','ToolTip':'Insert a tube'}

class insertElbow: 
  def Activated (self):
    import pipeForms
    pipeFormObj=pipeForms.insertElbowForm()
  def GetResources(self):
    return{'Pixmap':'Std_Tool2','MenuText':'Insert a curve','ToolTip':'Insert a curve'}

class insertFlange:
  def Activated (self):
    import pipeForms
    pipeFormObj=pipeForms.insertFlangeForm()
  def GetResources(self):
    return{'Pixmap':'Std_Tool3','MenuText':'Insert a flange','ToolTip':'Insert a flange'}

class mateEdges:
  def Activated (self):
    import pipeCmd
    pipeCmd.alignTheTube()
    FreeCAD.activeDocument().recompute()
  def GetResources(self):
    return{'Pixmap':'python','MenuText':'Mate pipes edges','ToolTip':'Mate two terminations through their edges'}

class rotateAx:
  def Activated (self):
    import pipeForms
    pipeFormObj=pipeForms.rotateForm()
  def GetResources(self):
    return{'Pixmap':'python','MenuText':'Rotate through axis','ToolTip':'Rotate an object around an axis of its Shape'}

class rotateEdge:
  def Activated (self):
    import pipeForms
    pipeFormObj=pipeForms.rotateEdgeForm()
  def GetResources(self):
    return{'Pixmap':'python','MenuText':'Rotate through edge','ToolTip':'Rotate an object around the axis of a circular edge'}

class flat:
  def Activated (self):
    import pipeCmd
    pipeCmd.flattenTheTube()
    FreeCAD.activeDocument().recompute()
  def GetResources(self):
    return{'Pixmap':'python','MenuText':'Put in the plane','ToolTip':'Put the selected component in the plane defined by 2 axis'}

#---------------------------------------------------------------------------
# Adds the commands to the FreeCAD command manager
#---------------------------------------------------------------------------
addCommand('insertPipe',insertPipe()) 
addCommand('insertElbow',insertElbow())
addCommand('insertFlange',insertFlange())
addCommand('mateEdges',mateEdges())
addCommand('rotateAx',rotateAx())
addCommand('rotateEdge',rotateEdge())
addCommand('flat',flat())

