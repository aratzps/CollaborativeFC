---
stepsCompleted: [1, 2, 3, 4]
inputDocuments:
  - '_bmad-output/prd.md'
  - '_bmad-output/architecture.md'
  - '_bmad-output/ux-design-specification.md'
  - '_bmad-output/api-contracts-root.md'
  - '_bmad-output/data-models-root.md'
  - '_bmad-output/ui-components-root.md'
  - '_bmad-output/dev-ops-info-root.md'
---

# CollaborativeFC - Epic Breakdown

## Overview

This document provides the complete epic and story breakdown for CollaborativeFC, decomposing the requirements from the PRD, UX Design if it exists, and Architecture requirements into implementable stories.

## Requirements Inventory

### Functional Requirements

FR1: The system can uniquely identify every OCP Node in a collaborative session.
FR2: The system can attribute every property change in a FreeCAD document to a specific Author ID and Timestamp.
FR3: Users can view the authorship history of any parametric feature in the document tree.
FR4: The system can synchronize property-level mutations across P2P nodes in real-time.
FR5: The system can detect when a local mutation sequence diverges from the network's "Main" branch.
FR6: The system can force a protocol version match across all connected nodes before allowing edits.
FR7: The system can store the local mutation ledger in a dedicated persistent cache (%AppData%).
FR8: The system can execute a FreeCAD recomputation in a background "headless" process.
FR9: The system can validate a mutation sequence for "Sequential Parity" (proving rebase = edit).
FR10: Users can select between multiple validation tiers (Basic Regeneration, Geometric Sanity, or Mass Property check).
FR11: The system can detect "Topological Naming" breaks where feature references are lost during rebase.
FR12: The system can identify and flag overlapping property edits between authors.
FR13: Users can initiate a "Live Surgery" session to resolve conflicts.
FR14: The system can invite specific conflicting authors into an active collaborative session.
FR15: Users can visualize conflicting geometries using 3D Ghost Overlays ("Current" vs "Incoming").
FR16: Users can interactively accept or reject specific property mutations from a peer's branch.
FR17: Users can continue making parametric edits while disconnected from the P2P network.
FR18: The system can monitor "Mutation Drift" volume specifically during offline work.
FR19: Users can configure a maximum drift threshold before the system locks editing.
FR20: The system can notify users of "High-Drift" risk via native OS notifications.
FR21: Users can export a "Static Snapshot" as a fallback if a rebase is unresolvable.

### NonFunctional Requirements

NFR1: Property Sync Latency: Mutation signals (text-based property changes) must propagate across the P2P network in <200ms.
NFR2: Local Recompute Resource Cap: Background "Headless" recomputation must be throttled to use no more than 3 cores (or 30% total CPU).
NFR3: Surgical Suite UI Responsiveness: The transition from the standard CAD view to the "Social Conflict" overlay must be instantaneous (<1 second).
NFR4: Geometric Parity: Use Strict Version Enforcement to guarantee 0.0% geometric deviation between local recomputes.
NFR5: Silent Corruption Detection: Perform a Cryptographic Hash of the local 3D model state after every recompute to verify against network "Truth".
NFR6: Network Recovery: Local P2P node must recover and resync missed mutations within 5 seconds of regaining connectivity.
NFR7: Local Data Encryption: Persistent mutation ledger in %AppData% must be encrypted using AES-256.
NFR8: Peer Authentication: P2P connections validated via Public-Key Infrastructure (PKI).

### Additional Requirements

**Technical (Architecture):**
- **Starter Template**: Use Custom FreeCAD Workbench Boilerplate (`Mod/CollaborativeFC/` structure).
- **Process Model**: OCP Sidecar as a Foreground-Attached Process (SubprocessManager).
- **Communication**: WAMP (Autobahn/Twisted) for sync, Unix Sockets for IPC.
- **Safety**: "Fail-to-Read-Only" gate if Sidecar/Lease fails or heartrate is lost.
- **Data**: State-based CRDTs and SHA-256 Geometric Hashing for 0.0% divergence.
- **Security**: PKI-based peer identity; AES-256-GCM local ledger encryption.
- **UI**: WebView2 (v143.0.3650.80) for Surgical HUD transparent overlay.

