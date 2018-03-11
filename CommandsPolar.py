#(c) 2016 R. T. LGPL: part of Flamingo tools w.b. for FreeCAD

__title__="polarTools toolbar"
__author__="oddtopus"
__url__="github.com/oddtopus/flamingo"
__license__="LGPL 3"

# import FreeCAD modules
import FreeCAD, FreeCADGui,inspect , os

# helper -------------------------------------------------------------------
# FreeCAD TemplatePyMod module  
# (c) 2007 Juergen Riegel LGPL

def addCommand(name,cmdObject):
	(list,num) = inspect.getsourcelines(cmdObject.Activated)
	pos = 0
	# check for indentation
	while(list[1][pos] == ' ' or list[1][pos] == '\t'):
		pos += 1
	source = ""
	for i in range(len(list)-1):
		source += list[i+1][pos:]
	FreeCADGui.addCommand(name,cmdObject,source)

#---------------------------------------------------------------------------
# The command classes
#---------------------------------------------------------------------------

class drawPolygon:
  def Activated(self):
    import polarUtilsCmd as puc
    import FreeCAD, FreeCADGui
    from PySide import QtGui as qg
    if (FreeCADGui.Selection.countObjectsOfType('Sketcher::SketchObject')==0):
      qg.QMessageBox().information(None,'Incorrect input','First select at least one sketch.')
    else:
      n=int(qg.QInputDialog.getText(None,"draw a Polygon","Number of sides?")[0])
      R=float(qg.QInputDialog.getText(None,"draw a Polygon","Radius of circumscribed circle?")[0])
      for sk in FreeCADGui.Selection.getSelection():
        if sk.TypeId=="Sketcher::SketchObject":
          puc.disegna(sk,puc.cerchio(R,n))
    
  def GetResources(self):
    return{'Pixmap':os.path.join(os.path.dirname(os.path.abspath(__file__)),"icons","poligono.svg"),'MenuText':'Make-a-polygon','ToolTip':'Draws n-polygon in a circle'}

class drawFromFile():
  def Activated(self):
    import polarUtilsCmd as puc
    import FreeCAD
    doc=FreeCAD.activeDocument()
    sketch=doc.addObject("Sketcher::SketchObject","imported")
    sketch.Placement = FreeCAD.Placement(FreeCAD.Vector(0.000000,0.000000,0.000000),FreeCAD.Rotation(0.000000,0.000000,0.000000,1.000000))
    puc.disegna(sketch,puc.getFromFile())
    
  def GetResources(self):
    return{'Pixmap':os.path.join(os.path.dirname(os.path.abspath(__file__)),"icons","daFile.svg"),'MenuText':'Polygon from file','ToolTip':'The file .csv must be ";" separated: column A = radius, column B = angle'}

class queryModel:

  def Activated(self):
    import FreeCAD, FreeCADGui, qForms
    form = qForms.QueryForm(FreeCADGui.Selection)

  def GetResources(self):
    return{'Pixmap':os.path.join(os.path.dirname(os.path.abspath(__file__)),"icons","query.svg"),'Accel':"Q,M",'MenuText':'query the model','ToolTip':'Click objects to print infos'}
    
class moveWorkPlane:
  '''
  Tool to set the DraftWorkingPlane according existing geometry of 
  the model.
  The normal of plane is set:
  * 1st according the selected face,
  * then according the plane defined by a curved edge,
  * at last according the plane defined by two straight edges.
  The origin is set:
  * 1st according the selected vertex,
  * then according the center of curvature of a curved edge,
  * at last according the intersection of two straight edges.
  '''
  def Activated(self):
    import polarUtilsCmd
    polarUtilsCmd.setWP()

  def GetResources(self):
    return{'Pixmap':os.path.join(os.path.dirname(os.path.abspath(__file__)),"icons","grid.svg"),'MenuText':'align Workplane','ToolTip':'Moves and rotates the drafting workplane with points, edges and faces'}
    
class rotateWorkPlane:

  def Activated(self):
    import FreeCAD, FreeCADGui, qForms
    form = qForms.rotWPForm()

  def GetResources(self):
    return{'Pixmap':os.path.join(os.path.dirname(os.path.abspath(__file__)),"icons","rotWP.svg"),'MenuText':'rotate Workplane','ToolTip':'Spin the Draft working plane about one of its axes'}
    
class offsetWorkPlane:

  def Activated(self):
    if hasattr(FreeCAD,'DraftWorkingPlane') and hasattr(FreeCADGui,'Snapper'):
      import polarUtilsCmd
      s=FreeCAD.ParamGet("User parameter:BaseApp/Preferences/Mod/Draft").GetInt("gridSize")
      sc=[float(x*s) for x in [1,1,.2]]
      arrow =polarUtilsCmd.arrow(FreeCAD.DraftWorkingPlane.getPlacement(),scale=sc,offset=s)
      from PySide.QtGui import QInputDialog as qid
      offset=qid.getInteger(None,'Offset Work Plane','Offset: ')
      if offset[1]:
        polarUtilsCmd.offsetWP(offset[0])
      #FreeCADGui.ActiveDocument.ActiveView.getSceneGraph().removeChild(arrow.node)
      arrow.closeArrow()
  def GetResources(self):
    return{'Pixmap':os.path.join(os.path.dirname(os.path.abspath(__file__)),"icons","offsetWP.svg"),'MenuText':'offset Workplane','ToolTip':'Shifts the WP alongg its normal.'}
    
class hackedL:

  def Activated(self):
    import polarUtilsCmd
    form = polarUtilsCmd.hackedLine()

  def GetResources(self):
    return{'Pixmap':os.path.join(os.path.dirname(os.path.abspath(__file__)),"icons","hackedL.svg"),'Accel':"H,L",'MenuText':'draw a DWire','ToolTip':'WP is re-positioned at each point. Possible to spin and offset it.'}
    
class moveHandle:

  def Activated(self):
    import polarUtilsCmd
    FreeCADGui.Control.showDialog(polarUtilsCmd.handleDialog())
    #form = polarUtilsCmd.handleDialog()

  def GetResources(self):
    return{'Pixmap':os.path.join(os.path.dirname(os.path.abspath(__file__)),"icons","moveHandle.svg"),'Accel':"M,H",'MenuText':'Move objects','ToolTip':'Move quickly objects inside viewport'}
    
class dpCalc:

  def Activated(self):
    import fe_ChEDL
    FreeCADGui.Control.showDialog(fe_ChEDL.dpCalcDialog())

  def GetResources(self):
    return{'MenuText':'Pressure loss calculator','ToolTip':'Calculate pressure loss in "pypes" using ChEDL libraries.\n See __doc__ of the module for futher information.'}

#---------------------------------------------------------------------------
# Adds the commands to the FreeCAD command manager
#---------------------------------------------------------------------------
addCommand('drawPolygon',drawPolygon()) 
addCommand('drawFromFile',drawFromFile())
addCommand('queryModel',queryModel()) 
addCommand('moveWorkPlane',moveWorkPlane()) 
addCommand('rotateWorkPlane',rotateWorkPlane())
addCommand('offsetWorkPlane',offsetWorkPlane())
addCommand('hackedL',hackedL())
addCommand('moveHandle',moveHandle())
addCommand('dpCalc',dpCalc())
