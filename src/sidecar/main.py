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

logging.basicConfig(level=logging.INFO, format='%(asctime)s - [Sidecar] %(message)s')

class CollaborativeSession(ApplicationSession):
    def onJoin(self, details):
        global _wamp_session
        logging.info("Joined WAMP realm '{}'".format(details.realm))
        _wamp_session = self
        
        # Subscribe to remote mutations
        self.subscribe(self.on_remote_mutation, "ocp.update.property")

    def on_remote_mutation(self, payload):
        global _incoming_queue
        # Loopback Protection: Don't process our own broadcast
        # Ideally check session ID, but for now check payload['author'] vs our local author?
        # Actually, the workbench handles author ID. Sidecar doesn't know "who am I" yet.
        # So we just queue everything, and let Workbench discard its own if needed.
        # WAIT: Crossbar reflects publishing to subscriber by default unless exclude_me=True.
        
        logging.info(f"Received Remote Mutation: {payload.get('object')}.{payload.get('property')}")
        _incoming_queue.append(payload)

    def onDisconnect(self):
        global _wamp_session
        logging.info("WAMP Disconnected")
        _wamp_session = None

class WorkbenchIPC(protocol.Protocol):
    """Handles raw TCP JSON messages from FreeCAD."""

    def connectionMade(self):
        self._buffer = b""

    def dataReceived(self, data):
        self._buffer += data
        logging.info(f"IPC Data Received: {len(data)} bytes | Total Buffer: {len(self._buffer)} bytes")
        try:
            # Try to decode the buffer
            msg = json.loads(self._buffer.decode())
            # If successful, we have a complete message (assuming 1 request per conn)
            self._buffer = b"" # Reset
            self.handle_request(msg)
        except json.JSONDecodeError:
            # Incomplete data, wait for more
            pass
        except Exception as e:
            logging.error(f"IPC Error: {e}")

    def handle_request(self, req):
        global _wamp_session, _ledger
        cmd = req.get("command")
        # logging.info(f"Processing Command: {cmd}")
        
        if cmd == "mutation":
            payload = req.get("payload", {})
            try:
                # 1. Write to Local Ledger
                mid = _ledger.append_mutation(
                    payload.get("author"),
                    payload.get("object"),
                    payload.get("property"),
                    payload.get("value")
                )
                logging.info(f"Local Mutation Recorded: {mid}")
                
                # 2. Broadcast via WAMP
                if _wamp_session:
                    from autobahn.twisted.wamp import PublishOptions
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
        runner = ApplicationRunner(url=WAMP_URL, realm=WAMP_REALM)
        # We hook into the connect method to prevent reactor stop on fail?
        # Actually, let's just use the runner normally but knowing it might fail.
        # If it fails, we need to keep reactor running for IPC.
        d = runner.run(CollaborativeSession, start_reactor=False)
        d.addErrback(lambda e: logging.warning(f"WAMP Connection Failed (Offline Mode): {e.value}"))

    # Schedule WAMP start
    reactor.callWhenRunning(start_wamp)

    # 3. Start Reactor (Main Loop)
    print("Entering Main Loop...", flush=True)
    try:
        reactor.run()
    except Exception as e:
        print(f"Reactor Crash: {e}", flush=True)
