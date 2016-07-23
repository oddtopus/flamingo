# FreeCAD Frame Tools module  
# (c) 2016 Riccardo Treu LGPL

class frameItObserver: 
    def __init__(self):
        import FreeCAD,FreeCADGui
        self.beam=self.edge=None
        FreeCADGui.Selection.clearSelection()
        try:
          self.av=FreeCADGui.activeDocument().activeView()
          self.stop=self.av.addEventCallback("SoKeyboardEvent",self.goOut)
          FreeCAD.Console.PrintMessage('\nSelect one beam and one edge\n')
          FreeCAD.Console.PrintWarning('*** [ESC] to exit. ***\n')
        except:
          FreeCAD.Console.PrintError('No view available\n')
          FreeCADGui.Selection.removeObserver(self)

    def __del__(self):
      FreeCAD.Console.PrintMessage('I "__del__".\n')
      self.av.removeEventCallback("SoKeyboardEvent",self.stop)
      FreeCADGui.Selection.removeObserver(self)
    
    def goOut(self,info):
      import FreeCAD, FreeCADGui, frameCmd
      down = (info["State"] == "DOWN")
      k=info['Key']
      if k=="ESCAPE":
        FreeCAD.Console.PrintMessage('I "exit".\n')
        self.av.removeEventCallback("SoKeyboardEvent",self.stop)
        FreeCADGui.Selection.removeObserver(self)
        
    def addSelection(self,doc,obj,sub,pnt):
      import FreeCAD, FreeCADGui, frameCmd
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

class fillFrameObserver: 
    import FreeCAD, FreeCADGui, frameCmd
    def __init__(self):
        import FreeCAD,FreeCADGui
        self.beam=None
        FreeCADGui.Selection.clearSelection()
        try:
          self.av=FreeCADGui.activeDocument().activeView()
          self.stop=self.av.addEventCallback("SoKeyboardEvent",self.goOut)
          FreeCADGui.Selection.clearSelection()
          FreeCAD.Console.PrintMessage('\nFirst select the base beam, then the edges.\n')
          FreeCAD.Console.PrintWarning('*** [ESC] to exit. ***\n')
        except:
          FreeCAD.Console.PrintError('No view available\n')
          FreeCADGui.Selection.removeObserver(self)

    def __del__(self):
      FreeCAD.Console.PrintMessage('I "__del__".\n')
      self.av.removeEventCallback("SoKeyboardEvent",self.stop)
      FreeCADGui.Selection.removeObserver(self)
    
    def goOut(self,info):
      import FreeCAD, FreeCADGui, frameCmd
      down = (info["State"] == "DOWN")
      k=info['Key']
      if k=="ESCAPE":
        FreeCAD.Console.PrintMessage('I "exit".\n')
        self.av.removeEventCallback("SoKeyboardEvent",self.stop)
        FreeCADGui.Selection.removeObserver(self)
        
    def addSelection(self,doc,obj,sub,pnt):
        import FreeCAD, FreeCADGui, frameCmd
        if self.beam==None and FreeCAD.getDocument(doc).getObject(obj).TypeId=='Part::FeaturePython':
          self.beam=FreeCAD.getDocument(doc).getObject(obj)
          FreeCAD.Console.PrintMessage('Beam type selected.\n')
        else:
          subObject=FreeCAD.getDocument(doc).getObject(obj).Shape.getElement(sub)
          if subObject.ShapeType=="Edge" and self.beam!=None:
            frameCmd.orientTheBeam(FreeCAD.activeDocument().copyObject(self.beam,True),subObject)

    def removeSelection(self,doc,obj,sub):
        return
    def setSelection(self,doc):
        return
    def clearSelection(self,doc):
        return

