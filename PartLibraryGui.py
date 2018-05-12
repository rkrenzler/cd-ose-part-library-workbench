# -*- coding: utf-8 -*-
# Author: Ruslan Krenzler.
# Date: 12 Mai 2018
# General classes for piping dialogs

import collections # Named touple
import math
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
	
	def rowCount(self, parent): 
		return len(self.table_data) 
 
	def columnCount(self, parent):
		return len(self.headers) 
 
	def data(self, index, role):
		if not index.isValid(): 
			return None
		elif role != QtCore.Qt.DisplayRole: 
			return None
		return self.table_data[index.row()][index.column()] 

	def getPartKey(self, rowIndex):
		key_index = self.headers.index(self.keyColumnName)
		return self.table_data[rowIndex][key_index]
	
	def getPartRowIndex(self, key):
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
	
	def headerData(self, col, orientation, role):
		if orientation ==QtCore. Qt.Horizontal and role == QtCore.Qt.DisplayRole:
			return self.headers[col]
		return None
		
class DialogParams:
	def __init__(self):
		self.document = None
		self.table = None
		self.dialogTitle = None
		self.selectionDialogTitle = None
		self.fittingType = None # Elbow, Tee, Coupling etc..
		self.dimensionsPixmap = None
		self.explanationText = None
		self.settingsName = None
		self.selectionMode = False
		self.keyColumnName = "Name" # Old style column name for the unique ID of the part.
	
class BaseDialog(QtGui.QDialog):
	QSETTINGS_APPLICATION = "OSE piping workbench"

	def __init__(self, params):
		super(BaseDialog, self).__init__()
		self.params = params
		self.initUi()
		if piping.HasFlamingoSupport():
			self.radioButtonFlamingo.setEnabled(True)			
		else:
			self.radioButtonFlamingo.setEnabled(False)
			
	def initUi(self): 
		Dialog = self # Added 
		self.result = -1 
		self.setupUi(self)
		# Fill table with dimensions. 
		self.initTable()

		# Restore previous user input. Ignore exceptions to prevent this part
		# part of the code to prevent GUI from starting, once settings are broken.
		try:
			self.restoreInput()
		except Exception as e:
			print ("Could not restore old user input!")
			print(e)
		self.show()

