#pipeTools scripted objects
#(c) 2016 Riccardo Treu LGPL

import FreeCAD, Part, frameCmd

################ CLASSES ###########################

class Pipe():
  '''Class for object PType="Pipe"
  Pipe(obj,[DN="DN50",OD=60.3,thk=3, H=100])
  obj: the "App::FeaturePython object"
  DN (string): nominal diameter
  OD (float): outside diameter
  thk (float): shell thickness
  H (float): length of pipe'''
  def __init__(self, obj,DN="DN50",OD=60.3,thk=3, H=100):
    obj.Proxy = self
    obj.addProperty("App::PropertyString","PType","Pipe","Type of tubeFeature").PType="Pipe"
    obj.addProperty("App::PropertyString","PRating","Pipe","Rating of pipeFeature").PRating="SCH-STD"
    obj.addProperty("App::PropertyString","PSize","Pipe","Nominal diameter").PSize=DN
    obj.addProperty("App::PropertyLength","OD","Pipe","Outside diameter").OD=OD
    obj.addProperty("App::PropertyLength","thk","Pipe","Wall thickness").thk=thk
    obj.addProperty("App::PropertyLength","ID","Pipe","Inside diameter").ID=obj.OD-2*obj.thk
    obj.addProperty("App::PropertyLength","Height","Pipe","Length of tube").Height=H
    obj.addProperty("App::PropertyString","Profile","Pipe","Section dim.").Profile=str(obj.OD)+"x"+str(obj.thk)
    

  def onChanged(self, fp, prop):
    #FreeCAD.Console.PrintMessage("Changed Pipe feature\n")
    return None

  def execute(self, fp):
    if fp.thk>fp.OD/2:
      fp.thk=fp.OD/2.1
    fp.ID=fp.OD-2*fp.thk
    fp.Profile=str(fp.OD)+"x"+str(fp.thk)
    fp.Shape = Part.makeCylinder(fp.OD/2,fp.Height).cut(Part.makeCylinder(fp.ID/2,fp.Height))
    #FreeCAD.Console.PrintMessage("Executed Pipe feature\n")
    
class Elbow():
  '''Class for object PType="Elbow"
  Elbow(obj,[DN="DN50",OD=60.3,thk=3,BA=90,BR=45.225])
  obj: the "App::FeaturePython object"
  DN (string): nominal diameter
  OD (float): outside diameter
  thk (float): shell thickness
  BA (float): bend angle
  BR (float): bend radius'''
  def __init__(self, obj,DN="DN50",OD=60.3,thk=3,BA=90,BR=45.225):
    obj.Proxy = self
    obj.addProperty("App::PropertyString","PType","Elbow","Type of pipeFeature").PType="Elbow"
    obj.addProperty("App::PropertyString","PRating","Elbow","Rating of pipeFeature").PRating="SCH-STD"
    obj.addProperty("App::PropertyString","PSize","Elbow","Nominal diameter").PSize=DN
    obj.addProperty("App::PropertyLength","OD","Elbow","Outside diameter").OD=OD
    obj.addProperty("App::PropertyLength","thk","Elbow","Wall thickness").thk=thk
    obj.addProperty("App::PropertyLength","ID","Elbow","Inside diameter").ID=obj.OD-2*obj.thk
    obj.addProperty("App::PropertyAngle","BendAngle","Elbow","Bend Angle").BendAngle=BA
    obj.addProperty("App::PropertyLength","BendRadius","Elbow","Bend Radius").BendRadius=BR
    obj.addProperty("App::PropertyString","Profile","Elbow","Section dim.").Profile=str(obj.OD)+"x"+str(obj.thk)
    obj.addProperty("App::PropertyVectorList","Ports","Elbow","Ports relative position").Ports=[FreeCAD.Vector(1,0,0),FreeCAD.Vector(0,1,0)]
    self.execute(obj)

  def onChanged(self, fp, prop):
    #FreeCAD.Console.PrintMessage("Changed Pipe feature\n")
    return None

  def execute(self, fp):
    if fp.BendAngle<180:
      if fp.thk>fp.OD/2:
        fp.thk=fp.OD/2.1
      fp.ID=fp.OD-2*fp.thk
      fp.Profile=str(fp.OD)+"x"+str(fp.thk)
      CenterOfBend=FreeCAD.Vector(fp.BendRadius,fp.BendRadius,0)
      ## make center-line ##
      R=Part.makeCircle(fp.BendRadius,CenterOfBend,FreeCAD.Vector(0,0,1),225-float(fp.BendAngle)/2,225+float(fp.BendAngle)/2)
      ## move the cl so that Placement.Base is the center of elbow ##
      from math import pi, cos, sqrt
      d=(fp.BendRadius*sqrt(2)-fp.BendRadius/cos(fp.BendAngle/180*pi/2))
      P=FreeCAD.Vector(-d*cos(pi/4),-d*cos(pi/4),0)
      R.translate(P)
      ## calculate Ports position ##
      fp.Ports=[R.valueAt(R.FirstParameter),R.valueAt(R.LastParameter)]
      ## make the shape of the elbow ##
      c=Part.makeCircle(fp.OD/2,fp.Ports[0],R.tangentAt(R.FirstParameter)*-1)
      b=Part.makeSweepSurface(R,c)
      p1=Part.Face(Part.Wire(c))
      p2=Part.Face(Part.Wire(Part.makeCircle(fp.OD/2,fp.Ports[1],R.tangentAt(R.LastParameter))))
      sol=Part.Solid(Part.Shell([b,p1,p2]))
      planeFaces=[f for f in sol.Faces if type(f.Surface)==Part.Plane]
      elbow=sol.makeThickness(planeFaces,-fp.thk,1.e-3)
      fp.Shape = elbow
      
