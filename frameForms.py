#(c) 2016 R. T. LGPL: part of Flamingo tools w.b. for FreeCAD

__title__="frameTools forms"
__author__="oddtopus"
__url__="github.com/oddtopus/flamingo"
__license__="LGPL 3"

import FreeCAD,FreeCADGui
import frameCmd
from PySide.QtCore import *
from PySide.QtGui import *
from os.path import join, dirname, abspath

class prototypeForm(QWidget):
  'prototype dialog for frame tools workbench'
  def __init__(self,winTitle='Title',btn1Text='Button1',btn2Text='Button2',initVal='someVal',units='someUnit', icon='flamingo.svg'):
    super(prototypeForm,self).__init__()
    self.setWindowFlags(Qt.WindowStaysOnTopHint)
    self.setWindowTitle(winTitle)
    iconPath=join(dirname(abspath(__file__)),"icons",icon)
    from PySide.QtGui import QIcon
    Icon=QIcon()
    Icon.addFile(iconPath)
    self.setWindowIcon(Icon) 
    self.move(QPoint(100,250))
    self.mainVL=QVBoxLayout()
    self.setLayout(self.mainVL)
    self.inputs=QWidget()
    self.inputs.setLayout(QFormLayout())
    self.edit1=QLineEdit(initVal)
    self.edit1.setMinimumWidth(40)
    self.edit1.setAlignment(Qt.AlignHCenter)
    self.edit1.setMaximumWidth(60)
    self.inputs.layout().addRow(units,self.edit1)
    self.mainVL.addWidget(self.inputs)
    self.radio1=QRadioButton()
    self.radio1.setChecked(True)
    self.radio2=QRadioButton()
    self.radios=QWidget()
    self.radios.setLayout(QFormLayout())
    self.radios.layout().setAlignment(Qt.AlignHCenter)
    self.radios.layout().addRow('move',self.radio1)
    self.radios.layout().addRow('copy',self.radio2)
    self.mainVL.addWidget(self.radios)
    self.btn1=QPushButton(btn1Text)
    self.btn1.setDefault(True)
    self.btn1.setFocus()
    self.btn2=QPushButton(btn2Text)
    self.buttons=QWidget()
    self.buttons.setLayout(QHBoxLayout())
    self.buttons.layout().addWidget(self.btn1)
    self.buttons.layout().addWidget(self.btn2)
    self.mainVL.addWidget(self.buttons)

class pivotForm:
  'dialog for pivotTheBeam()'
  def __init__(self):
    dialogPath=join(dirname(abspath(__file__)),"dialogs","pivot.ui")
    self.form=FreeCADGui.PySideUic.loadUi(dialogPath)
    self.form.edit1.setValidator(QDoubleValidator())
    self.form.btn1.clicked.connect(self.reverse)
  def accept(self):      #rotate
    FreeCAD.activeDocument().openTransaction('Rotate')
    if self.form.radio2.isChecked():
      FreeCAD.activeDocument().copyObject(FreeCADGui.Selection.getSelection()[0],True)
      frameCmd.pivotTheBeam(float(self.form.edit1.text()),ask4revert=False)
    else:
      frameCmd.pivotTheBeam(float(self.form.edit1.text()),ask4revert=False)
    FreeCAD.ActiveDocument.recompute()
    FreeCAD.activeDocument().commitTransaction()
  def reverse(self):
    FreeCAD.activeDocument().openTransaction('Reverse rotate')
    frameCmd.pivotTheBeam(-2*float(self.form.edit1.text()),ask4revert=False)
    self.form.edit1.setText(str(-1*float(self.form.edit1.text())))
    FreeCAD.activeDocument().commitTransaction()

