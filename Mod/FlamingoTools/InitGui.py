# from TemplatePyMod gui init module
# (c) 2007 Juergen Riegel LGPL

#****************************************************************************
#*                                                                          *
#*   Flamingo Tools Workbench:                                              *
#*       few tools to speed-up drawing                                      *
#*   Copyright (c) 2016 Riccardo Treu LGPL                                  *
#*                                                                          *
#*   This program is free software; you can redistribute it and/or modify   *
#*   it under the terms of the GNU Lesser General Public License (LGPL)     *
#*   as published by the Free Software Foundation; either version 2 of      *
#*   the License, or (at your option) any later version.                    *
#*   for detail see the LICENCE text file.                                  *
#*                                                                          *
#*   This program is distributed in the hope that it will be useful,        *
#*   but WITHOUT ANY WARRANTY; without even the implied warranty of         *
#*   MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the          *
#*   GNU Library General Public License for more details.                   *
#*                                                                          *
#*   You should have received a copy of the GNU Library General Public      *
#*   License along with this program; if not, write to the Free Software    *
#*   Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA  02111-1307   *
#*   USA                                                                    *
#*                                                                          *
#****************************************************************************

class flamingoToolsWorkbench ( Workbench ):
  "Test workbench object"
  Icon=FreeCAD.getResourceDir() + "Mod/FlamingoTools/flamingo.svg"
  MenuText = "Flamingo Tools WB"
  ToolTip = "Flamingo tools workbench"
  def Initialize(self):
    import CommandsEagle
    list = ["bareImport","doBrdImport","doBrdDispose"]
    self.appendToolbar("eagleTools",list)
    Log ('Loading Eagle tools: done\n')
    import CommandsSpSh
    list2=["findFirst","queryModel"]
    self.appendToolbar("spreadsheetTools",list2)
    Log ('Loading Spreadsheet tools: done\n')
    import CommandsPolar
    list3=["drawPolygon","drawFromFile"]
    self.appendToolbar("polarTools",list3)
    Log ('Loading Polar tools: done\n')
    import CommandsFrame
    list4=["frameIt","fillFrame","alignFlange","levelBeam","pivotBeam","alignEdge","rotJoin","shiftBeam","spinSect","stretchBeam","extend2edge","adjustFrameAngle"]
    self.appendToolbar("frameTools",list4)
    Log ('Loading Frame tools: done\n')
    menu = ["Flamingo tools"]
    self.appendMenu(menu,list4)
    self.appendMenu(menu,list)
    self.appendMenu(menu,list2)
    self.appendMenu(menu,list3)

    Log ('Loading Frame tools: done\n')
  
  def Activated(self):
    if hasattr(FreeCADGui,"draftToolBar"):
      FreeCADGui.draftToolBar.Activated()
    Msg("flamingoTools::Activated()\n")

  def Deactivated(self):
		Msg("flamingoTools::Deactivated()\n")

Gui.addWorkbench(flamingoToolsWorkbench)
