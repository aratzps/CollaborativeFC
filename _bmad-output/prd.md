---
stepsCompleted: [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11]
inputDocuments:
  - '_bmad-output/analysis/product-brief-CollaborativeFC-2025-12-18.md'
  - '_bmad-output/analysis/brainstorming-session-2025-12-18.md'
  - '_bmad-output/master-index.md'
  - '_bmad-output/api-contracts-root.md'
  - '_bmad-output/data-models-root.md'
  - '_bmad-output/dev-ops-info-root.md'
  - '_bmad-output/source-tree-analysis.md'
  - '_bmad-output/ui-components-root.md'
  - '_bmad-output/project-scan-report.json'
documentCounts:
  briefs: 1
  research: 0
  brainstorming: 1
  projectDocs: 7
workflowType: 'prd'
lastStep: 11
project_name: 'CollaborativeFC'
user_name: 'Aratz'
date: '2025-12-18'
---

# Product Requirements Document - CollaborativeFC

**Author:** Aratz
**Date:** 2025-12-18

---

## Executive Summary

CollaborativeFC is a revolutionary open-source framework for FreeCAD that provides real-time multi-user synergy and professional version control features currently exclusive to high-end cloud-native platforms like Onshape. By implementing a Distributed Parametric Protocol and a "Social Merge" workflow, it enables engineering teams to work concurrently on complex models without "Merge Hell," while maintaining full sovereignty over their data through a P2P architecture.

### What Makes This Special

What truly sets CollaborativeFC apart is the move from "file-sync" to a **Distributed Parametric Protocol**. Instead of merging binary blobs or fixed snapshots, it facilitates a **Social Recompute** where every feature addition and variable change is owner-attributed and tracked. The **"Surgical Suite"** (Social Conflict Resolution) transforms the traditionally painful merge process into a productive interaction: it automatically invites relevant authors into a live, interactive 3D session to resolve topological or logical conflicts, turning "Merge Errors" into "Collaborative Design Reviews."

## Project Classification

**Technical Type:** desktop_app
**Domain:** scientific / CAD Engineering
**Complexity:** High
**Project Context:** Brownfield - extending existing system

CollaborativeFC integrates specifically with FreeCAD's parametric engine and the Open Collaboration Platform (OCP). The high complexity arises from the requirement to manage distributed state synchronization, topological recomputation, and real-time conflict negotiation across P2P nodes while ensuring 100% geometric integrity.

---

## Success Criteria

### User Success
- **Merge Confidence**: 90% of multi-branch merges involving >2 authors are resolved and recomputed in **under 15 minutes**.
- **Audit Clarity**: Users achieve 100% transparency in the "Surgical Suite"—every conflicting property is linked to a clear Author Alias and Timestamp.
- **Downtime Independence**: Zero productivity loss due to central server outages (measured by OCP P2P uptime in distributed teams).

### Business Success
- **Adoption Core**: Successfully migrate 3 active Open Source hardware projects from file-based PDM to CollaborativeFC for their main integration branch.
- **ROI**: Achieve a measurable **50% reduction in "Integration Day" overhead** (manual fixing time) for pilot hardware startups.

### Technical Success
- **Rebase Integrity**: 100% geometric parity between a "Sequential Edit" and a "Linear Rebase" of the same mutation set.
- **Sync Performance**: OCP node property synchronization remains under 200ms latency for assemblies with <500 tracked features.
- **Drift Tolerance**: The "Mutation Volume" lease accurately predicts rebase feasibility with >95% accuracy.

### Measurable Outcomes
- Average time spent in the "Surgical Suite" per conflict tracked via telemetry.
- Mutation density threshold before "Orange Alert" triggers.
- Successful P2P sync rates across varied network topologies (LAN vs Global).

## Product Scope

### MVP - Minimum Viable Product
- **DML Identity Extension**: Authorship and timestamp tracking for all FreeCAD properties.
- **Headless Rebase Validation**: Background re-computation engine to verify mutation sequences.
- **"Social Merge" Interaction**: UI to flag property overlaps and identify/invite authors for resolution.
- **Mutation Lease Monitor**: Basic volume counter and warning system for offline drift.
- **Basic 3D Ghosting**: Spatial visualization of "Current" vs "Incoming" geometries.

