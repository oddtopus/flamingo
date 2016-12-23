#(c) 2016 R. T. LGPL: part of Flamingo tools w.b. for FreeCAD

__title__="pypeTools dialogs"
__author__="oddtopus"
__url__="github.com/oddtopus/flamingo"
__license__="LGPL 3"

import FreeCAD,FreeCADGui,Part, csv
import frameCmd, pipeCmd
from frameForms import prototypeForm
from os import listdir
from os.path import join, dirname, abspath
from PySide.QtCore import *
from PySide.QtGui import *
from math import degrees
from DraftVecUtils import rounded

class protopypeForm(QWidget):
  'prototype dialog for insert pipeFeatures'
  def __init__(self,winTitle='Title', PType='Pipe', PRating='SCH-STD', icon='flamingo.svg'):
    '''
    __init__(self,winTitle='Title', PType='Pipe', PRating='SCH-STD')
      winTitle: the window's title
      PType: the pipeFeature type
      PRating: the pipeFeature pressure rating class
    It lookups in the directory ./tables the file PType+"_"+PRating+".csv",
    imports it's content in a list of dictionaries -> .pipeDictList and
    shows a summary in the QListWidget -> .sizeList
    Also create a property -> PRatingsList with the list of available PRatings for the 
    selected PType.   
    '''
    super(protopypeForm,self).__init__()
    self.move(QPoint(100,250))
    self.PType=PType
    self.PRating=PRating
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
    self.currentRatingLab=QLabel(self.PRating+':')
    self.firstCol.layout().addWidget(self.currentRatingLab)
    self.sizeList=QListWidget()
    self.sizeList.setMaximumWidth(120)
    self.firstCol.layout().addWidget(self.sizeList)
    self.pipeDictList=[]
    self.fileList=listdir(join(dirname(abspath(__file__)),"tables"))
    self.fillSizes()
    self.PRatingsList=[s.lstrip(PType+"_").rstrip(".csv") for s in self.fileList if s.startswith(PType)]
    self.secondCol=QWidget()
    self.secondCol.setLayout(QVBoxLayout())
    self.combo=QComboBox()
    self.combo.addItem('<none>')
    try:
      self.combo.addItems([o.Label for o in FreeCAD.activeDocument().Objects if hasattr(o,'PType') and o.PType=='PypeLine'])
    except:
      None
    self.combo.setMaximumWidth(100)
    self.secondCol.layout().addWidget(self.combo)
    self.ratingList=QListWidget()
    self.ratingList.setMaximumWidth(100)
    self.ratingList.addItems(self.PRatingsList)
    self.ratingList.itemClicked.connect(self.changeRating)
    self.ratingList.setCurrentRow(0)
    self.ratingList.setMaximumHeight(100)
    self.secondCol.layout().addWidget(self.ratingList)
    self.btn1=QPushButton('Insert')
    self.btn1.setMaximumWidth(100)
    self.secondCol.layout().addWidget(self.btn1)
    self.mainHL.addWidget(self.secondCol)
    self.combo.currentIndexChanged.connect(self.setCurrentPL)
    self.currentPL=None
  def setCurrentPL(self):
    if self.combo.currentText() not in ['<none>','<new>']:
      self.currentPL=FreeCAD.ActiveDocument.getObjectsByLabel(self.combo.currentText())[0]
    else:
      self.current=None
  def fillSizes(self):
    self.sizeList.clear()
    for fileName in self.fileList:
      if fileName==self.PType+'_'+self.PRating+'.csv':
        f=open(join(dirname(abspath(__file__)),"tables",fileName),'r')
        reader=csv.DictReader(f,delimiter=';')
        self.pipeDictList=[DNx for DNx in reader]
        f.close()
        for row in self.pipeDictList:
          s=row['PSize']
          if row.has_key('OD'):
            s+=" - "+row['OD']
          if row.has_key('thk'):
            s+="x"+row['thk']
          self.sizeList.addItem(s)
        break
  def changeRating(self,item):
    self.PRating=item.text()
    self.currentRatingLab.setText(self.PRating+':')
    self.fillSizes()
  def findDN(self,DN):
    result=None
    for row in self.pipeDictList:
      if row['PSize']==DN:
        result=row
        break
    return result
    
