#eagleTools dialogs
#(c) 2016 Riccardo Treu LGPL

import FreeCAD,FreeCADGui,eagleCmd
from PySide.QtCore import *
from PySide.QtGui import *

class eagleForm(QWidget):
  'prototype dialog for PCB components positioning'
  def __init__(self,winTitle='.brd import and displacement on PCB'):
    '''
    A FreeCAD-PCB simple extension
    '''
    super(eagleForm,self).__init__()
    self.move(QPoint(100,250))
    self.setWindowFlags(Qt.WindowStaysOnTopHint)
    self.setWindowTitle(winTitle)
    self.mainHL=QHBoxLayout()
    self.setLayout(self.mainHL)
    self.stuffList=QListWidget()
    self.stuffList.setMaximumWidth(120)
    self.stuffList.setCurrentRow(0)
    self.mainHL.addWidget(self.stuffList)
    self.stuffDictList=[]
    self.secondCol=QWidget()
    self.secondCol.setLayout(QVBoxLayout())
    self.btn1=QPushButton('Import .brd')
    self.btn1.setDefault(True)
    self.btn1.setFocus()
    self.secondCol.layout().addWidget(self.btn1)
    self.btn2=QPushButton('Place all')
    self.secondCol.layout().addWidget(self.btn2)
    self.mainHL.addWidget(self.secondCol)
    # check the model
    if 'Parts' in [o.Label for o in FreeCAD.activeDocument().Objects]:
    	if len(FreeCAD.activeDocument().Parts.OutList)>0:
    		FreeCAD.Console.PrintMessage('Parts has '+str(len(FreeCAD.activeDocument().Parts.OutList))+' components\n')
    	else:
    		FreeCAD.Console.PrintWarning('Parts has no components\n') 
    else:
    	FreeCAD.Console.PrintError('No group "Parts" found\n')

    # function assignment
    self.btn1.clicked.connect(self.importBrd)
    self.btn2.clicked.connect(self.placeStuff)
    # show dialog
    self.show()
    
  def importBrd(self):
    self.stuffDictList=eagleCmd.brdIn()
    for comp in FreeCAD.activeDocument().Parts.OutList:
      keysUpperCaseList=[k.upper() for k in self.stuffDictList.keys()]
      if comp.Label.upper() in keysUpperCaseList:
        self.stuffList.addItem(comp.Label.upper())
        
  def placeStuff(self):
    eagleCmd.brdCompare(self.stuffDictList)
