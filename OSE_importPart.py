# This file is a partial copy of https://github.com/hamish2014/FreeCAD_assembly2/blob/master/importPart.py
# From FreeCAD_assembly2 project

import FreeCAD

def importPart( filename, partName=None, doc_assembly=None ):
    if doc_assembly == None:
        doc_assembly = FreeCAD.ActiveDocument
    updateExistingPart = partName != None
    if updateExistingPart:
        FreeCAD.Console.PrintMessage("updating part %s from %s\n" % (partName,filename))
    else:
        FreeCAD.Console.PrintMessage("importing part from %s\n" % filename)
    doc_already_open = filename in [ d.FileName for d in FreeCAD.listDocuments().values() ]
    debugPrint(4, "%s open already %s" % (filename, doc_already_open))
    if doc_already_open:
        doc = [ d for d in FreeCAD.listDocuments().values() if d.FileName == filename][0]
    else:
        if filename.lower().endswith('.fcstd'):
            debugPrint(4, '  opening %s' % filename)
            doc = FreeCAD.openDocument(filename)
            debugPrint(4, '  succesfully opened %s' % filename)
        else: #trying shaping import http://forum.freecadweb.org/viewtopic.php?f=22&t=12434&p=99772#p99772x
            import ImportGui
            doc = FreeCAD.newDocument( os.path.basename(filename) )
            shapeobj=ImportGui.insert(filename,doc.Name)

    visibleObjects = [ obj for obj in doc.Objects
                       if hasattr(obj,'ViewObject') and obj.ViewObject.isVisible()
                       and hasattr(obj,'Shape') and len(obj.Shape.Faces) > 0 and 'Body' not in obj.Name] # len(obj.Shape.Faces) > 0 to avoid sketches, skip Body

    debugPrint(3, '%s objects %s' % (doc.Name, doc.Objects))
    if any([ 'importPart' in obj.Content for obj in doc.Objects]) and not len(visibleObjects) == 1:
        subAssemblyImport = True
        debugPrint(2, 'Importing subassembly from %s' % filename)
        tempPartName = 'import_temporary_part'
        obj_to_copy = doc_assembly.addObject("Part::FeaturePython",tempPartName)
        obj_to_copy.Proxy = Proxy_muxAssemblyObj()
        obj_to_copy.ViewObject.Proxy = ImportedPartViewProviderProxy()
        obj_to_copy.Shape =  muxObjects(doc)
        if (not updateExistingPart) or \
                (updateExistingPart and getattr( doc_assembly.getObject(partName),'updateColors',True)):
            muxMapColors(doc, obj_to_copy)
    else:
        subAssemblyImport = False
        if len(visibleObjects) != 1:
            if not updateExistingPart:
                msg = "A part can only be imported from a FreeCAD document with exactly one visible part. Aborting operation"
                QtGui.QMessageBox.information(  QtGui.qApp.activeWindow(), "Value Error", msg )
            else:
                msg = "Error updating part from %s: A part can only be imported from a FreeCAD document with exactly one visible part. Aborting update of %s" % (partName, filename)
            QtGui.QMessageBox.information(  QtGui.qApp.activeWindow(), "Value Error", msg )
        #QtGui.QMessageBox.warning( QtGui.qApp.activeWindow(), "Value Error!", msg, QtGui.QMessageBox.StandardButton.Ok )
            return
        obj_to_copy  = visibleObjects[0]

    if updateExistingPart:
        obj = doc_assembly.getObject(partName)
        prevPlacement = obj.Placement
        if not hasattr(obj, 'updateColors'):
            obj.addProperty("App::PropertyBool","updateColors","importPart").updateColors = True
        importUpdateConstraintSubobjects( doc_assembly, obj, obj_to_copy )
    else:
        partName = findUnusedObjectName( doc.Label + '_', document=doc_assembly )
        try:
            obj = doc_assembly.addObject("Part::FeaturePython",partName)
        except UnicodeEncodeError:
            safeName = findUnusedObjectName('import_', document=doc_assembly)
            obj = doc_assembly.addObject("Part::FeaturePython", safeName)
            obj.Label = findUnusedLabel( doc.Label + '_', document=doc_assembly )
        obj.addProperty("App::PropertyFile",    "sourceFile",    "importPart").sourceFile = filename
        obj.addProperty("App::PropertyFloat", "timeLastImport","importPart")
        obj.setEditorMode("timeLastImport",1)
        obj.addProperty("App::PropertyBool","fixedPosition","importPart")
        obj.fixedPosition = not any([i.fixedPosition for i in doc_assembly.Objects if hasattr(i, 'fixedPosition') ])
        obj.addProperty("App::PropertyBool","updateColors","importPart").updateColors = True
    obj.Shape = obj_to_copy.Shape.copy()
    if updateExistingPart:
        obj.Placement = prevPlacement
    else:
        for p in obj_to_copy.ViewObject.PropertiesList: #assuming that the user may change the appearance of parts differently depending on the assembly.
            if hasattr(obj.ViewObject, p) and p not in ['DiffuseColor']:
                setattr(obj.ViewObject, p, getattr(obj_to_copy.ViewObject, p))
        obj.ViewObject.Proxy = ImportedPartViewProviderProxy()
    if getattr(obj,'updateColors',True):
        obj.ViewObject.DiffuseColor = copy.copy( obj_to_copy.ViewObject.DiffuseColor )
        #obj.ViewObject.Transparency = copy.copy( obj_to_copy.ViewObject.Transparency )   # .Transparency property
        tsp = copy.copy( obj_to_copy.ViewObject.Transparency )   #  .Transparency workaround for FC 0.17 @ Nov 2016
        if tsp < 100 and tsp!=0:
            obj.ViewObject.Transparency = tsp+1
        if tsp == 100:
            obj.ViewObject.Transparency = tsp-1
        obj.ViewObject.Transparency = tsp   # .Transparency workaround end 
    obj.Proxy = Proxy_importPart()
    obj.timeLastImport = os.path.getmtime( filename )
    #clean up
    if subAssemblyImport:
        doc_assembly.removeObject(tempPartName)
    if not doc_already_open: #then close again
        FreeCAD.closeDocument(doc.Name)
        FreeCAD.setActiveDocument(doc_assembly.Name)
        FreeCAD.ActiveDocument = doc_assembly
    return obj

class Proxy_importPart:
    def execute(self, shape):
        pass
        
def debugPrint(arg1, msg):
    #Ignore arg1
    FreeCAD.Console.PrintLog(msg)

def findUnusedObjectName(alala, document):
    return "blbalbababa"
