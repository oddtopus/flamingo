# FreeCAD Frame Tools module  
# (c) 2016 Riccardo Treu LGPL

# import FreeCAD modules
import FreeCAD, FreeCADGui, inspect, os

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

class frameIt:
  def Activated(self):
    import FreeCAD, FreeCADGui, frameObservers, frameCmd
    s=frameObservers.frameItObserver()
    FreeCADGui.Selection.addObserver(s)
    
  def GetResources(self):
    return{'Pixmap':os.path.join(os.path.dirname(os.path.abspath(__file__)),"icons","beamFit.svg"),'MenuText':'Beam-fit','ToolTip':'Place one beam over the sketch of a frame'}

class spinSect:
  def Activated(self):
    import FreeCAD, FreeCADGui, frameCmd, pipeCmd
    from math import pi
    FreeCAD.activeDocument().openTransaction('Spin')
    for beam in FreeCADGui.Selection.getSelection():#frameCmd.beams():
      #frameCmd.spinTheBeam(beam,beam.Base.Placement.Rotation.Angle/pi*180+45)
      pipeCmd.rotateTheTubeAx(beam)
    FreeCAD.activeDocument().recompute()
    FreeCAD.activeDocument().commitTransaction()
        
  def GetResources(self):
    return{'Pixmap':os.path.join(os.path.dirname(os.path.abspath(__file__)),"icons","beamRot.svg"),'MenuText':'SpinTheBeam','ToolTip':'Rotates the section of the beam by 45 degrees'}

class fillFrame:
  def Activated(self):
    import frameForms
    frameFormObj=frameForms.fillForm()
      
  def GetResources(self):
    return{'Pixmap':os.path.join(os.path.dirname(os.path.abspath(__file__)),"icons","fillFrame.svg"),'MenuText':'fillTheFrame','ToolTip':'Fill the sketch of the frame with the selected beam'}

class alignFlange:
  def Activated(self):
    import FreeCAD, FreeCADGui, frameCmd, frameObservers
    faces=frameCmd.faces()
    beams=frameCmd.beams()
    if len(faces)==len(beams)>0:
      FreeCAD.activeDocument().openTransaction('AlignFlange')
      faceBase=faces.pop(0)
      beams.pop(0)
      for i in range(len(beams)):
        frameCmd.rotTheBeam(beams[i],faceBase,faces[i])
      FreeCAD.activeDocument().recompute()
      FreeCAD.activeDocument().commitTransaction()
    else:
      FreeCADGui.Selection.clearSelection()
      s=frameObservers.alignFlangeObserver()
      FreeCADGui.Selection.addObserver(s)

  def GetResources(self):
    return{'Pixmap':os.path.join(os.path.dirname(os.path.abspath(__file__)),"icons","flangeAlign.svg"),'MenuText':'alignFlange','ToolTip':'Rotates the section of the beam to make the faces parallel to the first selection'}

class shiftBeam:
  
  def Activated(self):
    import frameForms
    frameFormObj=frameForms.translateForm()

  def GetResources(self):
    return{'Pixmap':os.path.join(os.path.dirname(os.path.abspath(__file__)),"icons","beamShift.svg"),'MenuText':'shiftTheBeam','ToolTip':'Move one beam along one edge'}

class levelBeam:
  def Activated(self):
    import FreeCAD, FreeCADGui, frameCmd, frameObservers
    selex=Gui.Selection.getSelectionEx()
    faces=frameCmd.faces(selex)
    beams=[sx.Object for sx in selex]
    if len(faces)==len(beams)>1:
      FreeCAD.activeDocument().openTransaction('LevelTheBeams')
      beams.pop(0)
      fBase=faces.pop(0)
      for i in range(len(beams)):
        frameCmd.levelTheBeam(beams[i],[fBase,faces[i]])
      FreeCAD.activeDocument().commitTransaction()
    elif len(faces)!=len(beams):
      FreeCAD.Console.PrintError('Select only one face for each beam.\n')
    else:
      FreeCADGui.Selection.clearSelection()
      s=frameObservers.levelBeamObserver()
      FreeCADGui.Selection.addObserver(s)

  def GetResources(self):
    return{'Pixmap':os.path.join(os.path.dirname(os.path.abspath(__file__)),"icons","beamLevel.svg"),'MenuText':'levelTheBeam','ToolTip':'Shift the beams to line-up the faces to the first selection (faces must be //)'}

