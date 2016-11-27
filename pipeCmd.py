#pipeTools functions
#(c) 2016 Riccardo Treu LGPL

import FreeCAD, FreeCADGui, Part, frameCmd, pipeFeatures
from DraftVecUtils import rounded

############### AUX FUNCTIONS ###################### 

def readTable(fileName="Pipe_SCH-STD.csv"):
  '''
  readTable(fileName)
  Returns the list of dictionaries read from file in ./tables
    fileName: the file name without path; default="Pipe_SCH-STD.csv" 
  '''
  from os.path import join, dirname, abspath
  import csv
  f=open(join(dirname(abspath(__file__)),"tables",fileName),'r')
  reader=csv.DictReader(f,delimiter=';')
  table=[]
  for row in reader:
    table.append(row)
  f.close()
  return table

def shapeReferenceAxis(obj=None, axObj=None):
  # function to get the reference axis of the shape for rotateTheTubeAx()
  # used in rotateTheTubeEdge() and pipeForms.rotateForm().getAxis()
  '''
  shapeReferenceAxis(obj, axObj)
  Returns the direction of an axis axObj
  according the original Shape orientation of the object obj
  If arguments are None axObj is the normal to one circular edge selected
  and obj is the object selected.
  '''
  if obj==None and axObj==None:
    selex=FreeCADGui.Selection.getSelectionEx()
    if len(selex)==1 and len(selex[0].SubObjects)>0:
      sub=selex[0].SubObjects[0]
      if sub.ShapeType=='Edge' and sub.curvatureAt(0)>0:  
        axObj=sub.tangentAt(0).cross(sub.normalAt(0))
        obj=selex[0].Object
  X=obj.Placement.Rotation.multVec(FreeCAD.Vector(1,0,0)).dot(axObj)
  Y=obj.Placement.Rotation.multVec(FreeCAD.Vector(0,1,0)).dot(axObj)
  Z=obj.Placement.Rotation.multVec(FreeCAD.Vector(0,0,1)).dot(axObj)
  axShapeRef=FreeCAD.Vector(X,Y,Z)
  return axShapeRef

def isPipe(obj):
  'True if obj is a tube'
  return hasattr(obj,'PType') and obj.PType=='Pipe'

def isElbow(obj):
  'True if obj is a tube'
  return hasattr(obj,'PType') and obj.PType=='Elbow'

################## COMMANDS ########################

def simpleSurfBend(path=None,profile=None):
  'select the centerline and the O.D. and let it sweep'
  curva=FreeCAD.activeDocument().addObject("Part::Feature","CurvaSemplice")
  if path==None or profile==None:
    curva.Shape=Part.makeSweepSurface(*frameCmd.edges()[:2])
  elif path.ShapeType==profile.ShapeType=='Edge':
    curva.Shape=Part.makeSweepSurface(path,profile)

def makePipe(propList=[], pos=None, Z=None):
  '''add a Pipe object
  makePipe(propList,pos,Z);
  propList is one optional list with 4 elements:
    DN (string): nominal diameter
    OD (float): outside diameter
    thk (float): shell thickness
    H (float): length of pipe
  Default is "DN50 (SCH-STD)"
  pos (vector): position of insertion; default = 0,0,0
  Z (vector): orientation: default = 0,0,1
  Remember: property PRating must be defined afterwards
  '''
  if pos==None:
    pos=FreeCAD.Vector(0,0,0)
  if Z==None:
    Z=FreeCAD.Vector(0,0,1)
  a=FreeCAD.ActiveDocument.addObject("Part::FeaturePython","Tubo")
  if len(propList)==4:
    pipeFeatures.Pipe(a,*propList)
  else:
    pipeFeatures.Pipe(a)
  a.ViewObject.Proxy=0
  a.Placement.Base=pos
  rot=FreeCAD.Rotation(FreeCAD.Vector(0,0,1),Z)
  a.Placement.Rotation=rot.multiply(a.Placement.Rotation)
  return a

def makeElbow(propList=[], pos=None, Z=None):
  '''Adds an Elbow object
  makeElbow(propList,pos,Z);
    propList is one optional list with 5 elements:
      DN (string): nominal diameter
      OD (float): outside diameter
      thk (float): shell thickness
      BA (float): bend angle
      BR (float): bend radius
    Default is "DN50"
    pos (vector): position of insertion; default = 0,0,0
    Z (vector): orientation: default = 0,0,1
  Remember: property PRating must be defined afterwards
  '''
  if pos==None:
    pos=FreeCAD.Vector(0,0,0)
  if Z==None:
    Z=FreeCAD.Vector(0,0,1)
  a=FreeCAD.ActiveDocument.addObject("Part::FeaturePython","Curva")
  if len(propList)==5:
    pipeFeatures.Elbow(a,*propList)
  else:
    pipeFeatures.Elbow(a)
  a.ViewObject.Proxy=0
  a.Placement.Base=pos
  rot=FreeCAD.Rotation(FreeCAD.Vector(0,0,1),Z)
  a.Placement.Rotation=rot.multiply(a.Placement.Rotation)
  return a

