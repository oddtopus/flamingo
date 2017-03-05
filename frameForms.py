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

class pivotForm(prototypeForm):
  'dialog for pivotTheBeam()'
  def __init__(self):
    super(pivotForm,self).__init__('pivotForm','Rotate','Reverse','90','Angle - deg:','pivot.svg')
    self.edit1.setValidator(QDoubleValidator())
    self.btn1.clicked.connect(self.rotate)
    self.btn2.clicked.connect(self.reverse)
    self.show()
  def rotate(self):
    FreeCAD.activeDocument().openTransaction('Rotate')
    if self.radio2.isChecked():
      FreeCAD.activeDocument().copyObject(FreeCADGui.Selection.getSelection()[0],True)
      frameCmd.pivotTheBeam(float(self.edit1.text()),ask4revert=False)
    else:
      frameCmd.pivotTheBeam(float(self.edit1.text()),ask4revert=False)
    FreeCAD.activeDocument().commitTransaction()
  def reverse(self):
    FreeCAD.activeDocument().openTransaction('Reverse rotate')
    frameCmd.pivotTheBeam(-2*float(self.edit1.text()),ask4revert=False)
    self.edit1.setText(str(-1*float(self.edit1.text())))
    FreeCAD.activeDocument().commitTransaction()

class fillForm(prototypeForm):
  'dialog for fillFrame()'
  def __init__(self):
    super(fillForm,self).__init__('fillForm','Select','Fill','<select a beam>','','fillFrame.svg')
    self.beam=None
    self.edit1.setMinimumWidth(150)
    self.btn1.clicked.connect(self.select)
    self.btn2.clicked.connect(self.fill)
    self.radio2.setChecked(True)
    self.btn1.setFocus()
    self.show()
  def fill(self):
    if self.beam!=None and len(frameCmd.edges())>0:
      FreeCAD.activeDocument().openTransaction('Fill frame')
      if self.radio1.isChecked():
        frameCmd.placeTheBeam(self.beam,frameCmd.edges()[0])
      else:
        for edge in frameCmd.edges():
          struct=FreeCAD.activeDocument().copyObject(self.beam,True)
          frameCmd.placeTheBeam(struct,edge)
        FreeCAD.activeDocument().recompute()
      FreeCAD.activeDocument().commitTransaction()
  def select(self):
    if len(frameCmd.beams())>0:
      self.beam=frameCmd.beams()[0]
      self.edit1.setText(self.beam.Label+':'+self.beam.Profile)
      FreeCADGui.Selection.removeSelection(self.beam)

class extendForm(prototypeForm):
  'dialog for frameCmd.extendTheBeam()'
  def __init__(self):
    super(extendForm,self).__init__('extendForm','Extend','Target','<select target>','','extend.svg')
    self.edit1.setMinimumWidth(150)
    selex = FreeCADGui.Selection.getSelectionEx()
    self.btn1.clicked.connect(self.extend)
    self.btn2.clicked.connect(self.getTarget)
    if len(selex):
      self.target=selex[0].SubObjects[0]
      self.edit1.setText(selex[0].Object.Label+':'+self.target.ShapeType)
      self.btn1.setFocus()
      FreeCADGui.Selection.removeSelection(selex[0].Object)
    else:
      self.target=None
    self.radios.hide()
    self.show()
  def getTarget(self):
    selex = FreeCADGui.Selection.getSelectionEx()
    if len(selex[0].SubObjects)>0 and hasattr(selex[0].SubObjects[0],'ShapeType'):
      self.target=selex[0].SubObjects[0]
      self.edit1.setText(selex[0].Object.Label+':'+self.target.ShapeType)
      FreeCADGui.Selection.clearSelection()
  def extend(self):
    if self.target!=None and len(frameCmd.beams())>0:
      FreeCAD.activeDocument().openTransaction('Extend beam')
      for beam in frameCmd.beams():
        frameCmd.extendTheBeam(beam,self.target)
      FreeCAD.activeDocument().commitTransaction()
      FreeCAD.activeDocument().recompute()
      
