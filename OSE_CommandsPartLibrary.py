#***************************************************************************
#*                                                                         *
#*  This file is part of the FreeCAD_Workbench_Starter project.            *
#*                                                                         *
#*                                                                         *
#*  Copyright (C) 2017                                                     *
#*  Stephen Kaiser <freesol29@gmail.com>                                   *
#*                                                                         *
#*  This library is free software; you can redistribute it and/or          *
#*  modify it under the terms of the GNU Lesser General Public             *
#*  License as published by the Free Software Foundation; either           *
#*  version 2 of the License, or (at your option) any later version.       *
#*                                                                         *            
#*  This library is distributed in the hope that it will be useful,        *
#*  but WITHOUT ANY WARRANTY; without even the implied warranty of         *
#*  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU      *
#*  Lesser General Public License for more details.                        *
#*                                                                         *
#*  You should have received a copy of the GNU Lesser General Public       *
#*  License along with this library; if not, If not, see                   *
#*  <http://www.gnu.org/licenses/>.                                        *
#*                                                                         *
#*                                                                         *
#***************************************************************************

import FreeCAD, Part, OSEBasePartLibrary
from FreeCAD import Gui
import copy

COMMAND_TABLE = [
 {"Command":"A", "ButtonImage":"DrawStyleWireFrame.svg", "Csv":"test_a.csv", "MenuText":"Command A",
 	"ToolTip":"This is a test command A",},
 {"Command":"B", "ButtonImage":"DrawStyleWireFrame.svg", "Csv":"test_b.csv", "MenuText":"Command A",
 	"ToolTip":"This is a test command B"}
 {"Command":"C", "ButtonImage":"DrawStyleWireFrame.svg", "Csv":"test_c.csv", "MenuText":"Command C",
 	"ToolTip":"This is a test command C"} 	
]

# Initalize command list. It is used in InitGui.py.
COMMAND_LIST=[]

for row in COMMAND_TABLE:
	COMMAND_LIST.append(row["Command"])
	
class OSE_CommandButtonClass():
    """Command to add the printer frame"""

    def __init__(self, row):
        self.row = copy.deepcopy(row)

    def GetResources(self):
        return {'Pixmap'  : OSEBasePartLibrary.ICON_PATH + '/'+self.row["ButtonImage"], # the name of a svg file available in the resources
#                'Accel' : "Shift+S", # a default shortcut (optional)
                'MenuText': self.row["ToolTip"],
                'ToolTip' : self.row["ToolTip"]}

    def Activated(self):
        "Do something here when button is clicked"
        FreeCAD.Console.PrintMessage("Workbench is working!")
        if Gui.ActiveDocument == None:
            FreeCAD.newDocument()
#        view = Gui.activeDocument().activeView()
        doc=FreeCAD.activeDocument()
        n=list()
        c = Part.Circle() 
        c.Radius=2.0
        f = doc.addObject("Part::Feature", "Circle") # create a document with a circle feature
        f.Shape = c.toShape() # Assign the circle shape to the shape property
        doc.recompute()
        return

    def IsActive(self):
        """Here you can define if the command must be active or not (greyed) if certain conditions
        are met or not. This function is optional."""
        return True

# Add commands from the list

for row in COMMAND_TABLE:
	Gui.addCommand(row["Command"], OSE_CommandButtonClass(row)) 