class insertPipeForm(protopypeForm):
  '''
  Dialog to insert tubes.
  For position and orientation you can select
    - one or more straight edges (centerlines)
    - one or more curved edges (axis and origin across the center)
    - one or more vertexes 
    - nothing 
  Default length = 200 mm.
  Available one button to reverse the orientation of the last or selected tubes.
  '''
  def __init__(self):
    super(insertPipeForm,self).__init__("Insert pipes","Pipe","SCH-STD","pipe.svg")
    self.sizeList.setCurrentRow(0)
    self.ratingList.setCurrentRow(0)
    self.btn1.clicked.connect(self.insert)
    self.edit1=QLineEdit(' <insert lenght>')
    self.edit1.setAlignment(Qt.AlignHCenter)
    self.edit1.setMaximumWidth(100)
    self.secondCol.layout().addWidget(self.edit1)
    self.btn2=QPushButton('Reverse')
    self.btn2.setMaximumWidth(100)
    self.secondCol.layout().addWidget(self.btn2)
    self.btn2.clicked.connect(self.reverse) #lambda: pipeCmd.rotateTheTubeAx(self.lastPipe,FreeCAD.Vector(1,0,0),180))
    self.btn3=QPushButton('Apply')
    self.btn3.setMaximumWidth(100)
    self.secondCol.layout().addWidget(self.btn3)
    self.btn3.clicked.connect(self.apply)
    self.btn1.setDefault(True)
    self.btn1.setFocus()
    self.show()
    self.lastPipe=None
  def reverse(self):     # revert orientation of selected or last inserted pipe
    selPipes=[p for p in FreeCADGui.Selection.getSelection() if hasattr(p,'PType') and p.PType=='Pipe']
    if len(selPipes):
      for p in selPipes:
        pipeCmd.rotateTheTubeAx(p,FreeCAD.Vector(1,0,0),180)
    else:
      pipeCmd.rotateTheTubeAx(self.lastPipe,FreeCAD.Vector(1,0,0),180)
  def insert(self):      # insert the pipe
    d=self.pipeDictList[self.sizeList.currentRow()]
    FreeCAD.activeDocument().openTransaction('Insert pipe')
    try:
      H=float(self.edit1.text())
    except:
      H=200
    if len(frameCmd.edges())==0:
      propList=[d['PSize'],float(d['OD']),float(d['thk']),H]
      vs=[v for sx in FreeCADGui.Selection.getSelectionEx() for so in sx.SubObjects for v in so.Vertexes]
      if len(vs)==0:
        self.lastPipe=pipeCmd.makePipe(propList)
        if self.combo.currentText()!='<none>':
          pipeCmd.moveToPyLi(self.lastPipe,self.combo.currentText())
      else:
        for v in vs:
          self.lastPipe=pipeCmd.makePipe(propList,v.Point)
        if self.combo.currentText()!='<none>':
          pipeCmd.moveToPyLi(self.lastPipe,self.combo.currentText())
    else:
      for edge in frameCmd.edges():
        if edge.curvatureAt(0)==0:
          propList=[d['PSize'],float(d['OD']),float(d['thk']),edge.Length]
          self.lastPipe=pipeCmd.makePipe(propList,edge.valueAt(0),edge.tangentAt(0))
        else:
          objs=[o for o in FreeCADGui.Selection.getSelection() if hasattr(o,'PSize') and hasattr(o,'OD') and hasattr(o,'thk')]
          if len(objs)>0:
            propList=[objs[0].PSize,objs[0].OD,objs[0].thk,H]
          else:
            propList=[d['PSize'],float(d['OD']),float(d['thk']),H]
          self.lastPipe=pipeCmd.makePipe(propList,edge.centerOfCurvatureAt(0),edge.tangentAt(0).cross(edge.normalAt(0)))
        if self.combo.currentText()!='<none>':
          pipeCmd.moveToPyLi(self.lastPipe,self.combo.currentText())
    FreeCAD.activeDocument().commitTransaction()
    FreeCAD.activeDocument().recompute()
  def apply(self):
    for obj in FreeCADGui.Selection.getSelection():
      d=self.pipeDictList[self.sizeList.currentRow()]
      if hasattr(obj,'PType') and obj.PType==self.PType:
        #for k in d.keys():
        #  obj.setExpression(k,d[k])
        obj.PSize=d['PSize']
        obj.OD=d['OD']
        obj.thk=d['thk']
        obj.PRating=self.PRating
        FreeCAD.activeDocument().recompute()

