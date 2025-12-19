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
- **Sidecar Client (DONE):**
    - Refactored to use `Twisted` reactor and `autobahn` WAMP client.
    - Implemented robust IPC protocol with logic to handle fragmentation and one-shot requests.
    - Added "Offline Mode" resilience (Sidecar runs IPC even if WAMP connection fails).
- **WAMP Router (TODO):**
    - Need to set up a WAMP router (Crossbar.io or basic Twisted router).
    - Current state: Sidecar searches for `ws://localhost:8080/ws`.
    - Next steps: Install/Run router and verify broadcast.
- **Verification:**
    - [x] Handshake between Workbench and Sidecar (IPC Pong).
    - [x] Sidecar attempts WAMP connection (Log: "WAMP Connection Failed").
    - [ ] Real-time mutation broadcast seen in router logs.
