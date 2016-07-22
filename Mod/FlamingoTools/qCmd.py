import FreeCAD, FreeCADGui

class infos:
  
  def __init__(self):
    self.mode = False
    FreeCAD.Console.PrintMessage("Create instance of infos\n")

  def __del__(self):
    FreeCAD.Console.PrintMessage("Delete instance of infos\n")

  def enter(self):
    if (self.mode):
      return
    FreeCAD.Console.PrintMessage("\n ** Enter query mode **\nPress 'Q' to get more info on the objects selected.\n'Esc' to exit.\n")
    self.av = FreeCADGui.ActiveDocument.ActiveView
    self.cb = self.av.addEventCallback("SoMouseButtonEvent",self.query)
    self.ex = self.av.addEventCallback("SoKeyboardEvent",self.exit)
    self.inf = self.av.addEventCallback("SoKeyboardEvent",self.winfo)
    self.mode = True

  def leave(self):
    if (not self.mode):
      return
    FreeCAD.Console.PrintMessage("\n ** Leave query mode **\n")
    self.av.removeEventCallback("SoMouseButtonEvent",self.cb)
    self.av.removeEventCallback("SoKeyboardEvent",self.ex)
    self.av.removeEventCallback("SoKeyboardEvent",self.inf)
    self.mode = False
    
  def query(self, info):
    down = (info["State"] == "DOWN")
    pos = info["Position"]
    if (down):
      #pnt = self.av.getPoint(pos[0],pos[1])
      #FreeCAD.Console.PrintMessage("Clicked on position: ("+str(pos[0])+", "+str(pos[0])+")")
      #msg = " -> (%f,%f,%f)\n" % (pnt.x, pnt.y, pnt.z)
      #FreeCAD.Console.PrintMessage(msg)
      pass

  def winfo(self,info):
    print "***********\n"
    if (info["Key"] in ["q","Q"]) and (info["State"] == "DOWN"):
      selex=FreeCADGui.Selection.getSelectionEx()
      i=0
      if selex!=[]:
        for obj in selex:
          print str(i)+"\n->\t Selected Object name: "+obj.Object.Name+"\n"
          if obj.Object.TypeId=="Part::FeaturePython" and hasattr(obj.Object,"Height"):
            print "Base: ", obj.Object.Placement.Base
            print "Rot. axis:\n", obj.Object.Placement.Rotation.Axis
            print "Rot. angle:\n", round(obj.Object.Placement.Rotation.Angle*180/3.14159,1)," deg"
          if obj.HasSubObjects:
            for sub in obj.SubObjects:
              print " subobject: ", selex[0].SubObjects[0].TypeId
              if sub.ShapeType=='Vertex':
                print "  position = ",sub.Point
              if sub.ShapeType=='Edge':
                print "  length = ",sub.Length
              if sub.ShapeType=='Face':
                print "  area = ",sub.Area
          i+=1
      
  def exit(self, info):
    esc = (info["Key"] == "ESCAPE")
    if (esc):
      self.leave()
