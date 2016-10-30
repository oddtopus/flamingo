# Utilities for spreadsheets  
# (c) 2016 Riccardo Treu LGPL

global alpha
alpha='ABCDEFGHJKILMNOPQRSTUVWXYZ'

def cellRC(sp,target):
  'arg1=spreadsheet,arg2=target; return row of target'
  import xml.etree.ElementTree as et
  cells=et.fromstring(sp.cells.Content)
  for cell in cells:
    if cell.get('content')==target:
      addr=cell.get('address')
      #print addr+'\n'
      row=addr.lstrip(alpha)
      return row
  #print "There are no "+target+" in this sheet."

def makeDict(sp):
  'arg1=spreadsheet; returns dict[\'address\']=\'content\''
  import xml.etree.ElementTree as et
  cells=et.fromstring(sp.cells.Content)
  d=dict()
  for c in cells:
    d[c.attrib['address']]=c.attrib['content']
  return d

def setTipo(l,w):
  'arg1=length,arg2=width'
  import FreeCAD
  fpTipo=FreeCAD.activeDocument().tipo
  fpTipo.length=l
  fpTipo.width=w
  FreeCAD.activeDocument().recompute()
  
def getTipo(sp,target):
  'arg1=spreadsheet,arg2=str_Target; returns [length,width]'
  d=makeDict(sp)
  row=cellRC(sp,target)
  l=d['C'+row]
  w=d['D'+row]
  setTipo(l,w)
  return [l,w]

def getTipi(sp):
  'arg1=spreadsheet; returns [contents in column A]'
  d=makeDict(sp)
  return [d[k] for k in d.keys() if k.startswith('A')]  
