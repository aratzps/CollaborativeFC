# Story 3.2: Geometric Hash Validation (SHA-256)

**Status:** In Progress
**Epic:** Epic 3: Headless Recompute & Geometric Parity

## Description
As a developer,
I want the system to generate a deterministic "Geometric Checksum" (Hash) of the modified object's shape,
So that I can mathematically verify if my peer sees exactly what I see (Geometric Parity) and detect divergence even if properties match.

## Acceptance Criteria
- [ ] **Given** a FreeCAD Shape in the Sidecar's Shadow Document
- [ ] **When** a mutation is applied and recomputed
- [ ] **Then** the system must calculate a `geometric_hash` based on the topology (Vertices, Edges, Faces).
- [ ] **And** this hash must be stable (deterministic) across identical geometries.
- [ ] **And** this hash must change if the geometry changes (e.g. Volume changes).
- [ ] **And** the Sidecar must compare this calculated hash with the `incoming_hash` from the peer.
- [ ] **And** if they differ, it must log a `DIVERGENCE` warning (which the Workbench already traps).

## Implementation Notes
- **Hashing Strategy:**
    1.  **Composite Signature (Level 1):** `SHA256(Volume + Area + CenterOfMass)`. Fast, good for gross divergence.
    2.  **Topology Walk (Level 2 T-BREP):** Sort vertices, edges, faces by canonical order and hash their properties. Precise, handles "same volume, different shape".
    - *Decision:* Start with **Composite Signature** + **Vertex Count** for MVP speed.
- **Python Implementation:**
    - `hashlib.sha256(f"{obj.Shape.Volume:.6f}|{obj.Shape.Area:.6f}|{len(obj.Shape.Vertexes)}".encode()).hexdigest()`
- **Update Sidecar:**
    - Modify `_replay_on_shadow` to calculate this hash.
    - Check against `payload.get('geometric_hash')`.

## Risks
- Floating point indeterminism (different CPUs might round Volume slightly differently).
    - Mitigation: Round to 6 decimal places before hashing.
