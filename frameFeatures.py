#(c) 2016 R. T. LGPL: part of Flamingo tools w.b. for FreeCAD

__title__="frameTools objects"
__author__="oddtopus"
__url__="github.com/oddtopus/flamingo"
__license__="LGPL 3"

import FreeCAD, FreeCADGui, Part
from PySide.QtCore import *
from PySide.QtGui import *
from os import listdir
from os.path import join, dirname, abspath

################ DIALOGS #############################

class frameLineForm(QWidget):
  '''
  prototype dialog for insert frameFeatures
  '''
  def __init__(self,winTitle='FrameLine Manager', icon='frameline.svg'):
    super(frameLineForm,self).__init__()
    self.move(QPoint(100,250))
    self.setWindowFlags(Qt.WindowStaysOnTopHint)
    self.setWindowTitle(winTitle)
    from PySide.QtGui import QIcon
    Icon=QIcon()
    iconPath=join(dirname(abspath(__file__)),"icons",icon)
    Icon.addFile(iconPath)
    self.setWindowIcon(Icon) 
    self.mainHL=QHBoxLayout()
    self.setLayout(self.mainHL)
    self.firstCol=QWidget()
    self.firstCol.setLayout(QVBoxLayout())
    self.lab1=QLabel('  Profiles:')
    self.firstCol.layout().addWidget(self.lab1)
    self.sectList=QListWidget()
    self.sectList.setMaximumWidth(120)
    self.updateSections()
    self.firstCol.layout().addWidget(self.sectList)
    self.radio1=QRadioButton()
    self.radio1.setChecked(True)
    self.radios=QWidget()
    self.radios.setLayout(QFormLayout())
    self.radios.layout().setAlignment(Qt.AlignHCenter)
    self.radios.layout().addRow('Copy profile ',self.radio1)
    self.firstCol.layout().addWidget(self.radios)
    self.mainHL.addWidget(self.firstCol)
    self.secondCol=QWidget()
    self.secondCol.setLayout(QVBoxLayout())
    self.combo=QComboBox()
    self.combo.addItem('<new>')
    self.combo.activated[str].connect(self.setCurrent)
    try:
      self.combo.addItems([o.Label for o in FreeCAD.activeDocument().Objects if hasattr(o,'FType') and o.FType=='FrameLine'])
    except:
      None
    self.combo.setMaximumWidth(100)
    if FreeCAD.__activeFrameLine__ and FreeCAD.__activeFrameLine__ in [self.combo.itemText(i) for i in range(self.combo.count())]:
      self.combo.setCurrentIndex(self.combo.findText(FreeCAD.__activeFrameLine__))
    self.combo.currentIndexChanged.connect(self.setCurrentFL)
    self.secondCol.layout().addWidget(self.combo)
    self.btn0=QPushButton('Insert')
    self.btn0.setMaximumWidth(100)
    self.secondCol.layout().addWidget(self.btn0)
    self.btn0.clicked.connect(self.insert)
    self.edit1=QLineEdit('<name>')
    self.edit1.setAlignment(Qt.AlignHCenter)
    self.edit1.setMaximumWidth(100)
    self.secondCol.layout().addWidget(self.edit1)
    self.btn1=QPushButton('Redraw')
    self.btn1.clicked.connect(self.redraw)
    self.btn1.setMaximumWidth(100)
    self.secondCol.layout().addWidget(self.btn1)
    self.btn2=QPushButton('Get Path')
    self.btn2.clicked.connect(self.getPath)
    self.btn2.setMaximumWidth(100)
    self.secondCol.layout().addWidget(self.btn2)
    self.btn3=QPushButton('Get Profile')
    self.btn3.clicked.connect(self.getProfile)
    self.btn3.setMaximumWidth(100)
    self.secondCol.layout().addWidget(self.btn3)
    self.btn4=QPushButton('Clear')
    self.btn4.clicked.connect(self.clear)
    self.btn4.setMaximumWidth(100)
    self.secondCol.layout().addWidget(self.btn4)
    self.mainHL.addWidget(self.secondCol)
    self.show()
    self.current=None
  def setCurrentFL(self,FLName=None):
    if self.combo.currentText() not in ['<none>','<new>']:
      FreeCAD.__activeFrameLine__= self.combo.currentText()
    else:
      FreeCAD.__activeFrameLine__=None
  def updateSections(self):
    self.sectList.clear()
    self.sectList.addItems([o.Label for o in FreeCAD.ActiveDocument.Objects if hasattr(o,'Shape') and ((type(o.Shape)==Part.Wire and o.Shape.isClosed()) or (type(o.Shape)==Part.Face and type(o.Shape.Surface)==Part.Plane))])
  def setCurrent(self,flname):
    if flname!='<new>':
      self.current=FreeCAD.ActiveDocument.getObjectsByLabel(flname)[0]
      FreeCAD.Console.PrintMessage('current FrameLine = '+self.current.Label+'\n')
    else:
      self.current=None
      FreeCAD.Console.PrintMessage('current FrameLine = None\n')
    return
  def insert(self):
    from frameCmd import makeFrameLine
    if self.combo.currentText()=='<new>':
      n=self.edit1.text()
      if n and n!='<name>':
        a=makeFrameLine(name=n)
      else:
        a=makeFrameLine()
      self.combo.addItem(a.Label)
  def redraw(self):
    if self.current and self.current.Profile and self.current.Base:
      if self.radio1.isChecked():
        self.current.Proxy.update(self.current)
      else:
        self.current.Proxy.update(self.current, copyProfile=False)
      self.updateSections()
    else:
      FreeCAD.Console.PrintError('Select a Path and a Profile before\n')
  def clear(self):
    if self.current:
      self.current.Proxy.purge(self.current)
      self.updateSections()
  def getPath(self):
    if self.current:
      sel=FreeCADGui.Selection.getSelection()
      if sel:
        base=sel[0]
        if base.TypeId in ['Part::Part2DObjectPython','Sketcher::SketchObject']:
          self.current.Base=base
        else:
          FreeCAD.Console.PrintError('Not a Wire nor Sketch\n')
  def getProfile(self):
    if self.current:
      from frameCmd import beams
      if beams():
        self.current.Profile=beams()[0].Base
      elif self.sectList.selectedItems():
        prof= FreeCAD.ActiveDocument.getObjectsByLabel(self.sectList.selectedItems()[0].text())[0]
        prof.Placement.Base=FreeCAD.Vector()
        self.current.Profile=prof
    
