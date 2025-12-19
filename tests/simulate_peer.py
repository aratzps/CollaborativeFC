import asyncio
from autobahn.asyncio.component import Component, run

# Configuration
ROUTER_URL = "ws://localhost:8080/ws"
REALM = "realm1"

# The Fake Mutation
FAKE_MUTATION = {
    "author": "GhostUser",
    "object": "Pad",   # Make sure you have a 'Pad' object in FreeCAD!
    "property": "Length",
    "value": 50.0,     # Changing value to ensure we see visual update too
    "geometric_hash": "FORCE_DIVERGENCE"
}

comp = Component(transports=ROUTER_URL, realm=REALM)

@comp.on_join
async def joined(session, details):
    print(f"ghost: Joined realm '{details.realm}'")
    
    # Broadcast the mutation
    print(f"ghost: Broadcasting mutation: {FAKE_MUTATION}")
    session.publish("ocp.update.property", FAKE_MUTATION, options=None)
    
    print("ghost: Mutation sent. Leaving...")
    await session.leave()

if __name__ == "__main__":
    print("Starting Ghost Peer...")
    run([comp])
