# FreeCAD Frame Tools module  
# (c) 2016 Riccardo Treu LGPL
import FreeCAD, FreeCADGui, frameCmd

class frameObserverPrototype(object): 
    def __init__(self,msg):
      self.beam=self.edge=None
      FreeCADGui.Selection.clearSelection()
      try:
        self.av=FreeCADGui.activeDocument().activeView()
        self.stop=self.av.addEventCallback("SoKeyboardEvent",self.goOut)
        FreeCAD.Console.PrintMessage('\n'+msg+'\n')
        FreeCAD.Console.PrintWarning('*** [ESC] to exit. ***\n')
      except:
        FreeCAD.Console.PrintError('No view available\n')
        FreeCADGui.Selection.removeObserver(self)
    def goOut(self,info):
      down = (info["State"] == "DOWN")
      k=info['Key']
      if k=="ESCAPE":
        FreeCAD.Console.PrintMessage("I'm escaping.\n")
        self.av.removeEventCallback("SoKeyboardEvent",self.stop)
        FreeCADGui.Selection.removeObserver(self)
        
class frameItObserver(frameObserverPrototype): 
    def __init__(self):
      super(frameItObserver,self).__init__('Select one beam and one edge')
      self.beam=self.edge=None
    def addSelection(self,doc,obj,sub,pnt):
      selex=FreeCADGui.Selection.getSelectionEx()
      if self.beam==None and hasattr(selex[len(selex)-1].Object,'Height'):
        self.beam=selex[len(selex)-1].Object
        FreeCAD.Console.PrintMessage('Beam selected\n')
      elif self.edge==None and selex[len(selex)-1].SubObjects[0].ShapeType=='Edge':
        self.edge=selex[len(selex)-1].SubObjects[0]
        FreeCAD.Console.PrintMessage('Edge selected\n')
      if self.edge!=None and self.beam!=None:
        frameCmd.placeTheBeam(self.beam,self.edge)
        FreeCAD.Console.PrintMessage('Beam placed.\n')
        FreeCAD.Console.PrintWarning('Select another beam and another edge.\n[ESC] to exit.\n')
        self.beam=self.edge=None
        FreeCAD.activeDocument().recompute()

class fillFrameObserver(frameObserverPrototype): 
    def __init__(self):
        super(fillFrameObserver,self).__init__('First select the base beam, then the edges')
        self.beam=None
    def addSelection(self,doc,obj,sub,pnt):
        if self.beam==None and FreeCAD.getDocument(doc).getObject(obj).TypeId=='Part::FeaturePython':
          self.beam=FreeCAD.getDocument(doc).getObject(obj)
          FreeCAD.Console.PrintMessage('Beam type selected.\n')
        else:
          subObject=FreeCAD.getDocument(doc).getObject(obj).Shape.getElement(sub)
          if subObject.ShapeType=="Edge" and self.beam!=None:
            frameCmd.placeTheBeam(FreeCAD.activeDocument().copyObject(self.beam,True),subObject)

class levelBeamObserver(frameObserverPrototype):
    def __init__(self):
      super(levelBeamObserver,self).__init__('First select the target plane, then the faces to align')
      self.targetFace=None
    def addSelection(self,doc,obj,sub,pnt):
      subObject=FreeCAD.getDocument(doc).getObject(obj).Shape.getElement(sub)
      if subObject.ShapeType=="Face":
        if self.targetFace==None:
          self.targetFace=subObject
          FreeCAD.Console.PrintMessage('Target face selected.\n')
        else:
          beam=FreeCAD.getDocument(doc).getObject(obj)
          FreeCAD.activeDocument().openTransaction('levelTheBeam')
          frameCmd.levelTheBeam(beam,[self.targetFace,subObject])
          FreeCAD.activeDocument().commitTransaction()
          FreeCAD.Console.PrintMessage('Face moved.\n')
          FreeCAD.Console.PrintWarning('Select another face or press [ESC].\n')

class alignFlangeObserver(frameObserverPrototype):
    def __init__(self):
      super(alignFlangeObserver,self).__init__('Select the target face, then the others')
      self.faceBase=None
    def addSelection(self,doc,obj,sub,pnt):
      subObject=FreeCAD.getDocument(doc).getObject(obj).Shape.getElement(sub)
      if subObject.ShapeType=="Face":
        if self.faceBase==None:
          self.faceBase=subObject
          FreeCAD.Console.PrintMessage('Target face selected.\n')
        else:
          FreeCAD.activeDocument().openTransaction('alignFlange')
          frameCmd.rotTheBeam(FreeCAD.getDocument(doc).getObject(obj),self.faceBase,subObject)
          FreeCAD.activeDocument().commitTransaction()

