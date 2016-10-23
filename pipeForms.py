#pipeTools dialogs
#(c) 2016 Riccardo Treu LGPL

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
  def __init__(self,winTitle='Title', PType='Pipe', PRating='SCH-STD'):
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
    self.mainHL=QHBoxLayout()
    self.setLayout(self.mainHL)
    self.sizeList=QListWidget()
    self.sizeList.setMaximumWidth(120)
    self.sizeList.setCurrentRow(0)
    self.mainHL.addWidget(self.sizeList)
    self.pipeDictList=[]
    self.fileList=listdir(join(dirname(abspath(__file__)),"tables"))
    self.fillSizes()
    self.PRatingsList=[s.lstrip(PType+"_").rstrip(".csv") for s in self.fileList if s.startswith(PType)]
    self.secondCol=QWidget()
    self.secondCol.setLayout(QVBoxLayout())
    self.ratingList=QListWidget()
    self.ratingList.setMaximumWidth(120)
    self.ratingList.addItems(self.PRatingsList)
    self.ratingList.itemClicked.connect(self.changeRating)
    self.ratingList.setCurrentRow(0)
    self.secondCol.layout().addWidget(self.ratingList)
    self.btn1=QPushButton('Insert')
    self.secondCol.layout().addWidget(self.btn1)
    self.mainHL.addWidget(self.secondCol)
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
    self.fillSizes()
    
