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
from Draft import get3DView
from sys import platform

class prototypeForm(QWidget): #OBSOLETE: no more used. Replaced by prototypeDialog
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

class prototypeDialog(object): 
  # ACHTUNG: "self.call" DISABLED IN WINDOWS OS, DUE TO UNHANDLED RUN-TIME EXCEPTION
  'prototype for dialogs.ui with callback function'
  def __init__(self,dialog='anyFile.ui'):
    dialogPath=join(dirname(abspath(__file__)),"dialogs",dialog)
    FreeCAD.Console.PrintMessage(dialogPath+"\n")
    self.form=FreeCADGui.PySideUic.loadUi(dialogPath)
    FreeCAD.Console.PrintMessage(dialogPath+" loaded\n")
    if platform.startswith('win'):
      FreeCAD.Console.PrintWarning("No keyboard shortcuts.\n")
    else:
      FreeCAD.Console.PrintMessage('Keyboard shortcuts available.\n"S" to select\n"RETURN" to perform action\n')
      try:
        self.view=get3DView()
        self.call=self.view.addEventCallback("SoEvent", self.action)
      except:
        FreeCAD.Console.PrintError('No view available.\n')
  def action(self,arg):
    'Default function executed by callback'
    if arg['Type']=='SoKeyboardEvent':
      if arg['Key'] in ['s','S'] and arg['State']=='DOWN':# and FreeCADGui.Selection.getSelection():
        self.selectAction()
      elif arg['Key']=='RETURN' and arg['State']=='DOWN':
        self.accept()
      elif arg['Key']=='ESCAPE' and arg['State']=='DOWN':
        self.reject()
    if arg['Type']=='SoMouseButtonEvent':
      CtrlAltShift=[arg['CtrlDown'],arg['AltDown'],arg['ShiftDown']]
      if arg['Button']=='BUTTON1' and arg['State']=='DOWN': self.mouseActionB1(CtrlAltShift)
      elif arg['Button']=='BUTTON2' and arg['State']=='DOWN': self.mouseActionB2(CtrlAltShift)
      elif arg['Button']=='BUTTON3' and arg['State']=='DOWN': self.mouseActionB3(CtrlAltShift)
  def selectAction(self):
    'MUST be redefined in the child class'
    pass
  def mouseActionB1(self,CtrlAltShift):
    'MUST be redefined in the child class'
    pass
  def mouseActionB2(self,CtrlAltShift):
    'MUST be redefined in the child class'
    pass
  def mouseActionB3(self,CtrlAltShift):
    'MUST be redefined in the child class'
    pass
  def reject(self):
    'CAN be redefined to remove other attributes, such as arrow()s or label()s'
    try: self.view.removeEventCallback('SoEvent',self.call)
    except: pass
    if FreeCAD.ActiveDocument: FreeCAD.ActiveDocument.recompute()
    FreeCADGui.Control.closeDialog()

class fillForm(prototypeDialog):
  'dialog for fillFrame()'
  def __init__(self):
    super(fillForm,self).__init__('fillframe.ui')
    self.beam=None
    self.form.btn1.clicked.connect(self.selectAction)
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
  def selectAction(self):
    if len(frameCmd.beams())>0:
      self.beam=frameCmd.beams()[0]
      self.form.label.setText(self.beam.Label+':'+self.beam.Profile)
      FreeCADGui.Selection.removeSelection(self.beam)

class extendForm(prototypeDialog):
  'dialog for frameCmd.extendTheBeam()'
  def __init__(self):
    super(extendForm,self).__init__('extend.ui')
    selex = FreeCADGui.Selection.getSelectionEx()
    self.form.btn1.clicked.connect(self.selectAction)
    if len(selex):
      self.target=selex[0].SubObjects[0]
      self.form.label.setText(selex[0].Object.Label+':'+self.target.ShapeType)
      FreeCADGui.Selection.removeSelection(selex[0].Object)
    else:
      self.target=None
  def selectAction(self):
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
      