class levelBeamObserver:
    import FreeCAD, FreeCADGui, frameCmd
    def __init__(self):
        import FreeCADGui,FreeCAD
        self.targetFace=None
        try:
          self.av=FreeCADGui.activeDocument().activeView()
          self.stop=self.av.addEventCallback("SoKeyboardEvent",self.goOut)
          FreeCAD.Console.PrintMessage('\nFirst select the target, then the faces to align.\n')
          FreeCAD.Console.PrintWarning('*** [ESC] to exit. ***\n')
          FreeCADGui.Selection.clearSelection()
        except:
          FreeCAD.Console.PrintError('No view available\n')
          FreeCADGui.Selection.removeObserver(self)

    def __del__(self):
      FreeCAD.Console.PrintMessage('I "__del__".\n')
      self.av.removeEventCallback("SoKeyboardEvent",self.stop)
      FreeCADGui.Selection.removeObserver(self)
    
    def goOut(self,info):
      import FreeCAD, FreeCADGui
      down = (info["State"] == "DOWN")
      k=info['Key']
      if k=="ESCAPE":
        FreeCAD.Console.PrintMessage('I "exit".\n')
        self.av.removeEventCallback("SoKeyboardEvent",self.stop)
        FreeCADGui.Selection.removeObserver(self)
        
    def addSelection(self,doc,obj,sub,pnt):
        import FreeCAD, FreeCADGui, frameCmd
        subObject=FreeCAD.getDocument(doc).getObject(obj).Shape.getElement(sub)
        if subObject.ShapeType=="Face":
          if self.targetFace==None:
            self.targetFace=subObject
          else:
            beam=FreeCAD.getDocument(doc).getObject(obj)
            frameCmd.levelTheBeam(beam,[self.targetFace,subObject])

class alignFlangeObserver:
    import FreeCAD, FreeCADGui, frameCmd
    def __init__(self):
        import FreeCADGui,FreeCAD
        self.faceBase=None
        try:
          self.av=FreeCADGui.activeDocument().activeView()
          self.stop=self.av.addEventCallback("SoKeyboardEvent",self.goOut)
          FreeCAD.Console.PrintMessage('\nSelect the base face, then the others.\n')
          FreeCAD.Console.PrintWarning('*** [ESC] to exit. ***\n')
          FreeCADGui.Selection.clearSelection()
        except:
          FreeCAD.Console.PrintError('No view available\n')
          FreeCADGui.Selection.removeObserver(self)

    def __del__(self):
      FreeCAD.Console.PrintMessage('I "__del__".\n')
      self.av.removeEventCallback("SoKeyboardEvent",self.stop)
      FreeCADGui.Selection.removeObserver(self)
    
    def goOut(self,info):
      import FreeCAD, FreeCADGui
      down = (info["State"] == "DOWN")
      k=info['Key']
      if k=="ESCAPE":
        FreeCAD.Console.PrintMessage('I "exit".\n')
        self.av.removeEventCallback("SoKeyboardEvent",self.stop)
        FreeCADGui.Selection.removeObserver(self)
        
    def addSelection(self,doc,obj,sub,pnt):
        import FreeCAD, FreeCADGui, frameCmd
        subObject=FreeCAD.getDocument(doc).getObject(obj).Shape.getElement(sub)
        if subObject.ShapeType=="Face":
          if self.faceBase==None:
            self.faceBase=subObject
            FreeCAD.Console.PrintMessage('Target face selected.\n')
          else:
            frameCmd.rotTheBeam(FreeCAD.getDocument(doc).getObject(obj),self.faceBase,subObject)

class alignEdgeObserver:
    import FreeCAD, FreeCADGui, frameCmd
    def __init__(self):
        import FreeCADGui,FreeCAD
        self.edges=[]
        try:
          self.av=FreeCADGui.activeDocument().activeView()
          self.stop=self.av.addEventCallback("SoKeyboardEvent",self.goOut)
          FreeCAD.Console.PrintMessage('\nSelect two edges.\n')
          FreeCAD.Console.PrintWarning('*** [ESC] to exit. ***\n')
          FreeCADGui.Selection.clearSelection()
        except:
          FreeCAD.Console.PrintError('No view available\n')
          FreeCADGui.Selection.removeObserver(self)

    def __del__(self):
      FreeCAD.Console.PrintMessage('I "__del__".\n')
      self.av.removeEventCallback("SoKeyboardEvent",self.stop)
      FreeCADGui.Selection.removeObserver(self)
    
    def goOut(self,info):
      import FreeCAD, FreeCADGui
      down = (info["State"] == "DOWN")
      k=info['Key']
      if k=="ESCAPE":
        FreeCAD.Console.PrintMessage('I "exit".\n')
        self.av.removeEventCallback("SoKeyboardEvent",self.stop)
        FreeCADGui.Selection.removeObserver(self)
        
    def addSelection(self,doc,obj,sub,pnt):
        import FreeCAD, FreeCADGui, frameCmd
        subObject=FreeCAD.getDocument(doc).getObject(obj).Shape.getElement(sub)
        if subObject.ShapeType=="Edge":
          self.edges.append(subObject)
          FreeCAD.Console.PrintMessage("Edge"+str(len(self.edges))+" OK\n")
        if len(self.edges)>1:
          sel=FreeCADGui.Selection.getSelection()
          beam=sel[len(sel)-1]
          frameCmd.joinTheBeamsEdges(beam,self.edges[0],self.edges[1])
          FreeCAD.Console.PrintMessage('Done.\n')
          self.edges=[]
          FreeCAD.Console.PrintWarning('Select other edges or [ESC] to exit\n')

