import unittest
import sys
import os
from unittest.mock import MagicMock

# Mock PySide2 before importing Sidebar if not available
try:
    from PySide2 import QtWidgets, QtCore
except ImportError:
    sys.modules['PySide2'] = MagicMock()
    sys.modules['PySide2.QtWidgets'] = MagicMock()
    sys.modules['PySide2.QtCore'] = MagicMock()
    sys.modules['PySide2.QtGui'] = MagicMock()

# Mock FreeCAD
sys.modules['FreeCAD'] = MagicMock()
sys.modules['FreeCADGui'] = MagicMock()

# Add Mod directory to path to allow import of CollaborativeFC
# Note: In the repo, the package is in Mod/CollaborativeFC/
repo_root = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
mod_path = os.path.join(repo_root, "Mod")
if mod_path not in sys.path:
    sys.path.insert(0, mod_path)

from CollaborativeFC import Sidebar

class TestSidebar(unittest.TestCase):
    def test_sidebar_init(self):
        """Verify Sidebar object can be created."""
        sidebar = Sidebar.PulseSidebar()
        self.assertIsNotNone(sidebar.dock)
        self.assertIsNotNone(sidebar.container)
        
    def test_js_api(self):
        """Verify JS API handles clicks."""
        api = Sidebar.JSApi()
        # Should not crash
        api.onPeerClick("TestPeer")

if __name__ == '__main__':
    unittest.main()