class fillForm:
  'dialog for fillFrame()'
  def __init__(self):
    dialogPath=join(dirname(abspath(__file__)),"dialogs","fillframe.ui")
    self.form=FreeCADGui.PySideUic.loadUi(dialogPath)
    self.beam=None
    self.form.btn1.clicked.connect(self.select)
  def accept(self):
    if self.beam!=None and len(frameCmd.edges())>0:
      FreeCAD.activeDocument().openTransaction('Fill frame')
      if self.form.radio1.isChecked():
        frameCmd.placeTheBeam(self.beam,frameCmd.edges()[0])
      else:
        for edge in frameCmd.edges():
          struct=FreeCAD.activeDocument().copyObject(self.beam,True)
          frameCmd.placeTheBeam(struct,edge)
        FreeCAD.activeDocument().recompute()
      FreeCAD.ActiveDocument.recompute()
      FreeCAD.activeDocument().commitTransaction()
  def select(self):
    if len(frameCmd.beams())>0:
      self.beam=frameCmd.beams()[0]
      self.form.label.setText(self.beam.Label+':'+self.beam.Profile)
      FreeCADGui.Selection.removeSelection(self.beam)

class extendForm:
  'dialog for frameCmd.extendTheBeam()'
  def __init__(self):
    dialogPath=join(dirname(abspath(__file__)),"dialogs","extend.ui")
    self.form=FreeCADGui.PySideUic.loadUi(dialogPath)
    selex = FreeCADGui.Selection.getSelectionEx()
    self.form.btn1.clicked.connect(self.getTarget)
    if len(selex):
      self.target=selex[0].SubObjects[0]
      self.form.label.setText(selex[0].Object.Label+':'+self.target.ShapeType)
      FreeCADGui.Selection.removeSelection(selex[0].Object)
    else:
      self.target=None
  def getTarget(self):
    selex = FreeCADGui.Selection.getSelectionEx()
    if len(selex[0].SubObjects)>0 and hasattr(selex[0].SubObjects[0],'ShapeType'):
      self.target=selex[0].SubObjects[0]
      self.form.label.setText(selex[0].Object.Label+':'+self.target.ShapeType)
      FreeCADGui.Selection.clearSelection()
  def accept(self):            # extend
    if self.target!=None and len(frameCmd.beams())>0:
      FreeCAD.activeDocument().openTransaction('Extend beam')
      for beam in frameCmd.beams():
        frameCmd.extendTheBeam(beam,self.target)
      FreeCAD.activeDocument().recompute()
      FreeCAD.activeDocument().commitTransaction()
      
class stretchForm:
  '''dialog for stretchTheBeam()
    [Get Length] measures the min. distance of the selected objects or
      the length of the selected edge or
      the Height of the selected beam
    [ Stretch ] changes the Height of the selected beams
  '''
  def __init__(self):
    self.L=None
    dialogPath=join(dirname(abspath(__file__)),"dialogs","beamstretch.ui")
    self.form=FreeCADGui.PySideUic.loadUi(dialogPath)
    self.form.edit1.setValidator(QDoubleValidator())
    self.form.edit1.editingFinished.connect(self.edit12L)
    self.form.btn1.clicked.connect(self.getL)
    self.form.slider.setMinimum(-100)
    self.form.slider.setMaximum(100)
    self.form.slider.setValue(0)
    self.form.slider.valueChanged.connect(self.changeL)
    self.labTail=None
  def edit12L(self):
    if self.form.edit1.text():
      self.L=float(self.form.edit1.text())
      self.form.slider.setValue(0)
  def changeL(self):
    if self.L:
      ext=self.L*(1+self.form.slider.value()/100.0)
      self.form.edit1.setText(str(ext))
  def getL(self):
    if self.labTail:
      self.labTail.removeLabel()
      self.labTail=None
    self.L=frameCmd.getDistance()
    if self.L:
      self.form.edit1.setText(str(self.L))
    elif frameCmd.beams():
      beam=frameCmd.beams()[0]
      self.L=float(beam.Height)
      self.form.edit1.setText(str(self.L))
    else:
      self.form.edit1.setText('') 
    self.form.slider.setValue(0)
    self.writeTail()
  def writeTail(self):
    if frameCmd.beams():
      beam=frameCmd.beams()[0]
      from polarUtilsCmd import label3D
      #sc=100
      #if hasattr(beam,'Width'): sc=float(beam.Width)
      #elif hasattr(beam,'OD'): sc=float(beam.OD)
      self.labTail=label3D(pl=beam.Placement, text='____TAIL') #, sizeFont=sc)
  def accept(self):        # stretch
    if self.labTail:
      self.labTail.removeLabel()
      self.labTail=None
    self.L=frameCmd.getDistance()
    if self.form.edit1.text():
      length=float(self.form.edit1.text())
      FreeCAD.activeDocument().openTransaction('Stretch beam')
      for beam in frameCmd.beams():
        delta=float(beam.Height)-length
        frameCmd.stretchTheBeam(beam,length)
        if self.form.tail.isChecked():
          beam.Placement.move(frameCmd.beamAx(beam).multiply(delta))
      FreeCAD.activeDocument().recompute()
      FreeCAD.activeDocument().commitTransaction()
  def reject(self):
    if self.labTail:
      self.labTail.removeLabel()
    FreeCADGui.Control.closeDialog()

