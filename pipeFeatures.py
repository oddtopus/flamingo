#(c) 2016 R. T. LGPL: part of Flamingo tools w.b. for FreeCAD

__title__="pypeTools objects"
__author__="oddtopus"
__url__="github.com/oddtopus/flamingo"
__license__="LGPL 3"
objs=['Pipe','Elbow','Reduct','Cap','Flange','Ubolt','Valve']
metaObjs=['PypeLine','PypeBranch']

import FreeCAD, FreeCADGui, Part, frameCmd, pipeCmd
from copy import copy
from os.path import join, dirname, abspath

vO=FreeCAD.Vector(0,0,0)
vX=FreeCAD.Vector(1,0,0)
vY=FreeCAD.Vector(0,1,0)
vZ=FreeCAD.Vector(0,0,1)

################ CLASSES ###########################

class pypeType(object):
  def __init__(self,obj):
    obj.Proxy = self
    obj.addProperty("App::PropertyString","PType","PBase","Type of tubeFeature").PType
    obj.addProperty("App::PropertyString","PRating","PBase","Rating of pipeFeature").PRating
    obj.addProperty("App::PropertyString","PSize","PBase","Nominal diameter").PSize
    obj.addProperty("App::PropertyVectorList","Ports","PBase","Ports position relative to the origin of Shape")
    obj.addProperty("App::PropertyFloat","Kv","PBase","Flow factor (m3/h/bar)").Kv
    obj.addExtension("Part::AttachExtensionPython",obj)
    #self.obj=obj sostituire con obj.Name e usare metodi per recuperare obj
    self.Name=obj.Name
  def execute(self, fp):
    fp.positionBySupport() # to recomute placement according the Support
  def nearestPort (self,point=None):
    '''
    nearestPort (point=None)
      Returns the Port nearest to  point 
      or to the selected geometry.
      (<portNr>, <portPos>, <portDir>)
    '''
    obj=FreeCAD.ActiveDocument.getObject(self.Name)
    if not point and FreeCADGui.ActiveDocument:
      try:
        selex=FreeCADGui.Selection.getSelectionEx()
        target=selex[0].Object
        so=selex[0].SubObjects[0]
      except:
        FreeCAD.Console.PrintError('No geometry selected\n')
        return None
      if type(so)==Part.Vertex: point=so.Point
      else: point=so.CenterOfMass
    if point:
      pos=pipeCmd.portsPos(obj)[0]; Z=pipeCmd.portsDir(obj)[0]
      i=nearest=0
      if len(obj.Ports)>1:
        for p in pipeCmd.portsPos(obj)[1:] :
          i+=1
          if (p-point).Length<(pos-point).Length:
            pos=p
            Z=pipeCmd.portsDir(obj)[i]
            nearest=i
      return nearest, pos, Z

class Pipe(pypeType):
  '''Class for object PType="Pipe"
  Pipe(obj,[PSize="DN50",OD=60.3,thk=3, H=100])
    obj: the "App::FeaturePython object"
    PSize (string): nominal diameter
    OD (float): outside diameter
    thk (float): shell thickness
    H (float): length of pipe'''
  def __init__(self, obj,DN="DN50",OD=60.3,thk=3, H=100):
    # initialize the parent class
    super(Pipe,self).__init__(obj)
    # define common properties
    obj.PType="Pipe"
    obj.PRating="SCH-STD"
    obj.PSize=DN
    # define specific properties
    obj.addProperty("App::PropertyLength","OD","Pipe","Outside diameter").OD=OD
    obj.addProperty("App::PropertyLength","thk","Pipe","Wall thickness").thk=thk
    obj.addProperty("App::PropertyLength","ID","Pipe","Inside diameter").ID=obj.OD-2*obj.thk
    obj.addProperty("App::PropertyLength","Height","Pipe","Length of tube").Height=H
    obj.addProperty("App::PropertyString","Profile","Pipe","Section dim.").Profile=str(obj.OD)+"x"+str(obj.thk)
  def onChanged(self, fp, prop):
    if prop=='ID' and fp.ID<fp.OD:
      fp.thk=(fp.OD-fp.ID)/2
  def execute(self, fp):
    if fp.thk>fp.OD/2:
      fp.thk=fp.OD/2
    fp.ID=fp.OD-2*fp.thk
    fp.Profile=str(fp.OD)+"x"+str(fp.thk)
    if fp.ID:
      fp.Shape = Part.makeCylinder(fp.OD/2,fp.Height).cut(Part.makeCylinder(fp.ID/2,fp.Height))
    else:
      fp.Shape = Part.makeCylinder(fp.OD/2,fp.Height)
    fp.Ports=[FreeCAD.Vector(),FreeCAD.Vector(0,0,float(fp.Height))]
    super(Pipe,self).execute(fp) # perform common operations

