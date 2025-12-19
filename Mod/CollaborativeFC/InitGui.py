import FreeCAD
import FreeCADGui
import os
import subprocess
import sys
import inspect
# Robust path discovery
def get_workbench_root():
    # Attempt 1: Check if __file__ is defined directly
    try:
        if '__file__' in globals():
            return os.path.dirname(os.path.abspath(__file__))
    except:
        pass

    # Attempt 2: Use inspect.currentframe()
    try:
        frame = inspect.currentframe()
        if frame:
            filename = inspect.getfile(frame)
            if filename:
                return os.path.dirname(os.path.abspath(filename))
    except:
        pass

    # Attempt 3: Use inspect.stack()
    try:
        stack = inspect.stack()
        if stack:
            return os.path.dirname(os.path.abspath(stack[0][1]))
    except:
        pass

    FreeCAD.Console.PrintError("[CollaborativeFC] Critical: Could not determine workbench root path!\n")
    return None

ROOT_DIR = get_workbench_root()
FreeCAD.CollaborativeFC_ROOT = ROOT_DIR

# Ensure ROOT_DIR and common site-packages are in sys.path
if ROOT_DIR:
    if ROOT_DIR not in sys.path:
        sys.path.append(ROOT_DIR)
        
    # Attempt to find user-installed packages from system python
    # This helps if dependencies were installed via 'pip install --user'
    try:
        import site
        user_site = site.getusersitepackages()
        if user_site and os.path.exists(user_site) and user_site not in sys.path:
            sys.path.append(user_site)
            FreeCAD.Console.PrintMessage(f"[CollaborativeFC] Added user site-packages: {user_site}\n")
    except Exception:
        pass

FreeCAD.Console.PrintMessage(f"[CollaborativeFC] Root: {ROOT_DIR}\n")

if ROOT_DIR:
    # Resolve symlinks to ensured we are in the repo structure
    REPO_MOD_DIR = os.path.realpath(ROOT_DIR)
    PROJECT_ROOT = os.path.abspath(os.path.join(REPO_MOD_DIR, "..", ".."))
    SIDECAR_PATH = os.path.join(PROJECT_ROOT, "src", "sidecar", "main.py")
    FreeCAD.CollaborativeFC_SIDECAR = SIDECAR_PATH
    FreeCAD.Console.PrintMessage(f"[CollaborativeFC] Sidecar Path: {SIDECAR_PATH}\n")
else:
    SIDECAR_PATH = None
    FreeCAD.CollaborativeFC_SIDECAR = None

# Global process handle
import SidecarManager

# Command to toggle the sidebar visibility
class CollaborativeFC_ToggleSidebar_Command:
    def GetResources(self):
        icon_path = ""
        root = getattr(FreeCAD, "CollaborativeFC_ROOT", None)
        if root:
            icon_path = os.path.join(root, "Resources", "icons", "social-pulse.png")
        
        return {
            'MenuText': 'Toggle Social Pulse',
            'ToolTip': 'Show/Hide the Social Pulse Sidebar',
            'Pixmap': icon_path if (icon_path and os.path.exists(icon_path)) else 'Std_ViewFitAll'
        }
    def Activated(self):
        try:
            from PySide6 import QtWidgets, QtCore
        except ImportError:
            from PySide2 import QtWidgets, QtCore
            
        FreeCAD.Console.PrintMessage("[CollaborativeFC] Toggle Sidebar command activated\n")
        
        # 1. Try to get the sidebar from the workbench instance (Most Reliable)
        wb = FreeCADGui.activeWorkbench()
        dock = None
        sidebar_obj = None
        
        if hasattr(wb, 'sidebar') and wb.sidebar:
            sidebar_obj = wb.sidebar
            dock = sidebar_obj.dock
        
        # 2. Fallback: Search the window
        if not dock:
            mw = FreeCADGui.getMainWindow()
            dock = mw.findChild(QtWidgets.QDockWidget, "CollaborativeFC_SocialPulse")

        if dock:
            # If it's closed/hidden, show it and re-dock it to be sure
            if not dock.isVisible():
                mw = FreeCADGui.getMainWindow()
                if dock.parent() != mw:
                    mw.addDockWidget(QtCore.Qt.RightDockWidgetArea, dock)
                dock.show()
                dock.raise_()
                FreeCAD.Console.PrintMessage("[CollaborativeFC] Sidebar restored and shown\n")
                
                # Ensure webview is running
                if sidebar_obj:
                    is_ready = getattr(sidebar_obj, 'webview_ready', False)
                    is_running = hasattr(sidebar_obj, 'thread') and sidebar_obj.thread.is_alive()
                    if not is_ready and not is_running:
                        sidebar_obj.setup_webview()
            else:
                dock.hide()
                FreeCAD.Console.PrintMessage("[CollaborativeFC] Sidebar hidden\n")
        else:
            FreeCAD.Console.PrintError("[CollaborativeFC] Sidebar dock widget not found!\n")

    def IsActive(self):
        return True

