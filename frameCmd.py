#(c) 2016 R. T. LGPL: part of Flamingo tools w.b. for FreeCAD

__title__="frameTools functions"
__author__="oddtopus"
__url__="github.com/oddtopus/flamingo"
__license__="LGPL 3"

import FreeCAD,FreeCADGui
import DraftGeomUtils as dgu
from DraftVecUtils import rounded

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
    #FreeCAD.Console.PrintMessage('\nFound '+str(len(eds))+' edge(s).\n')
  except:
    FreeCAD.Console.PrintError('\nNo valid selection.\n')
  return eds

def beams(sel=[]):
  '''
  Returns the selected "beams", i.e. FeaturePythons which have a Profile and an Height properties.
  '''
  if len(sel)==0:
    sel=FreeCADGui.Selection.getSelection()
  return [i for i in sel if i.TypeId=="Part::FeaturePython" and hasattr(i,"Height") and hasattr(i,"Profile")]

def faces(selex=[]):
  '''returns the list of faces in the selection set'''
  if len(selex)==0:
    selex=FreeCADGui.Selection.getSelectionEx()
  try:
    fcs=[f for sx in selex for so in sx.SubObjects for f in so.Faces]
    #FreeCAD.Console.PrintMessage('\nFound '+str(len(fcs))+' face(s).\n')
  except:
    FreeCAD.Console.PrintError('\nNo valid selection.\n')
  return fcs

def intersectionLines2(p1=None,v1=None,p2=None,v2=None):   # TODO!
  '''
  intersectionLines2(p1,v1,p2,v2)
  Returns the intersection between one line and the plane that includes the
  second line and orthogonal to the plane defined by both lines.
    p1,v1: the reference point and direction of first line
    p2,v2: the reference point and direction of second line
  '''
  if None in [p1,p2,v1,v2]:
    p1=edges()[0].valueAt(0)
    v1=edges()[0].tangentAt(0)
    p2=edges()[1].valueAt(0)
    v2=edges()[1].tangentAt(0)
  if isParallel(v1,v2):
    FreeCAD.Console.PrintError("Directions are pallel\n")
    return None
  else:
    dist=p1-p2
    norm=v2.cross(dist).cross(v1)
    #P1=FreeCAD.Vector(p1.x,p1.y,p1.z)
    return p1.projectToPlane(p2,norm)

def intersectionCLines(thing1=None, thing2=None):
  '''
  intersectionCLines(thing1=None, thing2=None)
  Returns the intersection (vector) of the center lines of thing1 and thing2.
  Things can be any combination of intersecting beams, pipes or edges.
  If less than 2 arguments are given, thing1 and thing2 are the first 2 beams
  or pipes found in the selection set.
  '''
  if not (thing1 and thing2):
    try:
      thing1,thing2=beams()[:2]
    except:
      FreeCAD.Console.PrintError('Insufficient arguments for intersectionCLines\n')
      return None
  edges=[]
  for thing in [thing1,thing2]:
    if beams([thing]):
      edges.append(vec2edge(thing.Placement.Base,beamAx(thing)))
    elif hasattr(thing,'ShapeType') and thing.ShapeType=='Edge':
      edges.append(thing)
  intersections=dgu.findIntersection(*edges, infinite1=True, infinite2=True)
  if len(intersections):
    return rounded(intersections[0])
  else:
    FreeCAD.Console.PrintError('No intersection found\n')
    return None
  