class insertElbowForm(protopypeForm):
  '''
  Dialog to insert one elbow.
  For position and orientation you can select
    - one vertex, 
    - one circular edge 
    - a pair of edges or pipes or beams
    - one pipe at one of its ends
    - nothing.
  In case one pipe is selected, its properties are applied to the elbow and 
  the tube or tubes are trimmed or extended automatically.
  Also available one button to trim/extend one selected pipe to the selected 
  edges, if necessary.
  '''
  def __init__(self):
    super(insertElbowForm,self).__init__("Insert elbows","Elbow","SCH-STD","elbow.svg")
    self.sizeList.setCurrentRow(0)
    self.ratingList.setCurrentRow(0)
    self.btn1.clicked.connect(self.insert)
    self.edit1=QLineEdit('<insert angle>')
    self.edit1.setAlignment(Qt.AlignHCenter)
    self.edit1.setMaximumWidth(100)
    self.secondCol.layout().addWidget(self.edit1)
    self.btn2=QPushButton('Trim/Extend')
    self.btn2.clicked.connect(self.trim)
    self.btn2.setMaximumWidth(100)
    self.secondCol.layout().addWidget(self.btn2)
    self.btn3=QPushButton('Apply')
    self.btn3.setMaximumWidth(100)
    self.secondCol.layout().addWidget(self.btn3)
    self.btn3.clicked.connect(self.apply)
    self.btn1.setDefault(True)
    self.btn1.setFocus()
    self.show()
    self.lastElbow=None
  def insert(self):    # insert the curve
    DN=OD=thk=PRating=None
    d=self.pipeDictList[self.sizeList.currentRow()]
    try:
      if float(self.edit1.text())>=180:
        self.edit1.setText("179")
      ang=float(self.edit1.text())
    except:
      ang=float(d['BendAngle'])
    selex=FreeCADGui.Selection.getSelectionEx()
    if len(selex)==0:     # no selection -> insert one elbow at origin
      propList=[d['PSize'],float(d['OD']),float(d['thk']),ang,float(d['BendRadius'])]
      FreeCAD.activeDocument().openTransaction('Insert elbow in (0,0,0)')
      self.lastElbow=pipeCmd.makeElbow(propList)
      if self.combo.currentText()!='<none>':
        pipeCmd.moveToPyLi(self.lastElbow,self.combo.currentText())
      FreeCAD.activeDocument().commitTransaction()
    elif len(selex)==1 and len(selex[0].SubObjects)==1:  #one selection -> ...
      if pipeCmd.isPipe(selex[0].Object):
        DN=selex[0].Object.PSize
        OD=float(selex[0].Object.OD)
        thk=float(selex[0].Object.thk)
        BR=None
        for prop in self.pipeDictList:
          if prop['PSize']==DN:
            BR=float(prop['BendRadius'])
        if BR==None:
          BR=1.5*OD/2
        propList=[DN,OD,thk,ang,BR]
      else:
        propList=[d['PSize'],float(d['OD']),float(d['thk']),ang,float(d['BendRadius'])]
      if selex[0].SubObjects[0].ShapeType=="Vertex":   # ...on vertex
        FreeCAD.activeDocument().openTransaction('Insert elbow on vertex')
        self.lastElbow=pipeCmd.makeElbow(propList,selex[0].SubObjects[0].Point)
        if self.combo.currentText()!='<none>':
          pipeCmd.moveToPyLi(self.lastElbow,self.combo.currentText())
        FreeCAD.activeDocument().commitTransaction()
      elif selex[0].SubObjects[0].ShapeType=="Edge" and  selex[0].SubObjects[0].curvatureAt(0)!=0: # ...on center of curved edge
        P=selex[0].SubObjects[0].centerOfCurvatureAt(0)
        Z=selex[0].SubObjects[0].tangentAt(0)
        FreeCAD.activeDocument().openTransaction('Insert elbow on curved edge')
        self.lastElbow=pipeCmd.makeElbow(propList,P,Z)
        if self.combo.currentText()!='<none>':
          pipeCmd.moveToPyLi(self.lastElbow,self.combo.currentText())
        FreeCAD.activeDocument().recompute()
        if pipeCmd.isPipe(selex[0].Object):
          Port0=self.lastElbow.Placement.Rotation.multVec(self.lastElbow.Ports[0])
          rot=FreeCAD.Rotation(Port0*-1,frameCmd.beamAx(selex[0].Object))
          self.lastElbow.Placement.Rotation=rot.multiply(self.lastElbow.Placement.Rotation)
          Port0=self.lastElbow.Placement.multVec(self.lastElbow.Ports[0])
          self.lastElbow.Placement.move(P-Port0)
        FreeCAD.activeDocument().commitTransaction()
    else:       # multiple selection -> insert one elbow at intersection of two edges or beams or pipes ##
      # selection of axes
      things=[]
      for objEx in selex:
        # if the profile is not defined and the selection is one piping object, take its profile for elbow
        if OD==thk==None and hasattr(objEx.Object,'PType') and objEx.Object.PType in ['Pipe','Elbow']: 
          DN=objEx.Object.PSize
          OD=objEx.Object.OD
          thk=objEx.Object.thk
          PRating=objEx.Object.PRating
        # if the object is a beam or pipe, append it to the "things"..
        if len(frameCmd.beams([objEx.Object]))==1:
          things.append(objEx.Object)
        else:
          # ..else append its edges
          for edge in frameCmd.edges([objEx]):
            things.append(edge)
        if len(things)>=2:
          break
      FreeCAD.activeDocument().openTransaction('Insert elbow on intersection')
      try:
        #create the feature
        if None in [DN,OD,thk,PRating]:
          propList=[d['PSize'],float(d['OD']),float(d['thk']),ang,float(d['BendRadius'])]
          self.lastElbow=pipeCmd.makeElbowBetweenThings(*things[:2],propList=propList)
          self.lastElbow.PRating=self.ratingList.item(self.ratingList.currentRow()).text()
        else:
          for prop in self.pipeDictList:
            if prop['PSize']==DN:
              BR=float(prop['BendRadius'])
          if BR==None:
            BR=1.5*OD/2
          propList=[DN,OD,thk,ang,BR]
          self.lastElbow=pipeCmd.makeElbowBetweenThings(*things[:2],propList=propList)
          self.lastElbow.PRating=PRating
        if self.combo.currentText()!='<none>':
          pipeCmd.moveToPyLi(self.lastElbow,self.combo.currentText())
      except:
        FreeCAD.Console.PrintError('Creation of elbow is failed\n')
      FreeCAD.activeDocument().commitTransaction()
      ####
    FreeCAD.activeDocument().recompute()
    
  def trim(self):
    if len(frameCmd.beams())==1:
      pipe=frameCmd.beams()[0]
      comPipeEdges=[e.CenterOfMass for e in pipe.Shape.Edges]
      eds=[e for e in frameCmd.edges() if not e.CenterOfMass in comPipeEdges]
      FreeCAD.activeDocument().openTransaction('Trim pipes')
      for edge in eds:
        frameCmd.extendTheBeam(frameCmd.beams()[0],edge)
      FreeCAD.activeDocument().commitTransaction()
    else:
      FreeCAD.Console.PrintError("Wrong selection\n")
  def apply(self):
    for obj in FreeCADGui.Selection.getSelection():
      d=self.pipeDictList[self.sizeList.currentRow()]
      if hasattr(obj,'PType') and obj.PType==self.PType:
        obj.PSize=d['PSize']
        obj.OD=d['OD']
        obj.thk=d['thk']
        try:
          obj.BendAngle=float(self.edit1.text())
        except:
          pass
        #obj.BendAngle=d['BendAngle']
        obj.BendRadius=d['BendRadius']
        obj.PRating=self.PRating
        FreeCAD.activeDocument().recompute()