class stretchForm(prototypeForm):
  '''dialog for stretchTheBeam()
    [Get Length] measures the min. distance of the selected objects or
      the length of the selected edge or
      the Height of the selected beam
    [ Stretch ] changes the Height of the selected beams
  '''
  def __init__(self):
    super(stretchForm,self).__init__('stretchForm','Get Length','Stretch','','mm','beamStretch.svg')
    self.L=None
    self.edit1.setMaximumWidth(150)
    self.edit1.setMinimumWidth(40)
    self.edit1.setValidator(QDoubleValidator())
    self.edit1.editingFinished.connect(self.edit12L)
    self.btn1.clicked.connect(self.getL)
    self.btn2.clicked.connect(self.stretch)
    self.btn1.setFocus()
    self.radios.hide()
    self.slider=QSlider(Qt.Horizontal)
    self.slider.setMinimum(-100)
    self.slider.setMaximum(100)
    self.slider.setValue(0)
    self.slider.valueChanged.connect(self.changeL)
    self.mainVL.addWidget(self.slider)
    self.show()
  def edit12L(self):
    if self.edit1.text():
      self.L=float(self.edit1.text())
      self.slider.setValue(0)
  def changeL(self):
    ext=self.L*(1+self.slider.value()/100.0)
    print ext
    self.edit1.setText(str(ext))
  def getL(self):
    self.L=frameCmd.getDistance()
    if self.L:
      self.edit1.setText(str(self.L))
    elif frameCmd.beams():
      self.L=float(frameCmd.beams()[0].Height)
      self.edit1.setText(str(self.L))
    else:
      self.edit1.setText('') 
    self.slider.setValue(0)
  def stretch(self):
    FreeCAD.activeDocument().openTransaction('Stretch beam')
    for beam in frameCmd.beams():
      frameCmd.stretchTheBeam(beam,float(self.edit1.text()))
    FreeCAD.activeDocument().recompute()
    FreeCAD.activeDocument().commitTransaction()
    
class translateForm(prototypeForm):   
  'dialog for moving blocks'
  def __init__(self):
    super(translateForm,self).__init__('translateForm','Displacement','Vector','0','x - mm','beamShift.svg')
    self.btn1.clicked.connect(self.getDisp)
    self.btn2.clicked.connect(self.getVect)
    self.edit1.setMaximumWidth(120)
    self.edit2=QLineEdit('0')
    self.edit2.setMinimumWidth(40)
    self.edit2.setAlignment(Qt.AlignHCenter)
    self.edit2.setMaximumWidth(120)
    self.inputs.layout().addRow('y - mm',self.edit2)
    self.edit3=QLineEdit('0')
    self.edit3.setMinimumWidth(40)
    self.edit3.setAlignment(Qt.AlignHCenter)
    self.edit3.setMaximumWidth(120)
    self.inputs.layout().addRow('z - mm',self.edit3)
    self.edit4=QLineEdit('1')
    self.edit4.setMinimumWidth(40)
    self.edit4.setAlignment(Qt.AlignHCenter)
    self.edit4.setMaximumWidth(120)
    self.inputs.layout().addRow('Multiple',self.edit4)
    self.edit5=QLineEdit('1')
    self.edit5.setMinimumWidth(40)
    self.edit5.setAlignment(Qt.AlignHCenter)
    self.edit5.setMaximumWidth(120)
    for e in [self.edit1,self.edit3,self.edit3,self.edit4,self.edit5]:
      e.setValidator(QDoubleValidator())
    self.inputs.layout().addRow('Steps',self.edit5)
    self.btn3=QPushButton('Translate')
    self.btn3.clicked.connect(self.translateTheBeams)
    self.buttons2=QWidget()
    self.buttons2.setLayout(QHBoxLayout())
    self.buttons2.layout().addWidget(self.btn3)
    self.mainVL.addWidget(self.buttons2)
    self.btn1.setDefault(False)
    self.btn3.setDefault(True)
    self.btn3.setFocus()
    self.show()
    #if len(frameCmd.edges())==1:
    #  self.getVect()
    #else:
    #  self.getDisp()
  def getDisp(self):
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
        self.edit4.setText(str(disp.Length))
        self.edit5.setText('1')
        disp.normalize()
        dx,dy,dz=list(disp)
        self.edit1.setText(str(round(dx,roundDigits)))
        self.edit2.setText(str(round(dy,roundDigits)))
        self.edit3.setText(str(round(dz,roundDigits)))
        FreeCADGui.Selection.clearSelection()
  def getVect(self):
    roundDigits=3
    if len(frameCmd.edges())>0:
      edge=frameCmd.edges()[0]
      self.edit4.setText(str(edge.Length))
      self.edit5.setText('1')
      dx,dy,dz=list(edge.tangentAt(0))
      self.edit1.setText(str(round(dx,roundDigits)))
      self.edit2.setText(str(round(dy,roundDigits)))
      self.edit3.setText(str(round(dz,roundDigits)))
      FreeCADGui.Selection.clearSelection()
  def translateTheBeams(self):
    scale=float(self.edit4.text())/float(self.edit5.text())
    disp=FreeCAD.Vector(float(self.edit1.text()),float(self.edit2.text()),float(self.edit3.text())).scale(scale,scale,scale)
    FreeCAD.activeDocument().openTransaction('Translate')    
    if self.radio2.isChecked():
      for o in set(FreeCADGui.Selection.getSelection()):
        FreeCAD.activeDocument().copyObject(o,True)
    for o in set(FreeCADGui.Selection.getSelection()):
      o.Placement.move(disp)
    FreeCAD.activeDocument().recompute()
    FreeCAD.activeDocument().commitTransaction()    

