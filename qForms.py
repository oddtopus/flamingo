# Dialo for query  
# (c) 2016 Riccardo Treu LGPL

from PySide import QtGui, QtCore
 
# UI Class definitions
 
class QueryForm(QtGui.QWidget):
  "form for qCmd.py"
  def __init__(self,Selection):
    super(QueryForm,self).__init__()
    self.initUI()
    self.Selection=Selection
  def initUI(self):
    self.setWindowTitle("QueryTool")
    self.setWindowFlags(QtCore.Qt.WindowStaysOnTopHint)
    self.setMouseTracking(True)
    #1st row
    self.labName = QtGui.QLabel("(seleziona un oggetto)", self)
    #2nd row
    self.labBaseVal = QtGui.QLabel("(base)", self)
    self.subFLayout1=QtGui.QFormLayout()
    self.subFLayout1.addRow('Base: ',self.labBaseVal)
    #3rd row
    self.labRotAng = QtGui.QLabel("(angle)", self)
    self.subFLayout2=QtGui.QFormLayout()
    self.subFLayout2.addRow('Rotation angle: ',self.labRotAng)
    # 4th row
    self.labRotAx = QtGui.QLabel("v = (x,y,z)", self)
    self.subFLayout3=QtGui.QFormLayout()
    self.subFLayout3.addRow('Rotation axis: ',self.labRotAx)
    # 5th row
    self.labSubObj = QtGui.QLabel("(Sub object property)", self)
    # 6th row
    self.labBeam = QtGui.QLabel("(Beam property)", self)
    # 7th row
    self.labProfile = QtGui.QLabel("(Profile property)", self)
    # 8th row
    self.pushButton1 = QtGui.QPushButton('QueryObject')
    self.pushButton1.setDefault(True)
    self.pushButton1.clicked.connect(self.onPushButton1)
    self.pushButton1.setMinimumWidth(90)
    self.cancelButton = QtGui.QPushButton('Exit')
    self.cancelButton.clicked.connect(self.onCancel)
    self.subHLayout1=QtGui.QHBoxLayout()
    self.subHLayout1.addWidget(self.pushButton1)
    self.subHLayout1.addWidget(self.cancelButton)
    # arrange the layout
    self.mainVLayout=QtGui.QVBoxLayout()
    self.mainVLayout.addWidget(self.labName)
    self.mainVLayout.addLayout(self.subFLayout1)
    self.mainVLayout.addLayout(self.subFLayout2)
    self.mainVLayout.addLayout(self.subFLayout3)
    self.mainVLayout.addWidget(self.labSubObj)
    self.mainVLayout.addWidget(self.labBeam)
    self.mainVLayout.addWidget(self.labProfile)
    self.mainVLayout.addLayout(self.subHLayout1)
    QtGui.QWidget.setLayout(self,self.mainVLayout)
    # now make the window visible
    self.show()
    
  def onPushButton1(self):
    from math import pi, degrees
    import frameCmd
    try:
      obj=self.Selection.getSelection()[0]
      self.labName.setText(obj.Label)
      self.labBaseVal.setText(str("P = %.1f,%.1f,%.1f"%tuple(obj.Placement.Base)))
      self.labRotAng.setText(str("%.2f " %(degrees(obj.Placement.Rotation.Angle))))
      ax=obj.Placement.Rotation.Axis
      self.labRotAx.setText(str("v = (%(x).2f,%(y).2f,%(z).2f)" %{'x':ax.x,'y':ax.y,'z':ax.z}))
      shapes=[y for x in self.Selection.getSelectionEx() for y in x.SubObjects if hasattr(y,'ShapeType')]
      if len(shapes)==1:
        sub=shapes[0]
        if sub.ShapeType=='Edge':
          self.labSubObj.setText(sub.ShapeType+': L = %.1f mm' %sub.Length)
        elif sub.ShapeType=='Face':
          self.labSubObj.setText(sub.ShapeType+': A = %.1f mm2' %sub.Area)
        elif sub.ShapeType=='Vertex':
          self.labSubObj.setText(sub.ShapeType+': pos = (%(x).1f,%(y).1f,%(z).1f)' %{'x':sub.X,'y':sub.Y,'z':sub.Z})
      elif len(shapes)>1:
        self.labSubObj.setText(shapes[0].ShapeType+' to '+shapes[1].ShapeType+': distance = %.1f mm' %(shapes[0].distToShape(shapes[1])[0]))
      else:
        self.labSubObj.setText(' ')
      if len(frameCmd.beams())==1:
        b=frameCmd.beams()[0]
        self.labBeam.setText(b.Label+": L=%.2f"%(b.Height))
        self.labProfile.setText("Profile: "+b.Profile)
      elif len(frameCmd.beams())>1:
        b1,b2=frameCmd.beams()[:2]
        self.labBeam.setText(b1.Label+"^"+b2.Label+": %.2f"%(degrees(frameCmd.beamAx(b1).getAngle(frameCmd.beamAx(b2)))))
        self.labProfile.setText("")
      else:
        self.labBeam.setText("")
        self.labProfile.setText("")
    except:
      pass
    
  def onCancel(self):
    self.close()

  #def mouseMoveEvent(self,event):
  #  self.labMousePos.setText("X: "+str(event.x()) + " Y: "+str(event.y()))