class insertFlangeForm(protopypeForm):
  '''
  Dialog to insert flanges.
  For position and orientation you can select
    - one or more circular edges,
    - one or more vertexes,
    - nothing.
  In case one pipe is selected, its properties are applied to the flange.
  Available one button to reverse the orientation of the last or selected 
  flanges.
  '''
  def __init__(self):
    super(insertFlangeForm,self).__init__("Insert flanges","Flange","DIN-PN16","flange.svg")
    self.sizeList.setCurrentRow(0)
    self.ratingList.setCurrentRow(0)
    self.btn1.clicked.connect(self.insert)
    self.btn2=QPushButton('Reverse')
    self.secondCol.layout().addWidget(self.btn2)
    self.btn2.clicked.connect(self.reverse) #lambda: pipeCmd.rotateTheTubeAx(self.lastFlange,FreeCAD.Vector(1,0,0),180))
    self.btn3=QPushButton('Apply')
    self.secondCol.layout().addWidget(self.btn3)
    self.btn3.clicked.connect(self.apply)
    self.btn1.setDefault(True)
    self.btn1.setFocus()
    self.show()
    self.lastFlange=None
  def reverse(self):
    selFlanges=[f for f in FreeCADGui.Selection.getSelection() if hasattr(f,'PType') and f.PType=='Flange']
    if len(selFlanges):
      for f in selFlanges:
        pipeCmd.rotateTheTubeAx(f,FreeCAD.Vector(1,0,0),180)
    else:
      pipeCmd.rotateTheTubeAx(self.lastFlange,FreeCAD.Vector(1,0,0),180)
  def insert(self):
    tubes=[t for t in frameCmd.beams() if hasattr(t,'PSize')]
    if len(tubes)>0 and tubes[0].PSize in [prop['PSize'] for prop in self.pipeDictList]:
      for prop in self.pipeDictList:
        if prop['PSize']==tubes[0].PSize:
          d=prop
          break
    else:
      d=self.pipeDictList[self.sizeList.currentRow()]
    propList=[d['PSize'],d['FlangeType'],float(d['D']),float(d['d']),float(d['df']),float(d['f']),float(d['t']),int(d['n'])]
    FreeCAD.activeDocument().openTransaction('Insert flange')
    if len(frameCmd.edges())==0:
      vs=[v for sx in FreeCADGui.Selection.getSelectionEx() for so in sx.SubObjects for v in so.Vertexes]
      if len(vs)==0:
        self.lastFlange=pipeCmd.makeFlange(propList)
        if self.combo.currentText()!='<none>':
          pipeCmd.moveToPyLi(self.lastFlange,self.combo.currentText())
      else:
        for v in vs:
          self.lastFlange=pipeCmd.makeFlange(propList,v.Point)
          if self.combo.currentText()!='<none>':
            pipeCmd.moveToPyLi(self.lastFlange,self.combo.currentText())
    else:
      for edge in frameCmd.edges():
        if edge.curvatureAt(0)!=0:
          self.lastFlange=pipeCmd.makeFlange(propList,edge.centerOfCurvatureAt(0),edge.tangentAt(0).cross(edge.normalAt(0)))
          pipeCmd.moveToPyLi(self.lastFlange,self.combo.currentText())
          if self.combo.currentText()!='<none>':
            pipeCmd.moveToPyLi(self.lastFlange,self.combo.currentText())
    FreeCAD.activeDocument().commitTransaction()
    FreeCAD.activeDocument().recompute()
  def apply(self):
    for obj in FreeCADGui.Selection.getSelection():
      d=self.pipeDictList[self.sizeList.currentRow()]
      if hasattr(obj,'PType') and obj.PType==self.PType:
        obj.PSize=d['PSize']
        obj.FlangeType=d['FlangeType']
        obj.D=d['D']
        obj.d=d['d']
        obj.df=d['df']
        obj.f=d['f']
        obj.t=d['t']
        obj.n=int(d['n'])
        obj.PRating=self.PRating
        FreeCAD.activeDocument().recompute()

