# FreeCAD Frame Tools module  
# (c) 2016 Riccardo Treu LGPL

import FreeCAD,FreeCADGui

def edges(selex=[], except1st=False):
  '''returns the list of edges in the selection set'''
  if len(selex)==0:
    selex=FreeCADGui.Selection.getSelectionEx()
  try:
    if except1st:
      eds=[e for sx in selex if sx!=selex[0] for so in sx.SubObjects for e in so.Edges]
    else:
      eds=[e for sx in selex for so in sx.SubObjects for e in so.Edges]
    FreeCAD.Console.PrintMessage('\nFound '+str(len(eds))+' edge(s).\n')
  except:
    FreeCAD.Console.PrintError('\nNo valid selection.\n')
  return eds

def beams(sel=[]):
  if len(sel)==0:
    sel=FreeCADGui.Selection.getSelection()
  return [i for i in sel if i.TypeId=="Part::FeaturePython" and hasattr(i,"Height")]

def vEdge(edge):
  '''returns the normalized direction of an edge'''
  if edge.ShapeType=='Edge':
    v=edge.valueAt(edge.LastParameter)-edge.valueAt(edge.FirstParameter)
    return v.normalize()

def faces(selex=[]):
  '''returns the list of faces in the selection set'''
  if len(selex)==0:
    selex=FreeCADGui.Selection.getSelectionEx()
  try:
    fcs=[f for sx in selex for so in sx.SubObjects for f in so.Faces]
    FreeCAD.Console.PrintMessage('\nFound '+str(len(fcs))+' face(s).\n')
  except:
    FreeCAD.Console.PrintError('\nNo valid selection.\n')
  return fcs

def placeTheBeam(beam, beamAx):
  '''arg1=beam, arg2=axis: moves and resizes the selected beam on the selected edge'''
  beam.Placement.Rotation=FreeCAD.Rotation(FreeCAD.Vector(0,0,1),0)
  if beam.TypeId=="Part::FeaturePython" and beamAx.TypeId=="Part::TopoShape":
    newdir=beam.Placement.Rotation.Axis.cross(beamAx.tangentAt(0))
    beam.Placement.Base=beamAx.valueAt(0)
    beam.Placement.Rotation=FreeCAD.Rotation(newdir,90)
    beam.Height=beamAx.Length
  else:
    FreeCAD.Console.PrintMessage("Wrong selection\n") 

def spinTheBeam(beam, angle):
  '''arg1=beam, arg2=angle: rotate the section of the beam'''
  if beam.TypeId=="Part::FeaturePython" and "Base" in beam.PropertiesList:
    beam.Base.Placement=FreeCAD.Placement(FreeCAD.Vector(0.0,0.0,0.0),FreeCAD.Rotation(FreeCAD.Vector(0.0,0.0,1.0),angle))

def orientTheBeam(beam, edge):
  '''arg1= beam, arg2= edge: copy, move and resize the selected beam on the selected edge'''
  vect=edge.valueAt(edge.LastParameter)-edge.valueAt(edge.FirstParameter)
  beam.Placement.Rotation=FreeCAD.Rotation(0,0,0,1)
  rot=FreeCAD.Rotation(beam.Placement.Rotation.Axis,vect)
  beam.Placement.Rotation=rot.multiply(beam.Placement.Rotation)    # this method is not fully accurate, probably for the deg/rot conversion: this don't allow verification of perpendicularity or parallelism with the .cross() method!
  beam.Placement.Base=edge.valueAt(0)
  beam.Height=edge.Length
  FreeCAD.activeDocument().recompute()

def rotTheBeam(beam,faceBase,faceAlign):
  '''arg1=beam, arg2=faceBase, arg3=faceToMakeParallel: rotate the beams to make the flanges parallel to that of first selection.'''
  n1=faceBase.normalAt(0,0)
  n2=faceAlign.normalAt(0,0)
  rot=FreeCAD.Rotation(n2,n1)
  beam.Placement.Rotation=rot.multiply(beam.Placement.Rotation)

def shiftTheBeam(beam,edge,dist=100):
  '''arg1=beam, arg2=edge, arg3=dist=100: shifts the beam along the edge by dist (default 100)'''
  vect=edge.valueAt(edge.LastParameter)-edge.valueAt(edge.FirstParameter)
  vect.normalize()
  beam.Placement.Base=beam.Placement.Base.add(vect*dist)
  from PySide.QtGui import QMessageBox as MBox
  dirOK=MBox.question(None, "", "Direction is correct?", MBox.Yes | MBox.No, MBox.Yes)
  if dirOK==MBox.No:
    beam.Placement.Base=beam.Placement.Base.add(vect*dist*-2)

