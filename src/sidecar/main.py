import sys
import os
import json
import logging
from twisted.internet import reactor, protocol, endpoints
from autobahn.twisted.wamp import ApplicationSession, ApplicationRunner
from ledger import LedgerManager

# Configuration
IPC_PORT = 5555
WAMP_URL = "ws://localhost:8080/ws"
WAMP_REALM = "realm1"
LEDGER_SECRET = "collaborative-fc-synergy-2025"

# Global State
_wamp_session = None
_ledger = LedgerManager(secret_key=LEDGER_SECRET)
_incoming_queue = []

# Initialize Headless FreeCAD Engine (Story 3.1)
try:
    # Ensure bin path is in sys.path (critical for finding mod libraries)
    fc_bin = os.path.dirname(sys.executable)
    if fc_bin not in sys.path: sys.path.append(fc_bin)
    
    import FreeCAD
    _shadow_doc = FreeCAD.newDocument("CollaborativeShadow")
    logging.info("Headless FreeCAD Engine Initialized. Shadow Document Ready.")
except Exception as e:
    logging.error(f"Failed to init FreeCAD Headless: {e}")
    _shadow_doc = None

logging.basicConfig(level=logging.INFO, format='%(asctime)s - [Sidecar] %(message)s')

def _replay_on_shadow(doc, payload):
    """Applies a mutation to the Shadow Document."""
    if not doc: return

    try:
        obj_name = payload.get("object")
        prop_name = payload.get("property")
        val_str = payload.get("value")
        
        obj = doc.getObject(obj_name)
        if not obj:
            # Auto-create for testing (Simulate 'Creation' event logic)
            if prop_name == "Length": # Hint it's a Pad or Box
                obj = doc.addObject("Part::Box", obj_name)
        
        if obj:
            val = float(val_str) if str(val_str).replace('.','',1).isdigit() else val_str
            try:
                setattr(obj, prop_name, val)
                doc.recompute()
                
                # Calculate simple geometry metric
                metric = "N/A"
                if hasattr(obj, "Shape"):
                    metric = f"Vol={obj.Shape.Volume:.2f}"
                
                print(f"[Shadow] SUCCESS: {obj_name}.{prop_name} -> {val} | {metric}", flush=True)
                logging.info(f"[Shadow] SUCCESS: {obj_name}.{prop_name} -> {val} | {metric}")
            except AttributeError:
                pass # Ignore non-Box props
            except Exception as e:
                logging.error(f"Shadow Replay Error ({prop_name}): {e}")
    except Exception as e:
        logging.error(f"Shadow Logic Crash: {e}")

class CollaborativeSession(ApplicationSession):
    def onJoin(self, details):
        global _wamp_session
        print(f"DEBUG: onJoin called for realm {details.realm}", flush=True)
        logging.info("Joined WAMP realm '{}'".format(details.realm))
        _wamp_session = self
        
        # Subscribe to remote mutations
        self.subscribe(self.on_remote_mutation, "ocp.update.property")

    def on_remote_mutation(self, payload):
        global _incoming_queue, _shadow_doc
        print(f"DEBUG: on_remote_mutation called for {payload}", flush=True)
        global _incoming_queue, _shadow_doc
        logging.info(f"Received Remote Mutation: {payload.get('object')}.{payload.get('property')}")
        
        # Replay on Shadow Doc
        _replay_on_shadow(_shadow_doc, payload)
        
        _incoming_queue.append(payload)

class WorkbenchIPC(protocol.Protocol):
    def __init__(self):
        self._buffer = b""

    def connectionMade(self):
        # logging.info("IPC Client Connected")
        pass

    def dataReceived(self, data):
        self._buffer += data
        try:
            msg = json.loads(self._buffer.decode())
            self._buffer = b"" # Reset buffer on success
            self.handle_request(msg)
        except json.JSONDecodeError:
            pass # Incomplete data, wait for more
        except Exception as e:
            logging.error(f"IPC Error: {e}")

    def handle_request(self, req):
        global _shadow_doc
        cmd = req.get("command")
        payload = req.get("payload")
        
        if cmd == "mutation":
            try:
                # 1. Write to Local Ledger
                mid = _ledger.append_mutation(
                    payload.get("author"),
                    payload.get("object"),
                    payload.get("property"),
                    payload.get("value")
                )
                logging.info(f"Local Mutation Recorded: {mid}")
                
                # 1.5 Replay on Shadow Document (Headless Recompute)
                _replay_on_shadow(_shadow_doc, payload)

                # 2. Broadcast via WAMP
                if _wamp_session:
                    # Correct import for PublishOptions
                    from autobahn.wamp.types import PublishOptions
                    _wamp_session.publish("ocp.update.property", payload, options=PublishOptions(exclude_me=True))
                    logging.info(f"Broadcasted Mutation: {mid}")
                else:
                    logging.warning("WAMP Offline - Sync Queued (Not implemented)")

                self.transport.write(json.dumps({"status": "ok", "id": mid}).encode())
            except Exception as e:
                logging.error(f"Mutation Failed: {e}")
                self.transport.write(json.dumps({"status": "error", "message": str(e)}).encode())

        elif cmd == "read_ledger":
            data = _ledger.read_all_mutations()
            self.transport.write(json.dumps(data).encode())
            
        elif cmd == "poll_queue":
            # Return and clear incoming queue
            global _incoming_queue
            snapshot = list(_incoming_queue)
            _incoming_queue.clear()
            self.transport.write(json.dumps(snapshot).encode())

        if cmd == "ping":
            wamp_status = "connected" if _wamp_session else "offline"
            resp = json.dumps({"status": "pong", "wamp": wamp_status}).encode()
            self.transport.write(resp)
            
        # Always close after request processed (One-Shot Protocol)
        self.transport.loseConnection()

class IPCFactory(protocol.Factory):
    def buildProtocol(self, addr):
        logging.info(f"IPC Client Connected: {addr}")
        return WorkbenchIPC()

if __name__ == "__main__":
    print("Starting OCP Sidecar (Twisted/Autobahn)...", flush=True)
    
    # 1. Start IPC Server
    try:
        endpoints.serverFromString(reactor, f"tcp:{IPC_PORT}").listen(IPCFactory())
        print(f"IPC Listening on port {IPC_PORT}", flush=True)
    except Exception as e:
        print(f"Failed to bind IPC: {e}", flush=True)
        sys.exit(1)

    # 2. Start WAMP Client (Robust)
    # The default ApplicationRunner stops the reactor if WAMP fails.
    # We must start WAMP *inside* the reactor or independently to avoid killing IPC.
    print("Initializing WAMP...", flush=True)

    from twisted.internet.error import ConnectionRefusedError
    
    def start_wamp():
        print("DEBUG: start_wamp called", flush=True)
        runner = ApplicationRunner(url=WAMP_URL, realm=WAMP_REALM)
        d = runner.run(CollaborativeSession, start_reactor=False)
        d.addCallback(lambda _: print("DEBUG: WAMP session finished", flush=True))
        d.addErrback(lambda e: print(f"DEBUG: WAMP Error: {e}", flush=True))

    # Schedule WAMP start
    reactor.callWhenRunning(start_wamp)

    # 3. Start Reactor (Main Loop)
    print("Entering Main Loop...", flush=True)
    try:
        reactor.run()
    except Exception as e:
        print(f"Reactor Crash: {e}", flush=True)