### Growth Features (Post-MVP)
- **Interactive Dependency Graphs**: Logic-layer visualization of assembly links.
- **Collaborative Sketcher**: Live multi-user drawing and constraint manipulation.

### Vision (Future)
- **Autonomous Parametric Healing**: AI-assisted suggestion and auto-fixing of topological conflicts based on design intent.
- **Global Decentralized CAD Registry**: A peer-to-peer marketplace for parametric sub-assemblies.

---

## User Journeys

### Journey 1: Sarah and the "Midnight Integration"
Sarah is working late on the final assembly of a drone chassis. Her lead designer in another time zone has just pushed a branch with a modified motor mount. Sarah tries to merge it, but **CollaborativeFC** flags a **Topological Conflict**: both designers modified the same base flange, but in slightly different geometric directions.

Instead of Sarah having to call her designer or spend 2 hours manually rebuilding the mount, she clicks **"Open Surgical Suite."** The system identifies the lead designer (Author: `Mark_LeadDSGN`) and Sarah sees a **3D Ghost Overlay** of both mount versions. She invites Mark into the session; he's online, and they spend 10 minutes looking at the **Interactive Dependency Graph** together. They see that Mark's change was more efficient, Sarah accepts his branch's properties for the flange, and the assembly recomputes flawlessly. Sarah goes to bed on time, confident the design is integral.

### Journey 2: Alex and the "Trusted Community PR"
Alex maintains a global Open Source EV project. A new contributor, `VoltDev_99`, submits a major modification to the battery cooling block—a complex part with 60+ features. Normally, Alex would spend an hour just downloading and recomputing this locally to check for "phantom" topological breaks.

Instead, Alex opens the **CollaborativeFC Diff View**. He filters the features by `Author: VoltDev_99` and instantly see high-res **Ghost Overlays** of the cooling fin changes. The **Headless Rebase Engine** has already flagged the PR as "Compatible with Main." Alex uses a **Collaborative Sketcher** note to ask `VoltDev_99` why a specific constraint was deleted. They resolve it in comments synced to the property, and Alex merges the work in 5 minutes. Alex feels like he can scale the project without becoming a bottleneck.

### Journey 3: The "Drift Lease" Warning (Edge Case)
An engineer on Sarah's team, `Leo`, is traveling and working offline on the drone's landing gear. He's making radical changes, unaware that the team has pivoted on the main mounting holes. As Leo works, his **Mutation Lease Monitor** in the FreeCAD sidebar slowly fills up.

Suddenly, the icon turns **Orange**. It warns him: *"Mutation density exceeds stability threshold for automatic rebase. Sync recommended to prevent manual merge surgery."* Leo realizes he's drifted too far. He finds a Wi-Fi hotspot, syncs his OCP node, and the system guides him through a minor "pre-merge" rebase before he creates any further unresolvable conflicts. No work is lost, and no integration hell is created.

### Journey Requirements Summary
- **Surgical Suite UI**: Real-time multi-user session management with 3D ghosting and dependency visualization.
- **OCP Integration**: Reliable property-level authorship and timestamp tracking synced across P2P nodes.
- **Headless Rebase API**: Background validation of mutation sequences for PR compatibility.
- **Drift Intelligence**: A monitor that calculates mutation risk based on feature dependency depth and offline volume.

---

## Domain-Specific Requirements

### Scientific/CAD Compliance & Integrity
CollabFC operates in the high-complexity engineering domain where mathematical reproducibility and geometric accuracy are non-negotiable.

#### Technical Integrity Policies
- **Strict Version Enforcement**: The protocol enforces the "Same-Version-Principle." OCP nodes lock write-access if a mismatch in FreeCAD or OCCT (OpenCASCADE) versions is detected, forcing a **Migration Sync** to prevent floating-point drift.
- **Topological Integrity**: leverage FreeCAD's unique identifiers during **Headless Rebase Validation**. System detects "Topological Naming" breaks (edge/face re-indexing) and flags them as blocking conflicts.

#### Validation Tiers (User-Selectable)
- **Tier 1: Basic Regeneration (Mandatory)**: Feature Tree recomputes without red-state errors.
- **Tier 2: Geometric Sanity**: Automatic `Part.check()` pass for manifold integrity and self-intersections.
- **Tier 3: Engineering Validation**: Comparison of Mass Properties (Volume, Mass, COM) to detect unintended design drift.

