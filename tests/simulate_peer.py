import asyncio
import time
import sys
from autobahn.asyncio.component import Component, run

# Configuration
ROUTER_URL = "ws://localhost:8080/ws"
REALM = "realm1"

PEER_NAME = "SimulatedPeer"
PEER_COLOR = "#F43F5E" # Rose

# Conflict Mutation: Changes Box Length to 80.0 (Simulates the conflict scenario)
CONFLICT_MUTATION = {
    "author": PEER_NAME,
    "object": "Box",
    "property": "Length",
    "value": 80.0,
    "geometric_hash": "FORCE_DIVERGENCE" # Special flag to trigger divergence check/red-alert
}

# Standard Mutation: Safe Width change
SAFE_MUTATION = {
    "author": PEER_NAME,
    "object": "Box",
    "property": "Width",
    "value": 25.0,
    "geometric_hash": "dummy_hash"
}

comp = Component(transports=ROUTER_URL, realm=REALM)

@comp.on_join
async def joined(session, details):
    print(f"[{PEER_NAME}]: Joined '{details.realm}'")

    # 1. Start Heartbeat Loop
    async def heartbeat_loop():
        while True:
            payload = {
                "name": PEER_NAME,
                "color": PEER_COLOR,
                "status": "Online",
                "timestamp": time.time()
            }
            session.publish("ocp.presence.heartbeat", payload)
            # print(f"[{PEER_NAME}] <3 Pulse sent")
            await asyncio.sleep(2.0)
    
    # Start heartbeat in background
    asyncio.create_task(heartbeat_loop())
    
    # 2. Interactive Loop
    print("\n--- SIMULATION CONTROLS ---")
    print(" [1] Send SAFE Mutation (Width=25.0)")
    print(" [2] Send CONFLICT Mutation (Length=80.0) -> Triggers HUD")
    print(" [3] Send BROKEN Topology (Length=999.0) -> Triggers Alert")
    print(" [q] Quit")
    print("---------------------------")

    # Note: Asyncio input is complex, using a simple polling loop for file/input 
    # isn't great in 'run()'. We'll use a simple timed sequence or just blocking input 
    # if we weren't in an event loop.
    # ALTERNATIVE: We just run a scenario sequence.
    
    # Let's run a "Scenario Mode" for the user to follow:
    print("\n>>> SIMULATION STARTED <<<")
    print("1. Sending Heartbeats... (Check your Sidebar)")
    await asyncio.sleep(5)
    
    print("\n2. Sending SAFE Mutation in 3 seconds...")
    await asyncio.sleep(3)
    session.publish("ocp.update.property", SAFE_MUTATION, options=None)
    print(">>> SAFE Mutation Sent.")
    
    print("\n3. Sending CONFLICT Mutation in 5 seconds (Get ready!)...")
    await asyncio.sleep(5)
    session.publish("ocp.update.property", CONFLICT_MUTATION, options=None)
    print(">>> CONFLICT Mutation Sent.")
    
    print("\nSimulation complete. Keeping session alive for heartbeats...")
    # Keep alive until user kills it
    while True:
        await asyncio.sleep(1)

if __name__ == "__main__":
    print(f"Starting {PEER_NAME}...")
    try:
        run([comp])
    except KeyboardInterrupt:
        pass