def intersectionLines(p1=None,v1=None,p2=None,v2=None): # OBSOLETE: replaced with intersectionCLines
  '''
  intersectionLines(p1,v1,p2,v2)
  If exist, returns the intersection (vector) between two lines 
    p1,v1: the reference point and direction of first line
    p2,v2: the reference point and direction of second line
  '''
  
  if None in [p1,p2,v1,v2]:
    eds=edges()[:2]
    p1,p2=[e.valueAt(0) for e in eds]
    v1,v2=[e.tangentAt(0) for e in eds]
  if not isParallel(v1,v2):  
    dist=p1-p2
    import numpy
    #M=numpy.matrix([list(v1),list(v2),list(dist)]) # does not work: it seems for lack of accuracy of FreeCAD.Base.Vector operations!
    rowM1=[round(x,2) for x in v1]
    rowM2=[round(x,2) for x in v2]
    rowM3=[round(x,2) for x in dist]
    M=numpy.matrix([rowM1,rowM2,rowM3])
    if numpy.linalg.det(M)==0: 
      #3 equations, 2 unknowns => 1 eq. must be dependent
      a11,a21,a31=list(v1)
      a12,a22,a32=list(v2*-1)
      M1=numpy.matrix([[a11,a12],[a21,a22]])
      M2=numpy.matrix([[a21,a22],[a31,a32]])
      M3=numpy.matrix([[a31,a32],[a11,a12]])
      pl1=list(p1)
      pl2=list(p2)
      if numpy.linalg.det(M1)!=0:
        k=numpy.linalg.inv(M1)*numpy.matrix([[pl2[0]-pl1[0]],[pl2[1]-pl1[1]]])
      elif numpy.linalg.det(M2)!=0:
        k=numpy.linalg.inv(M2)*numpy.matrix([[pl2[1]-pl1[1]],[pl2[2]-pl1[2]]])
      else:
        k=numpy.linalg.inv(M3)*numpy.matrix([[pl2[2]-pl1[2]],[pl2[0]-pl1[0]]])
      P=p1+v1*float(k[0]) # ..=p2+v2*float(k[1])
      #FreeCAD.Console.PrintWarning("k1 = "+str(float(k[0]))+"\nk2 = "+str(float(k[1]))+"\n")
      return rounded(P)
    else:     #se i vettori non sono complanari <=>  intersezione nulla
      FreeCAD.Console.PrintError('Lines are not in the same plane.\n')
      return None
  else:  #se i vettori sono paralleli <=>  intersezione nulla
    FreeCAD.Console.PrintError('Lines are parallel.\n')
    return None

def intersectionPlane(base=None,v=None,face=None):
  '''
  intersectionPlane(base,v,face)
  Returns the point (vector) at the intersection of a line and a plane.
    base (vector): the base point to be projected
    v (vector): the direction of the line that intersect the plane
    face (Face): the face that defines the plane to be intersect
  '''   
  # only for quick testing:
  if base==v==face==None:
    face = faces()[0]
    beam=beams()[0]
    base=beam.Placement.Base
    v=beamAx(beam)
  if isOrtho(v,face):
    FreeCAD.Console.PrintError('Direction of projection and Face are parallel.\n')
    return None
  else:
    # equation of plane: ax+by+cz+d=0
    a,b,c=list(face.normalAt(0,0))
    d=-face.CenterOfMass.dot(face.normalAt(0,0))
    #FreeCAD.Console.PrintMessage('a=%.2f b=%.2f c=%.2f d=%.2f\n' %(a,b,c,d))
    ## definition of line
    #FreeCAD.Console.PrintMessage('base=(%.2f,%.2f,%.2f)\n' %(base.x,base.y,base.z))
    #FreeCAD.Console.PrintMessage('v=(%.2f,%.2f,%.2f)\n' %(v.x,v.y,v.z))
    ##intersection
    k=-1*(a*base.x+b*base.y+c*base.z+d)/(a*v.x+b*v.y+c*v.z)
    #FreeCAD.Console.PrintMessage('k=%f\n' %float(k))
    P=base+v*k
    return rounded(P)

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
  return round(v[0].cross(v[1]).Length,2)==0 #v[0].cross(v[1]).Length==0

def beamAx(beam, vShapeRef=None):
  '''
  beamAx(beam, vShapeRef=None)
  Returns the new orientation of a vector referred to Shape's coordinates
  rotated according the Placement of the object.
    beam: the object (any)
    vShapeRef: the Shape's reference vector (defaults Z axis of Shape)
  '''
  if vShapeRef==None:
    vShapeRef=FreeCAD.Vector(0.0,0.0,1.0)
  return beam.Placement.Rotation.multVec(vShapeRef).normalize()

def getDistance(shapes=None):
  'measure the lenght of an edge or the distance of two shapes'
  if not shapes:
    shapes=[y for x in FreeCADGui.Selection.getSelectionEx() for y in x.SubObjects if hasattr(y,'ShapeType')]
  if len(shapes)==1 and shapes[0].ShapeType=='Edge':
      return shapes[0].Length
  elif len(shapes)>1:
    return shapes[0].distToShape(shapes[1])[0]
  else:
    return None

