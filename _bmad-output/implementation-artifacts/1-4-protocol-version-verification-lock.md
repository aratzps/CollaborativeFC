# Story 1.4: Protocol Version Verification & Lock

Status: ready-for-dev

## Story

As a team lead,
I want the workbench to verify that all peers are using the same protocol version before allowing edits,
So that we prevent geometric corruption caused by mismatched OCCT or recompute logic.

## Acceptance Criteria

- [x] **Handshake Verification**: Perform a handshake to verify the **CollaborativeFC Protocol Version** (e.g., `1.0.0`) and **FreeCAD/OCCT Build ID**.
- [x] **Mismatch Lockdown**: If a mismatch is detected, the workbench must display a **Critical Error** overlay.
- [x] **Write Locking**: All write-access (editing) to the document must be **locked** until the user updates to the matching version (FR6).
- [x] **Sidebar Status**: The "Social Pulse" sidebar must show a "Version Mismatch" status on the incompatible peer(s).

## Completion Notes (Phase 1)
- **Protocol Management**: Created `Constants.py` to centralize protocol versioning and FreeCAD build ID discovery.
- **Fail-to-Read-Only**: Implemented a global `LockManager` singleton that manages the "Session Lock" state and blocks workbench commands.
- **Visual Safety**: Created a custom `VersionMismatchOverlay` (Qt Dialog) that locks interaction when a version conflict occurs.
- **Sidebar Integration**: The WebView2 sidebar now asynchronously validates peer versions against the local node using the Python bridge.
- **Resilience**: Switched to absolute imports to handle FreeCAD's dynamic module loading environment.

## Resources & Files
- `Mod/CollaborativeFC/Constants.py`
- `Mod/CollaborativeFC/LockManager.py`
- `Mod/CollaborativeFC/Sidebar.py` (updated with handshake)
- `Mod/CollaborativeFC/Resources/sidebar/logic.js` (updated with version check)
- `Mod/CollaborativeFC/Resources/sidebar/styles.css` (new error styles)

## Dev Notes

- **Protocol Version**: Start with `1.0.0`.
- **Build ID**: In FreeCAD Python, use `FreeCAD.Version()`.
- **Locking Mechanism**: We can use a global flag `CollaborativeFC.version_lock`. If `True`, we can intercept property changes or disable the workbench tools.

## References

- [Source: _bmad-output/epics.md#Story 1.4: Protocol Version Verification & Lock]
- [FR6: The system can force a protocol version match across all connected nodes before allowing edits.]
