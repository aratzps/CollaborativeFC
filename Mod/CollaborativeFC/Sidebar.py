import os
import threading
import time
import logging
import sys

# RECURSION SHIELD: Give pythonnet massive room to avoid depth crashes
sys.setrecursionlimit(10000)

# SCORCHED EARTH SILENCING: Block all noise from the underlying bridges
class NoiseFilter(logging.Filter):
    def filter(self, record):
        msg = record.getMessage().lower()
        # Blocks the recursion and COM thread errors from flooding the console
        stop_words = ["recursion", "corewebview2", "com object", "empty.empty", "accessibility"]
        return not any(word in msg for word in stop_words)

for logger_name in ['pywebview', 'pythonnet', 'clr']:
    l = logging.getLogger(logger_name)
    l.setLevel(logging.CRITICAL)
    l.addFilter(NoiseFilter())
    l.propagate = False

try:
    from PySide6 import QtCore, QtGui, QtWidgets
    PYSIDE_VER = 6
except ImportError:
    try:
        from PySide2 import QtCore, QtGui, QtWidgets
        PYSIDE_VER = 2
    except ImportError:
        # Mock for headless tests
        PYSIDE_VER = 0
        QtCore = QtGui = QtWidgets = None

try:
    import webview
    HAS_WEBVIEW = True
except ImportError:
    HAS_WEBVIEW = False

# If we are in FreeCAD, FreeCAD and FreeCADGui are already imported
try:
    import FreeCAD
    import FreeCADGui
except ImportError:
    # Mock for testing outside FreeCAD
    class Mock:
        def PrintMessage(self, msg): print(msg)
    FreeCAD = Mock()

class JSApi:
    def __init__(self, sidebar):
        self.sidebar = sidebar

    def onUiReady(self):
        FreeCAD.Console.PrintMessage("[CollaborativeFC] JS UI is Ready. Sending peers...\n")
        self.sidebar.send_mock_peers()

    def onPeerClick(self, peer_name):
        FreeCAD.Console.PrintMessage(f"[CollaborativeFC] Peer Clicked in UI: {peer_name}\n")

    def validateVersion(self, remote_version, remote_build_id):
        """Called from JS when a peer's version info is received."""
        import Constants
        import LockManager
        
        is_ok, msg = Constants.verify_protocol(remote_version, remote_build_id)
        if not is_ok:
            LockManager.LockManager.get_instance().lock_workbench(msg)
            # Update the sidebar UI immediately to prevent interaction
            self.sidebar.setLocked(True)
            # We also send this back to the UI to update the peer status
            return {"status": "mismatch", "message": msg}
        return {"status": "ok"}