class stretchForm(prototypeDialog):
  '''dialog for stretchTheBeam()
    [Get Length] measures the min. distance of the selected objects or
      the length of the selected edge or
      the Height of the selected beam
    [ Stretch ] changes the Height of the selected beams
  '''
  def __init__(self):
    self.L=None
    super(stretchForm,self).__init__('beamstretch.ui')
    self.form.edit1.setValidator(QDoubleValidator())
    self.form.edit1.editingFinished.connect(self.edit12L)
    self.form.btn1.clicked.connect(self.selectAction)
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
      self.form.edit1.setText("%.3f" %ext)
  def selectAction(self):
    if self.labTail:
      self.labTail.removeLabel()
      self.labTail=None
    self.L=frameCmd.getDistance()
    if self.L:
      self.form.edit1.setText("%.3f"%self.L)
    elif frameCmd.beams():
      beam=frameCmd.beams()[0]
      self.L=float(beam.Height)
      self.form.edit1.setText("%.3f"%self.L)
    else:
      self.form.edit1.setText('') 
    self.form.slider.setValue(0)
    self.writeTail()
  def writeTail(self):
    if frameCmd.beams():
      beam=frameCmd.beams()[0]
      from polarUtilsCmd import label3D
      self.labTail=label3D(pl=beam.Placement, text='____TAIL')
  def accept(self):
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
          disp=frameCmd.beamAx(beam).multiply(delta)
          beam.Placement.move(disp)
        elif self.form.both.isChecked():
          disp=frameCmd.beamAx(beam).multiply(delta/2.0)
          beam.Placement.move(disp)
      FreeCAD.activeDocument().recompute()
      FreeCAD.activeDocument().commitTransaction()
  def reject(self): # redefined to remove label from the scene
    if self.labTail:
      self.labTail.removeLabel()
    super(stretchForm,self).reject()

class translateForm(prototypeDialog):   
  'dialog for moving blocks'
  def __init__(self):
    super(translateForm,self).__init__("beamshift.ui")
    for e in [self.form.edit1,self.form.edit2,self.form.edit3,self.form.edit4,self.form.edit5]:
      e.setValidator(QDoubleValidator())
    self.form.btn1.clicked.connect(self.selectAction)
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
  def selectAction(self):
    shapes=[y for x in FreeCADGui.Selection.getSelectionEx() for y in x.SubObjects if hasattr(y,'ShapeType')][:2]
    if len(shapes)>1:
      self.getDistance()
    elif len(frameCmd.edges())>0:
      self.getLength()
  def accept(self):           # translate
    self.deleteArrow()
    scale=float(self.form.edit4.text())/float(self.form.edit5.text())
    disp=FreeCAD.Vector(float(self.form.edit1.text())*self.form.cbX.isChecked(),float(self.form.edit2.text())*self.form.cbY.isChecked(),float(self.form.edit3.text())*self.form.cbZ.isChecked()).scale(scale,scale,scale)
    FreeCAD.activeDocument().openTransaction('Translate')    
    if self.form.radio2.isChecked():
      for o in set(FreeCADGui.Selection.getSelection()):
        FreeCAD.activeDocument().copyObject(o,True)
    for o in set(FreeCADGui.Selection.getSelection()):
      o.Placement.move(disp)
    FreeCAD.activeDocument().recompute()
    FreeCAD.activeDocument().commitTransaction()    
  def deleteArrow(self):
    if self.arrow: self.arrow.closeArrow() #FreeCADGui.ActiveDocument.ActiveView.getSceneGraph().removeChild(self.arrow.node)
    self.arrow=None
  def reject(self): # redefined to remove arrow from scene
    self.deleteArrow()
    #try: self.view.removeEventCallback('SoEvent',self.call)
    #except: pass
    #if FreeCAD.ActiveDocument: FreeCAD.ActiveDocument.recompute()
    #FreeCADGui.Control.closeDialog()
    super(translateForm,self).reject()

class alignForm(prototypeDialog):   
  'dialog to flush faces'
  def __init__(self):
    super(alignForm,self).__init__('align.ui')
    self.faceRef=None
    self.selectAction()
    self.form.btn1.clicked.connect(self.selectAction)
    self.form.btnXY.clicked.connect(lambda: self.refPlane(FreeCAD.Vector(0,0,1)))
    self.form.btnXZ.clicked.connect(lambda: self.refPlane(FreeCAD.Vector(0,1,0)))
    self.form.btnYZ.clicked.connect(lambda: self.refPlane(FreeCAD.Vector(1,0,0)))
    self.form.X.setValidator(QDoubleValidator())
    self.form.btnNorm.clicked.connect(lambda: self.refPlane(FreeCAD.Vector(float(self.form.X.text()),float(self.form.Y.text()),float(self.form.Z.text()))))
    self.form.Y.setValidator(QDoubleValidator())
    self.form.Z.setValidator(QDoubleValidator())
  def selectAction(self):
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
    