def levelTheBeam(beam,faces):
  '''arg1=beams2move, arg2=[faces]: Shifts the second selection to make its flange coplanar to that of the first selection'''
  v=faces[0].CenterOfMass-faces[1].CenterOfMass
  n=faces[0].normalAt(0,0)
  dist=n.dot(v)
  beam.Placement.move(n.multiply(dist))

def joinTheBeamsEdges(beam,e1,e2):
    '''arg1=beam, arg2=edge target, arg3=edge start: aligns the edges'''
    beam.Placement.move(e1.distToShape(e2)[1][0][0]-e1.distToShape(e2)[1][0][1])

def pivotTheBeam():
  beam=FreeCADGui.Selection.getSelection()[0]
  edge=FreeCADGui.Selection.getSelectionEx()[0].SubObjects[0]
  from PySide.QtGui import QInputDialog as qid
  ang=float(qid.getText(None,"pivot a beam","angle?")[0])
  rot=FreeCAD.Rotation(edge.tangentAt(0),ang)
  beam.Placement.Rotation=rot.multiply(beam.Placement.Rotation)
  edgePost=FreeCADGui.Selection.getSelectionEx()[0].SubObjects[0]
  dist=edge.CenterOfMass-edgePost.CenterOfMass
  beam.Placement.move(dist)
  from PySide.QtGui import QMessageBox as MBox
  dirOK=MBox.question(None, "", "Direction is correct?", MBox.Yes | MBox.No, MBox.Yes)
  if dirOK==MBox.No:
    edge=FreeCADGui.Selection.getSelectionEx()[0].SubObjects[0]
    rot=FreeCAD.Rotation(edge.tangentAt(0),ang*-2)
    beam.Placement.Rotation=rot.multiply(beam.Placement.Rotation)
    edgePost=FreeCADGui.Selection.getSelectionEx()[0].SubObjects[0]
    dist=edge.CenterOfMass-edgePost.CenterOfMass
    beam.Placement.move(dist)

def stretchTheBeam(beam,L):
  if beam!=None and beam.TypeId=="Part::FeaturePython" and hasattr(beam,"Height"):
    beam.Height=L
      
def extendTheBeam(beam,target):
  vBase=beam.Placement.Base
  vBeam=beam.Placement.Rotation.multVec(FreeCAD.Vector(0.0,0.0,1.0))
  h=beam.Height
  vTop=vBase+vBeam.scale(h,h,h)
  if hasattr(target,"CenterOfMass"):
    distBase=vBase.distanceToPlane(target.CenterOfMass,vBeam)
    distTop=vTop.distanceToPlane(target.CenterOfMass,vBeam)
  elif target.ShapeType=="Vertex":
    distBase=vBase.distanceToPlane(target.Point,vBeam)
    distTop=vTop.distanceToPlane(target.Point,vBeam)
  if distBase*distTop>0:
    if abs(distBase)>abs(distTop):
      beam.Height+=FreeCAD.Units.Quantity(str(abs(distTop))+"mm")
    else:
      beam.Height+=FreeCAD.Units.Quantity(str(abs(distBase))+"mm")
      vMove=vBeam.normalize().scale(-distBase,-distBase,-distBase)
      beam.Placement.move(vMove)
  else:
    if abs(distBase)>abs(distTop):
      beam.Height-=FreeCAD.Units.Quantity(str(abs(distTop))+"mm")
    else:
      beam.Height-=FreeCAD.Units.Quantity(str(abs(distBase))+"mm")
      vMove=vBeam.normalize().scale(-distBase,-distBase,-distBase)
      beam.Placement.move(vMove)
  
  FreeCAD.activeDocument().recompute()

def rotjoinTheBeam():
  beam=beams()[1]
  e1,e2=edges()
  rot=FreeCAD.Rotation(e2.tangentAt(0),e1.tangentAt(0))
  beam.Placement.Rotation=rot.multiply(beam.Placement.Rotation)
  e2=edges()[1]
  joinTheBeamsEdges(beam,e1,e2)
