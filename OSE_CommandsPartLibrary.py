#***************************************************************************
#*                                                                         *
#*  This file is part of the FreeCAD_Workbench_Starter project.            *
#*                                                                         *
#*                                                                         *
#*  Copyright (C) 2017                                                     *
#*  Ruslan Krenzler                                                        *
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

import copy
import os.path

import FreeCAD
from FreeCAD import Gui

import OSE_BasePartLibrary as Base
import OSE_PartLibraryGui as PartLibraryGui

#COMMAND_TABLE = [
 #{"Command":"A", "ButtonImage":"DrawStyleWireFrame.svg", "Csv":"table_d3d.csv", "MenuText":"Command A",
 #	"ToolTip":"This is a test command A"},
#]

COMMAND_TABLE = [
    {"Command": "A", "ButtonImage": "DrawStyleWireFrame.svg", "Csv": "table_d3d.csv", "MenuText": "Command A",
     "ToolTip": "This is a test command A"},
    {"Command": "flachprofil", "ButtonImage": "DrawStyleWireFrame.svg",
     "Csv": "flachprofil.csv",
     "MenuText": "Add Flachprofil", "ToolTip": ""},
    {"Command": "Add L-Verbinder", "ButtonImage": "DrawStyleWireFrame.svg",
     "Csv": "l-verbinder.csv",
     "MenuText": "Add L-Verbinder", "ToolTip": ""},
    {"Command": "Add Mutter", "ButtonImage": "DrawStyleWireFrame.svg",
     "Csv": "muttern.csv",
     "MenuText": "Add Mutter", "ToolTip": ""},
    {"Command": "Add T-Slot", "ButtonImage": "DrawStyleWireFrame.svg",
     "Csv": "tslot.csv",
     "MenuText": "Add T-Slot", "ToolTip": ""},
    {"Command": "Add T-Verbinder", "ButtonImage": "DrawStyleWireFrame.svg",
     "Csv": "t-verbinder.csv",
     "MenuText": "Add T-Verbinder", "ToolTip": ""},
    {"Command": "Add Winkel", "ButtonImage": "DrawStyleWireFrame.svg",
     "Csv": "winkel.csv",
     "MenuText": "Add Winkel", "ToolTip": ""},
]


# Initalize command list. It is used in InitGui.py.
COMMAND_LIST = []

for row in COMMAND_TABLE:
    COMMAND_LIST.append(row["Command"])


class ButtonCommand():
    """Command to add the printer frame"""

    def __init__(self, row):
        self.row = copy.deepcopy(row)
        print("This command got row")
        print(row)

    def GetResources(self):
        return {'Pixmap': Base.ICON_PATH + '/' + self.row["ButtonImage"],  # the name of a svg file available in the resources
                #                'Accel' : "Shift+S", # a default shortcut (optional)
                'MenuText': self.row["MenuText"],
                'ToolTip': self.row["ToolTip"]}

    def Activated(self):
        "Do something here when button is clicked"
        FreeCAD.Console.PrintMessage("Workbench is working!")
        if Gui.ActiveDocument == None:
            FreeCAD.newDocument()
#        view = Gui.activeDocument().activeView()
        doc = FreeCAD.activeDocument()
        table_path = os.path.join(Base.TABLE_PATH, self.row["Csv"])
        PartLibraryGui.show_dialog(doc, table_path)

    def IsActive(self):
        """Here you can define if the command must be active or not (greyed) if certain conditions
        are met or not. This function is optional."""
        return True


# Add commands from the list

for row in COMMAND_TABLE:
    print("Adding command %s" % row["Command"])
    Gui.addCommand(row["Command"], ButtonCommand(row))
