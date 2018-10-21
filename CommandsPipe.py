#(c) 2016 R. T. LGPL: part of Flamingo tools w.b. for FreeCAD

__title__="pypeTools toolbar"
__author__="oddtopus"
__url__="github.com/oddtopus/flamingo"
__license__="LGPL 3"

# import FreeCAD modules
import FreeCAD, FreeCADGui,inspect, os

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
    pipForm=pipeForms.insertPipeForm()
  def GetResources(self):
    return{'Pixmap':os.path.join(os.path.dirname(os.path.abspath(__file__)),"icons","pipe.svg"),'MenuText':'Insert a tube','ToolTip':'Insert a tube'}

class insertElbow: 
  def Activated (self):
    import pipeForms,FreeCAD
    elbForm=pipeForms.insertElbowForm()
  def GetResources(self):
    return{'Pixmap':os.path.join(os.path.dirname(os.path.abspath(__file__)),"icons","elbow.svg"),'MenuText':'Insert a curve','ToolTip':'Insert a curve'}

class insertReduct: 
  def Activated (self):
    import pipeForms
    pipeFormObj=pipeForms.insertReductForm()
  def GetResources(self):
    return{'Pixmap':os.path.join(os.path.dirname(os.path.abspath(__file__)),"icons","reduct.svg"),'MenuText':'Insert a reduction','ToolTip':'Insert a reduction'}

class insertCap: 
  def Activated (self):
    import pipeForms
    pipeFormObj=pipeForms.insertCapForm()
  def GetResources(self):
    return{'Pixmap':os.path.join(os.path.dirname(os.path.abspath(__file__)),"icons","cap.svg"),'MenuText':'Insert a cap','ToolTip':'Insert a cap'}

class insertFlange:
  def Activated (self):
    import pipeForms
    pipeFormObj=pipeForms.insertFlangeForm()
  def GetResources(self):
    return{'Pixmap':os.path.join(os.path.dirname(os.path.abspath(__file__)),"icons","flange.svg"),'MenuText':'Insert a flange','ToolTip':'Insert a flange'}

class insertUbolt:
  def Activated (self):
    import pipeForms
    pipeFormObj=pipeForms.insertUboltForm()
  def GetResources(self):
    return{'Pixmap':os.path.join(os.path.dirname(os.path.abspath(__file__)),"icons","clamp.svg"),'MenuText':'Insert a U-bolt','ToolTip':'Insert a U-bolt'}

class insertPypeLine:
  def Activated (self):
    import pipeForms
    pipeFormObj=pipeForms.insertPypeLineForm()
  def GetResources(self):
    return{'Pixmap':os.path.join(os.path.dirname(os.path.abspath(__file__)),"icons","pypeline.svg"),'MenuText':'PypeLine Manager','ToolTip':'Open PypeLine Manager'}

class insertBranch:
  def Activated (self):
    import pipeForms
    #pipeCmd.makeBranch()
    pipeFormObj=pipeForms.insertBranchForm()
  def GetResources(self):
    return{'Pixmap':os.path.join(os.path.dirname(os.path.abspath(__file__)),"icons","branch.svg"),'MenuText':'Insert a branch','ToolTip':'Insert a PypeBranch'}

class breakPipe:
  def Activated (self):
    import pipeForms
    pipeFormObj=pipeForms.breakForm()
  def GetResources(self):
    return{'Pixmap':os.path.join(os.path.dirname(os.path.abspath(__file__)),"icons","break.svg"),'MenuText':'Break the pipe','ToolTip':'Break one pipe at point and insert gap'}

class mateEdges:
  def Activated (self):
    import pipeCmd
    FreeCAD.activeDocument().openTransaction('Mate')
    pipeCmd.alignTheTube()
    FreeCAD.activeDocument().commitTransaction()
    FreeCAD.activeDocument().recompute()
  def GetResources(self):
    return{'Pixmap':os.path.join(os.path.dirname(os.path.abspath(__file__)),"icons","mate.svg"),'Accel':"M,E",'MenuText':'Mate pipes edges','ToolTip':'Mate two terminations through their edges'}