def bisect(w1=None,w2=None):
  '''
  bisect(w1=None,w2=None)
  Returns the bisect vector between vectors w1 and w2.
  If no argument is given the function takes the selected edges, if any.
  '''
  if w1==w2==None and len(edges())>=2:
    w1,w2=[(e.CenterOfMass-FreeCAD.Vector(0,0,0)).normalize() for e in edges()[:2]]
  if w1!=None and w2!=None:
    w1.normalize()
    w2.normalize()
    #b=w2-w1
    b=FreeCAD.Vector()
    for i in range(3):
      b[i]=(w1[i]+w2[i])/2
    return b.normalize()
    
def ortho(w1=None,w2=None):
  '''
  ortho(w1=None,w2=None)
  Returns the orthogonal vector to vectors w1 and w2.
  If no argument is given the function takes the selected edges, if any.
  '''
  if w1==w2==None and len(edges())>=2:
    w1,w2=[e.tangentAt(0) for e in edges()[:2]]
  if w1!=None and w2!=None:
    return w1.cross(w2).normalize()

def vec2edge(point,direct):
  '''
  vec2edge(point,direct)
  Returns an edge placed at point with the orientation and length of direct.
  '''
  from Part import makeLine
  return makeLine(point,point+direct) 
  
def edgeName(obj=None,edge=None):
  if not obj or not edge:
    try:
      sx=FreeCADGui.Selection.getSelectionEx()[0]
      edge=sx.SubObjects[0]
      obj=sx.Object
    except:
      return None
  if hasattr(obj,'Shape'):
    i=1
    for e in obj.Shape.Edges:
      if e.isSame(edge):
        return obj,"Edge"+str(i)
      i+=1
    return None
  
############ COMMANDS #############

def spinTheBeam(beam, angle):  # OBSOLETE: replaced by rotateTheTubeAx
  '''arg1=beam, arg2=angle: rotate the section of the beam
  OBSOLETE: replaced by rotateTheTubeAx'''
  if beam.TypeId=="Part::FeaturePython" and "Base" in beam.PropertiesList:
    beam.Base.Placement=FreeCAD.Placement(FreeCAD.Vector(0.0,0.0,0.0),FreeCAD.Rotation(FreeCAD.Vector(0.0,0.0,1.0),angle))

def placeTheBeam(beam, edge):
  '''arg1= beam, arg2= edge: lay down the selected beam on the selected edge'''
  vect=edge.tangentAt(0)
  beam.Placement.Rotation=FreeCAD.Rotation(0,0,0,1)
  rot=FreeCAD.Rotation(beam.Placement.Rotation.Axis,vect)
  beam.Placement.Rotation=rot.multiply(beam.Placement.Rotation)
  beam.Placement.Base=edge.valueAt(0)
  beam.Height=edge.Length

def rotTheBeam(beam,faceBase,faceAlign):
  '''arg1=beam, arg2=faceBase, arg3=faceToMakeParallel: rotate the beams to make the flanges parallel to that of first selection.'''
  from Part import Face
  if type(faceBase)==Face:
    n1=faceBase.normalAt(0,0)
  elif type(faceBase)==FreeCAD.Base.Vector:
    n1=faceBase
  n2=faceAlign.normalAt(0,0)
  rot=FreeCAD.Rotation(n2,n1)
  beam.Placement.Rotation=rot.multiply(beam.Placement.Rotation)

def levelTheBeam(beam,faces):
  '''arg1=beams2move, arg2=[faces]: Shifts the second selection to make its flange coplanar to that of the first selection'''
  v=faces[0].CenterOfMass-faces[1].CenterOfMass
  n=faces[0].normalAt(0,0)
  dist=n.dot(v)
  beam.Placement.move(n.multiply(dist))

def joinTheBeamsEdges(beam,e1,e2):
    '''arg1=beam, arg2=edge target, arg3=edge start: aligns the edges'''
    beam.Placement.move(e1.distToShape(e2)[1][0][0]-e1.distToShape(e2)[1][0][1])

def pivotTheBeam(ang=90, edge=None, beam=None): #OBSOLETE: replaced with rotateTheBeamAround
  '''
  pivotTheBeam(ang=90)
  Rotates the selected object around the selected pivot (one of its edges)
  by ang degrees.
  '''
  #if len(edges())!=1:
  #  FreeCAD.Console.PrintError('Wrong selection\n')
  #  return None
  if not (edge and beam):
    try:
      edge=edges()[0]
      beam=FreeCADGui.Selection.getSelection()[0]
    except:
      return
  rot=FreeCAD.Rotation(edge.tangentAt(0),ang)
  beam.Placement.Rotation=rot.multiply(beam.Placement.Rotation)
  edgePost=edges()[0] #save position for revert
  dist=edge.CenterOfMass-edgePost.CenterOfMass
  beam.Placement.move(dist)
  