**User Experience (UX Design):**
- **Design Approach**: "Synergy Hybrid" (Qt for Native Tree, WebView2 for Sidebar/HUD).
- **Visuals**: "Mechanical Dark" theme, Peer "Glints" (Tree), and 3D Ghosting.
- **Interaction**: "Presence Without Intrusion", "3D-First Resolution", "Geometric Handshake" animation.
- **Workflow**: Unidirectional Data Flow (UI -> Command -> Sidecar -> Ledger -> UI Sync).
- **State Management**: "Observation Mode" (Camera Sync), "Drift Lockdown" recovery path.
- **Accessibility**: Multi-modal authorship (Colors + Geometric Author Badges), WCAG 2.1 AA compliance.

### FR Coverage Map

FR1: Epic 1 - Identity & Presence
FR2: Epic 1 - Identity & Presence
FR3: Epic 1 - Identity & Presence
FR4: Epic 2 - Distributed Sync & Ledger
FR5: Epic 2 - Distributed Sync & Ledger
FR6: Epic 1 - Identity & Presence
FR7: Epic 2 - Distributed Sync & Ledger
FR8: Epic 3 - Headless Recompute & Parity
FR9: Epic 3 - Headless Recompute & Parity
FR10: Epic 3 - Headless Recompute & Parity
FR11: Epic 3 - Headless Recompute & Parity
FR12: Epic 4 - The Surgical Suite
FR13: Epic 4 - The Surgical Suite
FR14: Epic 4 - The Surgical Suite
FR15: Epic 4 - The Surgical Suite
FR16: Epic 4 - The Surgical Suite
FR17: Epic 5 - Offline & Drift
FR18: Epic 5 - Offline & Drift
FR19: Epic 5 - Offline & Drift
FR20: Epic 5 - Offline & Drift
FR21: Epic 5 - Offline & Drift

## Epic List

### Epic 1: Workspace Initialization & Peer Presence
Establish the "Ambient Synergy" environment where users can see their peers and be uniquely identified.
**FRs covered:** FR1, FR2, FR3, FR6.

### Epic 2: Distributed Mutation Sync & Ledger
Enable real-time parametric property synchronization between nodes.
**FRs covered:** FR4, FR5, FR7.

### Epic 3: Headless Recompute & Geometric Parity
Ensure all distributed peers maintain 100% geometric agreement.
**FRs covered:** FR8, FR9, FR10, FR11.

### Epic 4: The Surgical Suite (Conflict Resolution)
Provide a professional, visual environment for resolving topological clashes.
**FRs covered:** FR12, FR13, FR14, FR15, FR16.

### Epic 5: Offline Lifecycle & Drift Management
Manage the risks of disconnected work with proactive warnings.
**FRs covered:** FR17, FR18, FR19, FR20, FR21.

## Epic 1: Workspace Initialization & Peer Presence

Establish the "Ambient Synergy" environment where users can see their peers and be uniquely identified.

### Story 1.1: Core Workbench & Sidecar Lifecycle

As an engineer,
I want the CollaborativeFC workbench to initialize and launch the OCP Sidecar,
So that I can start a collaborative session with zero manual infrastructure management.

**Acceptance Criteria:**

**Given** I have installed the CollaborativeFC add-on in `Mod/`
**When** I switch to the "Collaborative" workbench in FreeCAD
**Then** the `InitGui.py` file must register the workbench and its custom icons
**And** the system must launch the `src/sidecar/main.py` as a background-attached process
**And** the FreeCAD UI must display a "Sidecar Connected" status in the status bar

### Story 1.2: Peer Identity & Social Pulse Sidebar (UI)

As an engineer,
I want to see a live list of active peers in the "Social Pulse" sidebar,
So that I have instant awareness of who is present and active in the collaborative session.