def makeElbowBetweenThings(thing1=None, thing2=None, propList=None):
  '''
  makeElbowBetweenThings(thing1, thing2, propList=None):
  Place one elbow at the intersection of thing1 and thing2.
  Things can be any combination of intersecting beams, pipes or edges.
  If nothing is passed as argument, the function attempts to take the
  first two edges selected in the view.
  propList is one optional list with 5 elements:
    DN (string): nominal diameter
    OD (float): outside diameter
    thk (float): shell thickness
    BA (float): bend angle - that will be recalculated! -
    BR (float): bend radius
  Default is "DN50 (SCH-STD)"
  Remember: property PRating must be defined afterwards
  '''
  from math import degrees
  if not (thing1 and thing2):
    thing1,thing2=frameCmd.edges()[:2]
  P=frameCmd.intersectionCLines(thing1,thing2)
  directions=list()
  for thing in [thing1,thing2]:
    if frameCmd.beams([thing]):
      directions.append(rounded((frameCmd.beamAx(thing).multiply(thing.Height/2)+thing.Placement.Base)-P))
    elif hasattr(thing,'ShapeType') and thing.ShapeType=='Edge':
      directions.append(rounded(thing.CenterOfMass-P))
  ang=180-degrees(directions[0].getAngle(directions[1]))
  if not propList:
    propList=["DN50",60.3,3.91,ang,45.24]
  else:
    #DN,OD,thk=propList[:3]
    #BR=propList[4]
    #propList=[DN,OD,thk,ang,BR]
    propList[3]=ang
  elb=makeElbow(propList,P,directions[0].negative().cross(directions[1].negative()))
  ## elb.PRating=PRating
  # mate the elbow ends with the pipes or edges
  b=frameCmd.bisect(directions[0],directions[1])
  elbBisect=frameCmd.beamAx(elb,FreeCAD.Vector(1,1,0))
  rot=FreeCAD.Rotation(elbBisect,b)
  elb.Placement.Rotation=rot.multiply(elb.Placement.Rotation)
  # trim automatically the adjacent tubes
  FreeCAD.activeDocument().recompute()
  portA=elb.Placement.multVec(elb.Ports[0])
  portB=elb.Placement.multVec(elb.Ports[1])
  for tube in [t for t in [thing1,thing2] if frameCmd.beams([t])]:
    vectA=tube.Shape.Solids[0].CenterOfMass-portA
    vectB=tube.Shape.Solids[0].CenterOfMass-portB
    if frameCmd.isParallel(vectA,frameCmd.beamAx(tube)):
      frameCmd.extendTheBeam(tube,portA)
    else:
      frameCmd.extendTheBeam(tube,portB)
  #FreeCAD.activeDocument().recompute()
  return elb

def makeFlange(propList=[], pos=None, Z=None):
  '''Adds a Flange object
  makeFlange(propList,pos,Z);
    propList is one optional list with 8 elements:
      DN (string): nominal diameter
      FlangeType (string): type of Flange
      D (float): flange diameter
      d (float): bore diameter
      df (float): bolts holes distance
      f (float): bolts holes diameter
      t (float): flange thickness
      n (int): nr. of bolts
    Default is "DN50 (PN16)"
    pos (vector): position of insertion; default = 0,0,0
    Z (vector): orientation: default = 0,0,1
  Remember: property PRating must be defined afterwards
  '''
  if pos==None:
    pos=FreeCAD.Vector(0,0,0)
  if Z==None:
    Z=FreeCAD.Vector(0,0,1)
  a=FreeCAD.ActiveDocument.addObject("Part::FeaturePython","Flangia")
  if len(propList)==8:
    pipeFeatures.Flange(a,*propList)
  else:
    pipeFeatures.Flange(a)
  a.ViewObject.Proxy=0
  a.Placement.Base=pos
  rot=FreeCAD.Rotation(FreeCAD.Vector(0,0,1),Z)
  a.Placement.Rotation=rot.multiply(a.Placement.Rotation)
  return a

