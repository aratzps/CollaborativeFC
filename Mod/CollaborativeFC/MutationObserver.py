import socket
import json
import FreeCAD
import FreeCADGui

class MutationObserver:
    """
    Hooks into FreeCAD events to capture property changes and send them
    to the encrypted OCP Sidecar ledger.
    """
    def __init__(self, port=5555):
        self.port = port
        self.host = "127.0.0.1"
        self.author_id = "local_user" # Default
        
    def set_author(self, author_id):
        self.author_id = author_id

    def send_to_sidecar(self, command, payload):
        """Standard IPC sender to the Sidecar."""
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                s.settimeout(1.0)
                s.connect((self.host, self.port))
                request = {"command": command, "payload": payload}
                s.sendall(json.dumps(request).encode())
                
                data_chunks = []
                while True:
                    chunk = s.recv(4096)
                    if not chunk:
                        break
                    data_chunks.append(chunk)
                
                if data_chunks:
                    full_data = b"".join(data_chunks)
                    return json.loads(full_data.decode())
        except Exception as e:
            # Silently fail if sidecar is not reachable to avoid freezing FreeCAD
            pass
        return None

    def onAfterChange(self, obj, prop):
        """Standard property change hook."""
        self._process_change(obj, prop, "AfterChange")

    def _process_change(self, obj, prop, source):
        # 0. Safety Lock Check
        try:
            import LockManager
            if LockManager.LockManager.get_instance().check_lock():
                return
        except: pass

        # We avoid recording internal FreeCAD UI properties
        if prop in ["Proxy", "Visibility", "ViewObject", "Label", "ExpressionEngine"]:
            return

        try:
            val = getattr(obj, prop)
            # Serialize basic types and quantities
            if hasattr(val, 'Value'): val = val.Value
            
            payload = {
                "author": self.author_id,
                "object": obj.Name,
                "property": prop,
                "value": str(val)
            }
            
            # Signal Trace: Ground truth for signal reception
            FreeCAD.Console.PrintMessage(f"[CollaborativeFC] [{source}] Detect: {obj.Name}.{prop}\n")
            
            res = self.send_to_sidecar("mutation", payload)
            if not res or res.get("status") != "ok":
                # Only log if it's the first failure to avoid spamming
                if not hasattr(self, '_last_ipc_failed'):
                    FreeCAD.Console.PrintWarning("[CollaborativeFC] Sidecar not acknowledging mutations.\n")
                    self._last_ipc_failed = True
            else:
                self._last_ipc_failed = False
                
        except Exception as e:
            if "has no attribute" not in str(e):
                FreeCAD.Console.PrintError(f"[CollaborativeFC] Mutation capture error ({prop}): {e}\n")

    def onSaved(self, obj_name):
        """Triggered when the document is saved."""
        try:
            import LockManager
            if LockManager.LockManager.get_instance().check_lock():
                FreeCAD.Console.PrintWarning(f"[CollaborativeFC] Save Commit Blocked (Locked)\n")
                return

            payload = {
                "author": self.author_id,
                "object": obj_name,
                "property": "DOCUMENT_STATE",
                "value": "SAVED_COMMIT"
            }
            FreeCAD.Console.PrintMessage(f"[CollaborativeFC] [COMMIT] Checkpoint created for: {obj_name}\n")
            self.send_to_sidecar("mutation", payload)
        except Exception as e:
            FreeCAD.Console.PrintError(f"[CollaborativeFC] Save Checkpoint Failed: {e}\n")

    def read_ledger(self):
        """Retrieves and decrypts the entire ledger."""
        return self.send_to_sidecar("read_ledger", {})

    def poll_queue(self):
        """Checks sidecar for incoming network mutations."""
        return self.send_to_sidecar("poll_queue", {})

class DocumentObserver:
    """Proxy observer pinned to the App using standard FreeCAD Slot names."""
    def __init__(self, manager):
        self.manager = manager
        self.paused = False
        
    def pause(self): self.paused = True
    def resume(self): self.paused = False

    def onChanged(self, *args):
        if self.paused: return
        if len(args) >= 2:
            self.manager._process_change(args[-2], args[-1], "onChanged")

    def onAfterChange(self, *args):
        if self.paused: return
        if len(args) >= 2:
            self.manager.onAfterChange(args[-2], args[-1])
            
    # Standard FreeCAD Slot names for Global Observers
    def slotChangedObject(self, obj, prop):
        if self.paused: return
        self.manager._process_change(obj, prop, "slotChanged")

    def slotAfterChange(self, obj, prop):
        if self.paused: return
        self.manager.onAfterChange(obj, prop)

    # Document Lifecycle Slots
    def slotSavedDocument(self, *args): self._trigger_save(args)
    def onSaved(self, *args): self._trigger_save(args)

    def _trigger_save(self, args):
        try:
            # Simple Debounce: Don't record two saves within 1 second
            now = time.time()
            if hasattr(self, "_last_save_time") and (now - self._last_save_time) < 1.0:
                return
            self._last_save_time = now

            doc_name = "UnknownDoc"
            if len(args) > 0:
                if hasattr(args[0], "Name"): doc_name = args[0].Name
                elif isinstance(args[0], str): doc_name = args[0]
            
            FreeCAD.Console.PrintMessage(f"[CollaborativeFC] [COMMIT] Checkpoint created for: {doc_name}\n")
            self.manager.onSaved(doc_name)
        except Exception as e:
            FreeCAD.Console.PrintError(f"[CollaborativeFC] Save Signal Error: {e}\n")

# Global singleton access pinned to FreeCAD namespace to prevent GC
def start_observer(author_id="local_user"):
    # Check if we already have an observer pinned to the root
    if hasattr(FreeCAD, "CollaborativeFC_OBSERVER"):
        obs = getattr(FreeCAD, "CollaborativeFC_OBSERVER")
        if obs:
            obs.manager.set_author(author_id)
            return

    try:
        manager = MutationObserver()
        manager.set_author(author_id)
        proxy = DocumentObserver(manager)
        
        # PIN IT: This is the most important part for FreeCAD 1.0
        FreeCAD.CollaborativeFC_OBSERVER = proxy
        FreeCAD.addDocumentObserver(proxy)
        
        # Resilient Handshake Check (Give sidecar a moment to bind or fail WAMP)
        import time
        handshake = None
        for i in range(10): # Increased to 10 attempts (5 seconds total)
            handshake = manager.send_to_sidecar("ping", {})
            if handshake: break
            time.sleep(0.5)

        if handshake:
            wamp_status = handshake.get('wamp', 'unknown')
            FreeCAD.Console.PrintMessage(f"[CollaborativeFC] Mutation Engine Connected (IPC: {handshake.get('status')}, WAMP: {wamp_status})\n")
        else:
            FreeCAD.Console.PrintWarning("[CollaborativeFC] Mutation Engine Handshake Timeout. It may still be starting up.\n")
    except Exception as e:
        FreeCAD.Console.PrintError(f"[CollaborativeFC] Observer Pinning Failed: {e}\n")

def stop_observer():
    if hasattr(FreeCAD, "CollaborativeFC_OBSERVER"):
        obs = getattr(FreeCAD, "CollaborativeFC_OBSERVER")
        if obs:
            try:
                FreeCAD.removeDocumentObserver(obs)
                FreeCAD.Console.PrintMessage("[CollaborativeFC] Mutation Observer Unpinned.\n")
            except: pass
        delattr(FreeCAD, "CollaborativeFC_OBSERVER")
