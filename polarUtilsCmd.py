#(c) 2016 R. T. LGPL: part of Flamingo tools w.b. for FreeCAD

__title__="polarUtils functions"
__author__="oddtopus"
__url__="github.com/oddtopus/flamingo"
__license__="LGPL 3"

import math, FreeCAD, FreeCADGui, frameCmd
from os.path import join, dirname, abspath
from pivy import coin
from frameForms import prototypeDialog

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
  Z=FreeCAD.Vector(0,0,1)
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
  elif FreeCADGui.Selection.getSelection():
    normal=FreeCAD.DraftWorkingPlane.getRotation().multVec(Z)
  else:
    normal=Z
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
  else:
    point=FreeCAD.Vector()
  # move the draft WP
  FreeCAD.DraftWorkingPlane.alignToPointAndAxis(point,normal)
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
def offsetWP(delta):
  import FreeCAD,FreeCADGui
  if hasattr(FreeCAD,'DraftWorkingPlane') and hasattr(FreeCADGui,'Snapper'):
    rot=FreeCAD.DraftWorkingPlane.getPlacement().Rotation
    offset=rot.multVec(FreeCAD.Vector(0,0,delta))
    point=FreeCAD.DraftWorkingPlane.getPlacement().Base+offset
    FreeCAD.DraftWorkingPlane.alignToPointAndAxis(point,offset)
    FreeCADGui.Snapper.setGrid()
  
class arrow(object):
  '''
  This class draws a green arrow to be used as an auxiliary compass
  to show position and orientation of objects.
    arrow(pl=None, scale=[100,100,20],offset=100,name='ARROW')
  '''
  def __init__(self,pl=None, scale=[100,100,20],offset=100,name='ARROW'):
    # define main properties
    self.view=FreeCADGui.ActiveDocument.ActiveView
    self.sg=self.view.getSceneGraph()
    self.cb=self.view.addEventCallbackPivy(coin.SoMouseButtonEvent.getClassTypeId(), self.pickCB)
    # define OpenInventor properties
    self.node=coin.SoSeparator() #self.node=coin.SoSelection()
    self.name=name
    self.node.setName(self.name)
    self.color=coin.SoBaseColor(); self.color.rgb=0,0.8,0
    self.transform=coin.SoTransform(); self.transform.scaleFactor.setValue(scale)
    self.cone=coin.SoCone()
    # create children of node
    self.node.addChild(self.color)
    self.node.addChild(self.transform)
    self.node.addChild(self.cone)
    # draw the arrow and move it to its Placement with the specified offset
    self.sg.addChild(self.node)
    self.offset=offset
    if not pl:
      pl=FreeCAD.Placement()
    self.moveto(pl)
  def closeArrow(self):
    self.view.removeEventCallbackPivy(coin.SoMouseButtonEvent.getClassTypeId(), self.cb)
    self.sg.removeChild(self.node)
  def moveto(self,pl):
    import FreeCAD
    rotx90=FreeCAD.Base.Rotation(FreeCAD.Vector(0,1,0),FreeCAD.Vector(0,0,1))
    self.Placement=pl
    self.transform.rotation.setValue(tuple(self.Placement.Rotation.multiply(rotx90).Q))
    offsetV=self.Placement.Rotation.multVec(FreeCAD.Vector(0,0,self.offset))
    self.transform.translation.setValue(tuple(self.Placement.Base+offsetV))
  def pickCB(self, ecb):
    event=ecb.getEvent()
    arg=None
    if event.getState()==coin.SoMouseButtonEvent.DOWN:
      render_manager=self.view.getViewer().getSoRenderManager()
      doPick=coin.SoRayPickAction(render_manager.getViewportRegion())
      doPick.setPoint(coin.SbVec2s(*ecb.getEvent().getPosition()))
      doPick.apply(render_manager.getSceneGraph())
      points=doPick.getPickedPointList()
      if points.getLength():
        path=points[0].getPath()
        if str(tuple(path)[-2].getName())==self.name: self.pickAction(path,event,arg)
  def pickAction(self,path=None,event=None,arg=None): # sample
    if path:
      for n in path: 
        if str(n.getName())==self.name: 
          FreeCAD.Console.PrintMessage("You hit the %s\n"%self.name) #replace here the action to perform
    self.closeArrow()

