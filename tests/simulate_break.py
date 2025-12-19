import asyncio
from autobahn.asyncio.component import Component, run

# Configuration
ROUTER_URL = "ws://localhost:8080/ws"
REALM = "realm1"

# The Break Mutation
# Setting Length to 0 usually degenerates the shape
FAKE_MUTATION = {
    "author": "GhostUser",
    "object": "Box",   
    "property": "Length",
    "value": 0.0,    
    "geometric_hash": "dummy_hash" # We expect mismatch, but mainly checking TOPOLOGY log
}

comp = Component(transports=ROUTER_URL, realm=REALM)

@comp.on_join
async def joined(session, details):
    print(f"ghost: Joined realm '{details.realm}'")
    print(f"ghost: Broadcasting Break Mutation: {FAKE_MUTATION}")
    session.publish("ocp.update.property", FAKE_MUTATION, options=None)
    print("ghost: Mutation sent. Leaving...")
    await session.leave()

if __name__ == "__main__":
    print("Starting Ghost Breaker...")
    run([comp])
