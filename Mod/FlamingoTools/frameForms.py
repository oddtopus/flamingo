import FreeCAD,FreeCADGui
import frameCmd
from PySide.QtCore import *
from PySide.QtGui import *

class prototypeForm(QWidget):
  def __init__(self,winTitle,btn1Text,btn2Text,initVal):
    super(prototypeForm,self).__init__()
    self.setWindowFlags(Qt.WindowStaysOnTopHint)
    self.setWindowTitle(winTitle)
    self.mainVL=QVBoxLayout()
    self.setLayout(self.mainVL)
    self.edit1=QLineEdit(initVal)
    self.edit1.setMinimumWidth(150)
    self.edit1.setAlignment(Qt.AlignHCenter)
    self.mainVL.addWidget(self.edit1)
    self.radio1=QRadioButton()
    self.radio1.setChecked(True)
    self.radio2=QRadioButton()
    radios=QWidget()
    radios.setLayout(QFormLayout())
    radios.layout().setAlignment(Qt.AlignJustify)
    radios.layout().addRow('move',self.radio1)
    radios.layout().addRow('copy',self.radio2)
    self.mainVL.addWidget(radios)
    self.btn1=QPushButton(btn1Text)
    self.btn1.setDefault(True)
    self.btn2=QPushButton(btn2Text)
    buttons=QWidget()
    buttons.setLayout(QHBoxLayout())
    buttons.layout().addWidget(self.btn1)
    buttons.layout().addWidget(self.btn2)
    self.mainVL.addWidget(buttons)


class pivotForm(prototypeForm):
  def __init__(self):
    super(pivotForm,self).__init__('pivotForm','Rotate','Reverse','90')
    self.btn1.clicked.connect(self.rotate)
    self.btn2.clicked.connect(self.reverse)
    self.show()
    
  def rotate(self):
    if self.radio2.isChecked():
      FreeCAD.activeDocument().copyObject(FreeCADGui.Selection.getSelection()[0],True)
      frameCmd.pivotTheBeam(float(self.edit1.text()),ask4revert=False)
    else:
      frameCmd.pivotTheBeam(float(self.edit1.text()),ask4revert=False)
      
  def reverse(self):
    frameCmd.pivotTheBeam(-2*float(self.edit1.text()),ask4revert=False)
    self.close()

class shiftForm(prototypeForm):
  def __init__(self):
    super(shiftForm,self).__init__('shiftForm','Shift','Reverse','500')
    self.btn1.clicked.connect(self.shift)
    self.btn2.clicked.connect(self.reverse)
    self.show()
    
  def shift(self):
    edge=frameCmd.edges()[0]
    beam=frameCmd.beams()[0]
    if self.radio2.isChecked():
      FreeCAD.activeDocument().copyObject(FreeCADGui.Selection.getSelection()[0],True)
      frameCmd.shiftTheBeam(beam,edge,float(self.edit1.text()),ask4revert=False)
    else:
      frameCmd.shiftTheBeam(beam,edge,float(self.edit1.text()),ask4revert=False)
      
  def reverse(self):
    edge=frameCmd.edges()[0]
    beam=frameCmd.beams()[0]
    frameCmd.shiftTheBeam(beam,edge,-2*float(self.edit1.text()),ask4revert=False)
    self.close()

