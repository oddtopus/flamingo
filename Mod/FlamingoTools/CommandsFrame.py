# FreeCAD Frame Tools module  
# (c) 2016 Riccardo Treu LGPL

# import FreeCAD modules
import FreeCAD, FreeCADGui, inspect

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
    return{'Pixmap':str(FreeCAD.getResourceDir() + "Mod/FlamingoTools/beamFit.svg"),'MenuText':'Beam-fit','ToolTip':'Place one beam over the sketch of a frame'}

class spinSect:
  def Activated(self):
    import FreeCAD, FreeCADGui, frameCmd
    from math import pi
    #if FreeCADGui.Selection.countObjectsOfType("Part::FeaturePython")==1:
    #  for o in FreeCADGui.Selection.getSelection():
    #    if o.TypeId=="Part::FeaturePython":
    #      beam=o
    #      break
    for beam in frameCmd.beams():
      frameCmd.spinTheBeam(beam,beam.Base.Placement.Rotation.Angle/pi*180+45)
    #  frameCmd.spinTheBeam(beam,FreeCADGui.Selection.getSelection()[0].Base.Placement.Rotation.Angle/pi*180+45)
    FreeCAD.activeDocument().recompute()
        
  def GetResources(self):
    return{'Pixmap':str(FreeCAD.getResourceDir() + "Mod/FlamingoTools/beamRot.svg"),'MenuText':'Beam-fit','ToolTip':'Rotates the section of the beam by 45 degrees'}

class fillFrame:
  def Activated(self):
    import frameForms #frameCmd, frameObservers
    frameFormObj=frameForms.fillForm()
      
  def GetResources(self):
    return{'Pixmap':str(FreeCAD.getResourceDir() + "Mod/FlamingoTools/fillFrame.svg"),'MenuText':'fillTheFrame','ToolTip':'Fill the sketch of the frame with the selected beam'}

class alignFlange:
  def Activated(self):
    import FreeCAD, FreeCADGui, frameCmd, frameObservers
    faces=frameCmd.faces()
    beams=frameCmd.beams()
    if len(faces)==len(beams)>0:
      faceBase=faces.pop(0)
      beams.pop(0)
      for i in range(len(beams)):
        frameCmd.rotTheBeam(beams[i],faceBase,faces[i])
      FreeCAD.activeDocument().recompute()
    #elif len(faces)!=len(beams):
    #  FreeCAD.Console.PrintError('Please select only 1 face per beam!\n')
    else:
      FreeCADGui.Selection.clearSelection()
      s=frameObservers.alignFlangeObserver()
      FreeCADGui.Selection.addObserver(s)

  def GetResources(self):
    return{'Pixmap':str(FreeCAD.getResourceDir() + "Mod/FlamingoTools/flangeAlign.svg"),'MenuText':'alignFlange','ToolTip':'Rotates the section of the beam to make the faces parallel to the first selection'}

class shiftBeam:
  
  def Activated(self):
    import frameForms
    frameFormObj=frameForms.shiftForm()

  def GetResources(self):
    return{'Pixmap':str(FreeCAD.getResourceDir() + "Mod/FlamingoTools/beamShift.svg"),'MenuText':'shiftTheBeam','ToolTip':'Move one beam along one edge'}

class levelBeam:
  def Activated(self):
    import FreeCAD, FreeCADGui, frameCmd, frameObservers
    selex=Gui.Selection.getSelectionEx()
    faces=frameCmd.faces(selex)
    beams=[sx.Object for sx in selex]
    if len(faces)==len(beams)>0:
      beams.pop(0)
      fBase=faces.pop(0)
      for i in range(len(beams)):
        frameCmd.levelTheBeam(beams[i],[fBase,faces[i]])
    elif len(faces)!=len(beams):
      FreeCAD.Console.PrintError('Select only one face for each beam.\n')
    else:
      FreeCADGui.Selection.clearSelection()
      s=frameObservers.levelBeamObserver()
      FreeCADGui.Selection.addObserver(s)

  def GetResources(self):
    return{'Pixmap':str(FreeCAD.getResourceDir() + "Mod/FlamingoTools/beamLevel.svg"),'MenuText':'levelTheBeam','ToolTip':'Shift the beams to line-up the faces to the first selection (faces must be //)'}