# The following lines are from QtDesigner .ui-file processed by pyside-uic
# pyside-uic --indent=0 create-coupling.ui -o tmp.py
#
# The file paths needs to be adjusted manually. For example
# self.label.setPixmap(QtGui.QPixmap(GetMacroPath()+"coupling-dimensions.png"))
# os.path.join(OSEBasePartLibrary.IMAGE_PATH, self.params.dimensionsPixmap)
# access datata in some special FreeCAD directory.
	def setupUi(self, Dialog):
		Dialog.setObjectName("Dialog")
		Dialog.resize(800, 733)
		self.verticalLayout = QtGui.QVBoxLayout(Dialog)
		self.verticalLayout.setObjectName("verticalLayout")
		self.outputTypeWidget = QtGui.QWidget(Dialog)
		self.outputTypeWidget.setMinimumSize(QtCore.QSize(0, 55))
		self.outputTypeWidget.setLayoutDirection(QtCore.Qt.LeftToRight)
		self.outputTypeWidget.setObjectName("outputTypeWidget")
		self.groupBox = QtGui.QGroupBox(self.outputTypeWidget)
		self.groupBox.setGeometry(QtCore.QRect(10, 0, 263, 58))
		self.groupBox.setObjectName("groupBox")
		self.horizontalLayout = QtGui.QHBoxLayout(self.groupBox)
		self.horizontalLayout.setContentsMargins(0, 0, 0, 0)
		self.horizontalLayout.setObjectName("horizontalLayout")
		self.radioButtonSolid = QtGui.QRadioButton(self.groupBox)
		self.radioButtonSolid.setEnabled(True)
		self.radioButtonSolid.setChecked(True)
		self.radioButtonSolid.setObjectName("radioButtonSolid")
		self.horizontalLayout.addWidget(self.radioButtonSolid)
		self.radioButtonFlamingo = QtGui.QRadioButton(self.groupBox)
		self.radioButtonFlamingo.setEnabled(False)
		self.radioButtonFlamingo.setChecked(False)
		self.radioButtonFlamingo.setObjectName("radioButtonFlamingo")
		self.horizontalLayout.addWidget(self.radioButtonFlamingo)
		self.radioButtonParts = QtGui.QRadioButton(self.groupBox)
		self.radioButtonParts.setObjectName("radioButtonParts")
		self.horizontalLayout.addWidget(self.radioButtonParts)
		self.verticalLayout.addWidget(self.outputTypeWidget)
		self.tableViewParts = QtGui.QTableView(Dialog)
		self.tableViewParts.setSelectionMode(QtGui.QAbstractItemView.SingleSelection)
		self.tableViewParts.setSelectionBehavior(QtGui.QAbstractItemView.SelectRows)
		self.tableViewParts.setObjectName("tableViewParts")
		self.verticalLayout.addWidget(self.tableViewParts)
		self.labelExplanation = QtGui.QLabel(Dialog)
		self.labelExplanation.setTextFormat(QtCore.Qt.AutoText)
		self.labelExplanation.setWordWrap(True)
		self.labelExplanation.setObjectName("labelExplanation")
		self.verticalLayout.addWidget(self.labelExplanation)
		self.labelImage = QtGui.QLabel(Dialog)
		self.labelImage.setText("")
		self.labelImage.setPixmap(os.path.join(OSEBasePartLibrary.IMAGE_PATH, self.params.dimensionsPixmap))
		self.labelImage.setAlignment(QtCore.Qt.AlignCenter)
		self.labelImage.setObjectName("labelImage")
		self.verticalLayout.addWidget(self.labelImage)
		self.buttonBox = QtGui.QDialogButtonBox(Dialog)
		self.buttonBox.setOrientation(QtCore.Qt.Horizontal)
		self.buttonBox.setStandardButtons(QtGui.QDialogButtonBox.Cancel|QtGui.QDialogButtonBox.Ok)
		self.buttonBox.setObjectName("buttonBox")
		self.verticalLayout.addWidget(self.buttonBox)

		self.retranslateUi(Dialog)
		QtCore.QObject.connect(self.buttonBox, QtCore.SIGNAL("accepted()"), Dialog.accept)
		QtCore.QObject.connect(self.buttonBox, QtCore.SIGNAL("rejected()"), Dialog.reject)
		QtCore.QMetaObject.connectSlotsByName(Dialog)

	def retranslateUi(self, Dialog):
		Dialog.setWindowTitle(QtGui.QApplication.translate("Dialog", self.params.dialogTitle, None, QtGui.QApplication.UnicodeUTF8))
		self.groupBox.setTitle(QtGui.QApplication.translate("Dialog", "Output type:", None, QtGui.QApplication.UnicodeUTF8))
		self.radioButtonSolid.setText(QtGui.QApplication.translate("Dialog", "Solid", None, QtGui.QApplication.UnicodeUTF8))
		self.radioButtonFlamingo.setText(QtGui.QApplication.translate("Dialog", "Flamingo", None, QtGui.QApplication.UnicodeUTF8))
		self.radioButtonParts.setText(QtGui.QApplication.translate("Dialog", "Parts", None, QtGui.QApplication.UnicodeUTF8))
		self.labelExplanation.setText(QtGui.QApplication.translate("Dialog", self.params.explanationText, None, QtGui.QApplication.UnicodeUTF8))

	def initTable(self):
		# Read table data from CSV
		self.model = pipingGui.PartTableModel(self.params.table.headers, self.params.table.data)
		self.model.keyColumnName = self.params.keyColumnName
		self.tableViewParts.setModel(self.model)
		
	def getSelectedPartName(self):
		sel = self.tableViewParts.selectionModel()
		if sel.isSelected:
			if len(sel.selectedRows())> 0:
				rowIndex = sel.selectedRows()[0].row()
				return self.model.getPartKey(rowIndex)
		return None

	def selectPartByName(self, partName):
		"""Select first row with a part with a name partName."""
		if partName is not None:
			row_i = self.model.getPartRowIndex(partName)
			if row_i >= 0:
				self.tableViewParts.selectRow(row_i)

	def createNewPart(self, document, table, partName, outputType):
		""" This function must be implement by the parent class.
		
		It must return a part if succees and None if fail."""
		pass

	def acceptCreationMode(self):
		"""User clicked OK"""
		# If there is no active document, show a warning message and do nothing.
		if self.params.document is None:
			text = "I have not found any active document were I can create an {0}.\n"\
				"Use menu File->New to create a new document first, "\
				"then try to create the {0} again.".format(self.params.fittingType)
			msgBox = QtGui.QMessageBox(QtGui.QMessageBox.Warning, "Creating of the %s failed.".format(
									self.params.fittingType), text)
			msgBox.exec_()
			super(BaseDialog, self).accept()
			return

		# Get suitable row from the the table.
		partName = self.getSelectedPartName()

		if partName is not None:
			outputType = self.getOutputType()
			part = self.createNewPart(self.params.document, self.params.table, partName, outputType)
			if part is not None:
				self.params.document.recompute()
				# Save user input for the next dialog call.
				self.saveInput()
				# Call parent class.
				super(BaseDialog, self).accept()
				
		else:
			msgBox = QtGui.QMessageBox()
			msgBox.setText("Select part")
			msgBox.exec_()

	def acceptSelectionMode(self):
		self.selectedPart = self.getSelectedPartName()

		if self.selectedPart is None:
			msgBox = QtGui.QMessageBox()
			msgBox.setText("Select part")
			msgBox.exec_()
		else:
			super(BaseDialog, self).accept()
	
	def accept(self):
		if self.params.selectionMode:
			return self.acceptSelectionMode()
		else:
			self.acceptCreationMode()

	def saveAdditionalData(self, settings):
		pass
					
	def saveInput(self):
		"""Store user input for the next run."""
		settings = QtCore.QSettings(BaseDialog.QSETTINGS_APPLICATION, self.params.settingsName)

		if self.radioButtonFlamingo.isChecked():
			settings.setValue("radioButtonsOutputType", piping.OUTPUT_TYPE_FLAMINGO)
		elif self.radioButtonParts.isChecked():
			settings.setValue("radioButtonsOutputType", piping.OUTPUT_TYPE_PARTS)
		else : # Default is solid.
			settings.setValue("radioButtonsOutputType", piping.OUTPUT_TYPE_SOLID)

		settings.setValue("LastSelectedPartNumber", self.getSelectedPartName())
		self.saveAdditionalData(settings)		
		settings.sync()

	def restoreAdditionalInput(self, settings):
		pass

	def restoreInput(self):
		settings = QtCore.QSettings(BaseDialog.QSETTINGS_APPLICATION, self.params.settingsName)
		
		output = int(settings.value("radioButtonsOutputType", piping.OUTPUT_TYPE_SOLID))
		if output == piping.OUTPUT_TYPE_FLAMINGO and piping.HasFlamingoSupport():
			self.radioButtonFlamingo.setChecked(True)			
		elif  output == piping.OUTPUT_TYPE_PARTS:
			self.radioButtonParts.setChecked(True)
		else: # Default is solid. output == piping.OUTPUT_TYPE_SOLID
			self.radioButtonSolid.setChecked(True)

		self.selectPartByName(settings.value("LastSelectedPartNumber"))
		self.restoreAdditionalInput(settings)

	def getOutputType(self):
		if self.radioButtonFlamingo.isChecked():
			return piping.OUTPUT_TYPE_FLAMINGO
		elif self.radioButtonParts.isChecked():
			return piping.OUTPUT_TYPE_PARTS
		else: # Default is solid.
			return piping.OUTPUT_TYPE_SOLID

	def showForSelection(self, partName=None):
		""" Show pipe dialog, to select pipe and not to create it.
		:param partName: name of the part to be selected. Use None if you do not want to select
		anything.
		"""
		# If required select
		self.params.selectionMode = True
		self.setWindowTitle(QtGui.QApplication.translate("Dialog", self.params.selectionDialogTitle,
					None, QtGui.QApplication.UnicodeUTF8))
		self.selectedPart = None
		if partName is not None:
			self.selectPartByName(partName)
		self.exec_()
		return self.selectedPart
		
	def showForCreation(self):
		self.params.selectionMode = False
		self.setWindowTitle(QtGui.QApplication.translate("Dialog", self.params.dialogTitle,
					None, QtGui.QApplication.UnicodeUTF8))
		self.exec_()
		
	
