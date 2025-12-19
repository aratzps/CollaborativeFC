import os
import subprocess
import sys
import FreeCAD
import FreeCADGui

# Global process handle
sidecar_process = None

def launch_sidecar():
    global sidecar_process
    if sidecar_process and sidecar_process.poll() is None:
        return # Already running

    sidecar_path = getattr(FreeCAD, "CollaborativeFC_SIDECAR", None)
    if not sidecar_path or not os.path.exists(sidecar_path):
        FreeCAD.Console.PrintError(f"[CollaborativeFC] Sidecar not found at: {sidecar_path}\n")
        return

    python_exe = sys.executable
    # On Windows, FreeCAD.exe is sys.executable. We need the bundled python.exe
    if sys.platform == "win32":
        bin_dir = os.path.dirname(python_exe)
        possible_python = os.path.join(bin_dir, "python.exe")
        if os.path.exists(possible_python):
            python_exe = possible_python
        else:
            python_exe = "python" # Fallback to PATH

    # Launch in background
    try:
        FreeCAD.Console.PrintMessage(f"[CollaborativeFC] Launching Sidecar: {python_exe}\n")
        
        # Capture output to a log for debugging
        log_path = os.path.join(os.path.dirname(sidecar_path), "sidecar_output.log")
        with open(log_path, "w") as log_file:
            sidecar_process = subprocess.Popen([python_exe, sidecar_path], 
                                             cwd=os.path.dirname(sidecar_path),
                                             stderr=log_file,
                                             stdout=log_file, # Use file instead of PIPE
                                             text=True)
        
        FreeCAD.Console.PrintMessage(f"[CollaborativeFC] Sidecar Engine Active. PID: {sidecar_process.pid}\n")
        
        if hasattr(FreeCADGui, "getMainWindow"):
            mw = FreeCADGui.getMainWindow()
            if mw:
                mw.statusBar().showMessage(f"Collaborative Engine Active (PID: {sidecar_process.pid})")
    except Exception as e:
        FreeCAD.Console.PrintError(f"[CollaborativeFC] Engine Launch Failed: {e}\n")
        
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
        try:
            sidecar_process.terminate()
        except:
            pass
        sidecar_process = None
