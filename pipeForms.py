#pipeTools dialogs
#(c) 2016 Riccardo Treu LGPL

import FreeCAD,FreeCADGui,csv
import frameCmd, pipeCmd
from frameForms import prototypeForm
from os import listdir
from os.path import join, dirname, abspath
from PySide.QtCore import *
from PySide.QtGui import *
from math import degrees

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
    self.btn1.setDefault(True)
    self.btn1.setFocus()
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
  If nothing is selected it places one tube in the origin with the selected size and height, or default = 200 mm.
  Available one button to reverse the orientation of the selected tube.
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
    self.btn2.clicked.connect(lambda: pipeCmd.rotateTheTubeAx(frameCmd.beams()[0],FreeCAD.Vector(1,0,0),180))
    self.btn3=QPushButton('Apply')
    self.secondCol.layout().addWidget(self.btn3)
    self.btn3.clicked.connect(self.apply)
    self.show()
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
          pipeCmd.makePipe(propList,edge.centerOfCurvatureAt(0),edge.tangentAt(0).cross(edge.normalAt(0)))
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
  It allows to select one vertex, one circular edge or a pair of edges or pipes or beams.
  If at least one tube is selected it automatically takes its size and apply   it to the elbows created. It also trim or extend automatically the tube.
  If nothing is selected, it places one elbow in the origin.
  Available button to trim/extend one selected pipe to the selected edges of the elbow, after it's modified (for example, changed the bend radius).
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
    FreeCAD.activeDocument().openTransaction('Insert elbow')
    if len(selex)==0:     # no selection -> insert one elbow at origin
      propList=[d['PSize'],float(d['OD']),float(d['thk']),ang,float(d['BendRadius'])]
      pipeCmd.makeElbow(propList)
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
        pipeCmd.makeElbow(propList,selex[0].SubObjects[0].Point)
      elif selex[0].SubObjects[0].ShapeType=="Edge" and  selex[0].SubObjects[0].curvatureAt(0)!=0: # ...on center of curved edge
        P=selex[0].SubObjects[0].centerOfCurvatureAt(0)
        Z=selex[0].SubObjects[0].tangentAt(0)
        e=pipeCmd.makeElbow(propList,P,Z)
        FreeCAD.activeDocument().recompute()
        if pipeCmd.isPipe(selex[0].Object):
          Port0=e.Placement.Rotation.multVec(e.Ports[0])
          rot=FreeCAD.Rotation(Port0*-1,frameCmd.beamAx(selex[0].Object))
          e.Placement.Rotation=rot.multiply(e.Placement.Rotation)
          Port0=e.Placement.multVec(e.Ports[0])
          #frameCmd.extendTheBeam(selex[0].Object,Port0)
          e.Placement.move(P-Port0)
    else:    
      ## insert one elbow at intersection of two edges or "beams" ##
      axes=[]
      # selection of axes
      for objEx in selex:
        if len(frameCmd.beams([objEx.Object]))==1:
          axes.append(objEx.Object.Placement.Base)
          axes.append(frameCmd.beamAx(objEx.Object))
          if OD==thk==None and hasattr(objEx.Object,'PType') and objEx.Object.PType=='Pipe': # if the selction is one pipe, take its profile for elbow
            DN=objEx.Object.PSize
            OD=objEx.Object.OD
            thk=objEx.Object.thk
            PRating=objEx.Object.PRating
        else:
          for edge in frameCmd.edges([objEx]):
            axes.append(edge.CenterOfMass)
            axes.append(edge.tangentAt(0))
      if len(axes)>=4:
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
        from math import pi
        ang=180-w1.getAngle(w2)*180/pi # ..-acos(w1.dot(w2))/pi*180
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
        b=frameCmd.bisect(w1*-1,w2*-1)
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
            print tube.Label," is parallel to A"
          else:
            frameCmd.extendTheBeam(tube,portB)
            print tube.Label," is parallel to B"
          FreeCAD.activeDocument().recompute()
      ####
    FreeCAD.activeDocument().commitTransaction()
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
  If at least one tube is selected it automatically takes its Nominal Size and apply it to the flange created, if it is included in the Nominal Size list of the flange.
  If vertexes are selected, it places the flange at the selected vertexes.
  If nothing is selected it places one flange in the origin with the selected size.
  '''
  def __init__(self):
    super(insertFlangeForm,self).__init__("Insert flanges","Flange","DIN-PN16")
    self.sizeList.item(0).setSelected(True)
    self.ratingList.item(0).setSelected(True)
    self.btn1.clicked.connect(self.insert)
    self.btn3=QPushButton('Apply')
    self.secondCol.layout().addWidget(self.btn3)
    self.btn3.clicked.connect(self.apply)
    self.show()
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
        pipeCmd.makeFlange(propList)
      else:
        for v in vs:
          pipeCmd.makeFlange(propList,v.Point)
    else:
      for edge in frameCmd.edges():
        if edge.curvatureAt(0)!=0:
          pipeCmd.makeFlange(propList,edge.centerOfCurvatureAt(0),edge.tangentAt(0).cross(edge.normalAt(0)))
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
