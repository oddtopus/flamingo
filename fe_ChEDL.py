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
import FreeCAD,FreeCADGui, csv
pq=FreeCAD.Units.parseQuantity
from PySide import QtCore, QtGui
from os.path import join, dirname, abspath
from PySide.QtCore import *
from PySide.QtGui import *
from math import pi
from os.path import join, dirname, abspath
try:
  from fluids import friction,fittings, Reynolds, K_from_f, dP_from_K
  from thermo import Chemical, Mixture, identifiers
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
    fluids=['water','air','methane','ethane','propane','butane','CCCCCC','CCCCCCCC','vinegar','acetone','HF','HCl']
    self.form.comboFluid.addItems(fluids)
    self.form.comboFluid.addItems(['<custom fluid>']) 
    self .form.comboWhat.addItems([o.Label for o in FreeCAD.ActiveDocument.Objects if hasattr(o,'PType') and o.PType=='PypeBranch' ])
    self.form.editFlow.setValidator(QDoubleValidator())
    self.form.editRough.setValidator(QDoubleValidator())
    self.form.editPressure.setValidator(QDoubleValidator())
    self.form.editTemperature.setValidator(QDoubleValidator())
    self.form.editDensity.setValidator(QDoubleValidator())
    self.form.editViscosity.setValidator(QDoubleValidator())
    self.form.comboFluid.currentIndexChanged.connect(self.checkFluid)
    self.form.editTemperature.textChanged.connect(self.checkFluid)
    self.form.editPressure.textChanged.connect(self.checkFluid)
    self.form.editDensity.textChanged.connect(self.setRho)
    self.form.editViscosity.textChanged.connect(self.setMu)
    self.form.radioLiquid.released.connect(self.setLiquid)
    self.form.radioGas.released.connect(self.setGas)
    self.form.butExport.clicked.connect(self.export)
    self.form.comboWhat.currentIndexChanged.connect(lambda: self.form.labResult.setText('---'))
    self.isLiquid=True
    self.checkFluid()
  def accept(self):
    Dp=Ltot=nc=0
    elements=list()
    Q=float(self.form.editFlow.text())/3600
    if not self.isLiquid:
      Q=Q/self.Rho
    if self.form.comboWhat.currentText()=='<on selection>':
      elements = FreeCADGui.Selection.getSelection()
    else:
      o=FreeCAD.ActiveDocument.getObjectsByLabel(self.form.comboWhat.currentText())[0]
      if hasattr(o,'PType') and o.PType=='PypeBranch':
        elements=[FreeCAD.ActiveDocument.getObject(name) for name in o.Tubes+o.Curves]
    self.form.editResults.clear()
    for o in elements:
      loss=0
      if hasattr(o,'PType') and o.PType in ['Pipe','Elbow']:
        ID=float(o.ID)/1000
        e=float(self.form.editRough.text())*1e-6/ID
        v=Q/((ID)**2*pi/4)
        Re=Reynolds(V=v,D=ID,rho=self.Rho, mu=self.Mu)
        f=friction.friction_factor(Re, eD=e) # Darcy, =4xFanning
        if o.PType=='Pipe':
          L=float(o.Height)/1000
          Ltot+=L
          K=K_from_f(fd=f, L=L, D=ID)
          loss=dP_from_K(K,rho=self.Rho,V=v)
          FreeCAD.Console.PrintMessage('%s: %s\nID=%.2f\nV=%.2f\ne=%f\nf=%f\nK=%f\nL=%.3f\nDp = %.5f bar\n***'%(o.PType,o.Label,ID,v,e,f,K,L,loss/1e5))
          self.form.editResults.append('%s\t%.1f mm\t%.1f m/s\t%.5f bar'%(o.Label,ID*1000,v,loss/1e5))
        elif o.PType=='Elbow':
          ang=float(o.BendAngle)
          R=float(o.BendRadius)/1000
          nc+=1
          K=fittings.bend_rounded(ID,ang,f,R)
          loss=dP_from_K(K,rho=self.Rho,V=v)
          FreeCAD.Console.PrintMessage('%s: %s\nID=%.2f\nV=%.2f\ne=%f\nf=%f\nK=%f\nang=%.3f\nR=%f\nDp = %.5f bar\n***'%(o.PType,o.Label,ID,v,e,f,K,ang,R,loss/1e5))
          self.form.editResults.append('%s\t%.1f mm\t%.1f m/s\t%.5f bar'%(o.Label,ID*1000,v,loss/1e5))
        elif o.PType=='Reduct':
          pass
      elif hasattr(o,'Kv') and o.Kv>0:
        if self.isLiquid:
          loss=(Q*3600/o.Kv)**2*100000
        elif self.form.comboFluid.currentText()=='water' and not self.isLiquid:
          pass # TODO formula for steam
        else:
          pass # TODO formula for gases
        if hasattr(o,'ID'):
          ID = float(o.ID)/1000
          v=Q/(ID**2*pi/4)
        else: 
          v = 0
          ID = 0
        self.form.editResults.append('%s\t%.1f mm\t%.1f m/s\t%.5f bar'%(o.Label,ID*1000,v,loss/1e5))
      Dp+=loss
    if Dp>200: result=' = %.3f bar'%(Dp/100000)
    else: result=' = %.2e bar'%(Dp/100000)
    self.form.labResult.setText(result)
    self.form.labLength.setText('Total length = %.3f m' %Ltot)
    self.form.labCurves.setText('Nr. of curves = %i' %nc)
  def checkFluid(self):
    T=float(self.form.editTemperature.text())+273.16
    P=float(self.form.editPressure.text())*1e5
    self.isMixture=True
    if self.form.comboFluid.currentText()!='<custom fluid>':
      self.form.editDensity.setEnabled(False)
      self.form.editViscosity.setEnabled(False)
      try: 
        self.fluid=Chemical(self.form.comboFluid.currentText(),T=T,P=P)
        self.isMixture=False
      except: 
        self.fluid=Mixture(self.form.comboFluid.currentText(),T=T,P=P)
      if self.fluid.rhol and self.fluid.mul:
        self.setLiquid()
        self.form.radioLiquid.setChecked(True)
      elif self.fluid.rhog and self.fluid.mug:
        self.setGas()
        self.form.radioGas.setChecked(True)
      else:
        self.form.labState.setText('*** SOLID (no flow) ***')
        self.form.editFlow.setText('0')
      if not self.isMixture:
        CAS=identifiers.CAS_from_any(self.form.comboFluid.currentText())
        IUPAC=identifiers.IUPAC_name(CAS)
        formula=identifiers.formula(CAS)
        self.form.labName.setText('CAS = %s\nIUPAC = %s\nformula = %s'%(CAS,IUPAC,formula))
      else:
        self.form.labName.setText(self.form.comboFluid.currentText()+'\n(mixture)')
    else: # in progress custom fluid
      self.fluid=None
      self.form.labName.setText('*** CUSTOM FLUID ***')
      self.form.editDensity.setEnabled(True)
      self.form.editViscosity.setEnabled(True)
    self.form.labResult.setText('---')
  def setLiquid(self):
    if self.fluid:
      try:
        self.Rho=self.fluid.rhol
        self.Mu=self.fluid.mul
        self.form.editDensity.setText('%.4f' %self.Rho)
        self.form.editViscosity.setText('%.4f' %(self.Mu*1000000/self.Rho)) #conversion between kinematic and dynamic!!
      except:
        QMessageBox.warning(None,'No data found','It seems the fluid has not\na liquid state.')
        self.form.radioGas.setChecked(True)
        return
    self.isLiquid=True
    self.form.labState.setText('*** LIQUID ***')
    self.form.labQ.setText('Flow (m3/h)')
    self.form.labResult.setText('---')
  def setGas(self):
    if self.fluid:
      try:
        self.Rho=self.fluid.rhog
        self.Mu=self.fluid.mug
        self.form.editDensity.setText('%.4f' %self.Rho)
        self.form.editViscosity.setText('%.4f' %(self.Mu*1000000/self.Rho)) #conversion between kinematic and dynamic!!
      except:
        QMessageBox.warning(None,'No data found','It seems the fluid has not\na gas state.')
        self.form.radioLiquid.setChecked(True)
        return
    self.isLiquid=False
    self.form.labState.setText('*** GAS/VAPOUR ***')
    self.form.labQ.setText('Flow (kg/h)')
    self.form.labResult.setText('---')
  def setRho(self):
    self.Rho=float(self.form.editDensity.text())
    print("%f kg/m3" %self.Rho)
  def setMu(self):
    self.Mu=float(self.form.editViscosity.text())*self.Rho/1000000 # conversion between kinematic and dynamic!!
    print("%f Pa*s" %self.Mu)
  def export(self):
    rows=list()
    fields=['Item','ID (mm)','v (m/s)','Dp (bar)']
    for row in self.form.editResults.toPlainText().split('\n'):
      record=[cell.rstrip(' mm bar m/s') for cell in row.split('\t')]
      print(record)
      rows.append(dict(zip(fields,record)))
    f=QtGui.QFileDialog.getSaveFileName()[0]
    if f:
      dpFile=open(abspath(f),'w')
      w=csv.DictWriter(dpFile,fields,restval='-',delimiter=';')
      w.writeheader()
      w.writerows(rows)
      dpFile.close()
