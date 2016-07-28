from PySide import QtGui, QtCore
 
# UI Class definitions
 
class QueryForm(QtGui.QWidget):
  "form for qCmd.py"
  def __init__(self,Selection):
    QtGui.QWidget.__init__(self)
    self.initUI()
    self.Selection=Selection
  def initUI(self):
    # define window    xLoc,yLoc,xDim,yDim
    self.setGeometry(  250, 250, 400, 200)
    self.setWindowTitle("QueryTool")
    self.setWindowFlags(QtCore.Qt.WindowStaysOnTopHint)
    self.setMouseTracking(True)
    # widgets 1st row
    self.labName = QtGui.QLabel("(seleziona un oggetto)", self)
    # widgets 2nd row
    labBase = QtGui.QLabel("Base:", self)
    self.labBaseVal = QtGui.QLabel("(base)", self)
    subHLayout1=QtGui.QHBoxLayout()
    subHLayout1.addWidget(labBase)
    subHLayout1.addWidget(self.labBaseVal)
    # widgets 3rd row
    labRot = QtGui.QLabel("Rotation:", self)
    self.labRotVal = QtGui.QLabel("(rotation)", self)
    subHLayout2=QtGui.QHBoxLayout()
    subHLayout2.addWidget(labRot)
    subHLayout2.addWidget(self.labRotVal)
    # widgets 4th row
    pushButton1 = QtGui.QPushButton('QueryObject', self)
    pushButton1.clicked.connect(self.onPushButton1)
    pushButton1.setMinimumWidth(90)
    cancelButton = QtGui.QPushButton('Exit', self)
    cancelButton.clicked.connect(self.onCancel)
    cancelButton.setAutoDefault(True)
    self.labMousePos = QtGui.QLabel("            ", self)
    subHLayout3=QtGui.QHBoxLayout()
    subHLayout3.addWidget(pushButton1)
    subHLayout3.addWidget(cancelButton)
    subHLayout3.addWidget(self.labMousePos)
    # arrange the layout
    mainVLayout=QtGui.QVBoxLayout()
    mainVLayout.addWidget(self.labName)
    mainVLayout.addLayout(subHLayout1)
    mainVLayout.addLayout(subHLayout2)
    mainVLayout.addLayout(subHLayout3)
    QtGui.QWidget.setLayout(self,mainVLayout)
    # now make the window visible
    self.show()
    
  def onPushButton1(self):
    import FreeCADGui
    try:
      obj=self.Selection.getSelection()[0]
      self.labName.setText(obj.Label)
      self.labBaseVal.setText(str(obj.Placement.Base))
      self.labRotVal.setText(str(obj.Placement.Rotation))
    except:
      pass
    
  def onCancel(self):
    self.close()

  def mouseMoveEvent(self,event):
    self.labMousePos.setText("X: "+str(event.x()) + " Y: "+str(event.y()))

