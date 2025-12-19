# Implementation Plan: Gap Closure for Epics 1-4

This plan outlines the steps to address the remaining gaps identified in the evaluation of Epics 1-4 for CollaborativeFC.

## Phase 1: Real-time Peer Data (Epic 1 - Story 1.2)
**Goal:** Replace the mocked peer list in the Social Pulse Sidebar with real-time data from the WAMP mesh.

1.  **Backend (Sidecar) Updates (`src/sidecar/main.py`)**:
    *   Implement `wamp.session.on_join` and `wamp.session.on_leave` handlers (or `wamp.subscription.match` logic depends on WAMP router capabilities, but simplified: listen for `ocp.presence` topic).
    *   Since Crossbar.io provides meta-events, subscribe to `wamp.session.on_join` (if allowed) or implement a "Heartbeat" broadcast topic `ocp.presence.heartbeat`.
    *   **Decision:** Use a simple `ocp.presence.heartbeat` topic where every node causes a broadcast on join and periodically.
    *   Maintain a `_peer_registry` dictionary in `CollaborativeSession`.
    *   Add a new IPC command `get_peers` to return this registry to the Frontend.

2.  **Frontend (FreeCAD) Updates**:
    *   Modify `Mod/CollaborativeFC/MutationObserver.py`: Add `get_peers()` method that sends the IPC command.
    *   Modify `Mod/CollaborativeFC/InitGui.py`: Add a `_poll_peers` timer (e.g., every 2s).
    *   Modify `Mod/CollaborativeFC/Sidebar.py`: Replace `send_mock_peers` with `update_peers(peer_data)` called from `InitGui.py`.

## Phase 2: Surgical Suite Handshake (Epic 4 - Stories 4.1, 4.2, 4.3)
**Goal:** Make the "Accept/Reject" buttons functional and visual.

1.  **UI Updates (`Mod/CollaborativeFC/SurgicalOverlay.py`)**:
    *   Add "Timeline Scrubber" (QSlider) - *Visual placeholder active*.
    *   Add "Diff View" Toggle (QCheckBox) - *Visual placeholder active*.
    *   Ensure "Accept" and "Reject" emit distinct signals.

2.  **Logic Updates (`Mod/CollaborativeFC/InitGui.py`)**:
    *   Implement `on_hud_decision(decision)`:
        *   **If Reject**:
            *   Clear the incoming mutation queue for this specific object/prop.
            *   Remove the Ghost (`GhostManager.remove_ghost()`).
            *   Trigger a generic "Conflict Resolved" toast.
        *   **If Accept**:
            *   Read the mutation payload from the queue.
            *   Apply the mutation locally (`obj.Prop = val`).
            *   Trigger `doc.recompute()`.
            *   **Crucial:** Append this accepted state to the Local Ledger (as if it was a local edit) to confirm the new state.
            *   Remove Ghost.
            *   Dismiss HUD.

## Phase 3: Topological Analysis (Epic 3 - Story 3.3)
**Goal:** Detect broken references during recompute.

1.  **Backend Analysis (`src/sidecar/main.py`)**:
    *   Enhance `_replay_on_shadow`:
        *   After `doc.recompute()`, iterate through `obj.InList` (dependents).
        *   Check `dependent_obj.Status`. If it contains `Topological Error` or `Touched` but has `Shape.isNull()`, flag it.
        *   Return a `topological_error` flag in the IPC response or log it to a `ocp.alert.topology` list.

2.  **Frontend Alert**:
    *   If `InitGui.py` receives a mutation with `topo_error=True` (simulated via `_apply_mutations` recompute check), trigger the Surgical HUD automatically.

## Phase 4: Execution Sequence
1.  **Peer Presence**: Wire up the heartbeat and display real peers.
2.  **Surgical Logic**: Implement the Accept/Reject slot in `InitGui.py`.
3.  **Topological Check**: Enhance the Sidecar recompute validation.
