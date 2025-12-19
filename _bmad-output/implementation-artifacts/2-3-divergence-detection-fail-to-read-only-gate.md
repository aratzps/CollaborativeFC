# Story 2.3: Divergence Detection & "Fail-to-Read-Only" Gate

**Status:** In Progress
**Epic:** Epic 2: Distributed Mutation Sync & Ledger

## Description
As a team member,
I want the system to alert me if my local model diverges from the swarm truth,
So that I don't continue editing in a state that will cause unresolvable conflicts.

## Acceptance Criteria
- [ ] **Given** a mutation has just been received from a peer and applied locally
- [ ] **When** the local recompute finishes
- [ ] **Then** the Sidecar must compare the local `geometric_hash` with the hash received from the peer (FR5)
- [ ] **And** if the hashes mismatch (Divergence Detected), the workbench must trigger a **Safety Lock**
- [ ] **And** the FreeCAD UI must enter **"Read-Only Mode"** until the user performs a resync
- [ ] **And** the "Social Pulse" sidebar must display a **Divergence Warning** (Safety Orange alert)

## Implementation Notes
- **WAMP Subscription:** The Sidecar needs to listen to `ocp.update.property` (which it already does).
- **Loopback Handling:** We must ensure we don't process *our own* broadcasts as "incoming mutations". We can use the WAMP `exclude_me=True` option or filter by author ID.
- **Incoming Queue:** The Sidecar should store incoming mutations in a queue.
- **Workbench Polling:** The Workbench needs to poll the Sidecar (e.g., every 500ms) for "New Incoming Mutations".
- **Application Logic:** When the Workbench receives an incoming mutation, it must apply it to the FreeCAD document.
- **Hash Verification:** After applying, we generate a hash (placeholder for now, full geometric hash in Epic 3) and compare it.
- **Safety Lock:** Implement `setReadOnly(True)` on the document if mismatch occurs.