class translateForm:   
  'dialog for moving blocks'
  def __init__(self):
    dialogPath=join(dirname(abspath(__file__)),"dialogs","beamshift.ui")
    self.form=FreeCADGui.PySideUic.loadUi(dialogPath)
    for e in [self.form.edit1,self.form.edit2,self.form.edit3,self.form.edit4,self.form.edit5]:
      e.setValidator(QDoubleValidator())
    self.form.btn1.clicked.connect(self.getDisplacement)
    self.arrow=None
  def getDistance(self):
    self.deleteArrow()
    roundDigits=3
    shapes=[y for x in FreeCADGui.Selection.getSelectionEx() for y in x.SubObjects if hasattr(y,'ShapeType')][:2]
    if len(shapes)>1:    # if at least 2 shapes selected....
      base,target=shapes[:2]
      disp=None
      if base.ShapeType==target.ShapeType=='Vertex':
        disp=target.Point-base.Point
      elif base.ShapeType==target.ShapeType=='Edge':
        if base.curvatureAt(0):
          P1=base.centerOfCurvatureAt(0)
        else:
          P1=base.CenterOfMass
        if target.curvatureAt(0):
          P2=target.centerOfCurvatureAt(0)
        else:
          P2=target.CenterOfMass
        disp=P2-P1
      elif set([base.ShapeType,target.ShapeType])=={'Vertex','Edge'}:
        P=list()
        i=0
        for o in [base,target]:
          if o.ShapeType=='Vertex':
            P.append(o.Point)
          elif o.curvatureAt(0):
            P.append(o.centerOfCurvatureAt(0))
          else:
            return
          i+=1
        disp=P[1]-P[0]
      elif base.ShapeType=='Vertex' and target.ShapeType=='Face':
        disp=frameCmd.intersectionPlane(base.Point,target.normalAt(0,0),target)-base.Point
      elif base.ShapeType=='Face' and target.ShapeType=='Vertex':
        disp=target.Point-frameCmd.intersectionPlane(target.Point,base.normalAt(0,0),base)
        disp=P[1]-P[0]
      if disp!=None:
        self.form.edit4.setText(str(disp.Length))
        self.form.edit5.setText('1')
        disp.normalize()
        dx,dy,dz=list(disp)
        self.form.edit1.setText(str(round(dx,roundDigits)))
        self.form.edit2.setText(str(round(dy,roundDigits)))
        self.form.edit3.setText(str(round(dz,roundDigits)))
        FreeCADGui.Selection.clearSelection()
  def getLength(self):
    roundDigits=3
    if len(frameCmd.edges())>0:
      edge=frameCmd.edges()[0]
      self.form.edit4.setText(str(edge.Length))
      self.form.edit5.setText('1')
      dx,dy,dz=list(edge.tangentAt(0))
      self.form.edit1.setText(str(round(dx,roundDigits)))
      self.form.edit2.setText(str(round(dy,roundDigits)))
      self.form.edit3.setText(str(round(dz,roundDigits)))
      FreeCADGui.Selection.clearSelection()
      self.deleteArrow()
      from polarUtilsCmd import arrow
      where=FreeCAD.Placement()
      where.Base=edge.valueAt(0)
      where.Rotation=FreeCAD.Rotation(FreeCAD.Vector(0,0,1),edge.tangentAt(0))
      size=[edge.Length/20.0,edge.Length/10.0,edge.Length/20.0]
      self.arrow=arrow(pl=where,scale=size,offset=edge.Length/2.0)
  def getDisplacement(self):
    shapes=[y for x in FreeCADGui.Selection.getSelectionEx() for y in x.SubObjects if hasattr(y,'ShapeType')][:2]
    if len(shapes)>1:
      self.getDistance()
    elif len(frameCmd.edges())>0:
      self.getLength()
  def accept(self):           # translate
    self.deleteArrow()
    scale=float(self.form.edit4.text())/float(self.form.edit5.text())
    disp=FreeCAD.Vector(float(self.form.edit1.text()),float(self.form.edit2.text()),float(self.form.edit3.text())).scale(scale,scale,scale)
    FreeCAD.activeDocument().openTransaction('Translate')    
    if self.form.radio2.isChecked():
      for o in set(FreeCADGui.Selection.getSelection()):
        FreeCAD.activeDocument().copyObject(o,True)
    for o in set(FreeCADGui.Selection.getSelection()):
      o.Placement.move(disp)
    FreeCAD.activeDocument().recompute()
    FreeCAD.activeDocument().commitTransaction()    
  def deleteArrow(self):
    if self.arrow:
      FreeCADGui.ActiveDocument.ActiveView.getSceneGraph().removeChild(self.arrow.node)
      self.arrow=None
  def closeEvent(self,event):
    self.deleteArrow()