class Elbow(pypeType):
  '''Class for object PType="Elbow"
  Elbow(obj,[PSize="DN50",OD=60.3,thk=3,BA=90,BR=45.225])
    obj: the "App::FeaturePython" object
    PSize (string): nominal diameter
    OD (float): outside diameter
    thk (float): shell thickness
    BA (float): bend angle
    BR (float): bend radius'''
  def __init__(self, obj,DN="DN50",OD=60.3,thk=3,BA=90,BR=45.225):
    # initialize the parent class
    super(Elbow,self).__init__(obj)
    # define common properties
    obj.PType="Elbow"
    obj.PRating="SCH-STD"
    obj.PSize=DN
    # define specific properties
    obj.addProperty("App::PropertyLength","OD","Elbow","Outside diameter").OD=OD
    obj.addProperty("App::PropertyLength","thk","Elbow","Wall thickness").thk=thk
    obj.addProperty("App::PropertyLength","ID","Elbow","Inside diameter").ID=obj.OD-2*obj.thk
    obj.addProperty("App::PropertyAngle","BendAngle","Elbow","Bend Angle").BendAngle=BA
    obj.addProperty("App::PropertyLength","BendRadius","Elbow","Bend Radius").BendRadius=BR
    obj.addProperty("App::PropertyString","Profile","Elbow","Section dim.").Profile=str(obj.OD)+"x"+str(obj.thk)
    #obj.Ports=[FreeCAD.Vector(1,0,0),FreeCAD.Vector(0,1,0)]
    self.execute(obj)
  def onChanged(self, fp, prop):
    if prop=='ID' and fp.ID<fp.OD:
      fp.thk=(fp.OD-fp.ID)/2
  def execute(self, fp):
    if fp.BendAngle<180:
      if fp.thk>fp.OD/2:
        fp.thk=fp.OD/2
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
      #elbow=sol.makeThickness(planeFaces,-fp.thk,1.e-3)
      #fp.Shape = elbow
      if fp.thk<fp.OD/2:
        fp.Shape=sol.makeThickness(planeFaces,-fp.thk,1.e-3)
      else:
        fp.Shape=sol
      super(Elbow,self).execute(fp) # perform common operations
    