class stretchBeamObserver: 
    import FreeCAD, FreeCADGui, frameCmd
    def __init__(self):
        import FreeCAD,FreeCADGui
        self.beam=None
        FreeCADGui.Selection.clearSelection()
        try:
          self.av=FreeCADGui.activeDocument().activeView()
          self.stop=self.av.addEventCallback("SoKeyboardEvent",self.goOut)
          FreeCADGui.Selection.clearSelection()
          FreeCAD.Console.PrintMessage('\nFirst select the beam, then input the length.\n')
          FreeCAD.Console.PrintWarning('*** [ESC] to exit. ***\n')
        except:
          FreeCAD.Console.PrintError('No view available\n')
          FreeCADGui.Selection.removeObserver(self)

    def __del__(self):
      FreeCAD.Console.PrintMessage('I "__del__".\n')
      self.av.removeEventCallback("SoKeyboardEvent",self.stop)
      FreeCADGui.Selection.removeObserver(self)
    
    def goOut(self,info):
      import FreeCAD, FreeCADGui, frameCmd
      down = (info["State"] == "DOWN")
      k=info['Key']
      if k=="ESCAPE":
        FreeCAD.Console.PrintMessage('I "exit".\n')
        self.av.removeEventCallback("SoKeyboardEvent",self.stop)
        FreeCADGui.Selection.removeObserver(self)
        
    def addSelection(self,doc,obj,sub,pnt):
        import FreeCAD, FreeCADGui, frameCmd
        Obj=FreeCAD.getDocument(doc).getObject(obj)
        if self.beam==None and Obj.TypeId=='Part::FeaturePython' and hasattr(Obj,'Height'):
          self.beam=Obj
          FreeCAD.Console.PrintMessage('Beam type selected.\n')
          from PySide.QtGui import QInputDialog as qid
          dist=float(qid.getText(None,"stretch a beam","old length = "+str(self.beam.Height)+"\nnew length?")[0])
          frameCmd.stretchTheBeam(self.beam,dist)
          FreeCAD.activeDocument().recompute()
          self.av.removeEventCallback("SoKeyboardEvent",self.stop) #DON'T FORGET TO QUIT
          FreeCADGui.Selection.removeObserver(self)
          print "I quit."

class extend2edgeObserver: 
    import FreeCAD, FreeCADGui, frameCmd
    def __init__(self):
        import FreeCAD,FreeCADGui
        self.target=None
        FreeCADGui.Selection.clearSelection()
        try:
          self.av=FreeCADGui.activeDocument().activeView()
          self.stop=self.av.addEventCallback("SoKeyboardEvent",self.goOut)
          FreeCADGui.Selection.clearSelection()
          FreeCAD.Console.PrintMessage('\nFirst select the target edge, then the beams to extend.\n')
          FreeCAD.Console.PrintWarning('*** [ESC] to exit. ***\n')
        except:
          FreeCAD.Console.PrintError('No view available\n')
          FreeCADGui.Selection.removeObserver(self)

    def __del__(self):
      FreeCAD.Console.PrintMessage('I "__del__".\n')
      self.av.removeEventCallback("SoKeyboardEvent",self.stop)
      FreeCADGui.Selection.removeObserver(self)
    
    def goOut(self,info):
      import FreeCAD, FreeCADGui, frameCmd
      down = (info["State"] == "DOWN")
      k=info['Key']
      if k=="ESCAPE":
        FreeCAD.Console.PrintMessage('I "exit".\n')
        self.av.removeEventCallback("SoKeyboardEvent",self.stop)
        FreeCADGui.Selection.removeObserver(self)
        
    def addSelection(self,doc,obj,sub,pnt):
        import FreeCAD, FreeCADGui, frameCmd
        lastSel=FreeCAD.getDocument(doc).getObject(obj)
        subLastSel=lastSel.Shape.getElement(sub)
        if lastSel.TypeId=='Part::FeaturePython' and hasattr(lastSel,"Height") and self.target!=None:
          frameCmd.extendTheBeam(lastSel,self.target)
          self.av.removeEventCallback("SoKeyboardEvent",self.stop)
          FreeCADGui.Selection.removeObserver(self)
          print "I quit."
        if self.target==None and subLastSel.ShapeType=="Edge":
          self.target=subLastSel
          FreeCAD.Console.PrintMessage('Target selected.\n')

