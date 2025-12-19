# Story 3.1: Headless Recompute Service (Sidecar)

**Status:** In Progress
**Epic:** Epic 3: Headless Recompute & Geometric Parity

## Description
As a developer,
I want the Sidecar to have its own Headless FreeCAD instance or a reliable way to compute geometry without relying on the GUI thread,
So that hash generation and validation can happen asynchronously without freezing the UI.

## Acceptance Criteria
- [ ] **Given** the Sidecar is running
- [ ] **When** it receives a mutation involving geometric changes
- [ ] **Then** it must be able to load the relevant document (or a shadow copy)
- [ ] **And** perform a `doc.recompute()`
- [ ] **And** extract the `Shape` of the modified object
- [ ] **And** this must happen independently of the main FreeCAD GUI process (or effectively so).
*Note: Due to FreeCAD's single-process nature and GIL, a true parallel process is hard. We might spawn a "Shadow Worker" process or use the existing Sidecar process if it has access to FreeCAD libraries.*

## Implementation Notes
- **Challenge:** The Sidecar currently runs in a separate process (`python.exe` or `FreeCAD/bin/python.exe`). It does NOT implicitly have the open document loaded.
- **Approach:**
    1.  **Shared Memory / File Sync:** The Sidecar needs access to the `.FCStd` file.
    2.  **Shadow Copy:** When a session starts, we might save a shadow copy to `%TEMP%`.
    3.  **Instruction Replay:** The Sidecar replays the ledger on its own empty document to reach the same state.
- **Decision:** For Story 3.1, we will implement **"Instruction Replay"** on a headless document in the Sidecar process.
    - Sidecar imports `FreeCAD`.
    - Sidecar creates a new `App.Document`.
    - Sidecar applies all mutations from the ledger to this hidden document.
    - Result: Sidecar has a "Digital Twin" of the user's geometry.
- **Dependency:** Ensure `src/sidecar/main.py` can `import FreeCAD`. This depends on where `python.exe` is running from. We already fixed this in Story 1.1 by using the bundled python.

## Risks
- FreeCAD initialization time in Sidecar.
- TopoNaming issues if replay order varies (Ledger guarantees order).
- Performance of recomputing complex models in Python.
