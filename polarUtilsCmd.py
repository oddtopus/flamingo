#(c) 2016 R. T. LGPL: part of Flamingo tools w.b. for FreeCAD

__title__="polarUtils functions"
__author__="oddtopus"
__url__="github.com/oddtopus/flamingo"
__license__="LGPL 3"

import math

def cerchio(R=1, nseg=8):
  'arg1=R, arg2=nseg: returns a list of 3-uple for nseg+1 coordintates on the semi-circle centered in (0,0,0)'
  teta=[i*2*math.pi/nseg for i in range(nseg+1)]
  return [polar2xy(R,t) for t in teta]

def polar2xy(ro,teta):
  'arg1=ro1(length), arg2=teta(deg): returns [x,y,0]'
  return ro*math.cos(teta),ro*math.sin(teta),0

def getFromFile():
  '''Input polar coord. from .csv: returns a list of (x,y,0).
  The file must be ";" separated: column A = radius, column B = angle'''
  from PySide import QtGui
  fileIn=open(QtGui.QFileDialog().getOpenFileName()[0],'r')
  lines=fileIn.readlines()
  fileIn.close()
  xyCoord=[]
  for line in lines:
    polarCoord=line.split(';')
    xyCoord.append(polar2xy(float(polarCoord[0]),float(polarCoord[1])*math.pi/180))
  return xyCoord
  
def disegna(sk, pos):
  'arg1=sketch, arg2=pos (list of 3-uple): draws the segments of "pos" in "sketch" and close the polygon'
  import FreeCAD, Part, Sketcher
  lines=[]
  while len(pos)>1:
    lines.append(sk.addGeometry(Part.Line(FreeCAD.Vector(pos[0]),FreeCAD.Vector(pos[1]))))
    pos.pop(0)
  for i in range(len(lines)-1):
    sk.addConstraint(Sketcher.Constraint('Coincident',lines[i],2,lines[i+1],1))
  sk.addConstraint(Sketcher.Constraint('Coincident',lines[len(lines)-1],2,lines[0],1))
  FreeCAD.activeDocument().recompute()
  return lines

def setWP():
  'function to change working plane'
  import FreeCAD, FreeCADGui, frameCmd
  normal=point=None
  curves=[]
  straight=[]
  for edge in frameCmd.edges():
    if edge.curvatureAt(0)!=0:
      curves.append(edge)
    else:
      straight.append(edge)
  # define normal: 1st from face->2nd from curve->3rd from straight edges
  if frameCmd.faces():
    normal=frameCmd.faces()[0].normalAt(0,0)
  elif curves:
    normal=curves[0].tangentAt(0).cross(curves[0].normalAt(0))
  elif len(straight)>1:
    if straight and not frameCmd.isParallel(straight[0].tangentAt(0),straight[1].tangentAt(0)):
      normal=straight[0].tangentAt(0).cross(straight[1].tangentAt(0))
  # define point: 1st from vertex->2nd from centerOfCurvature->3rd from intersection->4th from center of edge
  points=[v.Point for sx in FreeCADGui.Selection.getSelectionEx() for v in sx.SubObjects if v.ShapeType=='Vertex']
  if not points:
    points=[edge.centerOfCurvatureAt(0) for edge in curves]
  if not points and len(straight)>1:
    inters=frameCmd.intersectionCLines(straight[0],straight[1])
    if inters:
      points.append(inters)
  if not points and len(straight):
    points.append(straight[0].CenterOfMass)
  if points:
    point=points[0]
  # move the draft WP
  if point and normal:
    FreeCAD.DraftWorkingPlane.alignToPointAndAxis(point,normal)
  else:
    FreeCAD.DraftWorkingPlane.alignToPointAndAxis(FreeCAD.Vector(),FreeCAD.Vector(0,0,1))
  FreeCADGui.Snapper.setGrid()
def rotWP(ax=None,ang=45):
  import FreeCAD, FreeCADGui
  if not ax:
    ax=FreeCAD.Vector(0,0,1)
  if hasattr(FreeCAD,'DraftWorkingPlane') and hasattr(FreeCADGui,'Snapper'):
    pl=FreeCAD.DraftWorkingPlane.getPlacement()
    pRot=FreeCAD.Placement(FreeCAD.Vector(),FreeCAD.Rotation(ax,ang))
    newpl=pl.multiply(pRot)
    FreeCAD.DraftWorkingPlane.setFromPlacement(newpl)
    FreeCADGui.Snapper.setGrid()
  return newpl
  
class arrow(object):
  '''
  This class draws a green arrow to be used as an auxiliary compass
  to show position and orientation of objects.
    arrow(pl=None, scale=[100,100,20],offset=100)
  '''
  def __init__(self,pl=None, scale=[100,100,20],offset=100):
    import FreeCAD, FreeCADGui
    from pivy import coin
    self.node=coin.SoSeparator()
    self.color=coin.SoBaseColor()
    self.color.rgb=0,0.8,0
    self.node.addChild(self.color)
    self.transform=coin.SoTransform()
    self.node.addChild(self.transform)
    self.cone=coin.SoCone()
    self.node.addChild(self.cone)
    FreeCADGui.ActiveDocument.ActiveView.getSceneGraph().addChild(self.node)
    self.transform.scaleFactor.setValue(scale)
    self.offset=offset
    if not pl:
      pl=FreeCAD.Placement()
    self.moveto(pl)
  def moveto(self,pl):
    import FreeCAD
    rotx90=FreeCAD.Base.Rotation(FreeCAD.Vector(0,1,0),FreeCAD.Vector(0,0,1))
    self.Placement=pl
    self.transform.rotation.setValue(tuple(self.Placement.Rotation.multiply(rotx90).Q))
    offsetV=self.Placement.Rotation.multVec(FreeCAD.Vector(0,0,self.offset))
    self.transform.translation.setValue(tuple(self.Placement.Base+offsetV))
    
    
