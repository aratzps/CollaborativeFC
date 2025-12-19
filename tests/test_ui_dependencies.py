import unittest
import importlib.util
import sys

print(f"Python Executable: {sys.executable}")

class TestUIDependencies(unittest.TestCase):
    def test_pywebview_installed(self):
        """Verify pywebview is installed."""
        if importlib.util.find_spec('webview') is None:
            self.fail("pywebview module not found")

    def test_pythonnet_installed(self):
        """Verify pythonnet is installed."""
        if importlib.util.find_spec('clr') is None:
            self.fail("pythonnet (clr) module not found")

if __name__ == '__main__':
    unittest.main()