class insertReductForm(protopypeForm):
  '''
  Dialog to insert concentric reductions.
  For position and orientation you can select
    - two pipes parallel (possibly co-linear)
    - one pipe at one of its ends
    - one pipe
    - one circular edge
    - one straight edge
    - one vertex
    - nothing (created at origin)
  In case one pipe is selected, its properties are applied to the reduction.
  Available one button to reverse the orientation of the last or selected 
  reductions.
  '''
  def __init__(self):
    super(insertReductForm,self).__init__("Insert concentric reductions","Reduct","SCH-STD","reduct.svg")
    self.sizeList.setCurrentRow(0)
    self.ratingList.setCurrentRow(0)
    self.ratingList.itemClicked.connect(self.changeRating2)
    self.sizeList.currentItemChanged.connect(self.fillOD2)
    self.ratingList.setCurrentRow(0)
    self.ratingList.setMaximumHeight(50)
    self.OD2list=QListWidget()
    self.OD2list.setMaximumWidth(100)
    self.OD2list.setMaximumHeight(80)
    self.secondCol.layout().addWidget(self.OD2list)
    self.btn2=QPushButton('Reverse')
    self.btn2.setMaximumWidth(100)
    self.secondCol.layout().addWidget(self.btn2)
    self.btn3=QPushButton('Apply')
    self.btn3.setMaximumWidth(100)
    self.secondCol.layout().addWidget(self.btn3)
    self.btn1.clicked.connect(self.insert)
    self.btn2.clicked.connect(self.reverse)
    self.btn3.clicked.connect(self.applyProp)
    self.btn1.setDefault(True)
    self.btn1.setFocus()
    self.fillOD2()
    self.show()
    self.lastReduct=None
  def applyProp(self):
    r=self.pipeDictList[self.sizeList.currentRow()]
    DN=r['PSize']
    OD1=float(r['OD'])
    OD2=float(self.OD2list.currentItem().text())
    thk1=float(r['thk'])
    try:
      thk2=float(r['thk2'].split('>')[self.OD2list.currentRow()])
    except:
      thk2=thk1
    H=r['H']
    reductions=[red for red in FreeCADGui.Selection.getSelection() if hasattr(red,'PType') and red.PType=='Reduct']
    if len(reductions):
      for reduct in reductions:
        reduct.PSize=DN
        reduct.PRating=self.PRating
        reduct.OD=OD1
        reduct.OD2=OD2
        reduct.thk=thk1
        reduct.thk2=thk2
        reduct.Height=H
    elif self.lastReduct:
      self.lastReduct.PSize=DN
      self.lastReduct.PRating=self.PRating
      self.lastReduct.OD=OD1
      self.lastReduct.OD2=OD2
      self.lastReduct.thk=thk1
      self.lastReduct.thk2=thk2
      self.lastReduct.Height=H
    FreeCAD.activeDocument().recompute()
  def fillOD2(self):
    self.OD2list.clear()
    self.OD2list.addItems(self.pipeDictList[self.sizeList.currentRow()]['OD2'].split('>'))
    self.OD2list.setCurrentRow(0)
  def reverse(self):
    selRed=[r for r in FreeCADGui.Selection.getSelection() if hasattr(r,'PType') and r. PType=='Reduct']
    if len(selRed):
      for r in selRed:
        pipeCmd.rotateTheTubeAx(r,FreeCAD.Vector(1,0,0),180)
    elif self.lastReduct:
      pipeCmd.rotateTheTubeAx(self.lastReduct,FreeCAD.Vector(1,0,0),180)
  def insert(self):
    r=self.pipeDictList[self.sizeList.currentRow()]
    pos=Z=H=None
    selex=FreeCADGui.Selection.getSelectionEx()
    pipes=[p.Object for p in selex if hasattr(p.Object,'PType') and p.Object.PType=='Pipe']
    if len(pipes)>1 and frameCmd.isParallel(frameCmd.beamAx(pipes[0]),frameCmd.beamAx(pipes[1])):                # if at least 2 pipes are selected...
      if pipes[0].OD>=pipes[1].OD:
        p1,p2=pipes[:2]
      else:
        p2,p1=pipes[:2]
      DN=p1.PSize
      OD1=float(p1.OD)
      OD2=float(p2.OD)
      thk1=float(p1.thk)
      thk2=float(p2.thk)
      H=float(self.findDN(DN)['H'])
      Z=p2.Shape.Solids[0].CenterOfMass-p1.Shape.Solids[0].CenterOfMass
      Z.normalize()
      pos=p1.Shape.Solids[0].CenterOfMass+Z*float(p1.Height/2)
    elif len(pipes)>0:            # if 1 pipe is selected...
      DN=pipes[0].PSize
      OD1=float(pipes[0].OD)
      OD2=float(self.OD2list.currentItem().text())
      thk1=float(pipes[0].thk)
      thk2=float(r['thk2'].split('>')[self.OD2list.currentRow()])
      H=float(self.findDN(DN)['H'])
      curves=[e for e in frameCmd.edges() if e.curvatureAt(0)>0]
      if len(curves): #...and 1 curve is selected...
        pos=curves[0].centerOfCurvatureAt(0)
      else: #...or no curve is selected...
        pos=pipes[0].Placement.Base
      Z= pos-pipes[0].Shape.Solids[0].CenterOfMass
    else:                         # if no pipe is selected...
      DN=r['PSize']
      OD1=float(r['OD'])
      OD2=float(self.OD2list.currentItem().text())
      thk1=float(r['thk'])
      try:
        thk2=float(r['thk2'].split('>')[self.OD2list.currentRow()])
      except:
        thk2=thk1
      H=r['H']
      if frameCmd.edges():    #...but 1 curve is selected...
        edge=frameCmd.edges()[0]
        if edge.curvatureAt(0)>0:
          pos=edge.centerOfCurvatureAt(0)
          Z=edge.tangentAt(0).cross(edge.normalAt(0))
        else:
          pos=edge.valueAt(0)
          Z=edge.tangentAt(0)
      elif selex and selex[0].SubObjects[0].ShapeType=="Vertex": #...or 1 vertex..
        pos=selex[0].SubObjects[0].Point
    if not H: # calculate length if it's not defined
      H=float(3*(OD1-OD2))
    propList=[DN,OD1,OD2,thk1,thk2,H]
    FreeCAD.activeDocument().openTransaction('Insert reduction')
    self.lastReduct=pipeCmd.makeReduct(propList,pos,Z)
    FreeCAD.activeDocument().commitTransaction()
    FreeCAD.activeDocument().recompute()
    if self.combo.currentText()!='<none>':
      pipeCmd.moveToPyLi(self.lastReduct,self.combo.currentText())
  def changeRating2(self,item):
    self.PRating=item.text()
    self.fillSizes()
    self.sizeList.setCurrentRow(0)
    self.fillOD2()

