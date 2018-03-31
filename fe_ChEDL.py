# -*- coding: utf-8 -*-
#
#  fe_ChEDL.py
#  
#  Copyright 2018 (oddtopus)
#  
#  This program is free software; you can redistribute it and/or modify
#  it under the terms of the GNU General Public License as published by
#  the Free Software Foundation; either version 2 of the License, or
#  (at your option) any later version.
#  
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#  
#  You should have received a copy of the GNU General Public License
#  along with this program; if not, write to the Free Software
#  Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston,
#  MA 02110-1301, USA.
#  
#(c) 2018 R. T. LGPL3

__title__="Front end for ChEDL"
__author__="oddtopus"
__url__="github.com/oddtopus"
__license__="LGPL 3"
__doc__='''
Frontend in FreeCAD of the python libraries "ChEDL":  
Caleb Bell (2016). fluids: Fluid dynamics component of Chemical Engineering Design Library (ChEDL)
https://github.com/CalebBell/fluids.
Caleb Bell (2016). thermo: Chemical properties component of Chemical Engineering Design Library (ChEDL)
https://github.com/CalebBell/thermo.
'''  
import FreeCAD,FreeCADGui
from PySide import QtCore, QtGui
from os.path import join, dirname, abspath
from PySide.QtCore import *
from PySide.QtGui import *
from math import pi
try:
  from fluids import friction,fittings, Reynolds, K_from_f, dP_from_K
  from thermo import Chemical
except:
  QMessageBox.warning(None,'Missing python module','''
  Please first install "fluids" and "thermo" libraries from ChEDL:\n\n
  \tpip install thermo, fluids\n\n
  Caleb Bell (2016). fluids: Fluid dynamics component of Chemical Engineering Design Library (ChEDL)\n
  https://github.com/CalebBell/fluids.\n
  Caleb Bell (2016). thermo: Chemical properties component of Chemical Engineering Design Library (ChEDL)\n
  https://github.com/CalebBell/thermo.''')
  FreeCAD.Console.PrintError('Please first install "fluids" and "thermo" libraries from ChEDL\n')

class dpCalcDialog:
  def __init__(self):
    dialogPath=join(dirname(abspath(__file__)),"dialogs","dp.ui")
    self.form=FreeCADGui.PySideUic.loadUi(dialogPath)
    self.form.comboFluid.addItems(['water'])
    self .form.comboWhat.addItems([o.Label for o in FreeCAD.ActiveDocument.Objects if hasattr(o,'PType') and o.PType=='PypeBranch' ])
    self.form.editFlow.setValidator(QDoubleValidator())
    self.form.editFlow.setText('1')
    self.form.editRough.setValidator(QDoubleValidator())
    self.form.editRough.setText('10')
  def accept(self):
    Dp=0
    elements=list()
    fluid=Chemical(self.form.comboFluid.currentText())
    Q=float(self.form.editFlow.text())/3600
    if self.form.comboWhat.currentText()=='<on selection>':
      elements = FreeCADGui.Selection.getSelection()
    else:
      o=FreeCAD.ActiveDocument.getObjectsByLabel(self.form.comboWhat.currentText())[0]
      if hasattr(o,'PType') and o.PType=='PypeBranch':
        elements=o.Tubes+o.Curves
    for o in elements:
      if hasattr(o,'PType') and o.PType in ['Pipe','Elbow']:
        ID=float(o.ID)/1000
        e=float(self.form.editRough.text())*1e-6/ID
        v=Q/((ID)**2*pi/4)
        Re=Reynolds(V=v,D=ID,rho=fluid.rhol, mu=fluid.mul)
        f=friction.friction_factor(Re, eD=e) # Darcy, =4xFanning
        if o.PType=='Pipe':
          L=float(o.Height)/1000
          K=K_from_f(fd=f, L=L, D=ID)
          FreeCAD.Console.PrintMessage('ID=%.2f\nV=%.2f\ne=%f\nf=%f\nK=%f\nL=%.3f\n***\n'%(ID,v,e,f,K,L))
          Dp+=dP_from_K(K,rho=fluid.rhol,V=v)
        elif o.PType=='Elbow':
          ang=float(o.BendAngle)
          R=float(o.BendRadius)/1000
          K=fittings.bend_rounded(ID,ang,f,R)
          FreeCAD.Console.PrintMessage('ID=%.2f\nV=%.2f\ne=%f\nf=%f\nK=%f\nang=%.3f\nR=%f\n***\n'%(ID,v,e,f,K,ang,R))
          Dp+=dP_from_K(K,rho=fluid.rhol,V=v)
        elif o.PType=='Reduct':
          pass
      if Dp>200: result=' = %.3f bar'%(Dp/100000)
      else: result=' = %.2e bar'%(Dp/100000)
      self.form.labResult.setText(result)
