# -*- coding: utf-8 -*-
# Author: Ruslan Krenzler.
# Date: 12 Mai 2018
# General classes for piping dialogs

import os.path

from PySide import QtCore, QtGui
import FreeCAD

import OSEBasePartLibrary
import piping
import pipingGui


class PartTableModel(QtCore.QAbstractTableModel):

    def __init__(self, headers, data, parent=None, *args):
        self.headers = headers
        self.table_data = data
        self.keyColumnName = None
        QtCore.QAbstractTableModel.__init__(self, parent, *args)

    def row_count(self, parent):
        return len(self.table_data)

        def column_count(self, parent):
            return len(self.headers)

        def data(self, index, role):
            if not index.isValid():
                return None
            elif role != QtCore.Qt.DisplayRole:
                return None
            return self.table_data[index.row()][index.column()]

        def get_part_key(self, row_index):
            key_index = self.headers.index(self.keyColumnName)
            return self.table_data[row_index][key_index]

        def get_part_row_index(self, key):
            """ Return row index of the part with key *key*.

            The *key* is usually refers to the part number.
            :param key: Key of the part.
            :return: Index of the first row whose key is equal to key
                            return -1 if no row find.
            """
            key_index = self.headers.index(self.keyColumnName)
            for row_i in range(key_index, len(self.table_data)):
                if self.table_data[row_i][key_index] == key:
                    return row_i
            return -1

        def header_data(self, col, orientation, role):
            if orientation == QtCore. Qt.Horizontal and role == QtCore.Qt.DisplayRole:
                return self.headers[col]
            return None


class DialogParams:
    def __init__(self):
        self.document = None
        self.table = None
        self.dialog_title = None
        self.selection_dialog_title = None
        self.fitting_type = None  # Elbow, Tee, Coupling etc..
        self.dimensions_pixmap = None
        self.explanation_text = None
        self.settings_name = None
        self.selection_mode = False
        # Old style column name for the unique ID of the part.
        self.key_column_name = "Name"


class BaseDialog(QtGui.QDialog):
    QSETTINGS_APPLICATION = "OSE piping workbench"

    def __init__(self, params):
        super(BaseDialog, self).__init__()
        self.params = params
        self.init_ui()

    def init_ui(self):
        self.result = -1
        self.setup_ui(self)
        # Fill table with dimensions.
        self.init_table()

        # Restore previous user input. Ignore exceptions to prevent this part
        # part of the code to prevent GUI from starting, once settings are broken.
        try:
            self.restore_input()
        except Exception as e:
            print("Could not restore old user input!")
            print(e)
        self.show()