# Command to show the Version Lock explicitly if active
class CollaborativeFC_ShowVersionError_Command:
    def GetResources(self):
        root = getattr(FreeCAD, "CollaborativeFC_ROOT", None)
        icon_path = os.path.join(root, "Resources", "icons", "social-pulse.png") if root else ""
        return {
            'MenuText': 'Check Protocol Status',
            'ToolTip': 'View the protocol compatibility status',
            'Pixmap': icon_path if (icon_path and os.path.exists(icon_path)) else 'Std_ViewFitAll'
        }
    def Activated(self):
        try:
            import LockManager
            lm = LockManager.LockManager.get_instance()
            if lm.check_lock():
                lm.show_overlay()
            else:
                try:
                    from PySide6 import QtWidgets
                except ImportError:
                    from PySide2 import QtWidgets
                QtWidgets.QMessageBox.information(None, "CollaborativeFC", f"Protocol match OK.\nNo issues detected.")
        except Exception as e:
            FreeCAD.Console.PrintError(f"[CollaborativeFC] Version Status Error: {e}\n")
    def IsActive(self):
        return True

# Command to simulate a peer edit (for Glint testing)
class CollaborativeFC_SimulatePeerEdit_Command:
    def GetResources(self):
        return {
            'MenuText': 'Simulate Peer Edit',
            'ToolTip': 'Cycle awareness glints on the selected object',
            'Pixmap': 'Std_ViewScreenShot'
        }
    def Activated(self):
        try:
            import LockManager
            lm = LockManager.LockManager.get_instance()
            if lm.check_lock():
                 lm.show_overlay()
                 return
        except:
            pass
             
        wb = FreeCADGui.activeWorkbench()
        if hasattr(wb, 'glint_manager'):
            # Ensure the manager exists
            if not wb.glint_manager:
                try:
                    import GlintManager
                    wb.glint_manager = GlintManager.GlintManager()
                except Exception as e:
                    FreeCAD.Console.PrintError(f"[CollaborativeFC] Glint Manager Creation Failed: {e}\n")
            
            # Ensure the hooks are installed (even if Activate failed to run)
            if wb.glint_manager and (not wb.glint_manager.tree_view or not wb.glint_manager.tree_proxy):
                try:
                    wb.glint_manager.init_ui_hooks()
                except Exception as e:
                    FreeCAD.Console.PrintError(f"[CollaborativeFC] Glint Hook Failed: {e}\n")
            
            if wb.glint_manager:
                wb.glint_manager.create_mock_glint()
            else:
                FreeCAD.Console.PrintError("[CollaborativeFC] Glint Manager not ready!\n")
        else:
            FreeCAD.Console.PrintError("[CollaborativeFC] Not in CollaborativeFC Workbench!\n")

    def IsActive(self):
        return True

