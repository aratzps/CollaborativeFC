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

# Command to Toggle the Surgical HUD (Overlay)
class CollaborativeFC_ToggleHUD_Command:
    def GetResources(self):
        return {
            'MenuText': 'Show Conflict HUD',
            'ToolTip': 'Toggle the Surgical Suite Overlay',
            'Pixmap': 'Std_ViewDetail'
        }

    def on_hud_decision(self, decision):
        try:
            import GhostManager
            gm = GhostManager.get_instance()
            
            # Context: We are acting on the Ghost's target
            target_obj = None
            if gm and gm.active_ghost:
                # Ghost name is 'Ghost_Label', real obj name should be derived or stored
                # For MVP, we assume the user selected the object before ghosting, 
                # or we just grab the mock 'Box' for this demo.
                # In a real impl, HUD would pass back the mutation ID.
                doc = FreeCAD.ActiveDocument
                target_obj = doc.getObject("Box") or doc.getObject("Pad")

            if decision == "accept":
                FreeCAD.Console.PrintMessage(f"[CollaborativeFC] HUD Decision: ACCEPT. Performing Geometric Handshake...\n")
                if target_obj:
                    # Apply the 'Proposed' value (Mock=80.0 from Activated below)
                    target_obj.Length = 80.0 
                    doc.recompute()
                    
                    # 1. Commit to Ledger (Confirming the resolution)
                    import MutationObserver
                    obs = getattr(FreeCAD, "CollaborativeFC_OBSERVER", None)
                    if obs:
                        payload = {
                            "author": obs.manager.author_id, # Confirmed by us
                            "object": target_obj.Name,
                            "property": "Length",
                            "value": "80.0",
                            "status": "RESOLVED"
                        }
                        obs.manager.send_to_sidecar("mutation", payload)
                        FreeCAD.Console.PrintMessage(f"[CollaborativeFC] Resolution committed to Ledger.\n")

            elif decision == "reject":
                FreeCAD.Console.PrintMessage(f"[CollaborativeFC] HUD Decision: REJECT. Reverting...\n")
                # No action needed on target_obj, just cleanup ghost
                
            # Cleanup
            if gm:
                gm.remove_ghost()
                
        except Exception as e:
            FreeCAD.Console.PrintError(f"[CollaborativeFC] HUD Decision Error: {e}\n")

    def Activated(self):
        try:
            import GhostManager
            gm = GhostManager.get_instance()
        except:
            gm = None

        wb = FreeCADGui.activeWorkbench()
        if not hasattr(wb, 'hud'):
            # Lazy Load
            try:
                import SurgicalOverlay
                mw = FreeCADGui.getMainWindow()
                wb.hud = SurgicalOverlay.SurgicalOverlay(mw)
                wb.hud.move(mw.width() // 2 - 200, 100)
                # CONNECT SIGNAL
                wb.hud.decision_made.connect(self.on_hud_decision)
            except Exception as e:
                FreeCAD.Console.PrintError(f"[CollaborativeFC] HUD Init Error: {e}\n")
                return

        if wb.hud.isVisible():
            # HIDE logic (Manual Toggle)
            wb.hud.hide()
            if gm:
                gm.remove_ghost()
        else:
            # SHOW
            wb.hud.show()
            wb.hud.raise_()
            
            # TRIGGER GHOST (Test Data)
            # Find a Box to ghost
            doc = FreeCAD.ActiveDocument
            if doc:
                box = doc.getObject("Box") or doc.getObject("Pad")
                if box and gm:
                    # Create a ghost with Length = 80 (Simulated Conflict)
                    gm.create_ghost(box, "Length", 80.0)
                else:
                    FreeCAD.Console.PrintWarning("[CollaborativeFC] No 'Box' or 'Pad' found to ghost.\n")

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
FreeCADGui.addCommand('CollaborativeFC_ToggleHUD', CollaborativeFC_ToggleHUD_Command())
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
        self.appendToolbar("Collaborative Pulse", ["CollaborativeFC_ToggleSidebar", "CollaborativeFC_SimulatePeerEdit", "CollaborativeFC_ToggleHUD", "CollaborativeFC_ShowVersionError", "CollaborativeFC_ViewLedger"])
        self.appendMenu("Collaborative", ["CollaborativeFC_ToggleSidebar", "CollaborativeFC_SimulatePeerEdit", "CollaborativeFC_ToggleHUD", "CollaborativeFC_ShowVersionError", "CollaborativeFC_ViewLedger"])
        
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

            # 6. Incoming Mutation Sync (WAMP)
            if not hasattr(self, 'sync_timer'):
                try: from PySide6 import QtCore 
                except: from PySide2 import QtCore
                self.sync_timer = QtCore.QTimer()
                self.sync_timer.timeout.connect(self._poll_incoming_mutations)
                self.sync_timer.start(500) # Poll every 500ms

            # 7. Peer Presence Poll (Every 2s)
            if not hasattr(self, 'presence_timer'):
                try: from PySide6 import QtCore 
                except: from PySide2 import QtCore
                self.presence_timer = QtCore.QTimer()
                self.presence_timer.timeout.connect(self._poll_peers)
                self.presence_timer.start(2000)

            FreeCAD.Console.PrintMessage("[CollaborativeFC] >>> COLLABORATIVE SESSION READY <<<\n")
            
        except Exception as e:
            FreeCAD.Console.PrintError(f"[CollaborativeFC] ACTIVATION FAILURE: {e}\n")
            import traceback
            FreeCAD.Console.PrintError(traceback.format_exc())

    def _poll_incoming_mutations(self):
        """Polls the sidecar for incoming property updates."""
        try:
            import MutationObserver
            # We access the singleton via the global hook
            obs = getattr(FreeCAD, "CollaborativeFC_OBSERVER", None)
            if obs:
                # Poll the queue
                mutations = obs.manager.poll_queue()
                if mutations and isinstance(mutations, list) and len(mutations) > 0:
                    FreeCAD.Console.PrintMessage(f"[CollaborativeFC] Syncing {len(mutations)} incoming mutations...\n")
                    self._apply_mutations(mutations)
        except Exception as e:
            FreeCAD.Console.PrintError(f"[CollaborativeFC] Sync Error: {e}\n")

    def _poll_peers(self):
        """Polls the sidecar for active peer list and updates the Sidebar."""
        try:
            obs = getattr(FreeCAD, "CollaborativeFC_OBSERVER", None)
            if obs:
                # 1. Status Check (Epic 5.1)
                status = obs.manager.get_status()
                if status:
                    wamp_state = status.get("wamp", "unknown")
                    buf_size = status.get("buffer_size", 0)
                    
                    if wamp_state == "offline":
                        msg = f"Offline Synergy - Buffering Mutations ({buf_size})"
                        try: FreeCADGui.getMainWindow().statusBar().showMessage(msg)
                        except: pass
                    elif wamp_state == "connected" and buf_size > 0:
                        # Draining buffer
                        msg = f"Synergy Online - Syncing Buffer ({buf_size})..."
                        try: FreeCADGui.getMainWindow().statusBar().showMessage(msg)
                        except: pass
                    # else: Online and Idle (Don't spam status bar)

                peers = obs.manager.get_peers()
                if peers is not None and self.sidebar:
                    self.sidebar.update_peers(peers)
        except Exception:
            pass # Silent fail to avoid log spam

    def _apply_mutations(self, mutations):
        """Applies a batch of mutations to the FreeCAD document."""
        doc = FreeCAD.ActiveDocument
        if not doc: return

        # Access the observer to pause it
        obs = getattr(FreeCAD, "CollaborativeFC_OBSERVER", None)
        if obs: obs.pause()
        
        try:
            seen_actions = set()
            local_author = str(obs.manager.author_id).strip()
            
            for m in mutations:
                incoming_author = str(m.get("author", "unknown")).strip()
                if incoming_author == local_author:
                    # FreeCAD.Console.PrintMessage(f"   [FILTER] Ignoring echo from {incoming_author}\n")
                    continue 

                obj_name = m.get("object")
                prop_name = m.get("property")
                value = m.get("value")
                
                # Dedup check (Object, Prop, Value)
                action_key = (obj_name, prop_name, str(value))
                if action_key in seen_actions:
                    continue
                seen_actions.add(action_key)
                
                obj = doc.getObject(obj_name)
                if obj:
                    old_value = None
                    try:
                        # Capture Old Value
                        if hasattr(obj, prop_name):
                             old_value = getattr(obj, prop_name)

                        # Log the attempt
                        FreeCAD.Console.PrintMessage(f"   [APPLY] {obj_name}.{prop_name} = {value}\n")
                        
                        # Apply the change
                        setattr(obj, prop_name, value)
                        
                        # NO Explicit Recompute here to avoid "Recursive Recompute" in PartDesign
                        # Trust FreeCAD to mark object 'touched' and recompute later.
                        
                    except Exception as e:
                        FreeCAD.Console.PrintError(f"   [APPLY ERROR] {e}\n")
            
            # Post-batch recompute?
            # User reported 'Recursive calling' crash. Removing this is safer.
            # FreeCAD GUI loop will handle dirty objects eventually.
            # doc.recompute() 
            

        except Exception as e:
             FreeCAD.Console.PrintError(f"Application Loop Error: {e}\n")
        finally:
            if obs: obs.resume()

    # --- Workbench-Level Slots ---
    def on_hud_decision(self, decision):
        """Handle Accept/Reject signals from the HUD."""
        try:
            import GhostManager
            gm = GhostManager.get_instance()
            
            # Context: We are acting on the Ghost's target
            target_obj = None
            if gm and gm.active_ghost:
                doc = FreeCAD.ActiveDocument
                # Try to find the original object from the ghost name "Ghost_Name"
                # This is heuristic for the MVP
                if hasattr(gm.active_ghost, "Name") and gm.active_ghost.Name.startswith("Ghost_"):
                     orig_name = gm.active_ghost.Name.replace("Ghost_", "")
                     target_obj = doc.getObject(orig_name)
                
                # Fallback for simulated test
                if not target_obj:
                    target_obj = doc.getObject("Box") or doc.getObject("Pad")

            if decision == "accept":
                FreeCAD.Console.PrintMessage(f"[CollaborativeFC] HUD Decision: ACCEPT. Performing Geometric Handshake...\n")
                if target_obj:
                    # In a real impl, we'd read this from the HUD card or the Ghost context
                    # For MVP, we know the conflict was 80.0 (or we grab it from Ghost if we stored it?)
                    # Getting it from Ghost is clean: Ghost.Length
                    try:
                        new_val = gm.active_ghost.Length.Value if hasattr(gm.active_ghost.Length, "Value") else 80.0
                        target_obj.Length = new_val
                    except:
                        target_obj.Length = 80.0

                    doc.recompute()
                    
                    # Commit to Ledger
                    import MutationObserver
                    obs = getattr(FreeCAD, "CollaborativeFC_OBSERVER", None)
                    if obs:
                        payload = {
                            "author": obs.manager.author_id,
                            "object": target_obj.Name,
                            "property": "Length",
                            "value": str(target_obj.Length.Value), # Actual
                            "status": "RESOLVED"
                        }
                        obs.manager.send_to_sidecar("mutation", payload)
                        FreeCAD.Console.PrintMessage(f"[CollaborativeFC] Resolution committed to Ledger.\n")

            elif decision == "reject":
                FreeCAD.Console.PrintMessage(f"[CollaborativeFC] HUD Decision: REJECT. Reverting...\n")
                if target_obj:
                     # 1. Ensure local state is Safe 
                     # (It should be, due to Revert-on-Divergence. We assume current state IS the safe state).
                     # Just force recompute to be sure.
                     doc.recompute()
                     
                     # 2. Broadcast Counter-Mutation to Peer (Force them to LOCAL value)
                     current_val = target_obj.Length.Value
                     
                     import MutationObserver
                     obs = getattr(FreeCAD, "CollaborativeFC_OBSERVER", None)
                     if obs:
                        payload = {
                            "author": obs.manager.author_id,
                            "object": target_obj.Name,
                            "property": "Length",
                            "value": str(current_val),
                            "status": "REJECTION_ENFORCED"
                        }
                        obs.manager.send_to_sidecar("mutation", payload)
                        FreeCAD.Console.PrintMessage(f"[CollaborativeFC] Rejection broadcast (Val={current_val}) to network.\n")
                
            # Cleanup
            if gm:
                gm.remove_ghost()
                
            # Hide HUD
            if self.sidebar and hasattr(self, 'hud'):
                self.hud.hide()
                
        except Exception as e:
            FreeCAD.Console.PrintError(f"[CollaborativeFC] Workbench HUD Decision Error: {e}\n")

    def _trigger_safety_lock(self, reason, target_obj=None, prop_name=None, proposed_val=None):
        """Triggers the Read-Only Safety Lock OR Surgical Suite."""
        FreeCAD.Console.PrintError(f"[CollaborativeFC] SAFETY TRIGGERED: {reason}\n")
        
        # Check if this is a "Surgical" candidate
        is_surgical = "Divergence" in reason or "Topo" in reason
        
        if is_surgical:
             # Just show the HUD (UX Decision)
             wb = FreeCADGui.activeWorkbench()
             
             # Lazy Load HUD if missing
             if not hasattr(wb, 'hud'):
                 try:
                     import SurgicalOverlay
                     mw = FreeCADGui.getMainWindow()
                     wb.hud = SurgicalOverlay.SurgicalOverlay(mw)
                     wb.hud.move(mw.width() // 2 - 200, 100)
                     # Standardize: Connect to the Workbench's own handler
                     wb.hud.decision_made.connect(self.on_hud_decision) 
                 except Exception as e:
                     FreeCAD.Console.PrintError(f"[CollaborativeFC] HUD Init Error: {e}\n")
                     return

             if hasattr(wb, 'hud'):
                 # Ensure it is visible (force show, do not toggle)
                 if not wb.hud.isVisible():
                     wb.hud.show()
                 wb.hud.raise_()
                 
                 # Create visual ghost
                 if target_obj and proposed_val:
                     try:
                         import GhostManager
                         gm = GhostManager.get_instance()
                         # Pass the CORRECT property name!
                         p_name = prop_name if prop_name else "Length"
                         gm.create_ghost(target_obj, p_name, proposed_val)
                     except Exception as e: 
                         FreeCAD.Console.PrintError(f"Ghost Error: {e}\n")

        # Standard Lock Logic
        import LockManager
        lm = LockManager.LockManager.get_instance()
        if not is_surgical:
            lm.lock_workbench(reason) 
            lm.show_overlay()

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
