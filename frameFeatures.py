#(c) 2016 R. T. LGPL: part of Flamingo tools w.b. for FreeCAD

__title__="frameTools objects"
__author__="oddtopus"
__url__="github.com/oddtopus/flamingo"
__license__="LGPL 3"

import FreeCAD, FreeCADGui, Part, csv
import ArchProfile
from Arch import makeStructure
from PySide.QtCore import *
from PySide.QtGui import *
from os import listdir
from os.path import join, dirname, abspath

################ DIALOGS #############################

class frameLineForm(QWidget):
  '''
  Dialog for frameFeatures management.
  From this you can:
  - insert a new Frameline object in the model,
  - select its profile,
  - select its path,
  - redraw it,
  - clear it.
  To select profiles, the 2D objects msut be included insied the "Profiles_set"
  group, either created manually or automatically by "Insert Std. Section" 
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
    self.cb1=QCheckBox(' Copy profile')
    self.cb1.setChecked(True)
    self.cb2=QCheckBox(' Move to origin')
    self.cb2.setChecked(True)
    self.radios=QWidget()
    self.radios.setLayout(QFormLayout())
    self.radios.layout().setAlignment(Qt.AlignHCenter)
    self.radios.layout().addRow(self.cb1)
    self.radios.layout().addRow(self.cb2)
    self.firstCol.layout().addWidget(self.radios)
    self.mainHL.addWidget(self.firstCol)
    self.secondCol=QWidget()
    self.secondCol.setLayout(QVBoxLayout())
    self.current=None    
    self.combo=QComboBox()
    self.combo.addItem('<new>')
    #self.combo.activated[str].connect(self.setCurrent)
    try:
      self.combo.addItems([o.Label for o in FreeCAD.activeDocument().Objects if hasattr(o,'FType') and o.FType=='FrameLine'])
    except:
      None
    self.combo.setMaximumWidth(100)
    self.combo.currentIndexChanged.connect(self.setCurrentFL)
    if FreeCAD.__activeFrameLine__ and FreeCAD.__activeFrameLine__ in [self.combo.itemText(i) for i in range(self.combo.count())]:
      self.combo.setCurrentIndex(self.combo.findText(FreeCAD.__activeFrameLine__))
    self.secondCol.layout().addWidget(self.combo)
    self.btn0=QPushButton('Insert')
    self.btn0.setMaximumWidth(100)
    self.secondCol.layout().addWidget(self.btn0)
    self.btn0.clicked.connect(self.insert)
    self.edit1=QLineEdit()
    self.edit1.setPlaceholderText('<name>')
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
  def setCurrentFL(self,FLName=None):
    if self.combo.currentText() not in ['<none>','<new>']:
      FreeCAD.__activeFrameLine__= self.combo.currentText()
      self.current=FreeCAD.ActiveDocument.getObjectsByLabel(self.combo.currentText())[0]
      FreeCAD.Console.PrintMessage('current FrameLine = '+self.current.Label+'\n')
      if self.current.Profile:
        FreeCAD.Console.PrintMessage('Profile: %s\n'%self.current.Profile.Label)
      else:
        FreeCAD.Console.PrintMessage('Profile not defined\n')
      if self.current.Base:
        FreeCAD.Console.PrintMessage('Path: %s\n'%self.current.Base.Label)
      else:
        FreeCAD.Console.PrintMessage('Path not defined\n')
    else:
      FreeCAD.__activeFrameLine__=None
      self.current=None
      FreeCAD.Console.PrintMessage('current FrameLine = None\n')
  def updateSections(self):
    self.sectList.clear()
    result=FreeCAD.ActiveDocument.findObjects("App::DocumentObjectGroup","Profiles_set")
    if result:
      self.sectList.addItems([o.Label for o in result[0].OutList if hasattr(o,'Shape') and ((type(o.Shape)==Part.Wire and o.Shape.isClosed()) or (type(o.Shape)==Part.Face and type(o.Shape.Surface)==Part.Plane))])
      if self.sectList.count():
        self.sectList.setCurrentRow(0)
    else:
      FreeCAD.Console.PrintError('No set of profiles in this document.\nCreate the sections first.\n')
  def setCurrent(self,flname):
    if flname!='<new>':
      self.current=FreeCAD.ActiveDocument.getObjectsByLabel(flname)[0]
      FreeCAD.Console.PrintMessage('current FrameLine = '+self.current.Label+'\n')
    else:
      self.current=None
      FreeCAD.Console.PrintMessage('current FrameLine = None\n')
  def insert(self):
    from frameCmd import makeFrameLine, edges, placeTheBeam
    from pipeCmd import moveToPyLi
    if self.combo.currentText()=='<new>':
      n=self.edit1.text()
      if n:
        a=makeFrameLine(name=n)
      else:
        a=makeFrameLine()
      self.combo.addItem(a.Label)
      self.combo.setCurrentIndex(self.combo.count()-1)
      if self.sectList.selectedItems():
        self.getProfile()
    elif self.sectList.selectedItems():
      prof= FreeCAD.ActiveDocument.getObjectsByLabel(self.sectList.selectedItems()[0].text())[0]
      for e in edges():
        if self.cb1.isChecked():
          s=makeStructure(FreeCAD.ActiveDocument.copyObject(prof))
        else:
          s=makeStructure(prof)
        placeTheBeam(s,e)
        moveToPyLi(s,self.current.Name)
      FreeCAD.ActiveDocument.recompute()
  def redraw(self):
    if self.current and self.current.Profile and self.current.Base:
      if self.cb1.isChecked():
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
          FreeCAD.Console.PrintWarning(self.current.Label+' base set to '+base.TypeId.split('::')[1]+'.\n')
        else:
          FreeCAD.Console.PrintError('Not a Wire nor Sketch\n')
      else:
        self.current.Base=None
        FreeCAD.Console.PrintWarning(self.current.Label+' base set to None.\n')
  def getProfile(self):
    if self.current:
      from frameCmd import beams
      if beams():
        self.current.Profile=beams()[0].Base
      elif self.sectList.selectedItems():
        prof= FreeCAD.ActiveDocument.getObjectsByLabel(self.sectList.selectedItems()[0].text())[0]
        if prof.Shape.ShapeType=='Wire' and self.cb2.isChecked():
          prof.Placement.move(FreeCAD.Vector(0,0,0)-prof.Shape.CenterOfMass)
        prof.Placement.Rotation=FreeCAD.Base.Rotation()
        self.current.Profile=prof

class insertSectForm(QWidget):
  ''' dialog for Arch.makeProfile
  This allows to create in the model the 2D profiles to be used
  for beams objects.
  It creates a group named "Profiles_set where the 2D objects are
  conveniently gathered and retrieved by the Frameline Manager.
  NOTE: It's also possible to create customized 2D profiles and drag-and-drop
  them inside this group."
  '''
  def __init__(self,winTitle='Insert section', icon='flamingo.svg'):
    '''
    __init__(self,winTitle='Title')
    '''
    super(insertSectForm,self).__init__()
    self.move(QPoint(100,250))
    self.setWindowFlags(Qt.WindowStaysOnTopHint)
    self.setWindowTitle(winTitle)
    iconPath=join(dirname(abspath(__file__)),"icons",icon)
    from PySide.QtGui import QIcon
    Icon=QIcon()
    Icon.addFile(iconPath)
    self.setWindowIcon(Icon) 
    self.mainHL=QHBoxLayout()
    self.setLayout(self.mainHL)
    self.firstCol=QWidget()
    self.firstCol.setLayout(QVBoxLayout())
    self.mainHL.addWidget(self.firstCol)
    self.SType='IPE'
    self.currentRatingLab=QLabel('Section: '+self.SType)
    self.firstCol.layout().addWidget(self.currentRatingLab)
    self.sizeList=QListWidget()
    self.sizeList.setMaximumWidth(120)
    self.firstCol.layout().addWidget(self.sizeList)
    self.sectDictList=[]
    self.fileList=listdir(join(dirname(abspath(__file__)),"tables"))
    self.fillSizes()
    self.PRatingsList=[s.lstrip("Section_").rstrip(".csv") for s in self.fileList if s.startswith("Section")]
    self.secondCol=QWidget()
    self.secondCol.setLayout(QVBoxLayout())
    self.lab1=QLabel('Section types:')
    self.secondCol.layout().addWidget(self.lab1)
    self.ratingList=QListWidget()
    self.ratingList.setMaximumWidth(100)
    self.ratingList.addItems(self.PRatingsList)
    self.ratingList.itemClicked.connect(self.changeRating)
    self.ratingList.setCurrentRow(0)
    self.secondCol.layout().addWidget(self.ratingList)
    self.btn1=QPushButton('Insert')
    self.btn1.setMaximumWidth(100)
    self.btn1.clicked.connect(self.insert)
    self.secondCol.layout().addWidget(self.btn1)
    self.mainHL.addWidget(self.secondCol)
    self.show()
  def fillSizes(self):
    self.sizeList.clear()
    for fileName in self.fileList:
      if fileName=='Section_'+self.SType+'.csv':
        f=open(join(dirname(abspath(__file__)),"tables",fileName),'r')
        reader=csv.DictReader(f,delimiter=';')
        self.sectDictList=[x for x in reader]
        f.close()
        for row in self.sectDictList:
          s=row['SSize']
          self.sizeList.addItem(s)
  def changeRating(self,item):
    self.SType=item.text()
    self.currentRatingLab.setText('Section: '+self.SType)
    self.fillSizes()
  def insert(self):      # insert the section
    result=FreeCAD.ActiveDocument.findObjects("App::DocumentObjectGroup","Profiles_set")
    if result:
      group= result[0]
    else:
      group=FreeCAD.activeDocument().addObject("App::DocumentObjectGroup","Profiles_set")
    if self.sizeList.selectedItems():
      prop=self.sectDictList[self.sizeList.currentRow()]
      if prop['stype']=='C':
        from Draft import makeCircle
        s=makeCircle(float(prop['H']))
      else:
        s=ArchProfile.makeProfile([0,'SECTION',prop['SSize']+'-000',prop['stype'],float(prop['W']),float(prop['H']),float(prop['ta']),float(prop['tf'])])
      group.addObject(s)
    FreeCAD.activeDocument().recompute()

    
################ CLASSES ###########################

class FrameLine(object):
  '''Class for object FrameLine
  Has attributes Base (the path) and Profile to define the frame shape and 
  the type section's profile.
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

    