class PulseSidebar:
    def __init__(self):
        FreeCAD.Console.PrintMessage("[CollaborativeFC] PulseSidebar __init__ called\n")
        self.dock = QtWidgets.QDockWidget("Social Pulse")
        self.dock.setObjectName("CollaborativeFC_SocialPulse")
        self.dock.setAllowedAreas(QtCore.Qt.LeftDockWidgetArea | QtCore.Qt.RightDockWidgetArea)
        
        # Main container
        self.container = QtWidgets.QWidget()
        self.layout = QtWidgets.QVBoxLayout(self.container)
        self.layout.setContentsMargins(0, 0, 0, 0)
        
        # Sidebar path
        self.sidebar_dir = os.path.join(os.path.dirname(__file__), "Resources", "sidebar")
        self.index_path = os.path.join(self.sidebar_dir, "index.html")
        
        # Placeholder while webview loads
        self.placeholder = QtWidgets.QLabel("Connecting to Synergy Hub...")
        self.placeholder.setAlignment(QtCore.Qt.AlignCenter)
        self.placeholder.setStyleSheet("background-color: #1A1A1B; color: #94A3B8;")
        self.layout.addWidget(self.placeholder)
        
        if not HAS_WEBVIEW:
            self.placeholder.setText("Dependency Missing: pywebview\nPlease run 'pip install pywebview pythonnet'\nin your FreeCAD console.")
            self.placeholder.setStyleSheet("color: #EF4444; background-color: #1A1A1B;")
        
        self.dock.setWidget(self.container)
        
        self._webview_window_internal = None
        self.webview_window_active = False
        self.webview_ready = False

    def setup_webview(self):
        if not HAS_WEBVIEW:
            FreeCAD.Console.PrintError("[CollaborativeFC] setup_webview aborted: HAS_WEBVIEW is False\n")
            return
            
        try:
            import clr
            FreeCAD.Console.PrintMessage("[CollaborativeFC] clr (pythonnet) checked OK\n")
        except ImportError:
            FreeCAD.Console.PrintError("[CollaborativeFC] ERROR: pythonnet (clr) missing although pywebview is present. Try 'pip install pythonnet' in FreeCAD.\n")
            return

        FreeCAD.Console.PrintMessage("[CollaborativeFC] Spawning WebView thread...\n")
        # We start pywebview in a separate thread because webview.start() blocks
        self.thread = threading.Thread(target=self._run_webview, daemon=True)
        self.thread.start()
        
        # Start a timer to check for the window handle and reparent
        self.timer = QtCore.QTimer()
        self.timer.timeout.connect(self._check_and_embed)
        self.timer.start(100)

    def _run_webview(self):
        try:
            # HACK: Bypass pywebview thread check
            threading.current_thread().name = 'MainThread'
            
            # Title for identification
            self.internal_title = "Collaborative Social Pulse"
            
            idx_path = os.path.abspath(self.index_path)
            if not os.path.exists(idx_path):
                 root = getattr(FreeCAD, "CollaborativeFC_ROOT", None)
                 if root:
                     idx_path = os.path.join(root, "Resources", "sidebar", "index.html")

            if not os.path.exists(idx_path):
                FreeCAD.Console.PrintError(f"[CollaborativeFC] ERROR: index.html NOT FOUND\n")
                return

            url = "file:///" + idx_path.replace(os.sep, "/")
            
            self.api = JSApi(self)
            self._webview_window_internal = webview.create_window(
                self.internal_title, 
                url, 
                js_api=self.api,
                on_top=True, # Keep it visible while working
                width=340,
                height=600,
                min_size=(300, 500)
            )
            # Register close event to allow re-opening
            self._webview_window_internal.events.closed += self._on_window_closed
            
            # Use a separate flag to tell the UI we are alive, avoiding direct object access
            self.webview_window_active = True
            
            # Start the engine (this is the blocking call)
            # Use headless=True or similar if available? No, we need the window.
            webview.start(gui='edgechromium', debug=False)
        except Exception as e:
            self._on_window_closed()
            FreeCAD.Console.PrintError(f"[CollaborativeFC] WebView Engine Error: {e}\n")

    def _on_window_closed(self):
        """Cleanup when the floating window is closed."""
        self.webview_window_active = False
        self.webview_ready = False
        if hasattr(self, '_label_hidden'):
            delattr(self, '_label_hidden')
        # Reset placeholder text
        if hasattr(self, 'placeholder'):
            self.placeholder.setText("Social Pulse Window Closed.\nToggle the sidebar icon to restore.")
            self.placeholder.setStyleSheet("background-color: #1A1A1B; color: #94A3B8;")
        # Restart the check timer in case we toggle again
        if hasattr(self, 'timer'):
            self.timer.start(100)

    def _check_and_embed(self):
        # We've moved to "Floating Mode" for maximum stability (prevents FreeCAD crashes)
        # IMPORTANT: We use webview_window_active flag to avoid touching the native COM object from the Qt thread
        if getattr(self, 'webview_window_active', False):
            # Once loaded, we can hide the "Connecting" label in the dock
            if not hasattr(self, '_label_hidden') and self.webview_ready:
                self.placeholder.setText("Pulse Active (Floating Mode)\nCheck your main window for the list.")
                self.placeholder.setStyleSheet("color: #10B981; font-weight: bold;")
                self._label_hidden = True
                self.timer.stop()

    def send_mock_peers(self):
        # Access the window via the internal name to avoid auto-inspectors
        window = getattr(self, '_webview_window_internal', None)
        if not window:
            return
        
        self.webview_ready = True
        
        import Constants
        local_build = Constants.get_freecad_build_id()

        peers = [
            {"id": "p1", "name": "Sarah", "status": "Editing BasePlate", "color": "#A855F7", "isOnline": True, 
             "version": Constants.PROTOCOL_VERSION, "build": local_build},
            {"id": "p2", "name": "Alex", "status": "Viewing Ledger", "color": "#10B981", "isOnline": True,
             "version": "0.1.0", "build": local_build}, # SIMULATED MISMATCH
            {"id": "p3", "name": "Leo", "status": "Offline", "color": "#3B82F6", "isOnline": False,
             "version": Constants.PROTOCOL_VERSION, "build": local_build}
        ]
        
        try:
            import json
            peers_json = json.dumps(peers)
            # Evaluate JS to update the peer list in the frontend
            window.evaluate_js(f"window.updatePeers({peers_json})")
            FreeCAD.Console.PrintMessage("[CollaborativeFC] Pulse Data Synced Successfully.\n")
        except Exception as e:
            FreeCAD.Console.PrintError(f"[CollaborativeFC] Error updating peers: {e}\n")

    def setLocked(self, locked=True):
        """Disables interaction in the sidebar UI."""
        window = getattr(self, '_webview_window_internal', None)
        if window:
            try:
                state = "true" if locked else "false"
                window.evaluate_js(f"window.setSessionLocked({state})")
            except Exception:
                pass