# Before working with macros, try to load the dimension table.
def GuiCheckTable(tablePath):
	dimensionsUsed = []
	# Check if the CSV file exists.
	if os.path.isfile(tablePath) == False:
		text = "This tablePath requires %s  but this file does not exist."%(tablePath)
		msgBox = QtGui.QMessageBox(QtGui.QMessageBox.Warning, 
			"Creating of the part failed.", text)
		msgBox.exec_()
		return None # Error

        FreeCAD.Console.PrintMessage("Trying to load CSV file with dimensions: %s"%tablePath) 
	table = piping.CsvTable(dimensionsUsed)
	table.load(tablePath)

	if table.hasValidData == False:
		text = 'Invalid %s.\n'\
			'It must contain columns %s.'%(tablePath, ", ".join(dimensionsUsed))
		msgBox = QtGui.QMessageBox(QtGui.QMessageBox.Warning, "Creating of the part failed.", text)
		msgBox.exec_()
		return None # Error

	return table

import OSEBasePartLibrary
doc=FreeCAD.activeDocument()
table_path = OSEBasePartLibrary.TABLE_PATH + "/table_a.csv"

			
def show_dialog(row):
	table = GuiCheckTable(table_path) # Open a CSV file, check its content, and return it as a piping.CsvTable object.
	if table == None:
		return # Error
	document = FreeCAD.activeDocument()
		
	params = DialogParams()
	params.document = document
	params.table = table
	params.dialogTitle = "Create Coupling"
	params.fittingType = "Coupling"
	params.dimensionsPixmap = "coupling-dimensions.png"
	params.explanationText = "<html><head/><body><p>To construct a coupling we use these dimensions, elbow only these dimensions are used: alpha, L, N,  M, M1, POD, POD1, PThk, and PThk1. In Additinon, Flamingo uses the Schedule dimension if it is present in the table. All other dimensions are used for inromation only. </p></body></html>"
	params.settingsName = "coupling user input"
	params.keyColumnName = "PartNumber"
	form = BaseDialog(params)
	form.exec_()
	
show_dialog(None)