**Acceptance Criteria:**

**Given** I am in an active CollaborativeFC session with other peers connected
**When** I view the "Social Pulse" sidebar (implemented via WebView2)
**Then** the sidebar must display each peer's **Avatar** and **Author ID**
**And** the sidebar must show a visual **heartbeat/pulse indicator** (e.g., a color-coded dot) for each peer to signify their connection health
**And** clicking a peer avatar must trigger a camera alignment (Observation Mode) with that peer's current 3D viewport focus

### Story 1.3: Feature Tree "Glints" & Ownership Awareness

As an engineer,
I want the FreeCAD Feature Tree items to show "Glint" indicators when a peer is editing them,
So that I can proactively avoid editing the same features and prevent immediate conflicts.

**Acceptance Criteria:**

**Given** a peer is actively editing a feature's properties
**When** I look at my local FreeCAD Feature Tree
**Then** the corresponding tree item must display a color-coded **"Glint" pulse or border** matching the peer's avatar color
**And** hovering over the "Glint" must display a **Contextual Lens** (tooltip) showing the peer's name and the last edit timestamp (FR3)
**And** the feature's local properties must be visually "dimmed" in the property editor to signify a peer's active "Mutation Lease" (UX constraint)

### Story 1.4: Protocol Version Verification & Lock

As a team lead,
I want the workbench to verify that all peers are using the same protocol version before allowing edits,
So that we prevent geometric corruption caused by mismatched OCCT or recompute logic.

**Acceptance Criteria:**

**Given** I have just launched the CollaborativeFC workbench
**When** my OCP node connects to the peer swarm
**Then** the system must perform a handshake to verify the **CollaborativeFC Protocol Version** and **FreeCAD/OCCT Build ID**
**And** if a mismatch is detected, the workbench must display a **Critical Error** overlay
**And** all write-access (editing) to the document must be **locked** until the user updates to the matching version (FR6)
**And** the "Social Pulse" sidebar must show a "Version Mismatch" status on the incompatible peer(s)

## Epic 2: Distributed Mutation Sync & Ledger

Enable real-time parametric property synchronization between nodes.

### Story 2.1: Encrypted Local Mutation Ledger (DML)

As an engineer,
I want my parametric edits to be stored in a local, append-only encrypted ledger (`%AppData%`),
So that my work is cryptographically secure and I maintain full data sovereignty.

**Acceptance Criteria:**

**Given** I am making parametric edits in FreeCAD
**When** a property change is committed
**Then** the Sidecar must append the mutation (ID, Author, Value, Timestamp) to the local ledger file
**And** the ledger must be encrypted using **AES-256-GCM** (NFR7)
**And** the ledger must be stored in the persistent `%AppData%/CollaborativeFC` directory (FR7)
**And** the system must provide a "View Local Ledger" debug view to audit recent mutations

### Story 2.2: WAMP Property Sync & Dispatch

As a collaborator,
I want my parametric property changes to be broadcast to my peers in real-time,
So that we can work concurrently on the same assembly with minimal latency.

**Acceptance Criteria:**

**Given** I am in a collaborative session with one or more peers
**When** I change a property (e.g., `Length`, `Radius`) of a FreeCAD feature
**Then** the workbench must dispatch a mutation signal to the local OCP Sidecar
**And** the Sidecar must broadcast this mutation over **WAMP** using the `ocp.update.property` topic (Architecture Decision)
**And** the mutation signal must reach peers in **< 200ms** (NFR1)
**And** the Sidecar must include the `geometric_hash` in the payload for immediate verification (FR4)

### Story 2.3: Divergence Detection & "Fail-to-Read-Only" Gate

As a team member,
I want the system to alert me if my local model diverges from the swarm truth,
So that I don't continue editing in a state that will cause unresolvable conflicts.

**Acceptance Criteria:**

