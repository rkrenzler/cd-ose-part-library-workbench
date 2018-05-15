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
	 "Title":"Insert a Part",
     "ToolTip": "This is a test command A"},
    {"Command": "boxset", "ButtonImage": "DrawStyleWireFrame.svg",
     "Csv": "boxset.csv",
	 "Title":"Insert a part from box set",
     "MenuText": "Add Boxset", "ToolTip": ""},

    {"Command": "AddFlachprofil", "ButtonImage": "flachprofile.png",
	 "Title":"Insert a Flachprofil",
     "Csv": "flachprofile.csv",
     "MenuText": "Add Flachprofil", "ToolTip": ""},

    {"Command": "AddLframeset", "ButtonImage": "DrawStyleWireFrame.svg",
     "Csv": "lframeset.csv",
	 "Title":"Insert Lframeset",
     "MenuText": "Add Lframeset", "ToolTip": ""},

    {"Command": "AddLibresolarbox", "ButtonImage": "DrawStyleWireFrame.svg",
	 "Title":"Insert Libresolarbox",
     "Csv": "libresolarbox.csv",
     "MenuText": "Add Libresolarbox", "ToolTip": ""},

    {"Command": "AddSchraubenmutter", "ButtonImage": "nut.png",
	 "Title":"Insert a Schraubenmutter",
     "Csv": "schraubenmuttern.csv",
     "MenuText": "Add Schraubenmutter", "ToolTip": ""},

    {"Command": "AddTslotprofil", "ButtonImage": "tslot.png",
	 "Title":"Insert a T-Slot profil",
     "Csv": "tslotprofile.csv",
     "MenuText": "Add T-Slotprofil", "ToolTip": ""},

    {"Command": "AddVerbinder", "ButtonImage": "verbinder.png",
	 "Title":"Insert a Verbinder",
     "Csv": "verbinder.csv",
     "MenuText": "Add Verbinder", "ToolTip": ""},

    {"Command": "Add Winkel", "ButtonImage": "angle.png",
	 "Title":"Insert a Winkel",
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
        self.show_dialog(doc, self.row)

    def IsActive(self):
        """Here you can define if the command must be active or not (greyed) if certain conditions
        are met or not. This function is optional."""
        return True

    def show_dialog(self, document, row):
        table_path = os.path.join(Base.TABLE_PATH, row["Csv"])
        table = PartLibraryGui.gui_check_table(table_path)
        if table is None:
            return  # Error
        #    document = FreeCAD.activeDocument()

        params = PartLibraryGui.DialogParams()
        params.document = document
        params.table = table
        params.dialogTitle = row["Title"]
        # Use the same name for settings as for the table.
        params.settings_name = row["Csv"]
        params.key_column_name = "PartNumber"
        form = PartLibraryGui.BaseDialog(params)
        form.exec_()



# Add commands from the list

for row in COMMAND_TABLE:
    print("Adding command %s" % row["Command"])
    Gui.addCommand(row["Command"], ButtonCommand(row))