class insertUboltForm(protopypeForm):
  '''
  Dialog to insert U-bolts.
  For position and orientation you can select
    - one or more circular edges,
    - nothing.
  In case one pipe is selected, its properties are aplied to the flange.
  Available one button to reverse the orientation of the last or selected tubes.
  '''
  def __init__(self):
    super(insertUboltForm,self).__init__("Insert U-bolt","Clamp","DIN-UBolt","clamp.svg")
    self.sizeList.setCurrentRow(0)
    self.ratingList.setCurrentRow(0)
    self.btn1.clicked.connect(self.insert)
    self.btn2=QPushButton('Ref. face')
    self.btn2.setMaximumWidth(100)
    self.secondCol.layout().addWidget(self.btn2)
    self.btn2.clicked.connect(self.getReference)
    self.lab1=QLabel('- no ref. face -')
    self.lab1.setAlignment(Qt.AlignHCenter)
    self.lab1.setMaximumWidth(100)
    self.secondCol.layout().addWidget(self.lab1)
    self.btn2.setDefault(True)
    self.btn2.setFocus()
    self.edit1=QLineEdit('1')
    self.edit1.setAlignment(Qt.AlignHCenter)
    self.edit1.setMaximumWidth(100)
    self.secondCol.layout().addWidget(self.edit1)
    self.show()
    self.refNorm=None
    self.getReference()
  def getReference(self):
    selex=FreeCADGui.Selection.getSelectionEx()
    for sx in selex:
      if sx.SubObjects:
        planes=[f for f in frameCmd.faces([sx]) if type(f.Surface)==Part.Plane]
        if len(planes)>0:
          self.refNorm=rounded(planes[0].normalAt(0,0))
          self.lab1.setText("ref. Face on "+sx.Object.Label)
  def insert(self):
    selex=FreeCADGui.Selection.getSelectionEx()
    if len(selex)==0:
      d=self.pipeDictList[self.sizeList.currentRow()]
      propList=[d['PSize'],self.PRating,float(d['C']),float(d['H']),float(d['d'])]
      FreeCAD.activeDocument().openTransaction('Insert clamp in (0,0,0)')
      ub=pipeCmd.makeUbolt(propList)
      if self.combo.currentText()!='<none>':
        pipeCmd.moveToPyLi(ub,self.combo.currentText())
      FreeCAD.activeDocument().commitTransaction()
      FreeCAD.activeDocument().recompute()
    else:
      try:
        n=int(self.edit1.text())
      except:
        n=1
      FreeCAD.activeDocument().openTransaction('Insert clamp on tube')
      for objex in selex:
        if hasattr(objex.Object,'PType') and objex.Object.PType=='Pipe':
          d=[typ for typ in self.pipeDictList if typ['PSize']==objex.Object.PSize]
          if len(d)>0:
            d=d[0]
          else:
            d=self.pipeDictList[self.sizeList.currentRow()]
          propList=[d['PSize'],self.PRating,float(d['C']),float(d['H']),float(d['d'])]
          if n>1:
            step=(float(objex.Object.Height)-float(d['C']))/(n-1)
          else:
            step=(float(objex.Object.Height)-float(d['C']))
          for i in range(n):
            ub=pipeCmd.makeUbolt(propList,pos=objex.Object.Placement.Base, Z=frameCmd.beamAx(objex.Object))
            ub.Placement.move(frameCmd.beamAx(objex.Object).multiply(float(d['C'])/2+i*step))
            if self.refNorm:
              pipeCmd.rotateTheTubeAx(obj=ub,angle=degrees(self.refNorm.getAngle((frameCmd.beamAx(ub,FreeCAD.Vector(0,1,0))))))
            if self.combo.currentText()!='<none>':
              pipeCmd.moveToPyLi(ub,self.combo.currentText())
      FreeCAD.activeDocument().commitTransaction()
    FreeCAD.activeDocument().recompute()