# Command to View the Encrypted Local Ledger
class CollaborativeFC_ViewLedger_Command:
    def GetResources(self):
        root = getattr(FreeCAD, "CollaborativeFC_ROOT", None)
        # Using a distinct icon for the ledger
        icon_path = os.path.join(root, "Resources", "icons", "social-pulse.png") if root else "" 
        return {
            'MenuText': 'View Local Ledger',
            'ToolTip': 'Decrypt and audit the local mutation ledger',
            'Pixmap': icon_path if (icon_path and os.path.exists(icon_path)) else 'Std_ViewScreenShot'
        }
    def Activated(self):
        try:
            import MutationObserver
            try:
                from PySide6 import QtWidgets, QtCore
            except ImportError:
                from PySide2 import QtWidgets, QtCore
            import time
            
            observer = MutationObserver.MutationObserver()
            # Explicit connection check
            test_conn = observer.send_to_sidecar("ping", {})
            if test_conn is None:
                QtWidgets.QMessageBox.critical(None, "Ledger Audit", "Sidecar Engine is NOT responding.\nPlease ensure the workbench is activated correctly.")
                return

            ledger = observer.read_ledger()
            
            if ledger == []:
                QtWidgets.QMessageBox.information(None, "Ledger Audit", "The secure mutation ledger is currently empty.\nStart modeling to see your edits recorded!")
                return
            
            if not ledger:
                QtWidgets.QMessageBox.warning(None, "Ledger Audit", "Failed to retrieve ledger data.")
                return
            
            # Format the output for a dialog
            audit_log = "--- SECURE MUTATION LEDGER (DML) ---\n"
            audit_log += f"Found {len(ledger)} encrypted mutations.\n\n"
            for m in reversed(ledger):
                ts = m.get('timestamp', 0)
                audit_log += f"[{time.ctime(ts)}] {m.get('author')}: {m.get('object')}.{m.get('property')} -> {m.get('value')}\n"
            
            # Simple text popup
            scroll = QtWidgets.QScrollArea()
            label = QtWidgets.QLabel(audit_log)
            label.setTextInteractionFlags(QtCore.Qt.TextSelectableByMouse)
            label.setContentsMargins(20, 20, 20, 20)
            scroll.setWidget(label)
            scroll.setWindowTitle("CollaborativeFC Ledger Audit")
            scroll.setMinimumSize(600, 400)
            scroll.show()
            # Keep a reference to prevent GC
            self._dlg = scroll
        except Exception as e:
            FreeCAD.Console.PrintError(f"[CollaborativeFC] Ledger View Error: {e}\n")
    def IsActive(self):
        return True

FreeCADGui.addCommand('CollaborativeFC_ToggleSidebar', CollaborativeFC_ToggleSidebar_Command())
FreeCADGui.addCommand('CollaborativeFC_SimulatePeerEdit', CollaborativeFC_SimulatePeerEdit_Command())
FreeCADGui.addCommand('CollaborativeFC_ShowVersionError', CollaborativeFC_ShowVersionError_Command())
FreeCADGui.addCommand('CollaborativeFC_ViewLedger', CollaborativeFC_ViewLedger_Command())

