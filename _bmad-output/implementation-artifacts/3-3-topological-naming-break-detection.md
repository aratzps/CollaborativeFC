# Story 3.3: Topological Naming Break Detection

**Status:** In Progress
**Epic:** Epic 3: Headless Recompute & Geometric Parity

## Description
As a developer,
I want the system to detect when a mutation causes a "Topological Naming Break" (i.e., face/edge IDs shift unexpectedly),
So that I can warn the user that dependent operations (like Fillets or Constraints) might break on peer machines.

## Acceptance Criteria
- [ ] **Given** a mutation is applied in the Sidecar
- [ ] **When** the Sidecar recomputes the object
- [ ] **Then** it must check if the number of faces/edges has changed OR if the element naming map has shifted (if accessible).
- [ ] **And** if a potential break is detected, it should flag the mutation as `UNSTABLE_TOPOLOGY`.
- [ ] **And** this flag should be broadcast to peers.

## Implementation Notes
- **FreeCAD Internals:**
    - Use `Shape.getElementMap()` (if available in 1.0) or compare `Shape.Faces` lists.
    - Check if "Face1" in the old shape maps to a geometrically similar face in the new shape.
- **Sidecar Logic:**
    - Store `previous_topology_map` before recompute.
    - Compare with `current_topology_map` after recompute.
    - If `Face1` existed and now `Face1` is missing or has zero area (and `Face2` appeared), simpler heuristic:
        - Just count elements for MVP.
        - If Face Count changes, it's a high risk of TNP break.

## User's Question Check:
The user asked about "Unique IDs for operations". FreeCAD 1.0 has improved TNP handling using `ElementMap`. We should try to leverage `Shape.getElementMap()` to answer their request.

## Risks
- `getElementMap` might not be exposed robustly in the Python API for all object types.