class insertPypeLineForm(protopypeForm):
  '''
  Dialog to insert pypelines.
  '''
  def __init__(self):
    super(insertPypeLineForm,self).__init__("Insert pypelines","Pipe","SCH-STD","pypeline.svg")
    self.sizeList.setCurrentRow(0)
    self.ratingList.setCurrentRow(0)
    self.btn1.clicked.connect(self.insert)
    self.edit1=QLineEdit('<name>')
    self.edit1.setAlignment(Qt.AlignHCenter)
    self.edit1.setMaximumWidth(100)
    self.secondCol.layout().addWidget(self.edit1)
    self.edit2=QLineEdit('<bend radius>')
    self.edit2.setAlignment(Qt.AlignHCenter)
    self.edit2.setMaximumWidth(100)
    self.secondCol.layout().addWidget(self.edit2)
    self.btn2=QPushButton('Part list')
    self.btn2.setMaximumWidth(100)
    self.secondCol.layout().addWidget(self.btn2)
    self.btn2.clicked.connect(self.partList)
    self.btn3=QPushButton('Color')
    self.btn3.setMaximumWidth(100)
    self.secondCol.layout().addWidget(self.btn3)
    self.btn3.clicked.connect(self.changeColor)
    self.color=0.8,0.8,0.8
    self.combo.setItemText(0,'<new>')
    self.btn1.setDefault(True)
    self.btn1.setFocus()
    self.show()
  def insert(self):
    d=self.pipeDictList[self.sizeList.currentRow()]
    FreeCAD.activeDocument().openTransaction('Insert pype-line')
    if self.combo.currentText()=='<new>':
      plLabel=self.edit1.text()
      if plLabel=="<name>" or plLabel.strip()=="":
        plLabel="Tubatura"
      a=pipeCmd.makePypeLine(DN=d["PSize"],PRating=self.PRating,OD=float(d["OD"]),thk=float(d["thk"]), lab=plLabel, color=self.color)
      self.combo.addItem(a.Label)
    else:
      plname=self.combo.currentText()
      plcolor=FreeCAD.activeDocument().getObjectsByLabel(plname)[0].ViewObject.ShapeColor
      pipeCmd.makePypeLine(DN=d["PSize"],PRating=self.PRating,OD=float(d["OD"]),thk=float(d["thk"]), pl=plname, color=plcolor)
    FreeCAD.ActiveDocument.recompute()
    FreeCAD.activeDocument().commitTransaction()
  def changeColor(self):
    self.hide()
    col=QColorDialog.getColor().toTuple()[:3]
    self.color=tuple([c/255.0 for c in col])
    self.show()
  def partList(self):
    from PySide.QtGui import QFileDialog as qfd
    f=None
    f=qfd.getSaveFileName()[0]
    if f:
      if self.combo.currentText()!='<new>':
        group=FreeCAD.activeDocument().getObjectsByLabel(self.currentPL.Group)[0]
        fields=['Label','PType','PSize','Volume','Height']
        rows=list()
        for o in group.OutList:
          if hasattr(o,'PType') and o.PType in ['Pipe','Elbow','Flange','Clamp']:
            data=[o.Label,o.PType,o.PSize,o.Shape.Volume,'-']
            if o.PType=='Pipe':
              data[4]=o.Height
            rows.append(dict(zip(fields,data)))
        plist=open(abspath(f),'w')
        w=csv.DictWriter(plist,fields,restval='-',delimiter=';')
        w.writeheader()
        w.writerows(rows)
        plist.close()
        FreeCAD.Console.PrintMessage('Data saved in %s.\n' %f)
    