class Flange():
  '''Class for object PType="Flange"
  Flange(obj,[DN="DN50",FlangeType="SO", D=160, d=60.3,df=132, f=14 t=15,n=4])
  obj: the "App::FeaturePython object"
  DN (string): nominal diameter
  FlangeType (string): type of Flange
  D (float): flange diameter
  d (float): bore diameter
  df (float): bolts holes distance
  f (float): bolts holes diameter
  t (float): flange thickness
  n (int): nr. of bolts
  '''
  def __init__(self, obj,DN="DN50",FlangeType="SO",D=160,d=60.3,df=132,f=14, t=15, n=4):
    obj.Proxy = self
    obj.addProperty("App::PropertyString","PType","Flange","Type of pipeFeature").PType="Flange"
    obj.addProperty("App::PropertyString","PRating","Pipe","Rating of pipeFeature").PRating="DIN-PN16"
    obj.addProperty("App::PropertyString","PSize","Flange","Nominal diameter").PSize=DN
    obj.addProperty("App::PropertyString","FlangeType","Flange","Type of flange").FlangeType=FlangeType
    obj.addProperty("App::PropertyLength","D","Flange","Flange diameter").D=D
    obj.addProperty("App::PropertyLength","d","Flange","Bore diameter").d=d
    obj.addProperty("App::PropertyLength","df","Flange","Bolts distance").df=df
    obj.addProperty("App::PropertyLength","f","Flange","Bolts hole diameter").f=f
    obj.addProperty("App::PropertyLength","t","Flange","Thickness of flange").t=t
    obj.addProperty("App::PropertyInteger","n","Flange","Nr. of bolts").n=n
  def onChanged(self, fp, prop):
    #FreeCAD.Console.PrintMessage("Changed Pipe feature\n")
    return None
  def execute(self, fp):
    base=Part.Face(Part.Wire(Part.makeCircle(fp.D/2)))
    if fp.d>0:
      base=base.cut(Part.Face(Part.Wire(Part.makeCircle(fp.d/2))))
    if fp.n>0:
      hole=Part.Face(Part.Wire(Part.makeCircle(fp.f/2,FreeCAD.Vector(fp.df/2,0,0),FreeCAD.Vector(0,0,1))))
      hole.rotate(FreeCAD.Vector(0,0,0),FreeCAD.Vector(0,0,1),360/fp.n/2)
      for i in list(range(fp.n)):
        base=base.cut(hole)
        hole.rotate(FreeCAD.Vector(0,0,0),FreeCAD.Vector(0,0,1),360/fp.n)
    fp.Shape = base.extrude(FreeCAD.Vector(0,0,fp.t))
    
class Shell():
  def __init__(self,obj,L=800,W=400,H=500,thk=6):
    obj.Proxy=self
    obj.addProperty("App::PropertyLength","L","Tank","Tank's length").L=L
    obj.addProperty("App::PropertyLength","W","Tank","Tank's width").W=W
    obj.addProperty("App::PropertyLength","H","Tank","Tank's height").H=H
    obj.addProperty("App::PropertyLength","thk","Tank","Thikness of tank's shell").thk=thk
  def onChanged(self, fp, prop):
    return None
  def execute(self, fp):
    O=FreeCAD.Vector(0,0,0)
    vectL=FreeCAD.Vector(fp.L,0,0)
    vectW=FreeCAD.Vector(0,fp.W,0)
    vectH=FreeCAD.Vector(0,0,fp.H)
    base=[vectL,vectW,vectH]
    outline=[]
    for i in range(3):
      f1=Part.Face(Part.makePolygon([O,base[0],base[0]+base[1],base[1],O]))
      outline.append(f1)
      f2=f1.copy()
      f2.translate(base[2])
      outline.append(f2)
      base.append(base.pop(0))
    box=Part.Solid(Part.Shell(outline))
    tank=box.makeThickness([box.Faces[0],box.Faces[2]],-fp.thk,1.e-3)
    fp.Shape=tank
    
    