class Flange(pypeType):
  '''Class for object PType="Flange"
  Flange(obj,[PSize="DN50",FlangeType="SO", D=160, d=60.3,df=132, f=14 t=15,n=4, trf=0, drf=0, twn=0, dwn=0, ODp=0])
    obj: the "App::FeaturePython" object
    PSize (string): nominal diameter
    FlangeType (string): type of Flange
    D (float): flange diameter
    d (float): bore diameter
    df (float): bolts holes distance
    f (float): bolts holes diameter
    t (float): flange thickness
    n (int): nr. of bolts
    trf (float): raised-face thikness
    drf (float): raised-face diameter
    twn (float): welding-neck thikness
    dwn (float): welding-neck diameter
    ODp (float): outside diameter of pipe for wn flanges
  '''
  def __init__(self, obj,DN="DN50",FlangeType="SO",D=160,d=60.3,df=132,f=14, t=15, n=4, trf=0, drf=0, twn=0, dwn=0, ODp=0):
    # initialize the parent class
    super(Flange,self).__init__(obj)
    # define common properties
    obj.PType="Flange"
    obj.PRating="DIN-PN16"
    obj.PSize=DN
    # define specific properties
    obj.addProperty("App::PropertyString","FlangeType","Flange","Type of flange").FlangeType=FlangeType
    obj.addProperty("App::PropertyLength","D","Flange","Flange diameter").D=D
    obj.addProperty("App::PropertyLength","d","Flange","Bore diameter").d=d
    obj.addProperty("App::PropertyLength","df","Flange","Bolts distance").df=df
    obj.addProperty("App::PropertyLength","f","Flange","Bolts hole diameter").f=f
    obj.addProperty("App::PropertyLength","t","Flange","Thickness of flange").t=t
    obj.addProperty("App::PropertyInteger","n","Flange","Nr. of bolts").n=n
    obj.addProperty("App::PropertyLength","trf","Flange2","Thickness of raised face").trf=trf
    obj.addProperty("App::PropertyLength","drf","Flange2","Diameter of raised face").drf=drf
    obj.addProperty("App::PropertyLength","twn","Flange2","Length of welding neck").twn=twn
    obj.addProperty("App::PropertyLength","dwn","Flange2","Diameter of welding neck").dwn=dwn
    obj.addProperty("App::PropertyLength","ODp","Flange2","Outside diameter of pipe").ODp=ODp
  def onChanged(self, fp, prop):
    return None
  def execute(self, fp):
    base=Part.Face(Part.Wire(Part.makeCircle(fp.D/2)))
    if fp.d>0:
      base=base.cut(Part.Face(Part.Wire(Part.makeCircle(fp.d/2))))
    if fp.n>0:
      hole=Part.Face(Part.Wire(Part.makeCircle(fp.f/2,FreeCAD.Vector(fp.df/2,0,0),FreeCAD.Vector(0,0,1))))
      hole.rotate(FreeCAD.Vector(0,0,0),FreeCAD.Vector(0,0,1),360.0/fp.n/2)
      for i in list(range(fp.n)):
        base=base.cut(hole)
        hole.rotate(FreeCAD.Vector(0,0,0),FreeCAD.Vector(0,0,1),360.0/fp.n)
    flange = base.extrude(FreeCAD.Vector(0,0,fp.t))
    try: # Flange2: raised-face and welding-neck
      if fp.trf>0 and fp.drf>0:
        rf=Part.makeCylinder(fp.drf/2,fp.trf,vO,vZ*-1).cut(Part.makeCylinder(fp.d/2,fp.trf,vO,vZ*-1))
        flange=flange.fuse(rf)
      if fp.dwn>0 and fp.twn>0 and fp.ODp>0:
        wn=Part.makeCone(fp.dwn/2,fp.ODp/2,fp.twn,vZ*float(fp.t)).cut(Part.makeCylinder(fp.d/2,fp.twn,vZ*float(fp.t)))
        flange=flange.fuse(wn)
    except:
      pass
    fp.Shape = flange
    fp.Ports=[FreeCAD.Vector(),FreeCAD.Vector(0,0,float(fp.t))]
    super(Flange,self).execute(fp) # perform common operations