**Given** a mutation has just been received from a peer and applied locally
**When** the local recompute finishes
**Then** the Sidecar must compare the local `geometric_hash` with the hash received from the peer (FR5)
**And** if the hashes mismatch (Divergence Detected), the workbench must trigger a **Safety Lock**
**And** the FreeCAD UI must enter **"Read-Only Mode"** (Architecture Decision) until the user performs a resync
**And** the "Social Pulse" sidebar must display a **Divergence Warning** (Safety Orange alert)

## Epic 3: Headless Recompute & Geometric Parity

Ensure all distributed peers maintain 100% geometric agreement.

### Story 3.1: Headless Recompute Service (Sidecar)

As an engineer,
I want the OCP Sidecar to execute recomputations in a headless background process,
So that my primary FreeCAD UI remains responsive and free from "sync-induced lagging."

**Acceptance Criteria:**

**Given** a mutation has been received from a peer
**When** the Sidecar is instructed to validate the new model state
**Then** it must launch a headless FreeCAD or OCCT instance (FR8)
**And** the background process must be throttled to **< 30% total CPU/3 cores** (NFR2)
**And** the Sidecar must return a `geometric_snapshot_hash` once the computation is complete
**And** the main FreeCAD thread must continue to respond to user view/navigation events during the recompute

### Story 3.2: Geometric Hash Validation (SHA-256)

As a team member,
I want the system to cryptographically verify my local recomputed model against the swarm "Truth,"
So that I have absolute "0.0% deviation" certainty that my design matches my peers.

**Acceptance Criteria:**

**Given** the headless recompute service has finished a validation run for a new mutation
**When** the Sidecar generates the model's geometric hash (SHA-256)
**Then** it must compare this hash against the master branch hash received via WAMP (NFR5/FR5)
**And** if they match, the system must provide a **"Parity Confirmed"** signal to the local workbench
**And** the FreeCAD status bar must show a **"Geometric Integrity Confirmed"** success message
**And** if they mismatch, the system must trigger the **"Fail-to-Read-Only"** gate (defined in Epic 2)

### Story 3.3: Topological Naming Break Detection

As a designer,
I want to be alerted if a recompute causes references to be lost (Topological Naming Conflict),
So that I can enter the "Surgical Suite" and fix the references before they corrupt downstream features.

**Acceptance Criteria:**

**Given** a mutation sequence is being validated in the background recompute engine
**When** FreeCAD detects a "broken" feature reference (e.g., a lost Face or Edge ID)
**Then** the system must flag a **Topological Conflict** error (FR11)
**And** it must identify the specific **Parent Feature ID** and the **Daughter Feature ID** that lost its reference
**And** the workbench must automatically present the **"Enter Surgical Suite"** notification to resolution the dependency break
**And** the recompute process must halt at the point of failure to prevent "Cascading Error State."

## Epic 4: The Surgical Suite (Conflict Resolution)

Provide a professional, visual environment for resolving topological clashes.

### Story 4.1: Surgical Suite HUD (WebView2 Transparent Overlay)

As a designer,
I want a full-screen transparent WebView2 overlay (The Surgical Suite) to launch during conflicts,
So that I can resolve complex topological clashes in a high-fidelity, interactive environment.

**Acceptance Criteria:**

**Given** a conflict has been detected (FR12) and the user has selected "Enter Surgical Suite" (FR13)
**When** the HUD is triggered
**Then** a **transparent WebView2 window** must be rendered over the FreeCAD viewport (Architecture Decision).
**And** the HUD must transition from invisible to visible in **< 1 second** (NFR3).
**And** the HUD must display the **Conflict Resolution Card** for the specific feature in question.
**And** the HUD must support "Click-through" by default, only capturing mouse events when interacting with the resolution cards.

### Story 4.2: 3D Ghosting & Mutation Scrubbing

As an engineer,
I want to see a ghosted 3D overlay of a peer's proposed changes,
So that I can visually compare "Current" vs "Incoming" geometry before committing a resolution.

**Acceptance Criteria:**