# Standalone Workbench Definition without external imports
class CollaborativeFCWorkbench(FreeCADGui.Workbench):
    def GetClassName(self):
        return "Gui::PythonWorkbench"

    MenuText = "CollaborativeFC"
    ToolTip = "CollaborativeFC Workbench"

    def GetIcon(self):
        root = getattr(FreeCAD, "CollaborativeFC_ROOT", None)
        if root:
            icon_path = os.path.join(root, "Resources", "icons", "social-pulse.png")
            if os.path.exists(icon_path):
                return icon_path
        return ""

    def GetMenuText(self): 
        return "CollaborativeFC"
    
    def GetToolTip(self): 
        return "CollaborativeFC Workbench"

    sidebar = None
    glint_manager = None

    def Initialize(self):
        """Called once per session when FreeCAD starts up."""
        FreeCAD.Console.PrintMessage("[CollaborativeFC] Workbench INITIALIZE Started\n")
        
        # Add toolbars and menus
        self.appendToolbar("Collaborative Pulse", ["CollaborativeFC_ToggleSidebar", "CollaborativeFC_SimulatePeerEdit", "CollaborativeFC_ShowVersionError", "CollaborativeFC_ViewLedger"])
        self.appendMenu("Collaborative", ["CollaborativeFC_ToggleSidebar", "CollaborativeFC_SimulatePeerEdit", "CollaborativeFC_ShowVersionError", "CollaborativeFC_ViewLedger"])
        
        # Initialize the sidebar object early but keep it hidden
        if not self.sidebar:
            try:
                import Sidebar
                self.sidebar = Sidebar.PulseSidebar()
                # Explicitly add the dock widget during Initialization
                try:
                    from PySide6 import QtCore
                except ImportError:
                    from PySide2 import QtCore
                FreeCADGui.getMainWindow().addDockWidget(QtCore.Qt.RightDockWidgetArea, self.sidebar.dock)
                self.sidebar.dock.hide()
            except Exception as e:
                FreeCAD.Console.PrintError(f"[CollaborativeFC] Sidebar Prep Failed: {e}\n")

        FreeCAD.Console.PrintMessage("[CollaborativeFC] Workbench INITIALIZE Finished\n")

    def Activated(self):
        """Called when the user selects the workbench from the dropdown."""
        FreeCAD.Console.PrintMessage("\n[CollaborativeFC] >>> WORKBENCH ACTIVATED <<<\n")
        
        try:
            # 1. Start Support Processes (Non-blocking)
            import SidecarManager
            SidecarManager.launch_sidecar()
            
            # 2. Hook Mutation Observer (Local Ledger)
            try:
                import MutationObserver
                # Start or restart the document observer
                MutationObserver.start_observer(author_id="PlayerOne")
            except Exception as e:
                FreeCAD.Console.PrintError(f"[CollaborativeFC] Observer Error: {e}\n")

            # 3. UI Restoration (Sidebar)
            if self.sidebar:
                self.sidebar.dock.show()
                self.sidebar.dock.raise_()
                # Ensure webview is running if it wasn't
                if not getattr(self.sidebar, 'webview_ready', False):
                    self.sidebar.setup_webview()
                FreeCAD.Console.PrintMessage("[CollaborativeFC] Social Pulse Sidebar Restored.\n")
            
            # 4. Awareness Hooks (Glints)
            if not self.glint_manager:
                try:
                    import GlintManager
                    self.glint_manager = GlintManager.GlintManager()
                    self.glint_manager.init_ui_hooks()
                except Exception: pass

            # 5. Background Monitor (Protocol Lock & Session Lifecycle)
            if not hasattr(self, 'lock_check_timer'):
                try: from PySide6 import QtCore 
                except: from PySide2 import QtCore
                self.lock_check_timer = QtCore.QTimer()
                self.lock_check_timer.timeout.connect(self._monitor_version_lock)
                self.lock_check_timer.start(1000)

            FreeCAD.Console.PrintMessage("[CollaborativeFC] >>> COLLABORATIVE SESSION READY <<<\n")
            
        except Exception as e:
            FreeCAD.Console.PrintError(f"[CollaborativeFC] ACTIVATION FAILURE: {e}\n")
            import traceback
            FreeCAD.Console.PrintError(traceback.format_exc())

    def _monitor_version_lock(self):
        """Monitors the LockManager and triggers overlay if lock becomes active."""
        import LockManager
        lm = LockManager.LockManager.get_instance()
        if lm.check_lock():
            # If lock is newly detected and overlay isn't shown
            if not hasattr(self, '_version_overlay_shown') or not self._version_overlay_shown:
                lm.show_overlay()
                self._version_overlay_shown = True

    def Deactivated(self):
        """Called when the user switches to a different workbench."""
        FreeCAD.Console.PrintMessage("[CollaborativeFC] UI Stashed. Background sync remains active.\n")
        if self.sidebar:
            self.sidebar.dock.hide()
        
        # We NO LONGER call stop_observer() here. 
        # This ensures that even if you switch to PartDesign, we record your edits.
        pass

    def ContextMenu(self, recipient):
        # Add items to the context menu
        pass

# Register the workbench
FreeCADGui.addWorkbench(CollaborativeFCWorkbench())

# Hook into app exit to ensure termination
import atexit
import SidecarManager
atexit.register(SidecarManager.terminate_sidecar)