class Reduct(pypeType):
  '''Class for object PType="Reduct"
  Reduct(obj,[PSize="DN50",OD=60.3, OD2= 48.3, thk=3, thk2=None, H=None, conc=True])
    obj: the "App::FeaturePython object"
    PSize (string): nominal diameter (major)
    OD (float): major outside diameter
    OD2 (float): minor outside diameter
    thk (float): major shell thickness
    thk2 (float): minor shell thickness
    H (float): length of reduction
    conc (bool): True for a concentric reduction, False for eccentric
  If thk2 is None or 0, the same thickness is used at both ends.
  If H is None or 0, the length of the reduction is calculated as 3x(OD-OD2).
    '''
  def __init__(self, obj,DN="DN50",OD=60.3,OD2=48.3,thk=3, thk2=None, H=None, conc=True):
    # initialize the parent class
    super(Reduct,self).__init__(obj)
    # define common properties
    obj.PType="Reduct"
    obj.PRating="SCH-STD"
    obj.PSize=DN
    # define specific properties
    obj.addProperty("App::PropertyLength","OD","Reduct","Major diameter").OD=OD
    obj.addProperty("App::PropertyLength","OD2","Reduct","Minor diameter").OD2=OD2
    obj.addProperty("App::PropertyLength","thk","Reduct","Wall thickness").thk=thk
    obj.addProperty("App::PropertyLength","thk2","Reduct","Wall thickness")
    if not thk2:
      obj.thk2=thk
    else:
      obj.thk2=thk2
    obj.addProperty("App::PropertyBool","calcH","Reduct","Make the lenght variable")
    obj.addProperty("App::PropertyLength","Height","Reduct","Length of reduct")
    if not H:
      obj.calcH=True
      obj.Height=3*(obj.OD-obj.OD2)
    else:
      obj.calcH=False
      obj.Height=float(H)
    obj.addProperty("App::PropertyString","Profile","Reduct","Section dim.").Profile=str(obj.OD)+"x"+str(obj.OD2)
    obj.addProperty("App::PropertyBool","conc","Reduct","Concentric or Eccentric").conc=conc
  def onChanged(self, fp, prop):
    return None
  def execute(self, fp):
    if fp.OD>fp.OD2:
      if fp.calcH or fp.Height==0:
        fp.Height=3*(fp.OD-fp.OD2)
      fp.Profile=str(fp.OD)+"x"+str(fp.OD2)
      if fp.conc:
        sol = Part.makeCone(fp.OD/2,fp.OD2/2,fp.Height)
        if fp.thk<fp.OD/2 and fp.thk2<fp.OD2/2:
          fp.Shape=sol.cut(Part.makeCone(fp.OD/2-fp.thk,fp.OD2/2-fp.thk2,fp.Height))
        else:
          fp.Shape=sol
        fp.Ports=[FreeCAD.Vector(),FreeCAD.Vector(0,0,float(fp.Height))]
      else:
        C=Part.makeCircle(fp.OD/2,FreeCAD.Vector(0,0,0),FreeCAD.Vector(0,0,1))
        c=Part.makeCircle(fp.OD2/2,FreeCAD.Vector(0,0,0),FreeCAD.Vector(0,0,1))
        c.translate(FreeCAD.Vector((fp.OD-fp.OD2)/2,0,fp.Height))
        sol=Part.makeLoft([c,C],True)
        if fp.thk<fp.OD/2 and fp.thk2<fp.OD2/2:
          C=Part.makeCircle(fp.OD/2-fp.thk,FreeCAD.Vector(0,0,0),FreeCAD.Vector(0,0,1))
          c=Part.makeCircle(fp.OD2/2-fp.thk2,FreeCAD.Vector(0,0,0),FreeCAD.Vector(0,0,1))
          c.translate(FreeCAD.Vector((fp.OD-fp.OD2)/2,0,fp.Height))
          fp.Shape=sol.cut(Part.makeLoft([c,C],True))
        else:
          fp.Shape=sol
        fp.Ports=[FreeCAD.Vector(),FreeCAD.Vector((fp.OD-fp.OD2)/2,0,float(fp.Height))]
    super(Reduct,self).execute(fp) # perform common operations
    
class Cap(pypeType):
  '''Class for object PType="Cap"
  Cap(obj,[PSize="DN50",OD=60.3,thk=3])
    obj: the "App::FeaturePython object"
    PSize (string): nominal diameter
    OD (float): outside diameter
    thk (float): shell thickness'''
  def __init__(self, obj,DN="DN50",OD=60.3,thk=3):
    # initialize the parent class
    super(Cap,self).__init__(obj)
    # define common properties
    obj.PType="Cap"
    obj.PRating="SCH-STD"
    obj.PSize=DN
    # define specific properties
    obj.addProperty("App::PropertyLength","OD","Cap","Outside diameter").OD=OD
    obj.addProperty("App::PropertyLength","thk","Cap","Wall thickness").thk=thk
    obj.addProperty("App::PropertyLength","ID","Cap","Inside diameter").ID=obj.OD-2*obj.thk
    obj.addProperty("App::PropertyString","Profile","Cap","Section dim.").Profile=str(obj.OD)+"x"+str(obj.thk)
  def onChanged(self, fp, prop):
    return None
  def execute(self, fp):
    if fp.thk>fp.OD/2:
      fp.thk=fp.OD/2.1
    fp.ID=fp.OD-2*fp.thk
    fp.Profile=str(fp.OD)+"x"+str(fp.thk)
    D=float(fp.OD)
    s=float(fp.thk)
    sfera=Part.makeSphere(0.8*D,FreeCAD.Vector(0,0,-(0.55*D-6*s)))
    cilindro=Part.makeCylinder(D/2,D*1.7,FreeCAD.Vector(0,0,-(0.55*D-6*s+1)),FreeCAD.Vector(0,0,1))
    common=sfera.common(cilindro)
    fil=common.makeFillet(D/6.5,common.Edges)
    cut=fil.cut(Part.makeCylinder(D*1.1,D*2,FreeCAD.Vector(0,0,0),FreeCAD.Vector(0,0,-1)))
    cap=cut.makeThickness([f for f in cut.Faces if type(f.Surface)==Part.Plane],-s,1.e-3)
    fp.Shape = cap
    fp.Ports=[FreeCAD.Vector()]
    super(Cap,self).execute(fp) # perform common operations
    