class arrow_move(arrow):
  '''
  arrow_move(pl=None,direct=None,M=100)
    pl: the placement of the arrow
    direct: the displacement vector
    M: the scale of display
  This class derives from "arrow" and adds the ability to move the selected
  objects when the arrow is picked.  This is accomplished by redefining the
  method "pickAction".
  '''
  def __init__(self, pl=None, direct=None, M=100, objs=None):
    self.objs=objs
    self.edge=None
    # define direction
    self.scale=M
    if direct: self.direct=direct
    else: self.direct=FreeCAD.Vector(0,0,1)*M
    # define placement
    if not pl:pl=FreeCAD.Placement()
    # draw arrow
    super(arrow_move,self).__init__(pl=pl, scale=[M/2,M/2,M/10], offset=M/2)
  def pickAction(self,path=None,event=None,arg=None):
    FreeCAD.activeDocument().openTransaction('Quick move')
    if event.wasCtrlDown(): k=-1
    else: k=1
    sel=FreeCADGui.Selection.getSelection()
    if sel: self.objs=[o for o in sel if hasattr(o,'Shape')]
    if event.wasCtrlDown() and event.wasAltDown():
      if frameCmd.edges(): 
        self.edge=frameCmd.edges()[0]
        for o in self.objs: frameCmd.rotateTheBeamAround(o, self.edge, 90)
      elif self.edge:
        for o in self.objs: frameCmd.rotateTheBeamAround(o, self.edge, 90)
    else:
      for o in self.objs: o.Placement.move(self.direct*k)
      self.Placement.move(self.direct*k)
      pl,direct,M=[self.Placement,self.direct,self.scale]
      self.closeArrow()
      self.__init__(pl,direct,M,self.objs)
    FreeCAD.activeDocument().commitTransaction()

class handleDialog(prototypeDialog):
  def __init__(self):
    self.arrow=None
    super(handleDialog,self).__init__('disp.ui')
    self.form.edit1.setValidator(QDoubleValidator())
    #self.form.edit1.hide()#
    #self.form.lab1.hide()#
    self.form.btn1.clicked.connect(self.selectAction)
    from sys import platform
    if platform.startswith('win'):
      self.form.lab2.hide()
  def selectAction(self):
    self.objs=FreeCADGui.Selection.getSelection()
    L=direct=None
    pl=FreeCAD.Placement()
    # define general size of arrow
    if self.arrow: self.arrow.closeArrow()
    M=100.0
    moveSet=[o for o in FreeCADGui.Selection.getSelection() if hasattr(o,'Shape')]
    if moveSet:
      bb=moveSet[0].Shape.BoundBox
      for o in moveSet: bb=bb.united(o.Shape.BoundBox)
      edgesLens=[e.Length for o in moveSet for e in o.Shape.Edges]
      M=(bb.XLength+bb.YLength+bb.ZLength)/6.0
      # define placement of arrow
      orig=bb.Center
      orig[2]=bb.ZMax+bb.ZLength*0.1
      pl.move(orig)
    # define direction and displacement
    if self.form.edit1.text(): L=float(self.form.edit1.text())
    if frameCmd.faces():
      f=frameCmd.faces()[0]
      if L: direct=f.normalAt(0,0).normalize()*L
      else: direct=f.normalAt(0,0).normalize()*math.sqrt(f.Area)
    elif frameCmd.edges():
      e=frameCmd.edges()[0]
      if L: direct=e.tangentAt(0)*L
      else: direct=e.tangentAt(0).multiply(e.Length)
    # create the arrow_move object
    if direct: 
      pl.Rotation=FreeCAD.Rotation(FreeCAD.Vector(0,0,1),direct).multiply(pl.Rotation)
      self.arrow=arrow_move(pl=pl,direct=direct,M=M,objs=self.objs)
  def accept(self):
    self.reject()
  def reject(self):
    if self.arrow: self.arrow.closeArrow()
    try: self.view.removeEventCallback('SoEvent',self.call)
    except: pass
    FreeCADGui.Control.closeDialog()

class label3D(object):
  '''
  This class writes a 2D label in the 3D viewport.
  To be used as an auxiliary tool to show flags during execution
  of commands.
  Note: default text size is 7 units.
    label3D(pl=None, scale=[1,1,1], color=(1.0,0.6,0.0), text='TEXT')
  '''
  def __init__(self,pl=None, sizeFont=30, color=(1.0,0.6,0.0), text='TEXT'):
    import FreeCAD, FreeCADGui
    self.node=coin.SoSeparator()
    self.color=coin.SoBaseColor()
    self.color.rgb=color
    self.node.addChild(self.color)
    self.transform=coin.SoTransform()
    self.node.addChild(self.transform)
    self.font=coin.SoFont()
    self.node.addChild(self.font)
    self.font.size=sizeFont
    self.text=coin.SoText2()
    self.text.string=text
    self.node.addChild(self.text)
    self.sg=FreeCADGui.ActiveDocument.ActiveView.getSceneGraph()
    self.sg.addChild(self.node)
    if not pl:
      pl=FreeCAD.Placement()
    self.moveto(pl)
  def removeLabel(self):
    self.sg.removeChild(self.node)
  def moveto(self,pl):
    import FreeCAD
    self.Placement=pl
    self.transform.translation.setValue(tuple(self.Placement.Base))
    self.transform.rotation.setValue(tuple(self.Placement.Rotation.Q))

