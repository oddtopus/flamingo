# FreeCAD Frame Tools module  
# (c) 2016 Riccardo Treu LGPL

import FreeCAD,FreeCADGui

############## AUXILIARY FUNCTIONS ###############

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

def intersection(beam=None,face=None):   # funziona esattamente solo se d!=0, ovvero se l'origine non appartiene al piano della faccia, altrimenti approssima con coeff. "a,b,c" molto alti
  from numpy import matrix
  # only for quick testing:
  if face==None:
    face = faces()[0]
  if beam==None:
    beam=beams()[0]
  
  # definition of plane
  range=face.ParameterRange
  points=[face.valueAt(x,y) for x in range[:2] for y in range[2:]]
  m=[[p.x,p.y,p.z] for p in points[:3]]
  M=matrix(m)
  abc=M.getI()*matrix('-1;-1;-1')      
  a,b,c=[float(abc[i,0]) for i in [0,1,2]]
  d=1
  FreeCAD.Console.PrintMessage('a=%f b=%f c=%f d=%f\n' %(a,b,c,d))
  # definition of line
  base=beam.Placement.Base
  FreeCAD.Console.PrintMessage('base=(%.2f,%.2f,%.2f)\n' %(base.x,base.y,base.z))
  v=beam.Placement.Rotation.multVec(FreeCAD.Vector(0,0,1)).normalize()
  FreeCAD.Console.PrintMessage('v=(%.2f,%.2f,%.2f)\n' %(v.x,v.y,v.z))
  #intersection
  k=-1*(a*base.x+b*base.y+c*base.z+d)/(a*v.x+b*v.y+c*v.z)
  FreeCAD.Console.PrintMessage('k=%f\n' %float(k))
  P=base+v.scale(k,k,k)
  return P

def isOrtho(e1=None,e2=None):
  '"True" if two Edges or Vectors or the normal of Faces are orthogonal (with a margin)'
  v=[]
  if (e1==None or e2==None):
    if len(faces())>1:
      e1,e2=faces()[:2]
    elif len(edges())>1:
      e1,e2=edges()[:2]
  for e in [e1,e2]:
    if hasattr(e,'ShapeType'):
      if e.ShapeType=='Edge':
        v.append(e.tangentAt(0))
      elif e.ShapeType=='Face':
        v.append(e.normalAt(0,0))
    else:
      v.append(e)
  return round(v[0].dot(v[1]),2)==0

def isParallel(e1=None,e2=None):
  '"True" if two Edges or Vectors or the normal of Faces are parallel (with a margin)'
  v=[]
  if (e1==None or e2==None):
    if len(faces())>1:
      e1,e2=faces()[:2]
    elif len(edges())>1:
      e1,e2=edges()[:2]
  for e in [e1,e2]:
    if hasattr(e,'ShapeType'):
      if e.ShapeType=='Edge':
        v.append(e.tangentAt(0))
      elif e.ShapeType=='Face':
        v.append(e.normalAt(0,0))
    else:
      v.append(e)
  return round(v[0].cross(v[1]).Length,2)==0

def beamAx(beam):
  "returns the vector parallel to the beam's axis"
  return beam.Placement.Rotation.multVec(FreeCAD.Vector(0.0,0.0,1.0)).normalize()

def spinTheBeam(beam, angle):
  '''arg1=beam, arg2=angle: rotate the section of the beam'''
  if beam.TypeId=="Part::FeaturePython" and "Base" in beam.PropertiesList:
    beam.Base.Placement=FreeCAD.Placement(FreeCAD.Vector(0.0,0.0,0.0),FreeCAD.Rotation(FreeCAD.Vector(0.0,0.0,1.0),angle))

def getDistance():
  'measure the lenght of an edge or the distance of two shapes'
  shapes=[y for x in FreeCADGui.Selection.getSelectionEx() for y in x.SubObjects if hasattr(y,'ShapeType')]
  if len(shapes)==1 and shapes[0].ShapeType=='Edge':
      return shapes[0].Length
  elif len(shapes)>1:
    return shapes[0].distToShape(shapes[1])[0]
  else:
    return None

############ COMMANDS #############

