
#pipeTools functions
#(c) 2016 Riccardo Treu LGPL


import FreeCAD, FreeCADGui, Part, frameCmd, pipeFeatures

############### AUX FUNCTIONS ###################### 

def readTable(fileName="pipe_SCH-STD.csv"):
  '''
  readTable(fileName)
  Returns the dictionary read from file in ./tables
    fileName: the file name without path; default="pipe_SCH-STD.csv" 
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
  Z (vector): orientation: default = 0,0,0
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
  '''add an Elbow object
  makeElbow(propList,pos,Z);
  propList is one optional list with 5 elements:
    DN (string): nominal diameter
    OD (float): outside diameter
    thk (float): shell thickness
    BA (float): bend angle
    BR (float): bend radius
  Default is "DN50"
  pos (vector): position of insertion; default = 0,0,0
  Z (vector): orientation: default = 0,0,0
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

def makeFlange(propList=[], pos=None, Z=None):
  '''add a Flange object
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
  Z (vector): orientation: default = 0,0,0
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

def makeShell(L=800,W=400,H=500,thk=6):
  a=FreeCAD.ActiveDocument.addObject("Part::FeaturePython","Serbatoio")
  pipeFeatures.Shell(a)
  a.ViewObject.Proxy=0
  a.Placement.Base=FreeCAD.Vector(0,0,0)
  return a

def alignTheTube():
  '''
  Mates the selected 2 circular edges
  of 2 separate objects.
  '''
  try:
    t1,t2=FreeCADGui.Selection.getSelection()
    d1,d2=frameCmd.edges()
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
    
def extendTheTubes2intersection(pipe1=None,pipe2=None):
  '''
  Does what it says; also with beams.
  If arguments are None, it picks the first 2 selected beams().
  '''
  if pipe1==pipe2==None:
    pipe1,pipe2=frameCmd.beams()[:2]
  vectors=[]
  for pipe in [pipe1,pipe2]:
    vectors.append(pipe.Placement.Base)
    vectors.append(frameCmd.beamAx(pipe))
  P=frameCmd.intersectionLines(*vectors)
  if P!=None:
    frameCmd.extendTheBeam(pipe1,P)
    frameCmd.extendTheBeam(pipe2,P)
  else:
    FreeCAD.Console.PrintError('frameCmd.intersectionLines() has failed in extendTheTubes2intersection()!\n')