### Implementation Considerations
- **Version Compatibility Matrix**: Metadata mapping of PRD versions to specific FreeCAD/App-Image builds.
- **Conflict Granularity**: ID-link tracking to point users to exact broken property anchors during "Surgery."

---

## Innovation & Novel Patterns

### Detected Innovation Areas
- **Distributed Parametric Protocol (DPP)**: Shifting the industry paradigm from "Object Snapshots" to "Immutable Mutation Sequences." This allows for non-destructive, multi-user atomic edits on the same geometry.
- **The Surgical Suite (Social Merge)**: A novel UX pattern that treats a merge conflict as a **Live Multi-User Session**, automatically inviting relevant authors to resolve topological or logical overlaps in real-time.
- **Mutation Drift Leases**: A proactive P2P "Safety Valve" that predicts rebase feasibility based on local mutation volume and complexity before the user attempts a merge.

### Validation Approach
- **Headless Truth-Testing**: Cross-node validation where a secondary node (Shadow Peer) dry-runs the rebase sequence to confirm bit-perfect geometric parity before committing to the main branch.
- **Identity-Backed Auditing**: Every feature in the tree is permanently linked to an OCP NodeID, creating a living "Social Graph" of the design's evolution.

### Risk Mitigation
- **Fallback: The "Emergency Snapshot"**: If a rebase exceeds the complexity threshold or unresolvable topological errors occur, the system provides a one-click "Export to Static Branch" snapshot (Dead-Solid) to prevent total data loss.
- **Drift Lockdown**: If the Mutation Lease is ignored and drift exceeds 200%, the local node enters "Read Only Integration Mode"—forcing a merge/sync before further editing.

---

## Desktop App (Add-on) Specific Requirements

### Project-Type Overview
CollaborativeFC is a Windows-native FreeCAD Add-on that integrates a local P2P node into the CAD environment. It prioritizes protocol synchronicity over traditional "loose" file-syncing, ensuring all engineering peers are operating on the exact same logic engine.

### Platform & Update Strategy
- **Windows-Only MVP**: The initial release targets Windows to leverage consistent networking APIs and ensure stability with FreeCAD's Windows builds.
- **Forced Protocol Updates**: To prevent "Logic Drift," the add-on implements a **Strict Version Lock**. Peer-mismatched protocol versions lock writing and prompt for immediate update.

### System Integration (Architectural Specs)
- **OCP Sidecar Service**: Networking and Headless Recomputation run in a dedicated background process to prevent FreeCAD UI freezing.
- **Native Notifications**: Real-time "Social Merge" invitations and "Mutation Lease" alerts use the Windows Action Center.
- **AppData Persistence**: Local mutation ledgers and P2P credentials stored in `%AppData%/CollaborativeFC`.

### Offline Capabilities
- **Configurable Mutation Threshold**: Users can set a **Drift Limit** (e.g., max feature count or % volume change).
- **Local Lockout**: Reaching threshold while offline enters a protected "Read-Only" state until next sync.

---

## Project Scoping & Phased Development

### MVP Strategy & Philosophy
- **MVP Approach**: **Experience MVP (Synergy-First)**. We will deliver a highly polished "Surgical Suite" and real-time coordination experience. The goal is to prove that distributed teams can resolve complex parametric conflicts faster than via phone calls or manual rebuilds.
- **Resource Requirements**: A lean team of 3: One Backend Protocol Engineer (OCP/P2P), one CAD Integration Expert (FreeCAD/OpenCASCADE), and one UX/Frontend Dev (Surgical Suite UI).

### MVP Feature Set (Phase 1)
- **Core User Journeys Supported**:
    - Sarah's "Midnight Integration" (Live conflict resolution)
    - Leo's "Drift Lease" (Proactive sync alerts)
- **Must-Have Capabilities**:
    - Real-time property-level sync using OCP Sidecar.
    - "Surgical Suite" overlay with basic 3D Ghosting.
    - Forced protocol versioning lock.
    - Configurable mutation lease monitor.
    - Headless recompute validation engine.

### Post-MVP Features
- **Phase 2 (Growth)**: 
    - **Advanced Peer Review**: Integrating Alex's "Trusted Community PR" workflow with recompute validation status.
    - **Interactive Dependency Graphs** for easier conflict visualization.