class alignEdgeObserver(frameObserverPrototype):
    def __init__(self):
      super(alignEdgeObserver,self).__init__('Select two edges to join.')
      self.edges=[]
    def addSelection(self,doc,obj,sub,pnt):
      subObject=FreeCAD.getDocument(doc).getObject(obj).Shape.getElement(sub)
      if subObject.ShapeType=="Edge":
        self.edges.append(subObject)
        FreeCAD.Console.PrintMessage("Edge"+str(len(self.edges))+" OK\n")
      if len(self.edges)>1:
        sel=FreeCADGui.Selection.getSelection()
        beam=sel[len(sel)-1]
        FreeCAD.activeDocument().openTransaction('joinTheBeamsEdges')
        frameCmd.joinTheBeamsEdges(beam,self.edges[0],self.edges[1])
        FreeCAD.activeDocument().commitTransaction()
        FreeCAD.Console.PrintMessage('Done.\n')
        self.edges=[]
        FreeCAD.Console.PrintWarning('Select other edges or [ESC] to exit\n')

class stretchBeamObserver(frameObserverPrototype): #OBSOLETE: replaced with dialog
    def __init__(self):
      super(stretchBeamObserver,self).__init__('Select the beam and input the length')
      self.beam=None
    def addSelection(self,doc,obj,sub,pnt):
      Obj=FreeCAD.getDocument(doc).getObject(obj)
      if self.beam==None and Obj.TypeId=='Part::FeaturePython' and hasattr(Obj,'Height'):
        self.beam=Obj
        FreeCAD.Console.PrintMessage('Beam type selected.\n')
        from PySide.QtGui import QInputDialog as qid
        dist=float(qid.getText(None,"stretch a beam","old length = "+str(self.beam.Height)+"\nnew length?")[0])
        frameCmd.stretchTheBeam(self.beam,dist)
        FreeCAD.activeDocument().recompute()
        self.av.removeEventCallback("SoKeyboardEvent",self.stop)
        FreeCADGui.Selection.removeObserver(self)
        FreeCAD.Console.PrintMessage("I quit.")

class extendObserver(frameObserverPrototype): #OBSOLETE: replaced with dialog
    def __init__(self):
      super(extendObserver,self).__init__('First Select the target shape, then the beams to extend.')
      self.target=None
    def addSelection(self,doc,obj,sub,pnt):
      lastSel=FreeCAD.getDocument(doc).getObject(obj)
      subLastSel=lastSel.Shape.getElement(sub)
      if lastSel.TypeId=='Part::FeaturePython' and hasattr(lastSel,"Height") and self.target!=None:
        frameCmd.extendTheBeam(lastSel,self.target)
      if self.target==None and subLastSel.ShapeType in ["Edge","Face","Vertex"]:
        self.target=subLastSel
        FreeCAD.Console.PrintMessage('Target selected.\n')

class adjustAngleObserver(frameObserverPrototype): 
    def __init__(self):
      super(adjustAngleObserver,self).__init__('Select 2 edges')
      self.edges=[]
      self.beams=[]
    def addSelection(self,doc,obj,sub,pnt):
      lastSel=FreeCAD.getDocument(doc).getObject(obj)
      subLastSel=lastSel.Shape.getElement(sub)
      if lastSel.TypeId=='Part::FeaturePython' and hasattr(lastSel,"Height") and subLastSel.ShapeType=="Edge":
        self.edges.append(subLastSel)
        self.beams.append(lastSel)
        FreeCAD.Console.PrintMessage('Edge/beam pair nr.'+str(len(self.edges))+'  selected.\n')
      if (len(self.edges)==len(self.beams)==2):
        if frameCmd.isOrtho(*self.edges):
          self.beams.reverse()
          for i in range(len(self.edges)):
          	frameCmd.extendTheBeam(self.beams[i],self.edges[i])
          FreeCAD.Console.PrintWarning("Adjustment executed.\n")
        else:
          FreeCAD.Console.PrintError("Edges must be orthogonal.\n")
        self.edges=[]
        self.beams=[]
        FreeCADGui.Selection.clearSelection()
        FreeCAD.Console.PrintWarning("Repeat selection or press [ESC]\n")

class rotjoinObserver(frameObserverPrototype): 
    def __init__(self):
      super(rotjoinObserver,self).__init__('Select 2 edges =>[Ctrl]+select')
      self.edges=[]
    def addSelection(self,doc,obj,sub,pnt):
      lastSel=FreeCAD.getDocument(doc).getObject(obj)
      subLastSel=lastSel.Shape.getElement(sub)
      if subLastSel.ShapeType=="Edge":
        self.edges.append(subLastSel)
        FreeCAD.Console.PrintMessage('Edge'+str(len(self.edges))+' OK.\n')
      if len(self.edges)==2:
        try:
          FreeCAD.activeDocument().openTransaction('rotJoin')
          frameCmd.rotjoinTheBeam()
          FreeCAD.activeDocument().commitTransaction()
          FreeCAD.activeDocument().recompute()
          FreeCAD.Console.PrintWarning("Edges aligned.\n")
        except:
          FreeCAD.Console.PrintError("Edges must be selected holding [Ctrl] down for the correct execution. \nRetry.\n")
        self.edges=[]
        FreeCADGui.Selection.clearSelection()
        FreeCAD.Console.PrintWarning("Repeat selection or press [ESC]\n")