class rotateForm(prototypeForm):
  '''
  Dialog for rotateTheTubeAx().
  It allows to rotate one object respect to the axis of its shape.
  It's possible to get the rotation axis from one existing edge: select the
  reference edge and the object, then push [Get]
  '''
  def __init__(self):
    super(rotateForm,self).__init__('rotateForm','Rotate','Reverse','90','Angle - deg:')
    self.btn1.clicked.connect(self.rotate)
    self.btn1.setFocus()
    self.btn2.clicked.connect(self.reverse)
    self.vShapeRef = FreeCAD.Vector(0,0,1)
    self.shapeAxis=QWidget()
    self.shapeAxis.setLayout(QFormLayout())
    self.xval=QLineEdit("0")
    self.xval.setMinimumWidth(40)
    self.xval.setAlignment(Qt.AlignHCenter)
    self.xval.setMaximumWidth(60)
    self.shapeAxis.layout().addRow("Shape ref. axis - x",self.xval)
    self.yval=QLineEdit("0")
    self.yval.setMinimumWidth(40)
    self.yval.setAlignment(Qt.AlignHCenter)
    self.yval.setMaximumWidth(60)
    self.shapeAxis.layout().addRow("Shape ref. axis - y",self.yval)
    self.zval=QLineEdit("1")
    self.zval.setMinimumWidth(40)
    self.zval.setAlignment(Qt.AlignHCenter)
    self.zval.setMaximumWidth(60)
    self.shapeAxis.layout().addRow("Shape ref. axis - z",self.zval)    
    self.mainVL.addWidget(self.shapeAxis)
    self.btnGet=QPushButton("Get")
    self.btnX=QPushButton("-X-")
    self.btnX.setMaximumWidth(50)
    self.btnY=QPushButton("-Y-")
    self.btnY.setMaximumWidth(50)
    self.btnZ=QPushButton("-Z-")
    self.btnZ.setMaximumWidth(50)
    #self.mainVL.addWidget(self.btnGet)
    self.buttons3=QWidget()
    self.buttons3.setLayout(QHBoxLayout())
    self.buttons3.layout().addWidget(self.btnGet)
    self.buttons3.layout().addWidget(self.btnX)
    self.buttons3.layout().addWidget(self.btnY)
    self.buttons3.layout().addWidget(self.btnZ)
    self.mainVL.addWidget(self.buttons3)
    self.btnX.clicked.connect(self.setX)
    self.btnY.clicked.connect(self.setY)
    self.btnZ.clicked.connect(self.setZ)
    self.btnGet.clicked.connect(self.getAxis)
    self.getAxis()
    self.setMaximumWidth(200)
    self.btnGet.setMaximumWidth(30)
    self.btnX.setMaximumWidth(30)
    self.btnY.setMaximumWidth(30)
    self.btnZ.setMaximumWidth(30)
    self.btn1.setMaximumWidth(70)
    self.btn2.setMaximumWidth(70)
    self.btn1.setDefault(True)
    self.btn1.setFocus()
    self.show()
  def rotate(self):
    if len(FreeCADGui.Selection.getSelection())>0:
      obj = FreeCADGui.Selection.getSelection()[0]
      self.vShapeRef=FreeCAD.Vector(float(self.xval.text()),float(self.yval.text()),float(self.zval.text()))
      FreeCAD.activeDocument().openTransaction('Rotate')
      if self.radio2.isChecked():
        FreeCAD.activeDocument().copyObject(FreeCADGui.Selection.getSelection()[0],True)
      pipeCmd.rotateTheTubeAx(obj,self.vShapeRef,float(self.edit1.text()))
      FreeCAD.activeDocument().commitTransaction()
  def reverse(self):
    if len(FreeCADGui.Selection.getSelection())>0:
      obj = FreeCADGui.Selection.getSelection()[0]
      FreeCAD.activeDocument().openTransaction('Reverse rotate')
      pipeCmd.rotateTheTubeAx(obj,self.vShapeRef,-2*float(self.edit1.text()))
      self.edit1.setText(str(-1*float(self.edit1.text())))
      FreeCAD.activeDocument().commitTransaction()
  def setX(self):
    if self.xval.text()=='1':
      self.xval.setText('-1')
    elif self.xval.text()=='0':
      self.xval.setText('1')
    else:
      self.xval.setText('0')
  def setY(self):
    if self.yval.text()=='1':
      self.yval.setText('-1')
    elif self.yval.text()=='0':
      self.yval.setText('1')
    else:
      self.yval.setText('0')
  def setZ(self):
    if self.zval.text()=='1':
      self.zval.setText('-1')
    elif self.zval.text()=='0':
      self.zval.setText('1')
    else:
      self.zval.setText('0')
  def getAxis(self):
    coord=[]
    selex=FreeCADGui.Selection.getSelectionEx()
    if len(selex)==2 and len(selex[1].SubObjects)>0:
      sub=selex[0].SubObjects[0]
      if sub.ShapeType=='Edge':
        axObj=sub.tangentAt(0)
        obj=selex[1].Object
        coord=rounded(pipeCmd.shapeReferenceAxis(obj,axObj))
        self.xval.setText(str(coord[0]))
        self.yval.setText(str(coord[1]))
        self.zval.setText(str(coord[2]))
        FreeCADGui.Selection.removeSelection(selex[0].Object)

class rotateEdgeForm(prototypeForm):
  '''
  Dialog for rotateTheTubeEdge().
  It allows to rotate one object respect to the axis of one circular edge.
  '''
  def __init__(self):
    super(rotateEdgeForm,self).__init__('rotateEdgeForm','Rotate','Reverse','90','Angle - deg:')
    self.btn1.clicked.connect(self.rotate)
    self.btn2.clicked.connect(self.reverse)
    self.btn1.setDefault(True)
    self.btn1.setFocus()
    self.show()
  def rotate(self):
    if len(FreeCADGui.Selection.getSelection())>0:
      FreeCAD.activeDocument().openTransaction('Rotate')
      if self.radio2.isChecked():
        FreeCAD.activeDocument().copyObject(FreeCADGui.Selection.getSelection()[0],True)
      pipeCmd.rotateTheTubeEdge(float(self.edit1.text()))
      FreeCAD.activeDocument().commitTransaction()
  def reverse(self):
    FreeCAD.activeDocument().openTransaction('Reverse rotate')
    pipeCmd.rotateTheTubeEdge(-2*float(self.edit1.text()))
    self.edit1.setText(str(-1*float(self.edit1.text())))
    FreeCAD.activeDocument().commitTransaction()
