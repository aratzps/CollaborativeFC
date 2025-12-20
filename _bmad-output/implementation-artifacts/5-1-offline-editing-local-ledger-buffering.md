# Story 5.1: Offline Editing & Local Ledger Buffering

**Status**: Implemented
**Date**: 2025-12-19

## Implementation Details

### Sidecar (`src/sidecar/main.py`)
- **Offline Buffer**: Added `_offline_buffer` list to store mutation payloads when WAMP is disconnected.
- **Buffering Logic**: Inside the `mutation` command handler, checks `_wamp_session`. If None, buffers the payload.
- **Flush on Reconnect**: In `onJoin`, iterates `_offline_buffer` and publishes all pending mutations to `ocp.update.property`.
- **Status Reporting**: Added `get_status` IPC command returning:
  ```json
  {
    "wamp": "connected" | "offline",
    "buffer_size": int
  }
  ```

### Frontend (`Mod/CollaborativeFC/InitGui.py`)
- **Polling**: Updated `_poll_peers` to call `obs.manager.get_status()`.
- **UI Feedback**: Updates the FreeCAD Status Bar with:
  - `"Offline Synergy - Buffering Mutations (N)"`
  - `"Synergy Online - Syncing Buffer (N)..."`

### Mutation Observer
- Added `get_status()` pass-through method.

## Verification
- **Scenario 1 (Offline)**: Disconnect WAMP. Edit properties. Status bar shows buffering count increasing. Ledger records mutations.
- **Scenario 2 (Reconnect)**: Restore WAMP. Sidecar logs "Flushing X buffered mutations". Peers receive updates.

## Troubleshooting & Fixes (2025-12-19)
- **Recursive Recompute**: Fixed a crash where applying a batch of buffered mutations (200+) triggered FreeCAD's recursion protection. Solution: Removed explicit `doc.recompute()` inside the application loop.
- **Echo Loop**: Fixed an issue where flushed buffered mutations were echoed back to the sender by the WAMP router, causing an infinite loop and UI lag. Solution: Robust `author` filtering in `InitGui.py` `_apply_mutations` to ignore locally-authored changes.
- **Sidecar Stability**: Fixed a log-spam issue (Traceback hell) by properly stopping the `heartbeat_loop` when the WAMP transport is lost.
