#(c) 2016 R. T. LGPL: part of Flamingo tools w.b. for FreeCAD

__title__="frameTools objects"
__author__="oddtopus"
__url__="github.com/oddtopus/flamingo"
__license__="LGPL 3"

import FreeCAD, FreeCADGui
from PySide.QtCore import *
from PySide.QtGui import *
from os import listdir
from os.path import join, dirname, abspath

################ DIALOGS #############################

class frameLineForm(QWidget):
  '''
  prototype dialog for insert frameFeatures
  '''
  def __init__(self,winTitle='Title', icon='flamingo.svg'):
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
    self.sectList=QListWidget()
    self.sectList.setMaximumWidth(120)
    self.firstCol.layout().addWidget(self.sectList)
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
    #if FreeCAD.__activeFrameLine__ and FreeCAD.__activeFrameLine__ in [self.combo.itemText(i) for i in range(self.combo.count())]:
    #  self.combo.setCurrentIndex(self.combo.findText(FreeCAD.__activeFrameLine__))
    self.secondCol.layout().addWidget(self.combo)
    self.btn0=QPushButton('Insert')
    self.btn0.setMaximumWidth(100)
    self.secondCol.layout().addWidget(self.btn0)
    self.btn0.clicked.connect(self.insert)
    self.btn1=QPushButton('Update')
    self.btn1.clicked.connect(self.update)
    self.btn1.setMaximumWidth(100)
    self.secondCol.layout().addWidget(self.btn1)
    self.btn2=QPushButton('Get Base')
    self.btn2.clicked.connect(self.getBase)
    self.btn2.setMaximumWidth(100)
    self.secondCol.layout().addWidget(self.btn2)
    self.btn3=QPushButton('Get Beam')
    self.btn3.clicked.connect(self.getBeam)
    self.btn3.setMaximumWidth(100)
    self.secondCol.layout().addWidget(self.btn3)
    self.btn4=QPushButton('Purge')
    self.btn4.clicked.connect(self.purge)
    self.btn4.setMaximumWidth(100)
    self.secondCol.layout().addWidget(self.btn4)
    self.mainHL.addWidget(self.secondCol)
    self.show()
    self.current=None
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
      a=makeFrameLine()
      self.combo.addItem(a.Label)
    #s = Arch.makeStructure(length=100.0,width=100.0,height=1000.0)
    # p = Arch.makeProfile([219, 'UPE', 'UPE100', 'U', 100.0, 55.0, 4.5, 7.5])
    # s = Arch.makeStructure(p,height=1000.0)
    # s.Profile = "UPE100"
    #   Arch.makeStructure(FreeCAD.ActiveDocument.DWire001)
  def update(self):
    if self.current:
      self.current.Proxy.update(self.current)
  def purge(self):
    if self.current:
      self.current.Proxy.purge(self.current)
  def getBase(self):
    if self.current:
      sel=FreeCADGui.Selection.getSelection()
      from Part import Wire
      from Sketcher import Sketch
      if sel:
        base=sel[0]
        if type(base.Shape) in [Wire,Sketch]:
          self.current.Base=base
        else:
          FreeCAD.Console.PrintError('Not a Wire nor Sketch\n')
  def getBeam(self):
    if self.current:
      from frameCmd import beams
      if beams():
        self.current.Beam=beams()[0]
        FreeCAD.Console.PrintMessage('beam type for '+self.current.Label+' = '+self.current.Beam.Label+'\n')
    
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
    obj.addProperty("App::PropertyLink","Beam","FrameLine","the beam")
  def onChanged(self, fp, prop):
    if prop=='Label' and len(fp.InList):
      fp.InList[0].Label=fp.Label+"_pieces"
      fp.Group=fp.Label+"_pieces"
    if hasattr(fp,'Base') and prop=='Base' and fp.Base:
      FreeCAD.Console.PrintWarning(fp.Label+' Base has changed to '+fp.Base.Label+'\n')
  def purge(self,fp):
    group=FreeCAD.activeDocument().getObjectsByLabel(fp.Group)[0]
    from frameCmd import beams
    beams2purge=beams(group.OutList)
    if beams2purge:
      for b in beams2purge:
        FreeCAD.ActiveDocument.removeObject(b.Name)
  def update(self,fp):
    import frameCmd, pipeCmd
    if hasattr(fp.Base,'Shape'):
      edges=fp.Base.Shape.Edges
      if not edges:
        FreeCAD.Console.PrintError('Base has not valid edges\n')
        return
    group=FreeCAD.activeDocument().getObjectsByLabel(fp.Group)[0]
    if fp.Beam and fp.Base:
      FreeCAD.activeDocument().openTransaction('Update frameLine')
      for e in edges:
        beam=FreeCAD.activeDocument().copyObject(fp.Beam,True)
        frameCmd.placeTheBeam(beam,e)
        pipeCmd.moveToPyLi(beam,fp.Name)
      FreeCAD.activeDocument().recompute()
      FreeCAD.activeDocument().commitTransaction()
  def execute(self, fp):
    return None