class alignEdge:
  def Activated(self):
    import FreeCAD, FreeCADGui, frameCmd, frameObservers
    edges=frameCmd.edges()
    if len(edges)>=2 and len(FreeCADGui.Selection.getSelection())>=2:
      e1=edges.pop(0)
      beams=FreeCADGui.Selection.getSelection()[1:]
      if len(edges)==len(beams):
        pairs=[(beams[i],edges[i]) for i in range(len(beams))]
        FreeCAD.activeDocument().openTransaction('AlignEdge')
        for p in pairs:
          frameCmd.joinTheBeamsEdges(p[0],e1,p[1])
        FreeCAD.activeDocument().commitTransaction()
    else:
      FreeCADGui.Selection.clearSelection()
      s=frameObservers.alignEdgeObserver()
      FreeCADGui.Selection.addObserver(s)
    
  def GetResources(self):
    return{'Pixmap':os.path.join(os.path.dirname(os.path.abspath(__file__)),"icons","edgeAlign.svg"),'MenuText':'alignEdge','ToolTip':'Align two edges: select two or pre-select several'}

class pivotBeam:
  def Activated(self):
    import frameForms
    frameFormObj=frameForms.pivotForm()
      
    
  def GetResources(self):
    return{'Pixmap':os.path.join(os.path.dirname(os.path.abspath(__file__)),"icons","pivot.svg"),'MenuText':'pivotTheBeam','ToolTip':'Pivots the beam around an edge'}

class stretchBeam:
  def Activated(self):
    import frameForms
    frameFormObj=frameForms.stretchForm()
    
  def GetResources(self):
    return{'Pixmap':os.path.join(os.path.dirname(os.path.abspath(__file__)),"icons","beamStretch.svg"),'MenuText':'stretchTheBeam','ToolTip':'Changes the length of the beam, either according a preselected edge or a direct input'}

class extend:
  def Activated(self):
    import frameForms
    frameFormObj=frameForms.extendForm()
    
  def GetResources(self):
    return{'Pixmap':os.path.join(os.path.dirname(os.path.abspath(__file__)),"icons","extend.svg"),'MenuText':'extendTheBeam','ToolTip':'Extend the beam either to a face, a vertex or the c.o.m. of the selected object'}

class adjustFrameAngle:
  def Activated(self):
    import FreeCADGui, frameObservers
    FreeCADGui.Selection.clearSelection()
    s=frameObservers.adjustAngleObserver()
    FreeCADGui.Selection.addObserver(s)
    
  def GetResources(self):
    return{'Pixmap':os.path.join(os.path.dirname(os.path.abspath(__file__)),"icons","adjustAngle.svg"),'MenuText':'adjustFrameAngle','ToolTip':'Adjust the angle of frame by two edges'}

class rotJoin:
  def Activated(self):
    import FreeCAD, FreeCADGui, frameCmd, frameObservers
    try:
      if FreeCADGui.Selection.getSelectionEx()[0].SubObjects[0].ShapeType==FreeCADGui.Selection.getSelectionEx()[1].SubObjects[0].ShapeType=='Edge':
        FreeCAD.activeDocument().openTransaction('rotJoin')
        frameCmd.rotjoinTheBeam()
        FreeCAD.activeDocument().recompute()
        FreeCAD.activeDocument().commitTransaction()
    except:
      s=frameObservers.rotjoinObserver()
      FreeCADGui.Selection.addObserver(s)

  def GetResources(self):
    return{'Pixmap':os.path.join(os.path.dirname(os.path.abspath(__file__)),"icons","rotjoin.svg"),'MenuText':'rotJoinEdge','ToolTip':'Rotates and align the beam according another edge'}


#---------------------------------------------------------------------------
# Adds the commands to the FreeCAD command manager
#---------------------------------------------------------------------------
addCommand('frameIt',frameIt()) 
addCommand('spinSect',spinSect())
addCommand('fillFrame',fillFrame())
addCommand('alignFlange',alignFlange())
addCommand('shiftBeam',shiftBeam())
addCommand('levelBeam',levelBeam())
addCommand('alignEdge',alignEdge())
addCommand('pivotBeam',pivotBeam())
addCommand('stretchBeam',stretchBeam())
addCommand('extend',extend())
addCommand('adjustFrameAngle',adjustFrameAngle())
addCommand('rotJoin',rotJoin())