class insertPipeForm(protopypeForm):
  '''
  Dialog to insert tubes.
  If edges are selected, it places the tubes over the straight edges or at the center of the curved edges.
  If vertexes are selected, it places the tubes at the selected vertexes.
  If nothing is selected it places one tube in the origin with the selected 
  size and height, or default = 200 mm.
  Available one button to reverse the orientation of the last or selected tubes.
  '''
  def __init__(self):
    super(insertPipeForm,self).__init__("Insert pipes","Pipe","SCH-STD")
    self.sizeList.item(0).setSelected(True)
    self.ratingList.item(0).setSelected(True)
    self.btn1.clicked.connect(self.insert)
    self.edit1=QLineEdit(' <insert lenght>')
    self.edit1.setAlignment(Qt.AlignHCenter)
    self.secondCol.layout().addWidget(self.edit1)
    self.btn2=QPushButton('Reverse')
    self.secondCol.layout().addWidget(self.btn2)
    self.btn2.clicked.connect(self.reverse) #lambda: pipeCmd.rotateTheTubeAx(self.lastPipe,FreeCAD.Vector(1,0,0),180))
    self.btn3=QPushButton('Apply')
    self.secondCol.layout().addWidget(self.btn3)
    self.btn3.clicked.connect(self.apply)
    self.btn1.setDefault(True)
    self.btn1.setFocus()
    self.show()
    self.lastPipe=None
  def reverse(self):
    selPipes=[p for p in FreeCADGui.Selection.getSelection() if hasattr(p,'PType') and p.PType=='Pipe']
    if len(selPipes):
      for p in selPipes:
        pipeCmd.rotateTheTubeAx(p,FreeCAD.Vector(1,0,0),180)
    else:
      pipeCmd.rotateTheTubeAx(self.lastPipe,FreeCAD.Vector(1,0,0),180)
  
  def insert(self):
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
        pipeCmd.makePipe(propList)
      else:
        for v in vs:
          pipeCmd.makePipe(propList,v.Point)
    else:
      for edge in frameCmd.edges():
        if edge.curvatureAt(0)==0:
          propList=[d['PSize'],float(d['OD']),float(d['thk']),edge.Length]
          pipeCmd.makePipe(propList,edge.valueAt(0),edge.tangentAt(0))
        else:
          objs=[o for o in FreeCADGui.Selection.getSelection() if hasattr(o,'PSize') and hasattr(o,'OD') and hasattr(o,'thk')]
          if len(objs)>0:
            propList=[objs[0].PSize,objs[0].OD,objs[0].thk,H]
          else:
            propList=[d['PSize'],float(d['OD']),float(d['thk']),H]
          self.lastPipe=pipeCmd.makePipe(propList,edge.centerOfCurvatureAt(0),edge.tangentAt(0).cross(edge.normalAt(0)))
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
  It allows to select one vertex, one circular edge or a pair of edges or pipes 
  or beams.
  If at least one tube is selected it automatically takes its size and apply  
  it to the elbows created. It also trim or extend automatically the tube.
  If nothing is selected, it places one elbow in the origin.
  Available button to trim/extend one selected pipe to the selected edges of 
  the elbow, after it's modified (for example, changed the bend radius).
  '''
  def __init__(self):
    super(insertElbowForm,self).__init__("Insert elbows","Elbow","SCH-STD")
    self.sizeList.item(0).setSelected(True)
    self.ratingList.item(0).setSelected(True)
    self.btn1.clicked.connect(self.insert)
    self.edit1=QLineEdit('<insert angle>')
    self.edit1.setAlignment(Qt.AlignHCenter)
    self.secondCol.layout().addWidget(self.edit1)
    self.btn2=QPushButton('Trim/Extend')
    self.btn2.clicked.connect(self.trim)
    self.secondCol.layout().addWidget(self.btn2)
    self.btn3=QPushButton('Apply')
    self.secondCol.layout().addWidget(self.btn3)
    self.btn3.clicked.connect(self.apply)
    self.btn1.setDefault(True)
    self.btn1.setFocus()
    self.show()
  def insert(self):
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
      pipeCmd.makeElbow(propList)
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
        pipeCmd.makeElbow(propList,selex[0].SubObjects[0].Point)
        FreeCAD.activeDocument().commitTransaction()
      elif selex[0].SubObjects[0].ShapeType=="Edge" and  selex[0].SubObjects[0].curvatureAt(0)!=0: # ...on center of curved edge
        P=selex[0].SubObjects[0].centerOfCurvatureAt(0)
        Z=selex[0].SubObjects[0].tangentAt(0)
        FreeCAD.activeDocument().openTransaction('Insert elbow on curved edge')
        e=pipeCmd.makeElbow(propList,P,Z)
        FreeCAD.activeDocument().recompute()
        if pipeCmd.isPipe(selex[0].Object):
          Port0=e.Placement.Rotation.multVec(e.Ports[0])
          rot=FreeCAD.Rotation(Port0*-1,frameCmd.beamAx(selex[0].Object))
          e.Placement.Rotation=rot.multiply(e.Placement.Rotation)
          Port0=e.Placement.multVec(e.Ports[0])
          e.Placement.move(P-Port0)
        FreeCAD.activeDocument().commitTransaction()
    else:    
      ## insert one elbow at intersection of two edges or "beams" ##
      # selection of axes
      axes=[]
      for objEx in selex:
        # if the profile is not defined and the selection is one piping object, take its profile for elbow
        if OD==thk==None and hasattr(objEx.Object,'PType') and objEx.Object.PType in ['Pipe','Elbow']: 
          DN=objEx.Object.PSize
          OD=objEx.Object.OD
          thk=objEx.Object.thk
          PRating=objEx.Object.PRating
        # if the object is a beam or pipe, append it to the axes..
        if len(frameCmd.beams([objEx.Object]))==1:
          axes.append(objEx.Object.Placement.Base)
          axes.append(frameCmd.beamAx(objEx.Object))
        else:
          # ..else append its edges to axes
          for edge in frameCmd.edges([objEx]):
            axes.append(edge.CenterOfMass)
            axes.append(edge.tangentAt(0))
        if len(axes)>=4:
          break
      FreeCAD.activeDocument().openTransaction('Insert elbow on intersection')
      try:
        # get the position
        p1,v1,p2,v2=axes[:4]
        P=frameCmd.intersectionLines(p1,v1,p2,v2)
        if P!=None:
          if P!=p1:
            w1=P-p1  # weak patch, but it works!
          else:
            w1=P-(p1+v1)
          w1.normalize()
          if P!=p2:
            w2=P-p2
          else:
            w2=P-(p2+v2)
          w2.normalize()
        else:
          FreeCAD.Console.PrintError('frameCmd.intersectionLines() has failed!\n')
          return None
        # calculate the bending angle and the plane of the elbow
        ang=180-degrees(w1.getAngle(w2))
        #create the feature
        if None in [DN,OD,thk,PRating]:
          propList=[d['PSize'],float(d['OD']),float(d['thk']),ang,float(d['BendRadius'])]
          elb=pipeCmd.makeElbow(propList,P,axes[1].cross(axes[3]))
          elb.PRating=self.ratingList.item(self.ratingList.currentRow()).text()
        else:
          BR=None
          for prop in self.pipeDictList:
            if prop['PSize']==DN:
              BR=float(prop['BendRadius'])
          if BR==None:
            BR=1.5*OD/2
          propList=[DN,OD,thk,ang,BR]
          elb=pipeCmd.makeElbow(propList,P,axes[1].cross(axes[3]))
          elb.PRating=PRating
        # mate the elbow ends with the pipes or edges
        b=frameCmd.bisect(w1.negative(),w2.negative())
        elbBisect=frameCmd.beamAx(elb,FreeCAD.Vector(1,1,0))
        rot=FreeCAD.Rotation(elbBisect,b)
        elb.Placement.Rotation=rot.multiply(elb.Placement.Rotation)
        # trim automatically the adjacent tubes
        FreeCAD.activeDocument().recompute()
        portA=elb.Placement.multVec(elb.Ports[0])
        portB=elb.Placement.multVec(elb.Ports[1])
        for tube in frameCmd.beams():
          vectA=tube.Shape.Solids[0].CenterOfMass-portA
          vectB=tube.Shape.Solids[0].CenterOfMass-portB
          if frameCmd.isParallel(vectA,frameCmd.beamAx(tube)):
            frameCmd.extendTheBeam(tube,portA)
          else:
            frameCmd.extendTheBeam(tube,portB)
          FreeCAD.activeDocument().recompute()
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
  If edges are selected, it places the flange over the selected circular edges.
  If at least one tube is selected it automatically takes its Nominal Size and 
  apply it to the flange created, if it is included in the Nominal Size list of 
  the flange.
  If vertexes are selected, it places the flange at the selected vertexes.
  If nothing is selected it places one flange in the origin with the selected 
  size.
  Available one button to reverse the orientation of the last or selected 
  flanges.
  '''
  def __init__(self):
    super(insertFlangeForm,self).__init__("Insert flanges","Flange","DIN-PN16")
    self.sizeList.item(0).setSelected(True)
    self.ratingList.item(0).setSelected(True)
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
      else:
        for v in vs:
          self.lastFlange=pipeCmd.makeFlange(propList,v.Point)
    else:
      for edge in frameCmd.edges():
        if edge.curvatureAt(0)!=0:
          self.lastFlange=pipeCmd.makeFlange(propList,edge.centerOfCurvatureAt(0),edge.tangentAt(0).cross(edge.normalAt(0)))
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