class alignForm:   
  'dialog to flush faces'
  def __init__(self):
    dialogPath=join(dirname(abspath(__file__)),"dialogs","align.ui")
    self.form=FreeCADGui.PySideUic.loadUi(dialogPath)
    self.faceRef=None
    self.getRef()
    self.form.btn1.clicked.connect(self.getRef)
    self.form.btnXY.clicked.connect(lambda: self.refPlane(FreeCAD.Vector(0,0,1)))
    self.form.btnXZ.clicked.connect(lambda: self.refPlane(FreeCAD.Vector(0,1,0)))
    self.form.btnYZ.clicked.connect(lambda: self.refPlane(FreeCAD.Vector(1,0,0)))
    self.form.X.setValidator(QDoubleValidator())
    self.form.btnNorm.clicked.connect(lambda: self.refPlane(FreeCAD.Vector(float(self.form.X.text()),float(self.form.Y.text()),float(self.form.Z.text()))))
    #self.form.X.editingFinished.connect(
    self.form.Y.setValidator(QDoubleValidator())
    self.form.Z.setValidator(QDoubleValidator())
  def getRef(self):
    if frameCmd.faces():
      a=[(o,frameCmd.faces([o])[0]) for o in FreeCADGui.Selection.getSelectionEx() if frameCmd.faces([o])][0]
      self.faceRef=a[1]
      self.form.label.setText(a[0].Object.Label+':Face')
      FreeCADGui.Selection.clearSelection()
  def refPlane(self,norm):
    self.faceRef=norm
    if norm==FreeCAD.Vector(0,0,1):
      self.form.label.setText('plane XY')
    elif norm==FreeCAD.Vector(0,1,0):
      self.form.label.setText('plane XZ')
    elif norm==FreeCAD.Vector(1,0,0):
      self.form.label.setText('plane YZ')
    else:
      self.form.label.setText('normal: X=%.2f Y=%.2f Z=%.2f' %(norm.x,norm.y,norm.z))
    for edit in [self.form.X, self.form.Y, self.form.Z]:
      edit.clear()
  def accept(self):
    faces=frameCmd.faces()
    beams=frameCmd.beams()
    if len(faces)==len(beams)>0 and self.faceRef:
      FreeCAD.activeDocument().openTransaction('AlignFlange')
      for i in range(len(beams)):
        frameCmd.rotTheBeam(beams[i],self.faceRef,faces[i])
      FreeCAD.activeDocument().recompute()
      FreeCAD.activeDocument().commitTransaction()
    
    