class alignEdge:
  def Activated(self):
    import FreeCAD, FreeCADGui, frameCmd, frameObservers
    edges=frameCmd.edges()
    if len(edges)>=2 and len(FreeCADGui.Selection.getSelection())>=2:
      e1=edges.pop(0)
      beams=FreeCADGui.Selection.getSelection()[1:]
      if len(edges)==len(beams):
        pairs=[(beams[i],edges[i]) for i in range(len(beams))]
        for p in pairs:
          frameCmd.joinTheBeamsEdges(p[0],e1,p[1])
    else:
      FreeCADGui.Selection.clearSelection()
      s=frameObservers.alignEdgeObserver()
      FreeCADGui.Selection.addObserver(s)
    
  def GetResources(self):
    return{'Pixmap':str(FreeCAD.getResourceDir() + "Mod/FlamingoTools/edgeAlign.svg"),'MenuText':'alignEdge','ToolTip':'Align two edges: select two or pre-select several'}

class pivotBeam:
  def Activated(self):
    import frameForms
    FreeCADGui.Selection.clearSelection()
    frameFormObj=frameForms.pivotForm()
      
    
  def GetResources(self):
    return{'Pixmap':str(FreeCAD.getResourceDir() + "Mod/FlamingoTools/pivot.svg"),'MenuText':'fillTheFrame','ToolTip':'Pivots the beam around an edge'}

class stretchBeam:
  def Activated(self):
    import frameForms #FreeCAD, FreeCADGui, frameCmd, frameObservers
    frameFormObj=frameForms.stretchForm()
    
  def GetResources(self):
    return{'Pixmap':str(FreeCAD.getResourceDir() + "Mod/FlamingoTools/beamStretch.svg"),'MenuText':'stretchTheBeam','ToolTip':'Changes the length of the beam, either according a preselected edge or a direct input'}

class extend:
  def Activated(self):
    import frameForms #FreeCAD, FreeCADGui, frameCmd, frameObservers
    frameFormObj=frameForms.extendForm()
    
  def GetResources(self):
    return{'Pixmap':str(FreeCAD.getResourceDir() + "Mod/FlamingoTools/extend.svg"),'MenuText':'extend2edge','ToolTip':'Extend the beam either to a face, a vertex or the c.o.m. of the selected object'}

class adjustFrameAngle:
  def Activated(self):
    import FreeCAD, FreeCADGui, frameCmd, frameObservers
    edges=frameCmd.edges()
    beams=frameCmd.beams()
    if len(edges)==len(beams)==2:
      beams.reverse()
      for i in range(len(edges)):
      	frameCmd.extendTheBeam(beams[i],edges[i])
    else:
      FreeCADGui.Selection.clearSelection()
      s=frameObservers.adjustAngleObserver()
      FreeCADGui.Selection.addObserver(s)
    
    def Deactivated():
      FreeCADGui.Selection.removeObserver(s)
      FreeCAD.Console.PrintMessage('extend2edge stopped\n')
    
  def GetResources(self):
    return{'Pixmap':str(FreeCAD.getResourceDir() + "Mod/FlamingoTools/adjustAngle.svg"),'MenuText':'adjustFrameAngle','ToolTip':'Adjust the angle of frame by two edges'}

class rotJoin:
  def Activated(self):
    import FreeCAD, FreeCADGui, frameCmd, frameObservers
    try:
      if FreeCADGui.Selection.getSelectionEx()[0].SubObjects[0].ShapeType==FreeCADGui.Selection.getSelectionEx()[1].SubObjects[0].ShapeType=='Edge':
        frameCmd.rotjoinTheBeam()
        FreeCAD.activeDocument().recompute()
    except:
      s=frameObservers.rotjoinObserver()
      FreeCADGui.Selection.addObserver(s)
      #FreeCAD.Console.PrintError('Wrong selection\n')

  def Deactivated():
    FreeCADGui.Selection.removeObserver(s)
    FreeCAD.Console.PrintMessage('rotjoin stopped\n')

  def GetResources(self):
    return{'Pixmap':str(FreeCAD.getResourceDir() + "Mod/FlamingoTools/rotjoin.svg"),'MenuText':'rotJoinEdge','ToolTip':'Rotates and align the beam according another edge'}


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