class flat:  # tool implemented with pipeCmd.placeTheElbow()
  def Activated (self):
    import frameCmd, pipeCmd
    if len(frameCmd.beams())>1:
      p1,p2=frameCmd.beams()[:2]
      try:
        P=frameCmd.intersectionCLines(p1,p2)
        com1=p1.Shape.Solids[0].CenterOfMass
        com2=p2.Shape.Solids[0].CenterOfMass
        v1=P-com1
        v2=com2-P
        curves=[e for e in FreeCADGui.Selection.getSelection() if hasattr(e,'PType') and hasattr(e,'BendAngle')]
        if curves:
          FreeCAD.ActiveDocument.openTransaction('Place one curve')
          pipeCmd.placeoTherElbow(curves[0],v1,v2,P)
          FreeCAD.ActiveDocument.recompute() # recompute for the elbow
          port1,port2=pipeCmd.portsPos(curves[0])
          if (com1-port1).Length<(com1-port2).Length:
            frameCmd.extendTheBeam(p1,port1)
            frameCmd.extendTheBeam(p2,port2)
          else:
            frameCmd.extendTheBeam(p1,port2)
            frameCmd.extendTheBeam(p2,port1)
          FreeCAD.ActiveDocument.recompute() # recompute for the pipes
          FreeCAD.ActiveDocument.commitTransaction()
        else:
          FreeCAD.Console.PrintError('Select at least one elbow')
      except:
        FreeCAD.Console.PrintError('Intersection point not found\n')
    else:
      FreeCAD.Console.PrintError('Select two intersecting pipes\n')
  def GetResources(self):
    return{'Pixmap':os.path.join(os.path.dirname(os.path.abspath(__file__)),"icons","flat.svg"),'MenuText':'Fit one elbow','ToolTip':'Place the elbow between two pipes or beams'}

class extend2intersection:
  def Activated (self):
    import pipeCmd
    FreeCAD.activeDocument().openTransaction('Xtend2int')
    pipeCmd.extendTheTubes2intersection()
    FreeCAD.activeDocument().recompute()
    FreeCAD.activeDocument().commitTransaction()
  def GetResources(self):
    return{'Pixmap':os.path.join(os.path.dirname(os.path.abspath(__file__)),"icons","intersect.svg"),'MenuText':'Extends pipes to intersection','ToolTip':'Extends pipes to intersection'}

class extend1intersection:
  def Activated (self):
    import pipeCmd
    FreeCAD.activeDocument().openTransaction('Xtend1int')
    pipeCmd.extendTheTubes2intersection(both=False)
    FreeCAD.activeDocument().recompute()
    FreeCAD.activeDocument().commitTransaction()
  def GetResources(self):
    return{'Pixmap':os.path.join(os.path.dirname(os.path.abspath(__file__)),"icons","intersect1.svg"),'MenuText':'Extends pipe to intersection','ToolTip':'Extends pipe to intersection'}

class laydown:
  def Activated (self):
    import pipeCmd, frameCmd
    from Part import Plane
    refFace=[f for f in frameCmd.faces() if type(f.Surface)==Plane][0]
    FreeCAD.activeDocument().openTransaction('Lay-down the pipe')
    for b in frameCmd.beams():
      if pipeCmd.isPipe(b):
        pipeCmd.laydownTheTube(b,refFace)
    FreeCAD.activeDocument().recompute()
    FreeCAD.activeDocument().commitTransaction()
  def GetResources(self):
    return{'Pixmap':os.path.join(os.path.dirname(os.path.abspath(__file__)),"icons","laydown.svg"),'MenuText':'Lay-down the pipe','ToolTip':'Lay-down the pipe on the support plane'}

class raiseup:
  def Activated (self):
    import pipeCmd, frameCmd
    from Part import Plane
    selex=FreeCADGui.Selection.getSelectionEx()
    for sx in selex:
      sxFaces=[f for f in frameCmd.faces([sx]) if type(f.Surface)==Plane]
      if len(sxFaces)>0:
        refFace=sxFaces[0]
        support=sx.Object
    FreeCAD.activeDocument().openTransaction('Raise-up the support')
    for b in frameCmd.beams():
      if pipeCmd.isPipe(b):
        pipeCmd.laydownTheTube(b,refFace,support)
        break
    FreeCAD.activeDocument().recompute()
    FreeCAD.activeDocument().commitTransaction()
  def GetResources(self):
    return{'Pixmap':os.path.join(os.path.dirname(os.path.abspath(__file__)),"icons","raiseup.svg"),'MenuText':'Raise-up the support','ToolTip':'Raise the support to the pipe'}

