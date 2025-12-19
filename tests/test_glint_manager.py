import sys
import unittest
from unittest.mock import MagicMock
from PySide6 import QtCore, QtGui, QtWidgets

# Mock FreeCAD before importing GlintManager
sys.modules['FreeCAD'] = MagicMock()
sys.modules['FreeCADGui'] = MagicMock()

import GlintManager

class TestGlintManager(unittest.TestCase):
    def setUp(self):
        self.app = QtWidgets.QApplication.instance() or QtWidgets.QApplication(sys.argv)
        self.manager = GlintManager.GlintManager()
        
    def test_set_glint(self):
        self.manager.set_glint("Box", "p1", True)
        self.assertEqual(self.manager.active_glints.get("Box"), "p1")
        
        self.manager.set_glint("Box", None, False)
        self.assertIsNone(self.manager.active_glints.get("Box"))

    def test_proxy_model_data_background(self):
        source_model = QtGui.QStandardItemModel()
        source_model.appendRow(QtGui.QStandardItem("Box"))
        
        proxy = GlintManager.GlintProxyModel(self.manager, "#A855F7", "#10B981", "#3B82F6")
        proxy.setSourceModel(source_model)
        
        self.manager.set_glint("Box", "p1", True)
        index = proxy.index(0, 0)
        
        bg = proxy.data(index, QtCore.Qt.BackgroundRole)
        self.assertIsInstance(bg, QtGui.QBrush)
        self.assertEqual(bg.color().alpha(), 30)

    def test_proxy_model_data_decoration(self):
        source_model = QtGui.QStandardItemModel()
        source_model.appendRow(QtGui.QStandardItem("Box"))
        
        proxy = GlintManager.GlintProxyModel(self.manager, "#A855F7", "#10B981", "#3B82F6")
        proxy.setSourceModel(source_model)
        
        self.manager.set_glint("Box", "p1", True)
        index = proxy.index(0, 0)
        
        icon = proxy.data(index, QtCore.Qt.DecorationRole)
        self.assertIsInstance(icon, QtGui.QIcon)

if __name__ == "__main__":
    unittest.main()