class PypeLine2(pypeType):
  '''Class for object PType="PypeLine2"
  This object represent a collection of objects "PType" that are updated with the 
  methods defined in the Python class.
  At present time it creates, with the method obj.Proxy.update(,obj,[edges]), pipes and curves over 
  the given edges and collect them in a group named according the object's .Label.
  PypeLine2 features also the optional attribute ".Base":
  - Base can be a Wire or a Sketch or any object which has edges in its Shape.
  - Running "obj.Proxy.update(obj)", without any [edges], the class attempts to render the pypeline 
  (Pipe and Elbow objects) on the "obj.Base" edges: for well defined geometries 
  and open paths, this usually leads to acceptable results.
  - Running "obj.Proxy.purge(obj)" deletes from the model all Pipes and Elbows 
  that belongs to the pype-line.  
  - It's possible to add other objects afterwards (such as Flange, Reduct...) 
  using the relevant insertion dialogs but remember that these won't be updated 
  when the .Base is changed and won't be deleted if the pype-line is purged.
  - If Base is None, PypeLine2 behaves like a bare container of objects, 
  with possibility to group them automatically and extract the part-list. 
  '''
  def __init__(self, obj,DN="DN50",PRating="SCH-STD",OD=60.3,thk=3,BR=None, lab=None):
    # initialize the parent class
    super(PypeLine2,self).__init__(obj)
    # define common properties
    obj.PType="PypeLine"
    obj.PSize=DN
    obj.PRating=PRating
    if lab:
      obj.Label=lab
    # define specific properties
    if not BR:
      BR=0.75*OD
    obj.addProperty("App::PropertyLength","BendRadius","PypeLine2","the radius of bending").BendRadius=BR
    obj.addProperty("App::PropertyLength","OD","PypeLine2","Outside diameter").OD=OD
    obj.addProperty("App::PropertyLength","thk","PypeLine2","Wall thickness").thk=thk
    obj.addProperty("App::PropertyString","Group","PypeLine2","The group.").Group=obj.Label+"_pieces"
    group=FreeCAD.activeDocument().addObject("App::DocumentObjectGroup",obj.Group)
    group.addObject(obj)
    FreeCAD.Console.PrintWarning("Created group "+obj.Group+"\n")
    obj.addProperty("App::PropertyLink","Base","PypeLine2","the edges")
  def onChanged(self, fp, prop):
    if prop=='Label' and len(fp.InList):
      fp.InList[0].Label=fp.Label+"_pieces"
      fp.Group=fp.Label+"_pieces"
    if hasattr(fp,'Base') and prop=='Base' and fp.Base:
      FreeCAD.Console.PrintWarning(fp.Label+' Base has changed to '+fp.Base.Label+'\n')
    if prop=='OD':
      fp.BendRadius=0.75*fp.OD
  def purge(self,fp):
    group=FreeCAD.activeDocument().getObjectsByLabel(fp.Group)[0]
    for o in group.OutList:
      if hasattr(o,'PType') and o.PType in ['Pipe','Elbow']:
        FreeCAD.activeDocument().removeObject(o.Name)
  def update(self,fp,edges=None):
    import pipeCmd, frameCmd
    from DraftVecUtils import rounded
    from math import degrees
    if not edges and hasattr(fp.Base,'Shape'):
      edges=fp.Base.Shape.Edges
      if not edges:
        FreeCAD.Console.PrintError('Base has not valid edges\n')
        return
    pipes=list()
    for e in edges:
      #---Create the tube---
      p=pipeCmd.makePipe([fp.PSize,fp.OD,fp.thk,e.Length],pos=e.valueAt(0),Z=e.tangentAt(0))
      p.PRating=fp.PRating
      p.PSize=fp.PSize
      pipeCmd.moveToPyLi(p,fp.Label)
      pipes.append(p)
      n=len(pipes)-1
      if n and not frameCmd.isParallel(frameCmd.beamAx(pipes[n]),frameCmd.beamAx(pipes[n-1])):
        #---Create the curve---
        propList=[fp.PSize,fp.OD,fp.thk,90,fp.BendRadius]
        c=pipeCmd.makeElbowBetweenThings(edges[n],edges[n-1],propList)
        portA,portB=[c.Placement.multVec(port) for port in c.Ports]
        #---Trim the tube---
        p1,p2=pipes[-2:]
        frameCmd.extendTheBeam(p1,portA)
        frameCmd.extendTheBeam(p2,portB)
        pipeCmd.moveToPyLi(c,fp.Label)
  def execute(self, fp):
    return None

