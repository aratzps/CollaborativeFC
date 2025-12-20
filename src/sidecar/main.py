import sys
import os
import json
import logging
from twisted.internet import reactor, protocol, endpoints
from autobahn.twisted.wamp import ApplicationSession, ApplicationRunner
from twisted.internet import task
from ledger import LedgerManager
import time

# Configuration
IPC_PORT = 5555
WAMP_URL = "ws://localhost:8080/ws"
WAMP_REALM = "realm1"
LEDGER_SECRET = "collaborative-fc-synergy-2025"

# Global State
_wamp_session = None
_ledger = LedgerManager(secret_key=LEDGER_SECRET)
_incoming_queue = []
_offline_buffer = [] # Queue for outgoing mutations when offline
_peer_registry = {} # {session_id: {name, color, last_seen, ...}}

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

def calculate_geometric_hash(obj):
    """Generates a deterministic SHA256 hash of the object's geometry."""
    try:
        import hashlib
        if not hasattr(obj, "Shape"):
            return "no_shape"
            
        shape = obj.Shape
        # Composite Signature: Volume | Area | Vertices | Edges | Faces
        # Rounded to 6 decimals to avoid floating point jitter
        sig = f"{shape.Volume:.6f}|{shape.Area:.6f}|{len(shape.Vertexes)}|{len(shape.Edges)}|{len(shape.Faces)}"
        return hashlib.sha256(sig.encode()).hexdigest()
    except Exception as e:
        return f"hash_error_{e}"

def _replay_on_shadow(doc, payload):
    """Applies a mutation to the Shadow Document."""
    if not doc: return

    try:
        obj_name = payload.get("object")
        prop_name = payload.get("property")
        val_str = payload.get("value")
        incoming_hash = payload.get("geometric_hash")
        
        obj = doc.getObject(obj_name)
        if not obj:
            # Auto-create for testing (Simulate 'Creation' event logic)
            if prop_name == "Length": # Hint it's a Pad or Box
                obj = doc.addObject("Part::Box", obj_name)
        
        if obj:
            # Capture Pre-Mutation Topology
            pre_topology = "N/A"
            if hasattr(obj, "Shape") and not obj.Shape.isNull():
                pre_topology = (len(obj.Shape.Faces), len(obj.Shape.Edges))

            val = float(val_str) if str(val_str).replace('.','',1).isdigit() else val_str
            try:
                setattr(obj, prop_name, val)
                doc.recompute()
                
                # Capture Post-Mutation Topology
                post_topology = "N/A"
                if hasattr(obj, "Shape") and not obj.Shape.isNull():
                    post_topology = (len(obj.Shape.Faces), len(obj.Shape.Edges))
                
                # Detect Clean vs Broken Topology
                topo_status = "STABLE"
                is_broken = False
                
                # 1. Check for FreeCAD Error flags
                if hasattr(obj, "State") and "Error" in str(obj.State):
                    topo_status = f"CRITICAL_ERROR ({obj.State})"
                    is_broken = True
                
                # 2. Check for Null Shape (Lost Geometry)
                if hasattr(obj, "Shape") and obj.Shape.isNull():
                    topo_status = "NULL_SHAPE (Lost Geometry)"
                    is_broken = True

                # 3. Check Metric Stability
                if not is_broken and pre_topology != "N/A" and post_topology != "N/A":
                    if pre_topology != post_topology:
                        topo_status = f"UNSTABLE ({pre_topology} -> {post_topology})"
                        # Note: Change in face count isn't always a break, but it IS a topological shift
                        # that warrants a 'Surgical' warning via the glint or hud.
                
                if is_broken:
                     logging.error(f"[TOPO_BREAK] {obj_name} is broken: {topo_status}")
                     # In a real app, we would emit a specific 'topo_break' event here

                # Calculate Local Hash
                local_hash = calculate_geometric_hash(obj)
                
                # Validation
                status = "MATCH"
                if incoming_hash and incoming_hash != "dummy_hash":
                     if incoming_hash != local_hash:
                         status = "DIVERGENCE"
                         logging.warning(f"[DIVERGENCE] Hash Mismatch! Remote: {incoming_hash} vs Local: {local_hash}")
                
                 # Log both Hash Status and Topology Status
                msg = f"[Shadow] SUCCESS: {obj_name}.{prop_name} -> {val} | Hash={local_hash[:8]}... [{status}] | Topo={topo_status}"
                print(msg, flush=True)
                logging.info(msg)
                
            except AttributeError:
                pass # Ignore non-Box props
            except Exception as e:
                logging.error(f"Shadow Replay Error ({prop_name}): {e}")
    except Exception as e:
        logging.error(f"Shadow Logic Crash: {e}")