def makeReduct(propList=[], pos=None, Z=None):
  '''add a Reduct object
  '''
  if pos==None:
    pos=FreeCAD.Vector(0,0,0)
  if Z==None:
    Z=FreeCAD.Vector(0,0,1)
  a=FreeCAD.ActiveDocument.addObject("Part::FeaturePython","Riduz")
  if len(propList)==6:
    pipeFeatures.Reduct(a,*propList)
  else:
    pipeFeatures.Reduct(a)
  a.ViewObject.Proxy=0
  a.Placement.Base=pos
  rot=FreeCAD.Rotation(FreeCAD.Vector(0,0,1),Z)
  a.Placement.Rotation=rot.multiply(a.Placement.Rotation)
  return a

def makeUbolt(propList=[], pos=None, Z=None):
  '''Adds a Ubolt object:
  makeUbolt(propList,pos,Z);
    propList is one optional list with 5 elements:
      PSize (string): nominal diameter
      ClampType (string): the clamp type or standard
      C (float): the diameter of the U-bolt
      H (float): the total height of the U-bolt
      d (float): the rod diameter
    pos (vector): position of insertion; default = 0,0,0
    Z (vector): orientation: default = 0,0,1
  Remember: property PRating must be defined afterwards
  '''
  if pos==None:
    pos=FreeCAD.Vector(0,0,0)
  if Z==None:
    Z=FreeCAD.Vector(0,0,1)
  a=FreeCAD.ActiveDocument.addObject("Part::FeaturePython","U-Bolt")
  if len(propList)==5:
    pipeFeatures.Ubolt(a,*propList)
  else:
    pipeFeatures.Ubolt(a)
  a.ViewObject.Proxy=0
  a.Placement.Base=pos
  rot=FreeCAD.Rotation(FreeCAD.Vector(0,0,1),Z)
  a.Placement.Rotation=rot.multiply(a.Placement.Rotation)
  return a

def makeShell(L=800,W=400,H=500,thk=6):
  '''
  makeShell(L,W,H,thk)
  Adds the shell of a tank, given
    L(ength):        default=800
    W(idth):         default=400
    H(eight):        default=500
    thk (thickness): default=6
  '''
  a=FreeCAD.ActiveDocument.addObject("Part::FeaturePython","Serbatoio")
  pipeFeatures.Shell(a,L,W,H,thk)
  a.ViewObject.Proxy=0
  a.Placement.Base=FreeCAD.Vector(0,0,0)
  return a

def makePypeLine(DN="DN50",PRating="SCH-STD",OD=60.3,thk=3,BR=None, lab=None, pl=None):
  '''
  makePypeLine(DN="DN50",PRating="SCH-STD",OD=60.3,thk=3,BR=None, lab=None)
  Adds a pypeLine object creating pipes over the selected edges.
  Default tube is "DN50", "SCH-STD" and BR=1.5*OD.
  '''
  if not BR:
    BR=1.5*OD
  # create the pypeLine group
  if not pl:
    a=FreeCAD.ActiveDocument.addObject("Part::FeaturePython","Tubatura")
    pipeFeatures.PypeLine(a,DN,PRating,OD,thk,BR, lab)
    a.ViewObject.Proxy=0
    a.Placement.Base=FreeCAD.Vector(0,0,0)
    group=FreeCAD.activeDocument().addObject("App::DocumentObjectGroup",a.Group)
    group.addObject(a)
  else:
    a=FreeCAD.ActiveDocument.getObjectsByLabel(pl)[0]
    FreeCAD.Console.PrintWarning("Objects added to pypeline's group "+a.Group+"\n")
    group=FreeCAD.ActiveDocument.getObjectsByLabel(a.Group)[0]
  # create tubes and fittings
  pipes=list()
  for e in frameCmd.edges():
    p=makePipe([a.PSize,OD,thk,e.Length],pos=e.valueAt(0),Z=e.tangentAt(0))
    p.PRating=PRating
    p.PSize=DN
    pipes.append(p.Label)
    group.addObject(p)
  n=len(pipes)
  objPipes=list()
  if not BR:
    BR=0.75*OD
  for p in pipes:
    objPipes.append(FreeCAD.ActiveDocument.getObjectsByLabel(p)[0])
  for i in range(n-1):
    c=makeElbowBetweenThings(objPipes[i],objPipes[i+1],[DN,OD,thk,0,BR])
    group.addObject(c)
  objPipes=[]
  return a