class ViewProviderPypeLine:
  def __init__(self,vobj):
    vobj.Proxy = self
  def getIcon(self):
    from os.path import join, dirname, abspath
    return join(dirname(abspath(__file__)),"icons","pypeline.svg")
  def attach(self, vobj):
    self.ViewObject = vobj
    self.Object = vobj.Object

class Ubolt():
  '''Class for object PType="Clamp"
  UBolt(obj,[PSize="DN50",ClampType="U-bolt", C=76, H=109, d=10])
    obj: the "App::FeaturePython" object
    PSize (string): nominal diameter
    ClampType (string): the clamp type or standard
    C (float): the diameter of the U-bolt
    H (float): the total height of the U-bolt
    d (float): the rod diameter
  '''
  def __init__(self, obj,DN="DN50",ClampType="DIN-UBolt", C=76, H=109, d=10):
    obj.Proxy = self
    obj.addProperty("App::PropertyString","PType","Ubolt","Type of pipeFeature").PType="Clamp"
    obj.addProperty("App::PropertyString","ClampType","Ubolt","Type of clamp").ClampType=ClampType
    obj.addProperty("App::PropertyString","PSize","Ubolt","Size of clamp").PSize=DN
    obj.addProperty("App::PropertyLength","C","Ubolt","Arc diameter").C=C
    obj.addProperty("App::PropertyLength","H","Ubolt","Overall height").H=H
    obj.addProperty("App::PropertyLength","d","Ubolt","Rod diameter").d=d
    obj.addProperty("App::PropertyString","thread","Ubolt","Size of thread").thread="M"+str(d)
    obj.addProperty("App::PropertyVectorList","Ports","PBase","Ports position relative to the origin of Shape")
  def onChanged(self, fp, prop):
    return None
  def execute(self, fp):
    fp.thread="M"+str(float(fp.d))
    c=Part.makeCircle(fp.C/2,FreeCAD.Vector(0,0,0),FreeCAD.Vector(0,0,1),0,180)
    l1=Part.makeLine((fp.C/2,0,0),(fp.C/2,fp.C/2-fp.H,0))
    l2=Part.makeLine((-fp.C/2,0,0),(-fp.C/2,fp.C/2-fp.H,0))
    p=Part.Face(Part.Wire(Part.makeCircle(fp.d/2,c.valueAt(c.FirstParameter),c.tangentAt(c.FirstParameter))))
    path=Part.Wire([c,l1,l2])
    fp.Shape=path.makePipe(p)
    fp.Ports=[FreeCAD.Vector(0,0,1)]

class Shell():
  '''
  Class for a lateral-shell-of-tank object
  Shell(obj[,L=800,W=400,H=500,thk=6])
    obj: the "App::FeaturePython" object
    L (float): the length
    W (float): the width
    H (float): the height
    thk1 (float): the shell thickness
    thk2 (float): the top thickness
  '''
  def __init__(self,obj,L=800,W=400,H=500,thk1=6, thk2=8):
    obj.Proxy=self
    obj.addProperty("App::PropertyLength","L","Tank","Tank's length").L=L
    obj.addProperty("App::PropertyLength","W","Tank","Tank's width").W=W
    obj.addProperty("App::PropertyLength","H","Tank","Tank's height").H=H
    obj.addProperty("App::PropertyLength","thk1","Tank","Thikness of tank's shell").thk1=thk1
    obj.addProperty("App::PropertyLength","thk2","Tank","Thikness of tank's top").thk2=thk2
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
    tank=box.makeThickness([box.Faces[0],box.Faces[2]],-fp.thk1,1.e-3)
    top=Part.makeBox(fp.L-2*fp.thk1,fp.W-2*fp.thk1,fp.thk2,FreeCAD.Vector(fp.thk1,fp.thk1,fp.H-2*fp.thk2))
    fp.Shape=Part.makeCompound([tank,top])
    #fp.positionBySupport() # to recomute placement according the Support
    
