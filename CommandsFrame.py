#(c) 2016 R. T. LGPL: part of Flamingo tools w.b. for FreeCAD

__title__="frameTools toolbar"
__author__="oddtopus"
__url__="github.com/oddtopus/flamingo"
__license__="LGPL 3"

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
  '''
  Given a beam object and an edge in the model, this tool lay down the
  beam over the edge by selecting them one after the other until ESC is
  pressed.
  '''
  def Activated(self):
    import FreeCAD, FreeCADGui, frameObservers, frameCmd
    s=frameObservers.frameItObserver()
    FreeCADGui.Selection.addObserver(s)
    
  def GetResources(self):
    return{'Pixmap':os.path.join(os.path.dirname(os.path.abspath(__file__)),"icons","beamFit.svg"),'MenuText':'Place one-beam over one-edge','ToolTip':'Place one beam after the other over the edges'}

class spinSect:
  '''
  Tool to spin one object around the "Z" axis of its shape 
  by 45 degrees.
  '''
  def Activated(self):
    import FreeCAD, FreeCADGui, frameCmd, pipeCmd
    from math import pi
    FreeCAD.activeDocument().openTransaction('Spin')
    for beam in FreeCADGui.Selection.getSelection():
      pipeCmd.rotateTheTubeAx(beam)
    FreeCAD.activeDocument().recompute()
    FreeCAD.activeDocument().commitTransaction()
        
  def GetResources(self):
    return{'Pixmap':os.path.join(os.path.dirname(os.path.abspath(__file__)),"icons","beamRot.svg"),'MenuText':'Spin beams by 45 deg.','ToolTip':'Rotates the section of the beam by 45 degrees'}

class reverseBeam:
  '''
  Tool to spin one object around the "X" axis of its shape 
  by 180 degrees.
  Note: - if one edge of the object is selected, that is used
  as the pivot of rotation.
  '''
  def Activated(self):
    import FreeCAD, FreeCADGui, pipeCmd
    FreeCAD.activeDocument().openTransaction('Reverse')
    for objEx in FreeCADGui.Selection.getSelectionEx():
      pipeCmd.reverseTheTube(objEx)
    FreeCAD.activeDocument().recompute()
    FreeCAD.activeDocument().commitTransaction()
        
  def GetResources(self):
    return{'Pixmap':os.path.join(os.path.dirname(os.path.abspath(__file__)),"icons","reverse.svg"),'MenuText':'Reverse orientation','ToolTip':'Reverse the orientation of selected objects'}

class fillFrame:
  '''
  Dialog to create over multiple edges selected in the viewport the
  beams of the type of that previously chosen among those present
  in the model.
  '''
  def Activated(self):
    import frameForms
    #frameFormObj=frameForms.fillForm()
    FreeCADGui.Control.showDialog(frameForms.fillForm())
      
  def GetResources(self):
    return{'Pixmap':os.path.join(os.path.dirname(os.path.abspath(__file__)),"icons","fillFrame.svg"),'MenuText':'Fill the frame','ToolTip':'Fill the sketch of the frame with the selected beam'}

class alignFlange:
  '''
  Tool to rotate beams (or other objects) so that their surfaces are 
  parallel to one reference plane.
  If multiple faces are preselected, objects will be rotated according
  the first face in the selections set. Otherwise the program prompts
  to select one reference face and then the faces to be reoriented until
  ESC is pressed.
  '''
  def Activated(self):
    import frameForms
    FreeCADGui.Control.showDialog(frameForms.alignForm())

  def GetResources(self):
    return{'Pixmap':os.path.join(os.path.dirname(os.path.abspath(__file__)),"icons","flangeAlign.svg"),'MenuText':'alignFlange','ToolTip':'Rotates the section of the beam to make the faces parallel to another face'}

class shiftBeam:
  '''
  Dialog to translate and copy objects.
  * "x/y/z" textboxes: direct input of amount of translation in each 
  direction.
  * "Multiple" textbox: the multiple coefficient of the translation
  amount.
  * "Steps" textbox: the denominator of the translation amount. It's
  used when the amount of translation is to be covered in some steps.
  * "move/copy" radiobuttons: to select if the selected objects shall 
  be copied or only translated.
  * [Displacement] button: takes the amount and direction of translation
  from the distance of selected entities (points, edges, faces).
  * [Vector] button: defines the amount and direction of translation
  by the orientation and length of the selected edge.
  * [OK] button: execute the translation
  * [Cancel]: exits
  '''
  def Activated(self):
    import frameForms
    #frameFormObj=frameForms.translateForm()
    FreeCADGui.Control.showDialog(frameForms.translateForm())

  def GetResources(self):
    return{'Pixmap':os.path.join(os.path.dirname(os.path.abspath(__file__)),"icons","beamShift.svg"),'MenuText':'shiftTheBeam','ToolTip':'Translate objects by vectors defined on existing geometry'}

