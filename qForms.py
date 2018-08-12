#(c) 2016 R. T. LGPL: part of Flamingo tools w.b. for FreeCAD

__title__="query dialog"
__author__="oddtopus"
__url__="github.com/oddtopus/flamingo"
__license__="LGPL 3"

from PySide import QtGui, QtCore
import FreeCAD,FreeCADGui
 
# UI Class definitions
 
class QueryForm(QtGui.QDialog): #QWidget):
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
          if sub.curvatureAt(0)==0:
            self.labSubObj.setText(sub.ShapeType+':\tL = %.1f mm' %sub.Length)
          else:
            x,y,z=sub.centerOfCurvatureAt(0)
            d=2/sub.curvatureAt(0)
            self.labSubObj.setText(sub.ShapeType+':\tD = %.1f mm\n\tC = %.1f,%.1f,%.1f' %(d,x,y,z))
        elif sub.ShapeType=='Face':
          self.labSubObj.setText(sub.ShapeType+':\tA = %.1f mm2' %sub.Area)
        elif sub.ShapeType=='Vertex':
          self.labSubObj.setText(sub.ShapeType+': pos = (%(x).1f,%(y).1f,%(z).1f)' %{'x':sub.X,'y':sub.Y,'z':sub.Z})
      elif len(shapes)>1:
        self.labSubObj.setText(shapes[0].ShapeType+' to '+shapes[1].ShapeType+': distance = %.1f mm' %(shapes[0].distToShape(shapes[1])[0]))
      else:
        self.labSubObj.setText(' ')
      if len(frameCmd.beams())==1:
        b=frameCmd.beams()[0]
        self.labBeam.setText(b.Label+":\tL=%.2f"%(b.Height))
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

from PySide.QtCore import *
from PySide.QtGui import *
from os import listdir
from os.path import join, dirname, abspath

class rotWPForm(QDialog): #QWidget):
  '''
  Dialog to rotate the working plane about its axis.
  '''
  def __init__(self,winTitle='Rotate WP', icon='rotWP.svg'):
    super(rotWPForm,self).__init__()
    self.move(QPoint(100,250))
    self.setWindowFlags(Qt.WindowStaysOnTopHint)
    self.setWindowTitle(winTitle)
    iconPath=join(dirname(abspath(__file__)),"icons",icon)
    from PySide.QtGui import QIcon
    Icon=QIcon()
    Icon.addFile(iconPath)
    self.setWindowIcon(Icon) 
    self.grid=QGridLayout()
    self.setLayout(self.grid)
    self.radioX=QRadioButton('X')
    self.radioX.setChecked(True)
    self.radioY=QRadioButton('Y')
    self.radioZ=QRadioButton('Z')
    self.lab1=QLabel('Angle:')
    self.edit1=QLineEdit('45')
    self.edit1.setAlignment(Qt.AlignCenter)
    self.edit1.setValidator(QDoubleValidator())
    self.btn1=QPushButton('Rotate working plane')
    self.btn1.clicked.connect(self.rotate)
    self.grid.addWidget(self.radioX,0,0,1,1,Qt.AlignCenter)
    self.grid.addWidget(self.radioY,0,1,1,1,Qt.AlignCenter)
    self.grid.addWidget(self.radioZ,0,2,1,1,Qt.AlignCenter)
    self.grid.addWidget(self.lab1,1,0,1,1)
    self.grid.addWidget(self.edit1,1,1,1,2)
    self.grid.addWidget(self.btn1,2,0,1,3,Qt.AlignCenter)
    self.show()
    self.sg=FreeCADGui.ActiveDocument.ActiveView.getSceneGraph()
    s=FreeCAD.ParamGet("User parameter:BaseApp/Preferences/Mod/Draft").GetInt("gridSize")
    sc=[float(x*s) for x in [1,1,.2]]
    from polarUtilsCmd import arrow
    self.arrow =arrow(FreeCAD.DraftWorkingPlane.getPlacement(),scale=sc,offset=s)
  def rotate(self):
    if self.radioX.isChecked():
      ax=FreeCAD.Vector(1,0,0)
    elif self.radioY.isChecked():
      ax=FreeCAD.Vector(0,1,0)
    else:
      ax=FreeCAD.Vector(0,0,1)
    ang=float(self.edit1.text())
    import polarUtilsCmd as puc
    newpl=puc.rotWP(ax,ang)
    self.arrow.moveto(newpl)
  def closeEvent(self,event):
    self.sg.removeChild(self.arrow.node)
  def reject(self):
    self.sg.removeChild(self.arrow.node)
    self.close()
  def accept(self):
    self.rotate()