import DraftTools,Draft,qForms
from PySide.QtGui import *
class hackedLine(DraftTools.Line):
  '''
  One hack of the class DraftTools.Line
  to make 3D drafting easier.
  '''    
  def __init__(self, wireFlag=True):
    DraftTools.Line.__init__(self,wireFlag)
    self.Activated()
    dialogPath=join(dirname(abspath(__file__)),"dialogs","hackedline.ui")
    self.hackedUI=FreeCADGui.PySideUic.loadUi(dialogPath)
    self.hackedUI.btnRot.clicked.connect(self.rotateWP)
    self.hackedUI.btnOff.clicked.connect(self.offsetWP)
    self.hackedUI.btnXY.clicked.connect(lambda: self.alignWP(FreeCAD.Vector(0,0,1)))
    self.hackedUI.btnXZ.clicked.connect(lambda: self.alignWP(FreeCAD.Vector(0,1,0)))
    self.hackedUI.btnYZ.clicked.connect(lambda: self.alignWP(FreeCAD.Vector(1,0,0)))
    self.ui.layout.addWidget(self.hackedUI)
  def alignWP(self, norm):
      FreeCAD.DraftWorkingPlane.alignToPointAndAxis(self.node[-1],norm)
      FreeCADGui.Snapper.setGrid()
  def offsetWP(self):
    if hasattr(FreeCAD,'DraftWorkingPlane') and hasattr(FreeCADGui,'Snapper'):
      s=FreeCAD.ParamGet("User parameter:BaseApp/Preferences/Mod/Draft").GetInt("gridSize")
      sc=[float(x*s) for x in [1,1,.2]]
      varrow =arrow(FreeCAD.DraftWorkingPlane.getPlacement(),scale=sc,offset=s)
      offset=QInputDialog.getInteger(None,'Offset Work Plane','Offset: ')
      if offset[1]:
        offsetWP(offset[0])
      FreeCADGui.ActiveDocument.ActiveView.getSceneGraph().removeChild(varrow.node)
  def rotateWP(self):
    self.form=qForms.rotWPForm()
  def action(self,arg): #re-defintition of the method of parent
      "scene event handler"
      if arg["Type"] == "SoKeyboardEvent" and arg["State"]=='DOWN':
          # key detection
          if arg["Key"] == "ESCAPE":
              self.finish()
          elif arg["ShiftDown"] and arg["CtrlDown"]:
            if arg["Key"] in ('M','m'):
              if self.hackedUI.cb1.isChecked():
                self.hackedUI.cb1.setChecked(False)
              else:
                self.hackedUI.cb1.setChecked(True)
            elif arg["Key"] in ('O','o'):
              self.offsetWP()
            elif arg["Key"] in ('R','r'):
              self.rotateWP()
      elif arg["Type"] == "SoLocation2Event":
          # mouse movement detection
          self.point,ctrlPoint,info = DraftTools.getPoint(self,arg)
      elif arg["Type"] == "SoMouseButtonEvent":
          # mouse button detection
          if (arg["State"] == "DOWN") and (arg["Button"] == "BUTTON1"):
              if (arg["Position"] == self.pos):
                  self.finish(False,cont=True)
              else:
                  if (not self.node) and (not self.support):
                      DraftTools.getSupport(arg)
                      self.point,ctrlPoint,info = DraftTools.getPoint(self,arg)
                  if self.point:
                      self.ui.redraw()
                      self.pos = arg["Position"]
                      self.node.append(self.point)
                      self.drawSegment(self.point)
                      if self.hackedUI.cb1.isChecked():
                        rot=FreeCAD.DraftWorkingPlane.getPlacement().Rotation
                        normal=rot.multVec(FreeCAD.Vector(0,0,1))
                        FreeCAD.DraftWorkingPlane.alignToPointAndAxis(self.point,normal)
                        FreeCADGui.Snapper.setGrid()
                      if (not self.isWire and len(self.node) == 2):
                          self.finish(False,cont=True)
                      if (len(self.node) > 2):
                          if ((self.point-self.node[0]).Length < Draft.tolerance()):
                              self.undolast()
                              self.finish(True,cont=True)