class levelBeam:
  '''
  Tool to flush the parallel faces of two objects.
  
  Note: - actually the command takes to the same level, respect the
  position and orientation of the first face selected, the center-of-mass
  of all faces selected. Thus it translates the objects even if the
  faces are not parallel.
  '''
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
    return{'Pixmap':os.path.join(os.path.dirname(os.path.abspath(__file__)),"icons","beamLevel.svg"),'MenuText':'Flush the surfaces','ToolTip':'Shift the beams to line-up the faces to the first selection (faces must be //)'}

class alignEdge:
  '''
  Tool to mate two parallel edges.
  
  Notes: - actually the command moves the objects along the minimum
  distance of their selected edge to the first one. Thus it translates
  the object even if edges are not parallel.
  - It is also possible to select two edges of the same objects. With
  this method is possible to move quickly one object by steps defined
  on its own geometry.
  '''
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
    return{'Pixmap':os.path.join(os.path.dirname(os.path.abspath(__file__)),"icons","edgeAlign.svg"),'MenuText':'Mate the edges','ToolTip':'Join two edges: select two or pre-select several'}

class pivotBeam:
  '''
  Dialog to rotate objects around one edge in the model or principal axis.
  * Dial or textbox: the degree of rotation.
  * "copy items" checkbox: select if the objects will be also copied.
  * [Select axis] button: choose the pivot.
  * [X / Y / Z]: choose one principal axis as pivot.
  '''
  def Activated(self):
    import frameForms
    #frameFormObj=frameForms.pivotForm()
    FreeCADGui.Control.showDialog(frameForms.rotateAroundForm()) 
    
  def GetResources(self):
    return{'Pixmap':os.path.join(os.path.dirname(os.path.abspath(__file__)),"icons","around.svg"),'MenuText':'pivotTheBeam','ToolTip':'Rotates the beam around an axis (edge or center-of-curvature)'}

class stretchBeam:
  '''
  Dialog to change the length of beams.
  * "mm" textbox: the new length that will be applied to selected beams.
  * [OK] button: execute the stretch operation to the selected beams.
  * [Get Length] button: takes the new length from the selected geometry,
  either the length of a beam or edge or the distance between geometric
  entities (point, edges, faces).
  * [Cancel]: exits
  * slider: extends the reference length from -100% to +100%.
  
  '''
  def Activated(self):
    import frameForms
    #frameFormObj=frameForms.stretchForm()
    FreeCADGui.Control.showDialog(frameForms.stretchForm())
    
  def GetResources(self):
    return{'Pixmap':os.path.join(os.path.dirname(os.path.abspath(__file__)),"icons","beamStretch.svg"),'MenuText':'stretchTheBeam','ToolTip':'Changes the length of the beam, either according a preselected edge or a direct input'}

class extend:
  '''
  Dialog to extend one beam to one selected target.
  Note: - if entities are preselected before calling this command, the
  first entity is automatically taken as target and the object attached
  to it is removed from selection set.
  '''
  def Activated(self):
    import frameForms
    #frameFormObj=frameForms.extendForm()
    FreeCADGui.Control.showDialog(frameForms.extendForm())
    
  def GetResources(self):
    return{'Pixmap':os.path.join(os.path.dirname(os.path.abspath(__file__)),"icons","extend.svg"),'MenuText':'extendTheBeam','ToolTip':'Extend the beam either to a face, a vertex or the c.o.m. of the selected object'}

class adjustFrameAngle:
  '''
  Tool to adjust the beams at square angles of frames.
  '''
  def Activated(self):
    import FreeCADGui, frameObservers
    FreeCADGui.Selection.clearSelection()
    s=frameObservers.adjustAngleObserver()
    FreeCADGui.Selection.addObserver(s)
    
  def GetResources(self):
    return{'Pixmap':os.path.join(os.path.dirname(os.path.abspath(__file__)),"icons","adjustAngle.svg"),'MenuText':'adjustFrameAngle','ToolTip':'Adjust the angle of frame by two edges'}

class rotJoin:
  '''
  Tool to translate and rotate the beams to mate two edges.
  '''
  def Activated(self):
    import FreeCAD, frameCmd
    if len(frameCmd.beams())>1:
      FreeCAD.activeDocument().openTransaction('rotJoin')
      frameCmd.rotjoinTheBeam()
      FreeCAD.activeDocument().recompute()
      FreeCAD.activeDocument().commitTransaction()
    else:
      FreeCAD.Console.PrintError('Please select two edges of beams before\n')

  def GetResources(self):
    return{'Pixmap':os.path.join(os.path.dirname(os.path.abspath(__file__)),"icons","rotjoin.svg"),'MenuText':'rotJoinEdge','ToolTip':'Rotates and align the beam according another edge'}

