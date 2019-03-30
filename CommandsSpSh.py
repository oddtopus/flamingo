#(c) 2016 R. T. LGPL: part of Flamingo tools w.b. for FreeCAD

__title__="spreadSheetTools toolbar"
__author__="oddtopus"
__url__="github.com/oddtopus/flamingo"
__license__="LGPL 3"

# import FreeCAD modules
import FreeCAD, FreeCADGui,inspect, os

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

class findFirst:
  def Activated(self):
    from PySide import QtGui as qg
    def cellAddress(sp,target):
      import xml.etree.ElementTree as et
      cells=et.fromstring(sp.cells.Content)
      for cell in cells:
        if cell.get('content')==target:
          #print "*** "+target+" is in "+cell.get('address')+" ***"
          return cell.get('address')
      #print "There are no "+target+" in this sheet."

    doc=FreeCAD.activeDocument()
    s=[x for x in doc.Objects if x.TypeId.startswith('Spread')]
    if len(s):
      #print "There is at least 1 Sheet"
      target=qg.QInputDialog.getText(None,"findFirst()","String to search for?")
      i=cellAddress(s[0],target[0])
      import spreadCmd
      #print "From spreadCmd.py: row = "+spreadCmd.cellRC(s[0],target[0])
    else:
      #print "There are no sheets in this doc"
      pass
  def GetResources(self):
    return{'Pixmap':'Std_Tool1','MenuText':'Find first occurence','ToolTip':'Find content in sheet and print address'}


#---------------------------------------------------------------------------
# Adds the commands to the FreeCAD command manager
#---------------------------------------------------------------------------
addCommand('findFirst',findFirst()) 