class insertUboltForm(protopypeForm):
  '''
  Dialog to insert U-bolts.
  '''
  def __init__(self):
    super(insertUboltForm,self).__init__("Insert U-bolt","Clamp","DIN-UBolt")
    self.sizeList.item(0).setSelected(True)
    self.ratingList.item(0).setSelected(True)
    self.btn1.clicked.connect(self.insert)
    self.btn2=QPushButton('Ref. face')
    self.secondCol.layout().addWidget(self.btn2)
    self.btn2.clicked.connect(self.getReference)
    self.lab1=QLabel('- no ref. face -')
    self.lab1.setAlignment(Qt.AlignHCenter)
    self.secondCol.layout().addWidget(self.lab1)
    self.btn2.setDefault(True)
    self.btn2.setFocus()
    self.edit1=QLineEdit('1')
    self.edit1.setAlignment(Qt.AlignHCenter)
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
      pipeCmd.makeUbolt(propList)
      FreeCAD.activeDocument().commitTransaction()
      FreeCAD.activeDocument().recompute()
    else:
      try:
        n=int(self.edit1.text())
      except:
        n=1
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
          FreeCAD.activeDocument().openTransaction('Insert clamp on tube')
          for i in range(n):
            ub=pipeCmd.makeUbolt(propList,pos=objex.Object.Placement.Base, Z=frameCmd.beamAx(objex.Object))
            ub.Placement.move(frameCmd.beamAx(objex.Object).multiply(float(d['C'])/2+i*step))
            if self.refNorm:
              print self.refNorm
              print frameCmd.beamAx(ub,FreeCAD.Vector(0,1,0))
              print degrees(self.refNorm.getAngle((frameCmd.beamAx(ub,FreeCAD.Vector(0,1,0)))))
              pipeCmd.rotateTheTubeAx(obj=ub,angle=degrees(self.refNorm.getAngle((frameCmd.beamAx(ub,FreeCAD.Vector(0,1,0))))))
          FreeCAD.activeDocument().commitTransaction()
    FreeCAD.activeDocument().recompute()
    
