# Story 4.2: 3D Ghosting ("The Phantom Geometry")

**Status:** In Progress
**Epic:** Epic 4: The Surgical Suite

## Description
When a remote mutation causes a conflict (or pending approval), the system must visualize the "Proposed State" as a 3D Ghost overlaid on the current state.

## Acceptance Criteria
- [ ] **Given** a conflict is detected on "Part::Box"
- [ ] **When** the Conflict HUD appears
- [ ] **Then** a "Ghost" object (clone) must be created in the 3D scene.
- [ ] **And** this Ghost must have the remote property values applied (e.g. Length=100).
- [ ] **And** the Ghost must be semi-transparent (Transparency >= 60%) and colored Distinctly (e.g. Purple).
- [ ] **And** clicking "Reject" must delete the Ghost.
- [ ] **And** clicking "Accept" must delete the Ghost and apply values to the Real Object.

## Technical Approach
1.  **GhostManager.py**:
    -   `create_ghost(target_obj, prop, value)`
    -   `remove_ghost()`
2.  **Implementation**:
    -   `ghost = doc.copyObject(target_obj)`
    -   `ghost.Label = f"__Ghost__{target_obj.Label}"`
    -   `setattr(ghost, prop, value)`
    -   `ghost.ViewObject.ShapeColor = (0.5, 0.0, 0.5)` (Purple)
    -   `ghost.ViewObject.Transparency = 70`
3.  **Integration**:
    -   Call `GhostManager.create_ghost` when HUD shows.
    -   Call `GhostManager.remove_ghost` when HUD hides.

## Risks
- **Expensive Computations**: If the object is a complex Body, cloning and recomputing might freeze UI.
    -   *Mitigation:* For MVP, assumed primitives/simple shapes. Async recompute not possible in GUI thread easily.
- **Tree Pollution**: The Ghost appears in the Model Tree.
    -   *Mitigation:* Can we set `ghost.InList = False`? (FreeCAD API research needed).