class insertPath:
  '''
  Tool to create a continuous DWire over the path defined by the
  edges selected in the viewport, even if these are not continuous or
  belongs to different objects.
  '''
  def Activated(self):
    import pipeCmd
    FreeCAD.activeDocument().openTransaction('make Path')
    pipeCmd.makeW()
    FreeCAD.activeDocument().recompute()
    FreeCAD.activeDocument().commitTransaction()

  def GetResources(self):
    return{'Pixmap':os.path.join(os.path.dirname(os.path.abspath(__file__)),"icons","path.svg"),'MenuText':'insert Path','ToolTip':'Creates one path along selected edges'}

class FrameLineManager:
  '''
  Dialog to create and change properties of objects FrameLine
  providing the following features:
  * a list of beams' profiles previously included in the model 
  by "insertSection" dialog;
  * a combo-box to select the active FrameLine among those already
  created or <new> to create a new one;
  * a text-box where to write the name of the FrameLine that is going
  to be created; if nothing or "<name>", the FrameLined will be named
  as default "Telaio00n";
  * [Insert] button: creates a new FrameLine object or adds new members
  to the one selected in the combo-box if edges are selected in the
  active viewport.
  * [Redraw] button: creates new beams and places them over the selected
  path. New beams will be collected inside the group of the FrameLine.
  Does not create or update beams added to the FrameLine outside
  its defined path.
  * [Clear] button: deletes all beams in the FrameLine group. It applies
  also to beams added to the FrameLine outside its defined path.
  * [Get Path] button: assigns the Dwire selected to the attribute Path
  of the FrameLine object.
  * [Get Profile] button: changes the Profile attribute of the FrameLine
  object to the one of the beam selected in the viewport or the one 
  selected in the list.
  * "Copy profile" checkbox: if checked generates a new profile object
  for each beam in order to avoid multiple references in the model.
  * "Move to origin" checkbox: if checked, moves the center-of-mass
  of the profile to the origin of coordinates system: that makes the
  centerline of the beam coincide with the c.o.m. of the profile.
  
  Notes: - if the name of a FrameLine object is modified, also the name
  of the relevant group will change automatically but not viceversa. 
  '''
  def Activated(self):
    if FreeCAD.ActiveDocument:
      import frameFeatures
      frameFormObj=frameFeatures.frameLineForm()

  def GetResources(self):
    return{'Pixmap':os.path.join(os.path.dirname(os.path.abspath(__file__)),"icons","frameline.svg"),'MenuText':'FrameLine Manager','ToolTip':'Open FrameLine Manager'}

class FrameBranchManager:
  '''
  Dialog to create and change properties of objects FrameBranch
  '''
  def Activated(self):
    if FreeCAD.ActiveDocument:
      import frameFeatures
      FreeCADGui.Control.showDialog(frameFeatures.frameBranchForm())

  def GetResources(self):
    return{'Pixmap':os.path.join(os.path.dirname(os.path.abspath(__file__)),"icons","framebranch.svg"),'MenuText':'FrameBranch Manager','ToolTip':'Open FrameBranch Manager'}

class insertSection:
  '''
  Dialog to create the set of profiles to be used in the model for
  object FrameLine.
  * "Section:" list: it includes all the sections defined in the .csv
  file corresponding to the selected section type.
  * "Section types:" list: the types of profiles defined with the .csv
  files included in the folder /tables
  * [Insert] button: creates the group "Profiles_set", if not already
  existing, and adds to it the object of the selected profile.
  
  Notes: - other profiles tables can be created by adding the relevant
  .csv file in the /tables folder.
  - Other profiles can be drafted in the model and dragged inside
  the group "Profiles_set". 
  - The orientation of the DWires may influence the rendering of beams
  on the FrameLine.
  '''
  def Activated(self):
    if FreeCAD.ActiveDocument:
      import frameFeatures
      frameFormObj=frameFeatures.insertSectForm()

  def GetResources(self):
    return{'Pixmap':os.path.join(os.path.dirname(os.path.abspath(__file__)),"icons","sect.svg"),'MenuText':'Insert Std. Sections','ToolTip':'Creates in the model standard beam profiles to be used with Frameline Manager'}

#---------------------------------------------------------------------------
# Adds the commands to the FreeCAD command manager
#---------------------------------------------------------------------------
addCommand('frameIt',frameIt()) 
addCommand('spinSect',spinSect())
addCommand('reverseBeam',reverseBeam())
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
addCommand('insertPath',insertPath())
addCommand('FrameLineManager',FrameLineManager())
addCommand('insertSection',insertSection())
addCommand('FrameBranchManager',FrameBranchManager())
