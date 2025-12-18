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

    # Attempt 3: Try importing the package itself
    try:
        import importlib
        pkg = importlib.import_module('CollaborativeFC')
        if hasattr(pkg, '__file__') and pkg.__file__:
             return os.path.dirname(os.path.abspath(pkg.__file__))
    except Exception:
        pass

    FreeCAD.Console.PrintError("[CollaborativeFC] Critical: Could not determine workbench root path!\n")
    return None

ROOT_DIR = get_workbench_root()
FreeCAD.Console.PrintMessage(f"[CollaborativeFC] Root: {ROOT_DIR}\n")

if ROOT_DIR:
    # Resolve symlinks to ensured we are in the repo structure
    # If ROOT_DIR is in AppData (symlink), realpath puts us in Git Repo
    REPO_MOD_DIR = os.path.realpath(ROOT_DIR)
    # mod/CollaborativeFC -> .. -> mod -> .. -> Root
    # If compiled/installed, structure might differ, but for dev:
    PROJECT_ROOT = os.path.abspath(os.path.join(REPO_MOD_DIR, "..", ".."))
    SIDECAR_PATH = os.path.join(PROJECT_ROOT, "src", "sidecar", "main.py")
    FreeCAD.Console.PrintMessage(f"[CollaborativeFC] Sidecar Path: {SIDECAR_PATH}\n")
else:
    SIDECAR_PATH = None

# Global process handle
sidecar_process = None

def launch_sidecar():
    global sidecar_process
    if sidecar_process and sidecar_process.poll() is None:
        return # Already running

    if not SIDECAR_PATH or not os.path.exists(SIDECAR_PATH):
        FreeCAD.Console.PrintError(f"[CollaborativeFC] Sidecar not found at: {SIDECAR_PATH}\n")
        return

    python_exe = sys.executable
    # Launch in background
    try:
        sidecar_process = subprocess.Popen([python_exe, SIDECAR_PATH], cwd=os.path.dirname(SIDECAR_PATH))
        FreeCAD.Console.PrintMessage(f"[CollaborativeFC] Sidecar launched. PID: {sidecar_process.pid}\n")
        
        # Update Status Bar
        if hasattr(FreeCADGui, "getMainWindow"):
            mw = FreeCADGui.getMainWindow()
            if mw:
                mw.statusBar().showMessage(f"Sidecar Connected (PID: {sidecar_process.pid})")
    except Exception as e:
        FreeCAD.Console.PrintError(f"[CollaborativeFC] Failed to launch sidecar: {e}\n")

def terminate_sidecar():
    global sidecar_process
    if sidecar_process:
        FreeCAD.Console.PrintMessage(f"[CollaborativeFC] Terminating sidecar PID: {sidecar_process.pid}\n")
        sidecar_process.terminate()
        sidecar_process = None

# Standalone Workbench Definition without external imports
class CollaborativeFCWorkbench(FreeCADGui.Workbench):
    def GetClassName(self):
        return "Gui::PythonWorkbench"

    MenuText = "CollaborativeFC"
    ToolTip = "CollaborativeFC Workbench"

    def GetIcon(self):
        # Return path to the icon using discovered ROOT_DIR
        try:
            if ROOT_DIR:
                icon_path = os.path.join(ROOT_DIR, "Resources", "icons", "CollaborativeFC.svg")
                if os.path.exists(icon_path):
                    return icon_path
        except Exception:
            pass
        return ""

    def GetMenuText(self): 
        return "CollaborativeFC"
    
    def GetToolTip(self): 
        return "CollaborativeFC Workbench"

    def Initialize(self):
        # Initialize the workbench (add commands, toolbars, etc.)
        FreeCAD.Console.PrintMessage("[CollaborativeFC] Initialize called\n")
        pass

    def Activate(self):
        # Called when the workbench is activated
        FreeCAD.Console.PrintMessage("[CollaborativeFC] Activate called\n")
        launch_sidecar()

    def Deactivate(self):
        # Called when the workbench is deactivated
        FreeCAD.Console.PrintMessage("[CollaborativeFC] Deactivate called\n")
        pass

    def ContextMenu(self, recipient):
        # Add items to the context menu
        pass

# Register the workbench
FreeCADGui.addWorkbench(CollaborativeFCWorkbench())

# Hook into app exit to ensure termination
import atexit
atexit.register(terminate_sidecar)