class ViewProviderPypeBranch:
  def __init__(self,vobj):
    vobj.Proxy = self
    vobj.addExtension("Gui::ViewProviderGroupExtensionPython",self)  # GROUP test in progress!
    vobj.ExtensionProxy=self # GROUP test in progress!
  def getIcon(self):
    from os.path import join, dirname, abspath
    return join(dirname(abspath(__file__)),"icons","branch.svg")
  def attach(self, vobj):
    self.ViewObject = vobj
    self.Object = vobj.Object
  def setEdit(self,vobj,mode):
    return False
  def unsetEdit(self,vobj,mode):
    return
  def __getstate__(self):
    return None
  def __setstate__(self,state):
    return None
  def claimChildren(self):
    children=[FreeCAD.ActiveDocument.getObject(name) for name in self.Object.Tubes+self.Object.Curves]
    return children #self.Object.Tubes + self.Object.Curves
  def onDelete(self, feature, subelements): # subelements is a tuple of strings
    return True

class Valve(pypeType):
  '''Class for object PType="Valve"
  Pipe(obj,[PSize="DN50",VType="ball", OD=60.3, H=100])
    obj: the "App::FeaturePython object"
    PSize (string): nominal diameter
    PRating (string): ! the valve's type !
    OD (float): outside diameter
    H (float): length of valve'''
  def __init__(self, obj,DN="DN50",VType="ball",OD=72, ID=50, H=40, Kv=150):
    # initialize the parent class
    super(Valve,self).__init__(obj)
    # define common properties
    obj.PType="Valve"
    obj.PRating=VType
    obj.PSize=DN
    obj.Kv=Kv
    # define specific properties
    obj.addProperty("App::PropertyLength","OD","Valve","Outside diameter").OD=OD
    obj.addProperty("App::PropertyLength","ID","Valve","Inside diameter").ID=ID
    obj.addProperty("App::PropertyLength","Height","Valve","Length of tube").Height=H
  def execute(self, fp):
    c=Part.makeCone(fp.OD/2,fp.OD/5,fp.Height/2)
    v=c.fuse(c.mirror(FreeCAD.Vector(0,0,fp.Height/2),FreeCAD.Vector(0,0,1)))
    if fp.PRating.find('ball')+1 or fp.PRating.find('globe')+1:
      r=min(fp.Height*0.45,fp.OD/2)
      v=v.fuse(Part.makeSphere(r,FreeCAD.Vector(0,0,fp.Height/2)))
    fp.Shape = v
    fp.Ports=[FreeCAD.Vector(),FreeCAD.Vector(0,0,float(fp.Height))]
    super(Valve,self).execute(fp) # perform common operations
    
