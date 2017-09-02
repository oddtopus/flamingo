#(c) 2016 R. T. LGPL: part of Flamingo tools w.b. for FreeCAD

__title__="pypeTools functions"
__author__="oddtopus"
__url__="github.com/oddtopus/flamingo"
__license__="LGPL 3"

import FreeCAD, FreeCADGui, Part, frameCmd, pipeFeatures
from DraftVecUtils import rounded
objToPaint=['Pipe','Elbow','Reduct','Flange','Cap']

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
  'True if obj is an elbow'
  return hasattr(obj,'PType') and obj.PType=='Elbow'
  
def moveToPyLi(obj,plName):
  pl=FreeCAD.ActiveDocument.getObjectsByLabel(plName)[0]
  group=FreeCAD.ActiveDocument.getObjectsByLabel(pl.Group)[0]
  group.addObject(obj)
  if hasattr(obj,'PType') and obj.PType in objToPaint:
    obj.ViewObject.ShapeColor=pl.ViewObject.ShapeColor

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
  #rot=FreeCAD.Rotation(FreeCAD.Vector(0,-1,0),Z)
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
      #directions.append(frameCmd.beamAx(thing))
    elif hasattr(thing,'ShapeType') and thing.ShapeType=='Edge':
      directions.append(rounded(thing.CenterOfMass-P))
  ang=180-degrees(directions[0].getAngle(directions[1]))
  if not propList:
    propList=["DN50",60.3,3.91,ang,45.24]
  else:
    propList[3]=ang
  elb=makeElbow(propList,P,directions[0].negative().cross(directions[1].negative()))
  # mate the elbow ends with the pipes or edges
  b=frameCmd.bisect(directions[0],directions[1])
  elbBisect=rounded(frameCmd.beamAx(elb,FreeCAD.Vector(1,1,0))) #if not rounded, fail in plane xz
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
  '''Adds a Reduct object
  makeReduct(propList=[], pos=None, Z=None)
    propList is one optional list with 6 elements:
      PSize (string): nominal diameter
      OD (float): major diameter
      OD2 (float): minor diameter
      thk (float): major thickness
      thk2 (float): minor thickness
      H (float): length of reduction      
    pos (vector): position of insertion; default = 0,0,0
    Z (vector): orientation: default = 0,0,1
  Remember: property PRating must be defined afterwards
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
  a.ViewObject.ShapeColor=0.0,0.0,1.0
  a.ViewObject.Transparency=85
  return a

def makeCap(propList=[], pos=None, Z=None):
  '''add a Cap object
  makeCap(propList,pos,Z);
  propList is one optional list with 4 elements:
    DN (string): nominal diameter
    OD (float): outside diameter
    thk (float): shell thickness
  Default is "DN50 (SCH-STD)"
  pos (vector): position of insertion; default = 0,0,0
  Z (vector): orientation: default = 0,0,1
  Remember: property PRating must be defined afterwards
  '''
  if pos==None:
    pos=FreeCAD.Vector(0,0,0)
  if Z==None:
    Z=FreeCAD.Vector(0,0,1)
  a=FreeCAD.ActiveDocument.addObject("Part::FeaturePython","Fondo")
  if len(propList)==3:
    pipeFeatures.Cap(a,*propList)
  else:
    pipeFeatures.Cap(a)
  a.ViewObject.Proxy=0
  a.Placement.Base=pos
  rot=FreeCAD.Rotation(FreeCAD.Vector(0,0,1),Z)
  a.Placement.Rotation=rot.multiply(a.Placement.Rotation)
  return a

def makeW():
  edges=frameCmd.edges()
  if len(edges)>1:
    P0=edges[0].valueAt(0)
    P1=edges[0].valueAt(edges[0].LastParameter)
    Pint=frameCmd.intersectionCLines(edges[0],edges[1])
    d0=Pint-P0
    d1=Pint-P1
    if d1.Length>d0.Length:
      P0=P1
    eds=list()
    for i in range(len(edges)-1):
      P1=frameCmd.intersectionCLines(edges[i],edges[i+1])
      eds.append(Part.Edge(Part.Line(P0,P1)))
      P0=P1
    P1=edges[-1].valueAt(edges[-1].LastParameter)
    P2=edges[-1].valueAt(0)
    d1=P1-P0
    d2=P2-P0
    if d1.Length<d2.Length:
      P1=P2
    eds.append(Part.Edge(Part.Line(P0,P1)))
    w=Part.Wire(eds)
    points=[e.valueAt(0) for e in w.Edges]
    last=e.Edges[-1]
    points.append(last.valueAt(last.LastParameter))
    from Draft import makeWire
    p=makeWire(points)
    p.Label='Path'
    drawAsCenterLine(p)
    return p
  else:
    FreeCAD.Console.PrintError('Not enough edges/n')
    return None

def makePypeLine2(DN="DN50",PRating="SCH-STD",OD=60.3,thk=3,BR=None, lab="Tubatura", pl=None, color=(0.8,0.8,0.8)):
  '''
  makePypeLine2(DN="DN50",PRating="SCH-STD",OD=60.3,thk=3,BR=None, lab="Tubatura",pl=None, color=(0.8,0.8,0.8))
  Adds a PypeLine2 object creating pipes over the selected edges.
  Default tube is "DN50", "SCH-STD"
  Bending Radius is set to 0.75*OD.
  '''
  if not BR:
    BR=0.75*OD
  # create the pypeLine group
  if not pl:
    a=FreeCAD.ActiveDocument.addObject("Part::FeaturePython",lab)
    pipeFeatures.PypeLine2(a,DN,PRating,OD,thk,BR, lab)
    a.ViewObject.Proxy=0
    a.ViewObject.ShapeColor=color
    if len(FreeCADGui.Selection.getSelection())==1:
      obj=FreeCADGui.Selection.getSelection()[0]
      isWire=hasattr(obj,'Shape') and type(obj.Shape)==Part.Wire
      isSketch=hasattr(obj,'TypeId') and obj.TypeId=='Sketcher::SketchObject'
      if isWire or isSketch:
        a.Base=obj
        a.Proxy.update(a)
      if isWire:
        moveToPyLi(obj,a.Label)
        drawAsCenterLine(obj)
    elif frameCmd.edges():
      path=makeW()
      moveToPyLi(path,a.Label)
      a.Base=path
      a.Proxy.update(a)
  else:
    a=FreeCAD.ActiveDocument.getObjectsByLabel(pl)[0]
    group=FreeCAD.ActiveDocument.getObjectsByLabel(a.Group)[0]
    a.Proxy.update(a,frameCmd.edges())
    FreeCAD.Console.PrintWarning("Objects added to pypeline's group "+a.Group+"\n")
  return a

def updatePLColor(sel=None, color=None):
  if not sel:
    sel=FreeCADGui.Selection.getSelection()
  if sel:
    pl=sel[0]
    if hasattr(pl,'PType') and pl.PType=='PypeLine':
      if not color:
        color=pl.ViewObject.ShapeColor
      group=FreeCAD.activeDocument().getObjectsByLabel(pl.Group)[0]
      for o in group.OutList:
        if hasattr(o,'PType') and o.PType in objToPaint:
          o.ViewObject.ShapeColor=color
  else:
    FreeCAD.Console.PrintError('Select first one pype line\n')

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
    else: return
  except:
    FreeCAD.Console.PrintError("Wrong selection.\n")
    return None
  rot=FreeCAD.Rotation(n2,n1)
  t2.Placement.Rotation=rot.multiply(t2.Placement.Rotation)
  #traslazione centri di curvatura
  d1,d2=frameCmd.edges() #redo selection to get new positions
  dist=d1.centerOfCurvatureAt(0)-d2.centerOfCurvatureAt(0)
  t2.Placement.move(dist)
  #verifica posizione relativa
  com1,com2=[t.Shape.Solids[0].CenterOfMass for t in [t1,t2]]
  if isElbow(t2):
    pass
  elif (com1-d1.centerOfCurvatureAt(0)).dot(com2-d1.centerOfCurvatureAt(0))>0:
    reverseTheTube(FreeCADGui.Selection.getSelectionEx()[:2][1])
    
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

def reverseTheTube(objEx):
  '''
  reverseTheTube(objEx)
  Reverse the orientation of objEx spinning it 180 degrees around the x-axis
  of its shape.
  If an edge is selected, it's used as pivot.
  '''
  disp=None
  selectedEdges=[e for e in objEx.SubObjects if e.ShapeType=='Edge']
  if selectedEdges:
    for edge in frameCmd.edges([objEx]):
      if edge.curvatureAt(0):
        disp=edge.centerOfCurvatureAt(0)-objEx.Object.Placement.Base
        break
      elif frameCmd.beams([objEx.Object]):
        ax=frameCmd.beamAx(objEx.Object)
        disp=ax*((edge.CenterOfMass-objEx.Object.Placement.Base).dot(ax))
  rotateTheTubeAx(objEx.Object,FreeCAD.Vector(1,0,0),180)
  if disp:
    objEx.Object.Placement.move(disp*2)
  
def rotateTheTubeEdge(ang=45):
  if len(frameCmd.edges())>0 and frameCmd.edges()[0].curvatureAt(0)!=0:
    originalPos=frameCmd.edges()[0].centerOfCurvatureAt(0)
    obj=FreeCADGui.Selection.getSelection()[0]
    rotateTheTubeAx(vShapeRef=shapeReferenceAxis(),angle=ang)
    newPos=frameCmd.edges()[0].centerOfCurvatureAt(0)
    obj.Placement.move(originalPos-newPos)

def flattenTheTube(obj=None,v1=None,v2=None,X=None):
  '''
  flattenTheTube(obj=None,v1=None,v2=None, X=None)
  Put obj in the same plane defined by vectors v1 and v2 and move it to X.
    obj: the object to be rotated
    v1, v2: the vectors of the plane
    X: the Placement.Base
  If no parameter is defined: v1, v2 are the axis of the first two beams 
  in the selections set, X is their intersection and obj is the first other
  object in the selection set. 
  '''
  if None in [obj,v1,v2]:
    try:
      sel=FreeCADGui.Selection.getSelection()
      t1,t2=frameCmd.beams()[:2]
      v1=frameCmd.beamAx(t1)
      v2=frameCmd.beamAx(t2)
      sel.remove(t1)
      sel.remove(t2)
      obj=sel[0]
      X = frameCmd.intersectionCLines(t1,t2)
    except:
      FreeCAD.Console.PrintError('Not enough arguments\n')
      return
  obj.Placement.Rotation = FreeCAD.Rotation(frameCmd.beamAx(obj),v1.cross(v2)).multiply(obj.Placement.Rotation)
  obj.Placement.Base = X
    
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
    
def breakTheTubes(point,pipes=[],gap=0):
  '''
  breakTheTube(point,pipes=[],gap=0)
  Breaks the "pipes" at "point" leaving a "gap".
  '''
  pipes2nd=list()
  if not pipes:
    pipes=[p for p in frameCmd.beams() if isPipe(p)]
  if pipes:
    for pipe in pipes:
      if point<float(pipe.Height) and gap<(float(pipe.Height)-point):
        propList=[pipe.PSize,float(pipe.OD),float(pipe.thk),float(pipe.Height)-point-gap]
        pipe.Height=point
        Z=frameCmd.beamAx(pipe)
        pos=pipe.Placement.Base+Z*(float(pipe.Height)+gap)
        pipe2nd=makePipe(propList,pos,Z)
        pipes2nd.append(pipe2nd)
    FreeCAD.activeDocument().recompute()
  return pipes2nd
    
def drawAsCenterLine(obj):
  try:
    obj.ViewObject.LineWidth=4
    obj.ViewObject.LineColor=1.0,0.3,0.0
    obj.ViewObject.DrawStyle='Dashdot'
  except:
    FreeCAD.Console.PrintError('The object can not be center-lined\n')
  
def getElbowPort(elbow, portId=0):
  '''
  getElbowPort(elbow, portId=0)
   Returns the position of the specified port of elbow.
  '''
  if isElbow(elbow):
    return elbow.Placement.multVec(elbow.Ports[portId])

def rotateTheElbowPort(curve=None, port=0, ang=45):
  '''
  rotateTheElbowPort(curve=None, port=0, ang=45)
   Rotates one curve aroud one of its circular edges.
  '''
  if curve==None:
    try:
      curve=FreeCADGui.Selection.getSelection()[0]
      if not isElbow(curve):
        FreeCAD.Console.PrintError('Please select an elbow.\n')
        return
    except:
      FreeCAD.Console.PrintError('Please select something before.\n')
  rotateTheTubeAx(curve,curve.Ports[port],ang)
  
  
