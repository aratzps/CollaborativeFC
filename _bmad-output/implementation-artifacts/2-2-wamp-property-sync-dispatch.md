# Story 2.2: WAMP Property Sync & Dispatch

**Status:** In Progress
**Epic:** Epic 2: Distributed Mutation Sync & Ledger

## Description
As a collaborator,
I want my parametric property changes to be broadcast to my peers in real-time,
So that we can work concurrently on the same assembly with minimal latency.

## Acceptance Criteria
- [ ] **Given** I am in a collaborative session with one or more peers
- [ ] **When** I change a property (e.g., `Length`, `Radius`) of a FreeCAD feature
- [ ] **Then** the workbench must dispatch a mutation signal to the local OCP Sidecar
- [ ] **And** the Sidecar must broadcast this mutation over **WAMP** using the `ocp.update.property` topic
- [ ] **And** the mutation signal must reach peers in **< 200ms** (NFR1)
- [ ] **And** the Sidecar must include the `geometric_hash` in the payload for immediate verification (FR4)

## Implementation Notes
- Use `autobahn` or similar WAMP client library for Python.
- Connect to a public or local WAMP router (configurable, default: `ws://localhost:8080/ws`, Realm: `realm1`).
- The Sidecar already receives mutations via IPC.
- We need to add the WAMP Component lifecycle to `sidecar/main.py`.
- We need to implement `geometric_hash` generation (using SHA-256 of the value for now, or true geometry if possible, but the story mentions it specifically). Note: Story 3.2 covers full Geometric Hash Validation. For 2.2, we might just include a placeholder or basic hash.