def rotateTheBeamAround(b,e,ang=90): # for rotation around an axis
  '''
  rotateTheBeamAround(b,e,ang=90): rotates any Body around an edge
    b: any object with a Placement property
    e: the edge being axis of rotation
    ang: degrees of rotation
  '''
  rot=FreeCAD.Rotation(e.tangentAt(0),ang)
  from Part import Vertex
  P0=Vertex(b.Placement.Base)
  O=P0.distToShape(e)[1][0][1]
  P1=O+rot.multVec(P0.Point-O)
  b.Placement.Rotation=rot.multiply(b.Placement.Rotation)
  b.Placement.Base=P1 #rot.multVec(b.Placement.Base)
  
def stretchTheBeam(beam,L):
  if beam!=None and beam.TypeId=="Part::FeaturePython" and hasattr(beam,"Height"):
    beam.Height=L
      
def extendTheBeam(beam,target):
  '''arg1=beam, arg2=target: extend the beam to a plane, normal to its axis, defined by target.
  If target is a Vertex or a Vector, the plane is the one that includes the point defined by target.
  If target is a Face, the plane is the one that includes the intersection between the axis of beam and the plane of the face.
  Else, the plane is the one normal to the axis of beam that includes the CenterOfMass of target'''
  distBase=distTop=0
  vBase=beam.Placement.Base
  vBeam=beamAx(beam)
  h=beam.Height
  vTop=vBase+vBeam.multiply(h)
  if type(target)==FreeCAD.Vector:
    distBase=vBase.distanceToPlane(target,vBeam)
    distTop=vTop.distanceToPlane(target,vBeam)
  elif target.ShapeType=="Vertex":
    distBase=vBase.distanceToPlane(target.Point,vBeam)
    distTop=vTop.distanceToPlane(target.Point,vBeam)
  elif target.ShapeType=="Face":
    if not isOrtho(target,vBeam):
      from Part import Point
      Pint=Point(intersectionPlane(beam.Placement.Base,beamAx(beam),target)).toShape()
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
      vMove=vBeam.normalize().multiply(-distBase) 
      beam.Placement.move(vMove)
  else:
    if abs(distBase)>abs(distTop):
      beam.Height-=FreeCAD.Units.Quantity(str(abs(distTop))+"mm")
    else:
      beam.Height-=FreeCAD.Units.Quantity(str(abs(distBase))+"mm")
      vMove=vBeam.normalize().multiply(-distBase)
      beam.Placement.move(vMove)
  #FreeCAD.activeDocument().recompute()
  
def rotjoinTheBeam(beam=None,e1=None,e2=None):
  if not (beam and e1 and e2):
    beam=beams()[1]
    e1,e2=edges()
  rot=FreeCAD.Rotation(e2.tangentAt(0),e1.tangentAt(0))
  dist=dgu.findDistance(beam.Placement.Base,e1)
  delta=beam.Placement.Base-e2.CenterOfMass
  beam.Placement.Rotation=rot.multiply(beam.Placement.Rotation)
  beam.Placement.move(rounded(dist+rot.multVec(delta)))

def getSolids(allDoc=True):
  if allDoc:
    objects=FreeCAD.ActiveDocument.Objects
  else:
    objects=FreeCADGui.Selection.getSelection()
  FreeCADGui.Selection.clearSelection()
  for o in objects:
    if hasattr(o,'Shape') and o.Shape.Solids:
      FreeCADGui.Selection.addSelection(o)
      
def getFaces(allDoc=True):
  if allDoc:
    objects=FreeCAD.ActiveDocument.Objects
  else:
    objects=FreeCADGui.Selection.getSelection()
  FreeCADGui.Selection.clearSelection()
  for o in objects:
    if hasattr(o,'Shape'):
      for i in range(len(o.Shape.Faces)):
        print( str(o)+': '+str(i+1))
        FreeCADGui.Selection.addSelection(o,'Face'+str(i+1))