################ CLASSES ###########################

class FrameLine(object):
  '''Class for object FrameLine
  Has attributes Base and Beam to define the frame shape and the type of
  Structure object.
  Creates a group to collect the Structure objects.
  Provides methods update() and purge() to redraw the Structure objects
  when the Base is modified.
  '''
  def __init__(self, obj, section="IPE200", lab=None):
    obj.Proxy = self
    obj.addProperty("App::PropertyString","FType","FrameLine","Type of frameFeature").FType='FrameLine'
    obj.addProperty("App::PropertyString","FSize","FrameLine","Size of frame").FSize=section
    if lab:
      obj.Label=lab
    obj.addProperty("App::PropertyString","Group","FrameLine","The group.").Group=obj.Label+"_pieces"
    group=FreeCAD.activeDocument().addObject("App::DocumentObjectGroup",obj.Group)
    group.addObject(obj)
    FreeCAD.Console.PrintWarning("Created group "+obj.Group+"\n")
    obj.addProperty("App::PropertyLink","Base","FrameLine","the edges")
    obj.addProperty("App::PropertyLink","Profile","FrameLine","the profile")
  def onChanged(self, fp, prop):
    if prop=='Label' and len(fp.InList):
      fp.InList[0].Label=fp.Label+"_pieces"
      fp.Group=fp.Label+"_pieces"
    if prop=='Base' and fp.Base:
      FreeCAD.Console.PrintWarning(fp.Label+' Base has changed to '+fp.Base.Label+'\n')
    if prop=='Profile' and fp.Profile:
      fp.Profile.ViewObject.Visibility=False
      #fp.Profile.Placement.Base=FreeCAD.Vector(0,0,0) 
      FreeCAD.Console.PrintWarning(fp.Label+' Profile has changed to '+fp.Profile.Label+'\n')
  def purge(self,fp):
    group=FreeCAD.activeDocument().getObjectsByLabel(fp.Group)[0]
    from frameCmd import beams
    beams2purge=beams(group.OutList)
    if beams2purge:
      for b in beams2purge:
        profiles=b.OutList
        FreeCAD.ActiveDocument.removeObject(b.Name)
        for p in profiles:
          FreeCAD.ActiveDocument.removeObject(p.Name)
  def update(self,fp,copyProfile=True):
    import frameCmd, pipeCmd
    if hasattr(fp.Base,'Shape'):
      edges=fp.Base.Shape.Edges
      if not edges:
        FreeCAD.Console.PrintError('Base has not valid edges\n')
        return
    group=FreeCAD.activeDocument().getObjectsByLabel(fp.Group)[0]
    if fp.Profile:
      FreeCAD.activeDocument().openTransaction('Update frameLine')
      from Arch import makeStructure
      for e in edges:
        if copyProfile:
          p=FreeCAD.activeDocument().copyObject(fp.Profile,True)
        else:
          p=fp.Profile
        beam=makeStructure(p)
        frameCmd.placeTheBeam(beam,e)
        pipeCmd.moveToPyLi(beam,fp.Name)
      FreeCAD.activeDocument().commitTransaction()
    FreeCAD.activeDocument().recompute()
  def execute(self, fp):
    return None

#s = Arch.makeStructure(length=100.0,width=100.0,height=1000.0)
# p = Arch.makeProfile([219, 'UPE', 'UPE100', 'U', 100.0, 55.0, 4.5, 7.5])
# s = Arch.makeStructure(p,height=1000.0)
# s.Profile = "UPE100"
#   Arch.makeStructure(FreeCAD.ActiveDocument.DWire001)