# The following lines are from QtDesigner .ui-file processed by pyside-uic
# pyside-uic --indent=0 add-part.ui -o tmp.py
#
# The file paths needs to be adjusted manually. For example
# self.label.setPixmap(QtGui.QPixmap(GetMacroPath()+"coupling-dimensions.png"))
# os.path.join(OSEBasePartLibrary.IMAGE_PATH, self.params.dimensions_pixmap)
# access datata in some special FreeCAD directory.
    def setup_ui(self, dialog):
        dialog.setObjectName("Dialog")
        dialog.resize(800, 800)
        self.verticalLayout = QtGui.QVBoxLayout(dialog)
        self.verticalLayout.setObjectName("verticalLayout")
        self.tableViewParts = QtGui.QTableView(dialog)
        self.tableViewParts.setSelectionMode(
            QtGui.QAbstractItemView.SingleSelection)
        self.tableViewParts.setSelectionBehavior(
            QtGui.QAbstractItemView.SelectRows)
        self.tableViewParts.setObjectName("tableViewParts")
        self.verticalLayout.addWidget(self.tableViewParts)
        self.labelText = QtGui.QLabel(dialog)
        self.labelText.setTextFormat(QtCore.Qt.AutoText)
        self.labelText.setWordWrap(True)
        self.labelText.setObjectName("labelText")
        self.verticalLayout.addWidget(self.labelText)
        self.labelImage = QtGui.QLabel(dialog)
        self.labelImage.setText("")
        self.labelImage.setPixmap(os.path.join(
            OSEBasePartLibrary.IMAGE_PATH, self.params.dimensions_pixmap))
        self.labelImage.setAlignment(QtCore.Qt.AlignCenter)
        self.labelImage.setObjectName("labelImage")
        self.verticalLayout.addWidget(self.labelImage)
        self.buttonBox = QtGui.QDialogButtonBox(dialog)
        self.buttonBox.setOrientation(QtCore.Qt.Horizontal)
        self.buttonBox.setStandardButtons(
            QtGui.QDialogButtonBox.Cancel | QtGui.QDialogButtonBox.Ok)
        self.buttonBox.setObjectName("buttonBox")
        self.verticalLayout.addWidget(self.buttonBox)

        self.retranslate_ui(dialog)
        QtCore.QObject.connect(
            self.buttonBox, QtCore.SIGNAL("accepted()"), dialog.accept)
        QtCore.QObject.connect(
            self.buttonBox, QtCore.SIGNAL("rejected()"), dialog.reject)
        QtCore.QMetaObject.connectSlotsByName(dialog)

    def retranslate_ui(self, dialog):
        dialog.setWindowTitle(QtGui.QApplication.translate(
            "Dialog", self.params.dialog_title, None, QtGui.QApplication.UnicodeUTF8))
        self.labelText.setText(QtGui.QApplication.translate(
            "Dialog", self.params.explanation_text, None, QtGui.QApplication.UnicodeUTF8))

    def init_table(self):
        # Read table data from CSV
        self.model = pipingGui.PartTableModel(
            self.params.table.headers, self.params.table.data)
        self.model.keyColumnName = self.params.key_column_name
        self.tableViewParts.setModel(self.model)

    def get_selected_part_name(self):
        sel = self.tableViewParts.selectionModel()
        if sel.isSelected:
            if len(sel.selectedRows()) > 0:
                row_index = sel.selectedRows()[0].row()
                return self.model.getPartKey(row_index)
        return None

    def select_part_by_name(self, part_name):
        """Select first row with a part with a name partName."""
        if part_name is not None:
            row_i = self.model.getPartRowIndex(part_name)
            if row_i >= 0:
                self.tableViewParts.selectRow(row_i)

    def create_new_part(self, document, table, part_name):
        """ This function must be implement by the parent class.

        It must return a part if succees and None if fail."""
        pass

    def accept_creation_mode(self):
        """User clicked OK"""
        # If there is no active document, show a warning message and do nothing.
        if self.params.document is None:
            text = "I have not found any active document were I can create an {0}.\n"\
                "Use menu File->New to create a new document first, "\
                "then try to create the {0} again.".format(
                    self.params.fitting_type)
            msg_box = QtGui.QMessageBox(QtGui.QMessageBox.Warning, "Creating of the %s failed.".format(
                self.params.fitting_type), text)
            msg_box.exec_()
            super(BaseDialog, self).accept()
            return

        # Get suitable row from the the table.
        part_name = self.get_selected_part_name()

        if part_name is not None:
            part = self.create_new_part(
                self.params.document, self.params.table, part_name)
            if part is not None:
                self.params.document.recompute()
                # Save user input for the next dialog call.
                self.saveInput()
                # Call parent class.
                super(BaseDialog, self).accept()

        else:
            msg_box = QtGui.QMessageBox()
            msg_box.setText("Select part")
            msg_box.exec_()

    def accept_selection_mode(self):
        self.selectedPart = self.getSelectedPartName()

        if self.selectedPart is None:
            msg_box = QtGui.QMessageBox()
            msg_box.setText("Select part")
            msg_box.exec_()
        else:
            super(BaseDialog, self).accept()

    def accept(self):
        if self.params.selection_mode:
            return self.acceptSelectionMode()
        else:
            self.accept_creation_mode()

    def save_additional_data(self, settings):
        pass

    def save_input(self):
        """Store user input for the next run."""
        settings = QtCore.QSettings(
            BaseDialog.QSETTINGS_APPLICATION, self.params.settings_name)
        settings.setValue("LastSelectedPartNumber", self.get_selected_part_name())
        self.saveAdditionalData(settings)
        settings.sync()

    def restore_input(self):
        settings = QtCore.QSettings(
            BaseDialog.QSETTINGS_APPLICATION, self.params.settings_name)
        self.select_part_by_name(settings.value("LastSelectedPartNumber"))

    def show_for_selection(self, part_name=None):
        """ Show pipe dialog, to select pipe and not to create it.
        :param partName: name of the part to be selected. Use None if you do not want to select
        anything.
        """
        # If required select
        self.params.selection_mode = True
        self.setWindowTitle(QtGui.QApplication.translate("Dialog", self.params.selection_dialog_title,
                                                         None, QtGui.QApplication.UnicodeUTF8))
        self.selected_part = None
        if part_name is not None:
            self.select_part_by_name(part_name)
        self.exec_()
        return self.selectedPart

    def show_for_creation(self):
        self.params.selection_mode = False
        self.setWindowTitle(QtGui.QApplication.translate("Dialog", self.params.dialog_title,
                                                         None, QtGui.QApplication.UnicodeUTF8))
        self.exec_()


# Before working with macros, try to load the dimension table.
def gui_check_table(table_path):
    dimensions_used = []
    # Check if the CSV file exists.
    if os.path.isfile(table_path) is False:
        text = "This tablePath requires %s  but this file does not exist." % (
            table_path)
        msg_box = QtGui.QMessageBox(QtGui.QMessageBox.Warning,
                                   "Creating of the part failed.", text)
        msg_box.exec_()
        return None  # Error

    FreeCAD.Console.PrintMessage(
        "Trying to load CSV file with dimensions: %s" % table_path)
    table = piping.CsvTable(dimensions_used)
    table.load(table_path)

    if table.hasValidData is False:
        text = 'Invalid %s.\n'\
            'It must contain columns %s.' % (
                table_path, ", ".join(dimensions_used))
        msg_box = QtGui.QMessageBox(
            QtGui.QMessageBox.Warning, "Creating of the part failed.", text)
        msg_box.exec_()
        return None  # Error

    return table


doc = FreeCAD.activeDocument()
table_path = OSEBasePartLibrary.TABLE_PATH + "/table_a.csv"


def show_dialog(row):
    # Open a CSV file, check its content, and return it as a piping.CsvTable object.
    table = gui_check_table(table_path)
    if table is None:
        return  # Error
    document = FreeCAD.activeDocument()

    params = DialogParams()
    params.document = document
    params.table = table
    params.dialogTitle = "Insert Part"
    params.fittingType = "Part"
    params.dimensions_pixmap = "coupling-dimensions.png"
    params.explanation_text = "Exmlanation Text"
    params.settings_name = "coupling user input"
    params.key_column_name = "PartNumber"
    form = BaseDialog(params)
    form.exec_()


show_dialog(None)
