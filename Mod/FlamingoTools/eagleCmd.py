# FreeCAD Frame Tools module  
# (c) 2016 Riccardo Treu LGPL

import xml.etree.ElementTree as et
import FreeCAD as App
from PySide import QtGui as qg

doc=App.activeDocument()
try:
	if len(doc.Parts.OutList)>0:
		App.Console.PrintMessage('Parts has '+str(len(doc.Parts.OutList))+' components\n')
	else:
		App.Console.PrintMessage('Parts has no components') 
except:
	print 'no group "Parts" found'


def brdIn():
  fileName=qg.QFileDialog().getOpenFileName()
  board=fileName[0]
  try:
		radice=et.parse(board).getroot()
		el=[]
		pos=[]
		for ramo in radice.iter('element'):
			el.append(ramo)
		for e in el:
			x=float(e.attrib['x'])
			y=float(e.attrib['y'])
			if ('rot' in e.attrib) and (e.attrib['rot'].lstrip('R').isdigit()):
				rot=float(e.attrib['rot'].lstrip('R'))
			else:
				rot=0.0
			pos.append([e.attrib['name'],[x,y,rot]])
		dpos=dict(pos)
		for k in dpos.keys():
			App.Console.PrintMessage(str(k)+'\t'+str(dpos[k])+'\n')
		return dpos
  except:
		App.Console.PrintMessage('no such file\n')

def brdCompare(pos):
	doc=App.activeDocument()
	klist=[]
	for k in pos.keys():
		klist.append(k.upper())
	for comp in doc.Parts.OutList:
		if comp.Label.upper() in klist:
			print str(comp.Label)+' is in pos'
			try:
				comp.X=pos[str(comp.Label)][0]
				comp.Y=pos[str(comp.Label)][1]
				comp.Rot=pos[str(comp.Label)][2]
			except:
				comp.X=pos[str(comp.Label.upper())][0]
				comp.Y=pos[str(comp.Label.upper())][1]
				comp.Rot=pos[str(comp.Label.upper())][2]
		else:
			print str(comp.Label)+' is not in pos'