class adjustAngleObserver: 
    import FreeCAD, FreeCADGui, frameCmd
    def __init__(self):
        import FreeCAD,FreeCADGui
        self.edges=[]
        self.beams=[]
        FreeCADGui.Selection.clearSelection()
        try:
          self.av=FreeCADGui.activeDocument().activeView()
          self.stop=self.av.addEventCallback("SoKeyboardEvent",self.goOut)
          FreeCADGui.Selection.clearSelection()
          FreeCAD.Console.PrintMessage('\nSelect 2 edges\n')
          FreeCAD.Console.PrintWarning('*** [ESC] to exit. ***\n')
        except:
          FreeCAD.Console.PrintError('No view available\n')
          FreeCADGui.Selection.removeObserver(self)

    def __del__(self):
      FreeCAD.Console.PrintMessage('I "__del__".\n')
      self.av.removeEventCallback("SoKeyboardEvent",self.stop)
      FreeCADGui.Selection.removeObserver(self)
    
    def goOut(self,info):
      import FreeCAD, FreeCADGui, frameCmd
      down = (info["State"] == "DOWN")
      k=info['Key']
      if k=="ESCAPE":
        FreeCAD.Console.PrintMessage('I "exit".\n')
        self.av.removeEventCallback("SoKeyboardEvent",self.stop)
        FreeCADGui.Selection.removeObserver(self)
        
    def addSelection(self,doc,obj,sub,pnt):
        import FreeCAD, FreeCADGui, frameCmd
        lastSel=FreeCAD.getDocument(doc).getObject(obj)
        subLastSel=lastSel.Shape.getElement(sub)
        if lastSel.TypeId=='Part::FeaturePython' and hasattr(lastSel,"Height") and subLastSel.ShapeType=="Edge":
          self.edges.append(subLastSel)
          self.beams.append(lastSel)
          FreeCAD.Console.PrintMessage('Edge/beam pair nr.'+str(len(self.edges))+'  selected.\n')
        if len(self.edges)==len(self.beams)==2:
          self.beams.reverse()
          for i in range(len(self.edges)):
          	frameCmd.extendTheBeam(self.beams[i],self.edges[i])
          self.edges=[]
          self.beams=[]
          FreeCADGui.Selection.clearSelection()
          #FreeCADGui.Selection.removeObserver(self)
          FreeCAD.Console.PrintWarning("Adjustment executed.\nRepeat selection or press [ESC]\n")

class rotjoinObserver: 
    import FreeCAD, FreeCADGui, frameCmd
    def __init__(self):
        import FreeCAD,FreeCADGui
        self.edges=[]
        FreeCADGui.Selection.clearSelection()
        try:
          self.av=FreeCADGui.activeDocument().activeView()
          self.stop=self.av.addEventCallback("SoKeyboardEvent",self.goOut)
          FreeCADGui.Selection.clearSelection()
          FreeCAD.Console.PrintMessage('\nSelect 2 edges\n')
          FreeCAD.Console.PrintWarning('***[Ctrl]+select]***\n*** [ESC] to exit. ***\n')
        except:
          FreeCAD.Console.PrintError('No view available\n')
          FreeCADGui.Selection.removeObserver(self)

    def __del__(self):
      FreeCAD.Console.PrintMessage('I "__del__".\n')
      self.av.removeEventCallback("SoKeyboardEvent",self.stop)
      FreeCADGui.Selection.removeObserver(self)
    
    def goOut(self,info):
      import FreeCAD, FreeCADGui, frameCmd
      down = (info["State"] == "DOWN")
      k=info['Key']
      if k=="ESCAPE":
        FreeCAD.Console.PrintMessage('I "exit".\n')
        self.av.removeEventCallback("SoKeyboardEvent",self.stop)
        FreeCADGui.Selection.removeObserver(self)
        
    def addSelection(self,doc,obj,sub,pnt):
        import FreeCAD, FreeCADGui, frameCmd
        lastSel=FreeCAD.getDocument(doc).getObject(obj)
        subLastSel=lastSel.Shape.getElement(sub)
        if subLastSel.ShapeType=="Edge":
          self.edges.append(subLastSel)
          FreeCAD.Console.PrintMessage('Edge'+str(len(self.edges))+' OK.\n')
        if len(self.edges)==2:
          frameCmd.rotjoinTheBeam()
          FreeCAD.activeDocument().recompute()
          self.edges=[]
          FreeCADGui.Selection.clearSelection()
          #FreeCADGui.Selection.removeObserver(self)
          FreeCAD.Console.PrintWarning("Edges aligned.\nRepeat selection or press [ESC]\n")


