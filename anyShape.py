import FreeCAD, FreeCADGui, Part
import frameCmd
from os.path import *
from os import listdir
from pipeFeatures import pypeType

class AnyThing(pypeType): #object):
  '''Class for object TType="Anything"
  AnyThing(obj,name="Thing", fileName="", ports="0:0:0")
    obj: the "App::FeaturePython object"
    TType (string): name of the thing
    FileName (string): a valid .STEP .IGES or .brep
    ports: a string in the form "x0:y0:z0/x1:y1:z1/..." representing the position of ports 0,1....
    '''
  def __init__(self, obj,name="valve",fileName='ballDN15.stp',ports='0:0:0'):
    #obj.Proxy = self
    super(AnyThing,self).__init__(obj)
    # define common properties
    obj.PType="Any"
    # define specific properties
    obj.addProperty("App::PropertyString","FileName","AnyThing","The file of the shape (inside ./shapes)").FileName=fileName
    portslist=list()
    if ports:
      for port in ports.split('/'):
        portslist.append(FreeCAD.Vector([float(i) for i in port.split(":")]))
    obj.Ports=portslist
    if fileName:
      s=Part.Shape()
      path=join(dirname(abspath(__file__)),"shapes",fileName)
      if exists(path):
        s.read(path)
        obj.Shape=s
      else:
        FreeCAD.Console.PrintError("%s file doesn't exist" %fileName)
  def onChanged(self, fp, prop):
    pass
  def execute(self, fp):
    super(AnyThing,self).execute(fp) # perform common operations

def makeThing(n='Valvola', fn='ballDN15.stp', p='0:0:0', pos=None, Z=None):
  '''
  makeThing(n,fn,p,pos,Z)
    n = name
    fn = file name
    p = ports string (e.g. "0:0:0/0:0:69")
    pos = position Vector
    Z = orientation Vector
  '''
  if pos==None:
    pos=FreeCAD.Vector(0,0,0)
  if Z==None:
    Z=FreeCAD.Vector(0,0,1)
  a=FreeCAD.ActiveDocument.addObject("Part::FeaturePython",n)
  AnyThing(a, name=n, fileName=fn, ports=p)
  a.ViewObject.Proxy=0
  a.Placement.Base=pos
  rot=FreeCAD.Rotation(FreeCAD.Vector(0,0,1),Z)
  a.Placement.Rotation=rot.multiply(a.Placement.Rotation)
  return a

from frameForms import prototypeDialog

class shapeDialog(prototypeDialog):
  'dialog for any()'
  def __init__(self):
    super(shapeDialog,self).__init__('shapes.ui')
    self.shapesDir=join(dirname(abspath(__file__)),'shapes')
    self.cwd=self.shapesDir
    self.pipeDictList=list()
    self.filesListed=list()
    self.lastThing=None
    for n in listdir(self.cwd):
      absFile=join(self.cwd,n)
      if isdir(absFile): self.form.comboDirs.addItem(n)
      elif isfile(absFile)and n.upper().split(extsep)[-1] in ['STEP','STP','IGES','IGS','BREP','BRP']: self.form.listFiles.addItem(n)
    self.form.listFiles.setCurrentRow(0)
    self.form.comboDirs.currentIndexChanged.connect(self.fillFiles)
    self.form.listFiles.itemClicked.connect(self.checkListed)
  def accept(self):
    fname=self.form.listFiles.currentItem().text()
    row=None
    pos=None
    Z=None
    if self.form.comboDirs.currentText()=='<shapes>': sdir=''
    else: sdir=self.form.comboDirs.currentText()
    if fname in self.filesListed:
      for r in self.pipeDictList:
        if r["fileName"]==fname:
          row=r
          break
      name=row["name"]
      ports=row["ports"]
    else:
      name=fname.split('.')[0]
      ports='0:0:0'
    selex=FreeCADGui.Selection.getSelectionEx()
    if selex:
      vxs=[v for sx in selex for so in sx.SubObjects for v in so.Vertexes]
      cedges=[e for e in frameCmd.edges() if e.curvatureAt(0)!=0]
      faces=frameCmd.faces()
      if faces:
        x=(faces[0].ParameterRange[0]+faces[0].ParameterRange[1])/2
        y=(faces[0].ParameterRange[2]+faces[0].ParameterRange[3])/2
        pos=faces[0].valueAt(x,y)
        Z=faces[0].normalAt(x,y)
      elif cedges:
        pos=cedges[0].centerOfCurvatureAt(0)
        Z=cedges[0].tangentAt(0).cross(cedges[0].normalAt(0))
      elif vxs:
        pos=vxs[0].Point
    self.lastThing=makeThing(name,join(sdir,fname),ports,pos,Z)
    if row:
      self.lastThing.Kv=float(row["Kv"])
      self.lastThing.PSize=row["DN"]
      self.lastThing.PRating=row["PN"]
  def fillFiles(self):
    self.form.listFiles.clear()
    self.form.labListed.setText('-')
    if self.form.comboDirs.currentText()!='<shapes>':
      self.cwd=join(self.shapesDir,self.form.comboDirs.currentText())
    else:
      self.cwd=self.shapesDir
    for n in listdir(self.cwd):
      if isfile(join(self.cwd,n)) and n.upper().split(extsep)[-1] in ['STEP','STP','IGES','IGS','BREP','BRP']:
        self.form.listFiles.addItem(n)
      if n[:4]=='Any_' and n[-4:]=='.csv':
        f=open(join(self.cwd,n),'r')
        from csv import DictReader
        reader=DictReader(f,delimiter=';')
        self.pipeDictList=[DNx for DNx in reader]
        f.close()
        self.filesListed=[row['fileName'] for row in self.pipeDictList]
    self.form.listFiles.setCurrentRow(0)
  def checkListed(self):
    if self.form.listFiles.currentItem().text() in self.filesListed:
      self.form.labListed.setText('*** LISTED ***')
    else:
      self.form.labListed.setText('(unlisted)')
