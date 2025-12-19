try:
    from PySide6 import QtWebEngineWidgets
    from PySide6.QtWebEngineCore import QWebEnginePage
    print("SUCCESS: PySide6.QtWebEngineWidgets is available.")
except ImportError:
    print("FAIL: PySide6.QtWebEngineWidgets NOT found.")
    try:
        from PySide2 import QtWebEngineWidgets
        print("PARTIAL: PySide2.QtWebEngineWidgets is available (FreeCAD might be using PySide2?).")
    except ImportError:
        print("FAIL: No QtWebEngineWidgets found in PySide6 OR PySide2.")