class rotateAroundForm(prototypeDialog):
  '''
  Dialog for rotateTheBeamAround().
  It allows to rotate one object around one edge or the axis of a circular edge (or one principal axis.)
  '''
  def __init__(self):
    super(rotateAroundForm,self).__init__('rotAround.ui')
    self.form.edit1.setValidator(QDoubleValidator())
    self.form.btn1.clicked.connect(self.selectAction)
    self.form.btn2.clicked.connect(self.reverse)
    self.form.btnX.clicked.connect(lambda: self.getPrincipalAx('X'))
    self.form.btnY.clicked.connect(lambda: self.getPrincipalAx('Y'))
    self.form.btnZ.clicked.connect(lambda: self.getPrincipalAx('Z'))
    self.form.dial.valueChanged.connect(lambda: self.form.edit1.setText(str(self.form.dial.value())))
    self.form.edit1.editingFinished.connect(lambda: self.form.dial.setValue(int(self.form.edit1.text())))
    self.Axis=None
    self.arrow=None
    self.selectAction()
  def accept(self, ang=None):
    if not ang:
      ang=float(self.form.edit1.text())
    self.deleteArrow()
    objects=FreeCADGui.Selection.getSelection()
    if objects and self.Axis:
      FreeCAD.ActiveDocument.openTransaction('rotateTheBeamAround')
      for o in objects:
        if self.form.copyCB.isChecked():
          FreeCAD.activeDocument().copyObject(o,True)
        frameCmd.rotateTheBeamAround(o,self.Axis,ang)
      FreeCAD.ActiveDocument.commitTransaction()
  def reverse(self):
    ang=float(self.form.edit1.text())*-1
    self.form.edit1.setText('%.0f'%ang)
    self.form.dial.setValue(int(self.form.edit1.text()))
    self.accept(ang*2)
  def getPrincipalAx(self, ax='Z'):
    self.deleteArrow()
    from Part import Edge,Line
    O=FreeCAD.Vector()
    l=Line(O,FreeCAD.Vector(0,0,1000))
    if ax=='X':
      l=Line(O,FreeCAD.Vector(1000,0,0))
    elif ax=='Y':
      l=Line(O,FreeCAD.Vector(0,1000,0))
    self.Axis=Edge(l)
    self.form.lab1.setText("Principal: "+ax)
  def selectAction(self):
    edged = [objex for objex in FreeCADGui.Selection.getSelectionEx() if frameCmd.edges([objex])]
    if edged:
      self.Axis=frameCmd.edges([edged[0]])[0]
      self.deleteArrow()
      from polarUtilsCmd import arrow
      where=FreeCAD.Placement()
      where.Base=self.Axis.valueAt(self.Axis.LastParameter)
      where.Rotation=FreeCAD.Rotation(FreeCAD.Vector(0,0,1),self.Axis.tangentAt(self.Axis.LastParameter))
      size=[self.Axis.Length/20.0,self.Axis.Length/10.0,self.Axis.Length/20.0]
      self.arrow=arrow(pl=where,scale=size,offset=self.Axis.Length/10.0)
      if self.Axis.curvatureAt(0):
        O=self.Axis.centerOfCurvatureAt(0)
        n=self.Axis.tangentAt(0).cross(self.Axis.normalAt(0))
        from Part import Edge, Line
        self.Axis=(Edge(Line(FreeCAD.Vector(O),FreeCAD.Vector(O+n))))
      self.form.lab1.setText(edged[0].Object.Label+": edge")
  def deleteArrow(self):
    if self.arrow: self.arrow.closeArrow()
    self.arrow=None
  def reject(self): # redefined to remove arrow from scene
    self.deleteArrow()
    #try: self.view.removeEventCallback('SoEvent',self.call)
    #except: pass
    #if FreeCAD.ActiveDocument: FreeCAD.ActiveDocument.recompute()
    #FreeCADGui.Control.closeDialog()
    super(rotateAroundForm,self).reject()