def placeTheBeam(beam, edge):
  '''arg1= beam, arg2= edge: lay down the selected beam on the selected edge'''
  vect=edge.tangentAt(0)
  beam.Placement.Rotation=FreeCAD.Rotation(0,0,0,1)
  rot=FreeCAD.Rotation(beam.Placement.Rotation.Axis,vect)
  beam.Placement.Rotation=rot.multiply(beam.Placement.Rotation)  # this method is not fully accurate, probably for the deg/rot conversion: this don't allow verification of perpendicularity or parallelism with the .cross() method!
  beam.Placement.Base=edge.valueAt(0)
  beam.Height=edge.Length
  FreeCAD.activeDocument().recompute()

def rotTheBeam(beam,faceBase,faceAlign):
  '''arg1=beam, arg2=faceBase, arg3=faceToMakeParallel: rotate the beams to make the flanges parallel to that of first selection.'''
  n1=faceBase.normalAt(0,0)
  n2=faceAlign.normalAt(0,0)
  rot=FreeCAD.Rotation(n2,n1)
  beam.Placement.Rotation=rot.multiply(beam.Placement.Rotation)

def shiftTheBeam(beam,edge,dist=100, ask4revert=True):
  '''arg1=beam, arg2=edge, arg3=dist=100: shifts the beam along the edge by dist (default 100)'''
  vect=edge.valueAt(edge.LastParameter)-edge.valueAt(edge.FirstParameter)
  vect.normalize()
  beam.Placement.Base=beam.Placement.Base.add(vect*dist)
  if ask4revert:
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

def pivotTheBeam(ang=None, ask4revert=True):
  if len(edges())!=1:
    FreeCAD.Console.PrintError('Wrong selection\n')
    return None
  edge=edges()[0] #FreeCADGui.Selection.getSelectionEx()[0].SubObjects[0]
  beam=FreeCADGui.Selection.getSelection()[0]
  from PySide.QtGui import QInputDialog as qid
  if ang==None:
    ang=float(qid.getText(None,"pivot a beam","angle?")[0])
  rot=FreeCAD.Rotation(edge.tangentAt(0),ang)
  beam.Placement.Rotation=rot.multiply(beam.Placement.Rotation)
  edgePost=edges()[0] #FreeCADGui.Selection.getSelectionEx()[0].SubObjects[0]
  dist=edge.CenterOfMass-edgePost.CenterOfMass
  beam.Placement.move(dist)
  if ask4revert:
    from PySide.QtGui import QMessageBox as MBox
    dirOK=MBox.question(None, "", "Direction is correct?", MBox.Yes | MBox.No, MBox.Yes)
    if dirOK==MBox.No:
      edge=edges()[0] #FreeCADGui.Selection.getSelectionEx()[0].SubObjects[0]
      rot=FreeCAD.Rotation(edge.tangentAt(0),ang*-2)
      beam.Placement.Rotation=rot.multiply(beam.Placement.Rotation)
      edgePost=edges()[0] #FreeCADGui.Selection.getSelectionEx()[0].SubObjects[0]
      dist=edge.CenterOfMass-edgePost.CenterOfMass
      beam.Placement.move(dist)

def stretchTheBeam(beam,L):
  if beam!=None and beam.TypeId=="Part::FeaturePython" and hasattr(beam,"Height"):
    beam.Height=L
      
def extendTheBeam(beam,target):
  '''arg1=beam, arg2=target: extend the beam to a plane, normal to its axis, defined by target.
  If target is a Vertex the plane is the one that includes target.
  If target is a Face, the plane is the one that includes the intersection between the axis of beam and the plane of the face.
  Else, the plane is the one normal to the axis of beam that includes the CenterOfMass'''
  distBase=distTop=0
  vBase=beam.Placement.Base
  #vBeam=beam.Placement.Rotation.multVec(FreeCAD.Vector(0.0,0.0,1.0))
  vBeam=beamAx(beam)
  h=beam.Height
  vTop=vBase+vBeam.scale(h,h,h)
  if target.ShapeType=="Vertex":
    distBase=vBase.distanceToPlane(target.Point,vBeam)
    distTop=vTop.distanceToPlane(target.Point,vBeam)
  elif target.ShapeType=="Face":
    if not isOrtho(target,vBeam):
      from Part import Point
      Pint=Point(intersection(beam,target)).toShape()
      distBase=vBase.distanceToPlane(Pint.Point,vBeam)
      distTop=vTop.distanceToPlane(Pint.Point,vBeam)
  elif hasattr(target,"CenterOfMass"):
    distBase=vBase.distanceToPlane(target.CenterOfMass,vBeam)
    distTop=vTop.distanceToPlane(target.CenterOfMass,vBeam)
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