class rotateForm(prototypeForm):
  '''
  Dialog for rotateTheTubeAx().
  It allows to rotate one object respect to the axis of its shape.
  '''
  def __init__(self):
    super(rotateForm,self).__init__('rotateForm','Rotate','Reverse','90','Angle - deg:')
    self.btn1.clicked.connect(self.rotate)
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
    self.btnGet.setDefault(True)
    self.btnX=QPushButton("-X-")
    self.btnGet.setDefault(True)
    self.btnY=QPushButton("-Y-")
    self.btnGet.setDefault(True)
    self.btnZ=QPushButton("-Z-")
    self.mainVL.addWidget(self.btnGet)
    self.buttons3=QWidget()
    self.buttons3.setLayout(QHBoxLayout())
    self.buttons3.layout().addWidget(self.btnX)
    self.buttons3.layout().addWidget(self.btnY)
    self.buttons3.layout().addWidget(self.btnZ)
    self.mainVL.addWidget(self.buttons3)
    self.btnX.clicked.connect(self.setX)
    self.btnY.clicked.connect(self.setY)
    self.btnZ.clicked.connect(self.setZ)
    self.btnGet.clicked.connect(self.getAxis)
    self.btnX.setMaximumWidth(40)
    self.btnY.setMaximumWidth(40)
    self.btnZ.setMaximumWidth(40)
    self.btn1.setMaximumWidth(180)
    self.btn2.setMaximumWidth(180)
    self.btnGet.setMaximumWidth(180)
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
    if len(selex)==1 and len(selex[0].SubObjects)>0:
      sub=selex[0].SubObjects[0]
      if sub.ShapeType=='Edge' and sub.curvatureAt(0)>0:  
        axObj=sub.tangentAt(0).cross(sub.normalAt(0))
        obj=selex[0].Object
    #elif[..]
    coord=list(pipeCmd.shapeReferenceAxis(obj,axObj))
    if len(coord)==3:
      self.xval.setText(str(coord[0]))
      self.yval.setText(str(coord[1]))
      self.zval.setText(str(coord[2]))

class rotateEdgeForm(prototypeForm):
  '''
  Dialog for rotateTheTubeEdge().
  It allows to rotate one object respect to the axis of one circular edge.
  '''
  def __init__(self):
    super(rotateEdgeForm,self).__init__('rotateEdgeForm','Rotate','Reverse','90','Angle - deg:')
    self.btn1.clicked.connect(self.rotate)
    self.btn2.clicked.connect(self.reverse)
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