class PypeBranch2(pypeType): # use AttachExtensionPython
  '''Class for object PType="PypeBranch2"
  Single-line pipe branch linked to its center-line using AttachExtensionPython
  ex: a=PypeBranch2(obj,base,DN="DN50",PRating="SCH-STD",OD=60.3,thk=3,BR=None)
    type(obj)=FeaturePython
    type(base)=DWire or SketchObject
  '''
  def __init__(self, obj,base,DN="DN50",PRating="SCH-STD",OD=60.3,thk=3,BR=None):
    # initialize the parent class
    super(PypeBranch2,self).__init__(obj)
    # define common properties
    obj.PType="PypeBranch"
    obj.PSize=DN
    obj.PRating=PRating
    # define specific properties
    obj.addProperty("App::PropertyLength","OD","PypeBranch","Outside diameter").OD=OD
    obj.addProperty("App::PropertyLength","thk","PypeBranch","Wall thickness").thk=thk
    if not BR: BR=0.75*OD
    obj.addProperty("App::PropertyLength","BendRadius","PypeBranch","Bend Radius").BendRadius=BR
    obj.addProperty("App::PropertyStringList","Tubes","PypeBranch","The tubes of the branch.")
    obj.addProperty("App::PropertyStringList","Curves","PypeBranch","The curves of the branch.")
    obj.addProperty("App::PropertyLink","Base","PypeBranch","The path.")
    if hasattr(base,"Shape") and base.Shape.Edges: 
      obj.Base=base
    else:
      FreeCAD.Console.PrintError('Base not valid\n')
    obj.addExtension("App::GroupExtensionPython",obj)  # GROUP test in progress!
  def onChanged(self, fp, prop):
    if prop=='Base' and hasattr(fp,'OD') and hasattr(fp,'thk') and hasattr(fp,'BendRadius'):
      self.purge(fp)
      self.redraw(fp)
    if prop=='BendRadius' and hasattr(fp,'Curves'):
      BR=fp.BendRadius
      for curve in [FreeCAD.ActiveDocument.getObject(name) for name in fp.Curves]:
        curve.BendRadius=BR
    if prop=='OD' and hasattr(fp,'Tubes') and hasattr(fp,'Curves'):
      OD=fp.OD
      for obj in [FreeCAD.ActiveDocument.getObject(name) for name in fp.Tubes+fp.Curves]:
        if obj.PType=='Elbow': obj.BendRadius=OD*.75
        obj.OD=OD
      fp.BendRadius=OD*.75
    if prop=='thk' and hasattr(fp,'Tubes') and hasattr(fp,'Curves'):
      thk=fp.thk
      for obj in [FreeCAD.ActiveDocument.getObject(name) for name in fp.Tubes+fp.Curves]:
        if hasattr(obj,'thk'): obj.thk=thk
  def execute(self, fp):
    if len(fp.Tubes)!=len(fp.Base.Shape.Edges):
      self.purge(fp)
      self.redraw(fp)
      return
    from math import tan
    for i in range(len(fp.Tubes)):
      L=fp.Base.Shape.Edges[i].Length
      R=fp.BendRadius
      # adjust the curve
      if i<len(fp.Curves):
        c=FreeCAD.ActiveDocument.getObject(fp.Curves[i])
        v1,v2=[e.tangentAt(0) for e in fp.Base.Shape.Edges[i:i+2]]
        pipeCmd.placeTheElbow(c,v1,v2) 
        alfa=float(v1.getAngle(v2))/2
        L-=float(R*tan(alfa)) 
      # adjust the pipes
      if i: 
        v1,v2=[e.tangentAt(0) for e in fp.Base.Shape.Edges[i-1:i+1]]
        alfa=float(v1.getAngle(v2))/2
        tang=float(R*tan(alfa)) 
        L-=tang
        FreeCAD.ActiveDocument.getObject(fp.Tubes[i]).AttachmentOffset.Base=FreeCAD.Vector(0,0,tang)
      FreeCAD.ActiveDocument.getObject(fp.Tubes[i]).Height=L
  def redraw(self,fp): 
    from math import tan, degrees
    tubes=list()
    curves=list()
    if fp.Base:
      for i in range(len(fp.Base.Shape.Edges)):
        e=fp.Base.Shape.Edges[i]
        L=e.Length
        R=float(fp.BendRadius)
        offset=0
        #---Create the tube---
        if i>0: 
          alfa=e.tangentAt(0).getAngle(fp.Base.Shape.Edges[i-1].tangentAt(0))/2
          L-=R*tan(alfa)
          offset=R*tan(alfa)
        if i<(len(fp.Base.Shape.Edges)-1): 
          alfa=e.tangentAt(0).getAngle(fp.Base.Shape.Edges[i+1].tangentAt(0))/2
          L-=R*tan(alfa)
        eSupport='Edge'+str(i+1)
        t=pipeCmd.makePipe([fp.PSize,float(fp.OD),float(fp.thk),L])
        t.PRating=fp.PRating
        t.PSize=fp.PSize
        t.Support = [(fp.Base,eSupport)]
        t.MapMode = 'NormalToEdge'
        t.MapReversed = True
        t.AttachmentOffset=FreeCAD.Placement(FreeCAD.Vector(0,0,offset),FreeCAD.Rotation())
        tubes.append(t.Name)
        #---Create the curve---
        if i>0:
          e0=fp.Base.Shape.Edges[i-1]
          alfa=degrees(e0.tangentAt(0).getAngle(e.tangentAt(0)))
          c=pipeCmd.makeElbow([fp.PSize,float(fp.OD),float(fp.thk),alfa,R])
          c.PRating=fp.PRating
          c.PSize=fp.PSize
          O='Vertex'+str(i+1)
          c.MapReversed = False
          c.Support = [(fp.Base,O)]
          c.MapMode = 'Translate'
          pipeCmd.placeTheElbow(c,e0.tangentAt(0),e.tangentAt(0))
          curves.append(c.Name)
        fp.Tubes=tubes
        fp.Curves=curves
  def purge(self,fp):
    if hasattr(fp,'Tubes'):
      for name in fp.Tubes: FreeCAD.ActiveDocument.removeObject(name)
      fp.Tubes=[]
    if hasattr(fp,'Curves'):
      for name in fp.Curves: FreeCAD.ActiveDocument.removeObject(name)
      fp.Curves=[]