class joinPype:
  '''
  
  '''
  def Activated(self):
    import FreeCAD, FreeCADGui, pipeForms #pipeObservers
    # s=pipeObservers.joinObserver()
    FreeCADGui.Control.showDialog(pipeForms.joinForm()) #.Selection.addObserver(s)
    
  def GetResources(self):
    return{'Pixmap':os.path.join(os.path.dirname(os.path.abspath(__file__)),"icons","join.svg"),'MenuText':'Join pypes','ToolTip':'Select the part-pype and the port'} 

class insertValve:
  def Activated (self):
    import pipeForms
    #pipeFormObj=pipeForms.insertValveForm()
    #FreeCADGui.Control.showDialog(pipeForms.insertValveForm()) 
    pipeFormObj=pipeForms.insertValveForm()
  def GetResources(self):
    return{'Pixmap':os.path.join(os.path.dirname(os.path.abspath(__file__)),"icons","valve.svg"),'MenuText':'Insert a valve','ToolTip':'Insert a valve'}

class attach2tube:
  def Activated (self):
    import pipeCmd
    FreeCAD.activeDocument().openTransaction('Attach to tube')
    pipeCmd.attachToTube()
    FreeCAD.activeDocument().recompute()
    FreeCAD.activeDocument().commitTransaction()
  def GetResources(self):
    return{'Pixmap':os.path.join(os.path.dirname(os.path.abspath(__file__)),"icons","attach.svg"),'MenuText':'Attach  to tube','ToolTip':'Attach one pype to the nearest port of selected pipe'}

class point2point:

  def Activated(self):
    import pipeForms
    form = pipeForms.point2pointPipe()

  def GetResources(self):
    return{'Pixmap':os.path.join(os.path.dirname(os.path.abspath(__file__)),"icons","point2point.svg"),'MenuText':'draw a tube point-to-point','ToolTip':'Click on subsequent points.'}
    
class insertAny:
  '''
  Dialog to insert any object saved as .STEP, .IGES or .BREP in folder ../Mod/flamingo/shapes or subfolders.
  '''
  def Activated(self):
    import anyShape
    FreeCADGui.Control.showDialog(anyShape.shapeDialog()) 
    
  def GetResources(self):
    return{'MenuText':'Insert any shape','ToolTip':'Insert a STEP, IGES or BREP'}

class insertTank:
  def Activated(self):
    import FreeCADGui, pipeForms
    FreeCADGui.Control.showDialog(pipeForms.tankForm())
    
  def GetResources(self):
    return{'Pixmap':os.path.join(os.path.dirname(os.path.abspath(__file__)),"icons","tank.svg"),'MenuText':'Insert a tank','ToolTip':'Create tank and nozzles'} 

#---------------------------------------------------------------------------
# Adds the commands to the FreeCAD command manager
#---------------------------------------------------------------------------
addCommand('insertPipe',insertPipe()) 
addCommand('insertElbow',insertElbow())
addCommand('insertReduct',insertReduct())
addCommand('insertCap',insertCap())
addCommand('insertValve',insertValve())
addCommand('insertFlange',insertFlange())
addCommand('insertUbolt',insertUbolt())
addCommand('insertPypeLine',insertPypeLine())
addCommand('insertBranch',insertBranch())
addCommand('insertTank',insertTank())
addCommand('breakPipe',breakPipe())
addCommand('mateEdges',mateEdges())
addCommand('joinPype',joinPype())
addCommand('attach2tube',attach2tube())
addCommand('flat',flat())
addCommand('extend2intersection',extend2intersection())
addCommand('extend1intersection',extend1intersection())
addCommand('laydown',laydown())
addCommand('raiseup',raiseup())
addCommand('point2point',point2point())
addCommand('insertAny',insertAny())