class CollaborativeSession(ApplicationSession):
    def onJoin(self, details):
        global _wamp_session
        logging.info("Joined WAMP realm '{}'".format(details.realm))
        _wamp_session = self
        
        # Subscribe to remote mutations
        self.subscribe(self.on_remote_mutation, "ocp.update.property")
        self.subscribe(self.on_heartbeat, "ocp.presence.heartbeat")
        
        # Start Heartbeat Loop (every 2 seconds)
        self.hb_loop = task.LoopingCall(self.broadcast_heartbeat)
        self.hb_loop.start(2.0)

        # Flush Offline Buffer
        global _offline_buffer
        if _offline_buffer:
            logging.info(f"WAMP Reconnected - Flushing {len(_offline_buffer)} buffered mutations...")
            from autobahn.wamp.types import PublishOptions
            for payload in _offline_buffer:
                self.publish("ocp.update.property", payload, options=PublishOptions(exclude_me=True))
            _offline_buffer.clear()

    def onLeave(self, details):
        global _wamp_session
        logging.info("Left WAMP session: {}".format(details.reason))
        if _wamp_session == self:
            _wamp_session = None
        
        # Stop Heartbeat
        if hasattr(self, 'hb_loop') and self.hb_loop.running:
            self.hb_loop.stop()

    def onDisconnect(self):
        global _wamp_session
        logging.info("WAMP Transport Disconnected")
        if _wamp_session == self:
            _wamp_session = None
            
        # Stop Heartbeat
        if hasattr(self, 'hb_loop') and self.hb_loop.running:
            self.hb_loop.stop()

    def broadcast_heartbeat(self):
        # We broadcast our minimal status
        try:
            payload = {
                "name": "LocalUser", # In real app, this comes from config
                "color": "#A855F7", 
                "status": "Online",
                "timestamp": time.time()
            }
            self.publish("ocp.presence.heartbeat", payload)
        except Exception:
            # Swallow transport errors to avoid log spam if disconnect happens during loop
            pass

    def on_heartbeat(self, payload, details=None):
        global _peer_registry
        # details.publisher gives the session ID of the sender
        sender_id = details.publisher if details else "unknown"
        
        _peer_registry[sender_id] = {
            "id": sender_id,
            "name": payload.get("name", "Unknown"),
            "color": payload.get("color", "#999999"),
            "status": payload.get("status", "Online"),
            "last_seen": time.time()
        }

    def on_remote_mutation(self, payload):
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
                    logging.warning(f"WAMP Offline - Buffered Mutation: {mid}")
                    global _offline_buffer
                    _offline_buffer.append(payload)

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

        elif cmd == "get_peers":
            # Filter stale peers (> 5 seconds ago)
            now = time.time()
            active_peers = []
            for pid, pdata in list(_peer_registry.items()):
                if now - pdata.get("last_seen", 0) < 5.0:
                    active_peers.append(pdata)
                else:
                    # Optional: Prune
                    pass
            self.transport.write(json.dumps(active_peers).encode())

        elif cmd == "get_status":
            wamp_status = "connected" if _wamp_session else "offline"
            status = {
                "wamp": wamp_status,
                "buffer_size": len(_offline_buffer)
            }
            self.transport.write(json.dumps(status).encode())

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
        def on_disconnect(reason):
            logging.warning(f"WAMP Disconnected: {reason}. Retrying in 5s...")
            reactor.callLater(5.0, start_wamp)

        logging.info(f"Connecting to WAMP router at {WAMP_URL}...")
        runner = ApplicationRunner(url=WAMP_URL, realm=WAMP_REALM)
        d = runner.run(CollaborativeSession, start_reactor=False)
        
        # If connection fails immediately, errback is called.
        d.addErrback(lambda e: on_disconnect(e.value))
        
        # If session connects then disconnects later, callback is called.
        d.addCallback(lambda _: on_disconnect("Session Logic Finished"))

    # Schedule WAMP start
    reactor.callWhenRunning(start_wamp)

    # 3. Start Reactor (Main Loop)
    print("Entering Main Loop...", flush=True)
    try:
        reactor.run()
    except Exception as e:
        print(f"Reactor Crash: {e}", flush=True)
