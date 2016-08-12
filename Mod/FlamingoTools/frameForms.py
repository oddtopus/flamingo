import FreeCAD,FreeCADGui
import frameCmd
from PySide.QtCore import *
from PySide.QtGui import *

class prototypeForm(QWidget):
  def __init__(self,winTitle='Title',btn1Text='Button1',btn2Text='Button2',initVal='someVal',units='someUnit'):
    super(prototypeForm,self).__init__()
    self.setWindowFlags(Qt.WindowStaysOnTopHint)
    self.setWindowTitle(winTitle)
    self.mainVL=QVBoxLayout()
    self.setLayout(self.mainVL)
    self.inputs=QWidget()
    self.inputs.setLayout(QFormLayout())
    self.edit1=QLineEdit(initVal)
    self.edit1.setMinimumWidth(150)
    self.edit1.setAlignment(Qt.AlignHCenter)
    self.edit1.setMaximumWidth(60)
    self.inputs.layout().addRow(units,self.edit1)
    self.mainVL.addWidget(self.inputs)
    self.radio1=QRadioButton()
    self.radio1.setChecked(True)
    self.radio2=QRadioButton()
    self.radios=QWidget()
    self.radios.setLayout(QFormLayout())
    self.radios.layout().setAlignment(Qt.AlignJustify)
    self.radios.layout().addRow('move',self.radio1)
    self.radios.layout().addRow('copy',self.radio2)
    self.mainVL.addWidget(self.radios)
    self.btn1=QPushButton(btn1Text)
    self.btn1.setDefault(True)
    self.btn2=QPushButton(btn2Text)
    self.buttons=QWidget()
    self.buttons.setLayout(QHBoxLayout())
    self.buttons.layout().addWidget(self.btn1)
    self.buttons.layout().addWidget(self.btn2)
    self.mainVL.addWidget(self.buttons)

class pivotForm(prototypeForm):
  def __init__(self):
    super(pivotForm,self).__init__('pivotForm','Rotate','Reverse','90','Angle - deg:')
    self.btn1.clicked.connect(self.rotate)
    self.btn2.clicked.connect(self.reverse)
    self.show()
  def rotate(self):
    FreeCAD.activeDocument().openTransaction()
    if self.radio2.isChecked():
      FreeCAD.activeDocument().copyObject(FreeCADGui.Selection.getSelection()[0],True)
      frameCmd.pivotTheBeam(float(self.edit1.text()),ask4revert=False)
    else:
      frameCmd.pivotTheBeam(float(self.edit1.text()),ask4revert=False)
    FreeCAD.activeDocument().commitTransaction()
  def reverse(self):
    FreeCAD.activeDocument().openTransaction()
    frameCmd.pivotTheBeam(-2*float(self.edit1.text()),ask4revert=False)
    self.edit1.setText(str(-1*float(self.edit1.text())))
    FreeCAD.activeDocument().commitTransaction()

class shiftForm(prototypeForm):
  def __init__(self):
    super(shiftForm,self).__init__('shiftForm','Shift','Reverse','500','Distance  - mm:')
    self.btn1.clicked.connect(self.shift)
    self.btn2.clicked.connect(self.reverse)
    self.btn3=QPushButton('Get Distance')
    self.btn3.clicked.connect(self.getDist)
    self.buttons.layout().addWidget(self.btn3)
    self.show()
  def shift(self):
    edge=frameCmd.edges()[0]
    beam=frameCmd.beams()[0]
    FreeCAD.activeDocument().openTransaction()
    if self.radio2.isChecked():
      FreeCAD.activeDocument().copyObject(FreeCADGui.Selection.getSelection()[0],True)
      frameCmd.shiftTheBeam(beam,edge,float(self.edit1.text()),ask4revert=False)
    else:
      frameCmd.shiftTheBeam(beam,edge,float(self.edit1.text()),ask4revert=False)
    FreeCAD.activeDocument().commitTransaction()
  def reverse(self):
    FreeCAD.activeDocument().openTransaction()
    edge=frameCmd.edges()[0]
    beam=frameCmd.beams()[0]
    frameCmd.shiftTheBeam(beam,edge,-2*float(self.edit1.text()),ask4revert=False)
    self.edit1.setText(str(-1*float(self.edit1.text())))
    FreeCAD.activeDocument().commitTransaction()
  def getDist(self):
    shapes=[y for x in FreeCADGui.Selection.getSelectionEx() for y in x.SubObjects if hasattr(y,'ShapeType')]
    if len(shapes)==1 and shapes[0].ShapeType=='Edge':
        self.edit1.setText(str(shapes[0].Length))
    elif len(shapes)>1:
      self.edit1.setText(str(shapes[0].distToShape(shapes[1])[0]))
    

class fillForm(prototypeForm):
  def __init__(self):
    super(fillForm,self).__init__('fillForm','Select','Fill','<select a beam>','')
    self.beam=None
    self.btn1.clicked.connect(self.select)
    self.btn2.clicked.connect(self.fill)
    self.radio2.setChecked(True)
    self.btn1.setFocus()
    self.show()
  def fill(self):
    if self.beam!=None and len(frameCmd.edges())>0:
      FreeCAD.activeDocument().openTransaction()
      if self.radio1.isChecked():
        frameCmd.placeTheBeam(self.beam,frameCmd.edges()[0])
      else:
        for edge in frameCmd.edges():
          struct=FreeCAD.activeDocument().copyObject(self.beam,True)
          frameCmd.placeTheBeam(struct,edge)
        FreeCAD.activeDocument().recompute()
      FreeCAD.activeDocument().commitTransaction()
  def select(self):
    if frameCmd.beams()>0:
      self.beam=frameCmd.beams()[0]
      self.edit1.setText(self.beam.Label+':'+self.beam.Profile)
      self.btn2.setFocus()    

class extendForm(prototypeForm):
  'dialog for frameCmd.extendTheBeam()'
  def __init__(self):
    super(extendForm,self).__init__('extendForm','Target','Extend','<select a target shape>','')
    self.target=None
    self.btn1.clicked.connect(self.getTarget)
    self.btn1.setFocus()
    self.btn2.clicked.connect(self.extend)
    self.radios.hide()
    self.show()
  def getTarget(self):
    selex = FreeCADGui.Selection.getSelectionEx()
    if len(selex[0].SubObjects)>0 and hasattr(selex[0].SubObjects[0],'ShapeType'):
      self.target=selex[0].SubObjects[0]
      self.edit1.setText(selex[0].Object.Label+':'+self.target.ShapeType)
  def extend(self):
    if self.target!=None and len(frameCmd.beams())>0:
      FreeCAD.activeDocument().openTransaction()
      for beam in frameCmd.beams():
        frameCmd.extendTheBeam(beam,self.target)
      FreeCAD.activeDocument().commitTransaction()  