- **Phase 3 (Expansion)**: 
    - **Collaborative Sketcher** (Live multi-user constraints).
    - **Autonomous Parametric Healing** (AI-assisted conflict resolution).

### Risk Mitigation Strategy
- **Technical Risks**: FreeCAD's recompute engine freezing during sync to be mitigated by the **Sidecar Service** architecture.
- **Market Risks**: User distrust in P2P "Sovereignty" to be mitigated by open-source protocol transparency and local-first data caching.
- **Resource Risks**: If a full team is unavailable, we prioritize the **Headless Rebase Validation** and a **Minimal Text-Based Conflict Resolver** as the absolute core.

---

## Functional Requirements

### Identity & Authorship Tracking
- **FR1**: The system can uniquely identify every OCP Node in a collaborative session.
- **FR2**: The system can attribute every property change in a FreeCAD document to a specific Author ID and Timestamp.
- **FR3**: Users can view the authorship history of any parametric feature in the document tree.

### Distributed Synchronization (The OCP Sidecar)
- **FR4**: The system can synchronize property-level mutations across P2P nodes in real-time.
- **FR5**: The system can detect when a local mutation sequence diverges from the network's "Main" branch.
- **FR6**: The system can force a protocol version match across all connected nodes before allowing edits.
- **FR7**: The system can store the local mutation ledger in a dedicated persistent cache (`%AppData%`).

### Headless Recompute & Validation
- **FR8**: The system can execute a FreeCAD recomputation in a background "headless" process.
- **FR9**: The system can validate a mutation sequence for "Sequential Parity" (proving rebase = edit).
- **FR10**: Users can select between multiple validation tiers (Basic Regeneration, Geometric Sanity, or Mass Property check).
- **FR11**: The system can detect "Topological Naming" breaks where feature references are lost during rebase.

### The Surgical Suite (Social Conflict Resolution)
- **FR12**: The system can identify and flag overlapping property edits between authors.
- **FR13**: Users can initiate a "Live Surgery" session to resolve conflicts.
- **FR14**: The system can invite specific conflicting authors into an active collaborative session.
- **FR15**: Users can visualize conflicting geometries using 3D Ghost Overlays ("Current" vs "Incoming").
- **FR16**: Users can interactively accept or reject specific property mutations from a peer's branch.

### Offline Lifecycle & Drift Management
- **FR17**: Users can continue making parametric edits while disconnected from the P2P network.
- **FR18**: The system can monitor "Mutation Drift" volume specifically during offline work.
- **FR19**: Users can configure a maximum drift threshold before the system locks editing.
- **FR20**: The system can notify users of "High-Drift" risk via native OS notifications.
- **FR21**: Users can export a "Static Snapshot" as a fallback if a rebase is unresolvable.

---

## Non-Functional Requirements

### Performance (Local-First Synergy)
- **NFR1: Property Sync Latency**: Mutation signals (text-based property changes) must propagate across the P2P network in **<200ms**.
- **NFR2: Local Recompute Resource Cap**: Background "Headless" recomputation must be throttled to use **no more than 3 cores (or 30% total CPU)** to ensure the user's primary FreeCAD session remains lag-free.
- **NFR3: Surgical Suite UI Responsiveness**: The transition from the standard CAD view to the "Social Conflict" overlay must be instantaneous (**<1 second**).

### Reliability & Consistency
- **NFR4: Geometric Parity (The "Same Result" Rule)**: Because recompute happens locally on different hardware, the system must use **Strict Version Enforcement** (FR6) to guarantee that two different local recomputes of the same mutation sequence produce **0.0% geometric deviation**.
- **NFR5: Silent Corruption Detection**: The system must perform a **Cryptographic Hash** of the local 3D model state after every recompute. If a mismatch is detected against the network "Truth," the node must lock and resync.
- **NFR6: Network Recovery**: The local P2P node must recover and resync missed mutations within **5 seconds** of regaining internet/LAN connectivity.

### Security & Sovereignty
- **NFR7: Local Data Encryption**: The persistent mutation ledger stored in `%AppData%` must be encrypted using **AES-256**.
- **NFR8: Peer Authentication**: All P2P connections must be validated via **Public-Key Infrastructure (PKI)** to prevent unauthorized nodes from joining a project swarm.

---

<!-- Next section: Complete PRD -->