def alignTheTube():
  '''
  Mates the selected 2 circular edges
  of 2 separate objects.
  '''
  try:
    t1,t2=FreeCADGui.Selection.getSelection()[:2]
    d1,d2=frameCmd.edges()[:2]
    if d1.curvatureAt(0)!=0 and d2.curvatureAt(0)!=0:
      n1=d1.tangentAt(0).cross(d1.normalAt(0))
      n2=d2.tangentAt(0).cross(d2.normalAt(0))
  except:
    FreeCAD.Console.PrintError("Wrong selection.\n")
    return None
  rot=FreeCAD.Rotation(n2,n1)
  t2.Placement.Rotation=rot.multiply(t2.Placement.Rotation)
  #traslazione centri di curvatura
  d1,d2=frameCmd.edges() #redo selection to get new positions
  dist=d1.centerOfCurvatureAt(0)-d2.centerOfCurvatureAt(0)
  t2.Placement.move(dist)
  #controllo posizione
  #if len(t1.Shape.common(t2.Shape).Solids)>0:
  #  FreeCAD.Console.PrintWarning("Compenetration of solids!\n")
  #else:
  #  FreeCAD.Console.PrintMessage("OK.")
    
def rotateTheTubeAx(obj=None,vShapeRef=None, angle=45):
  '''
  rotateTheTubeAx(obj=None,vShapeRef=None,angle=45)
  Rotates obj around the vShapeRef axis of its Shape by an angle.
    obj: if not defined, the first in the selection set
    vShapeRef: if not defined, the Z axis of the Shape
    angle: default=45 deg
  '''
  if obj==None:
    obj=FreeCADGui.Selection.getSelection()[0]
  if vShapeRef==None:
    vShapeRef=FreeCAD.Vector(0,0,1)
  rot=FreeCAD.Rotation(frameCmd.beamAx(obj,vShapeRef),angle)
  obj.Placement.Rotation=rot.multiply(obj.Placement.Rotation)

def rotateTheTubeEdge(ang=45):
  if len(frameCmd.edges())>0 and frameCmd.edges()[0].curvatureAt(0)!=0:
    originalPos=frameCmd.edges()[0].centerOfCurvatureAt(0)
    obj=FreeCADGui.Selection.getSelection()[0]
    rotateTheTubeAx(vShapeRef=shapeReferenceAxis(),angle=ang)
    newPos=frameCmd.edges()[0].centerOfCurvatureAt(0)
    obj.Placement.move(originalPos-newPos)

def flattenTheTube(obj=None,v1=None,v2=None):
  '''
  flattenTheTube(obj=None,v1=None,v2=None)
  Put obj in the same plane defined by vectors v1 and v2.
    obj: the object to be rotated
    v1, v2: the vectors of the plane
  If no parameter is defined: v1, v2 are the axis of the first two beams 
  in the selections set and obj is the 3rd selection. 
  '''
  if obj==v1==v2==None:
    t1,t2,obj=FreeCADGui.Selection.getSelection()
    v1=frameCmd.beamAx(t1)
    v2=frameCmd.beamAx(t2)
  planeNorm=v1.cross(v2)
  rot=FreeCAD.Rotation(frameCmd.beamAx(obj),planeNorm)
  obj.Placement.Rotation=rot.multiply(obj.Placement.Rotation)
    
def extendTheTubes2intersection(pipe1=None,pipe2=None,both=True):
  '''
  Does what it says; also with beams.
  If arguments are None, it picks the first 2 selected beams().
  '''
  if not (pipe1 and pipe2):
    try:
      pipe1,pipe2=frameCmd.beams()[:2]
    except:
      FreeCAD.Console.PrintError('Insufficient arguments for extendTheTubes2intersection\n')
  P=frameCmd.intersectionCLines(pipe1,pipe2)
  if P!=None:
    frameCmd.extendTheBeam(pipe1,P)
    if both:
      frameCmd.extendTheBeam(pipe2,P)

def laydownTheTube(pipe=None, refFace=None, support=None):
  '''
  laydownTheTube(pipe=None, refFace=None, support=None)
  Makes one pipe touch one face if the center-line is parallel to it.
  If support is not None, support is moved towards pipe.
  '''
  if not(pipe and refFace):  # without argument take from selection set
    refFace=[f for f in frameCmd.faces() if type(f.Surface)==Part.Plane][0]
    pipe=[p for p in frameCmd.beams() if hasattr(p,'OD')] [0]
  try:
    if type(refFace.Surface)==Part.Plane and frameCmd.isOrtho(refFace,frameCmd.beamAx(pipe)) and hasattr(pipe,'OD'):
      dist=rounded(refFace.normalAt(0,0).multiply(refFace.normalAt(0,0).dot(pipe.Placement.Base-refFace.CenterOfMass)-float(pipe.OD)/2))
      if support:
        support.Placement.move(dist)
      else:
        pipe.Placement.move(dist.multiply(-1))
    else:
      FreeCAD.Console.PrintError('Face is not flat or not parallel to axis of pipe\n')
  except:
    FreeCAD.Console.PrintError('Wrong selection\n')