**Given** I am in the Surgical Suite HUD
**When** I hover over an "Incoming Mutation" card
**Then** the system must render a **Ghost Overlay** (low-alpha blueprint style) of the peer's feature geometry in the 3D viewport (FR15)
**And** the user must be able to "scrub" through the mutation history using a timeline slider to see the design's evolution
**And** the HUD must provide a **"Diff View"** toggle to highlight exactly which faces or edges have been modified.

### Story 4.3: Interactive "Geometric Handshake" (Accept/Reject)

As a collaborator, I want to interactively accept or reject specific peer mutations within the Surgical Suite, so that I can align our parametric model definitions with a single click.

**Acceptance Criteria:**

**Given** I am reviewing a conflict in the Surgical Suite HUD
**When** I click the **"Accept Incoming"** or **"Keep Local"** button on a resolution card (FR16)
**Then** the system must perform a **Geometric Handshake** animation (shrink-wrap ghost into solid).
**And** the Sidecar must update the local mutation ledger (DML) with the chosen state.
**And** the workbench must trigger a final local recompute to solidify the change.
**And** the HUD must automatically dismiss itself once the last conflict in the session is resolved.

## Epic 5: Offline Lifecycle & Drift Management

Manage the risks of disconnected work with proactive warnings.

### Story 5.1: Offline Editing & Local Ledger Buffering

As a traveling engineer,
I want to continue making parametric edits while disconnected from the OCP network,
So that I can remain productive during travel or internet outages.

**Acceptance Criteria:**

**Given** my OCP node has lost its P2P connection
**When** I make a parametric edit in FreeCAD (FR17)
**Then** the workbench must continue to commit mutations to the local **Encrypted DML Ledger**
**And** the status bar must change to **"Offline Synergy - Buffering Mutations"**
**And** the system must queue these mutations for automatic broadcast as soon as a network connection is re-established.

### Story 5.2: "Mutation Fuel Gauge" (Drift Monitoring)

As an offline user,
I want a visual indicator (The Mutation Fuel Gauge) of my current "Mutation Drift" volume,
So that I can proactively decide when to find a connection and sync before my rebase risk becomes too high.

**Acceptance Criteria:**

**Given** I am in an offline edit session
**When** I add or modify parametric features
**Then** the Sidebar must display a **Mutation Fuel Gauge** (FR18)
**And** the gauge must calculate "Drift" based on a combination of:
  1. Total offline mutation count.
  2. Depth of dependency impact (e.g., base flange edits weigh more than hole chamfers).
**And** the gauge must transition from **Safe (Green)** to **High-Risk (Orange)** as the volume increases.
**And** the gauge must be configurable via the "Project Settings" menu (FR19).

### Story 5.3: "Drift Lockdown" & Native Warning

As a team lead,
I want the system to block offline editing once a risk threshold is hit,
So that the user doesn't create unresolvable "Integration Hell" that disrupts the wider team.

**Acceptance Criteria:**

**Given** the "Mutation Fuel Gauge" has reached the critical threshold (e.g., 100%)
**When** the user attempts another edit
**Then** the workbench must lock the document in **"Read-Only" mode**
**And** trigger a **native Windows notification** alerting the user to "Sync Required" (FR20)
**And** the Sidebar must display a red **"Drift Exceeded: Connect to Sync"** status
**And** the user cannot unlock writing until a successful P2P rebase is performed

### Story 5.4: Emergency Static Snapshot Export

As a frustrated engineer,
I want to export my current offline work as a static file if a rebase fails or I remain locked out,
So that I can manually recover my geometry without losing hours of effort.

**Acceptance Criteria:**

**Given** I am in a "Drift Lockdown" state or facing an unresolvable merge conflict
**When** I click the **"Emergency Export"** button in the Sidebar
**Then** the system must save the current in-memory model state as a standard `.FCStd` file (timestamped backup)
**And** this file must be stripped of OCP metadata (converted to a static, unlinked document) (FR21)
**And** the system must display a toast notification: "Snapshot Saved: [Filename]"
