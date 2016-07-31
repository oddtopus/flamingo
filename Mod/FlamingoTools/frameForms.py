import FreeCAD,FreeCADGui
import frameCmd
from PySide.QtCore import *
from PySide.QtGui import *

class pivotForm(QWidget):
  def __init__(self):
    super(pivotForm,self).__init__()
    self.setWindowFlags(Qt.WindowStaysOnTopHint)
    #self.setMinimumSize(400,300)
    self.setWindowTitle('pivotForm')
    self.mainVL=QVBoxLayout()
    self.setLayout(self.mainVL)

    self.edit1=QLineEdit('90')
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
    self.btn1=QPushButton('Rotate')
    self.btn1.setDefault(True)
    self.btn1.clicked.connect(self.rotate)
    self.btn2=QPushButton('Reverse')
    self.btn2.clicked.connect(self.reverse)
    buttons=QWidget()
    buttons.setLayout(QHBoxLayout())
    buttons.layout().addWidget(self.btn1)
    buttons.layout().addWidget(self.btn2)
    self.mainVL.addWidget(buttons)

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

#form=frameForm1()