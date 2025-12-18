---
stepsCompleted: [1, 2, 3, 4]
inputDocuments: []
session_topic: 'Onshape-level parity for FreeCAD (Concurrent Editing, Version Control, Branching/Merging)'
session_goals: 'Define architectural path for branching/merging in OCP, define native VC UX for FreeCAD, address parametric conflict resolution.'
selected_approach: 'ai-recommended'
techniques_used: ['Mind Mapping', 'Morphological Analysis', 'What If Scenarios']
ideas_generated: [12]
context_file: 'c:/Users/aratz/Documents/DEV/CollaborativeFC/_bmad/bmm/data/project-context-template.md'
session_active: false
workflow_completed: true
---

# Brainstorming Session Results

**Facilitator:** Aratz
**Date:** 2025-12-18

## Session Overview

**Topic:** Onshape-level parity for FreeCAD (Concurrent Editing, Version Control, Branching/Merging)
**Goals:** Define architectural path for branching/merging in OCP, define native VC UX for FreeCAD, address parametric conflict resolution.

### Context Guidance

Focuses on software and product development considerations including User Problems, Feature Ideas, and Technical Approaches for collaborative CAD.

### Session Setup

Guided AI-facilitated brainstorming focused on bridge the gap between desktop parametric CAD and cloud-native collaborative workflows.

## Technique Selection

**Approach:** AI-Recommended Techniques
**Analysis Context:** Onshape-level parity for FreeCAD with focus on branching, merging, and conflict resolution.

**Recommended Techniques:**

- **Mind Mapping:** Establish a foundation by mapping what constitutes a "Version" in the OCP/DML stack.
- **Morphological Analysis:** Systematically map conflict scenarios (Object Type, Change Type, Conflict Type) to resolution strategies.
- **What If Scenarios:** Stress-test architectural proposals against radical possibilities (e.g., server-side recomputing).

**AI Rationale:** This sequence moves from structural understanding (Mind Map) to deep system exploration (Morphological Analysis) and finally to creative validation (What If).

## Idea Organization and Prioritization

### Theme 1: The "Marrow" (Identity & Data Model) - **PRIORITY 1**
*Focus: Establishing property-level authorship and reproducible history.*
- **Identity Model**: Use NodeID as root ID with User Alias for display.
- **Property Authorship**: Add `author_id` and `timestamp` to every synced property in `property.dml`.
- **History as Recipe**: Define versions as a sequence of feature tree history + variable states.

### Theme 2: The "Surgery" (Merge Resolution) - **PRIORITY 2 & 3**
*Focus: Interactive tools to resolve topological and logic conflicts.*
- **Rebase Engine**: Headless OCP validation run to detect "Drift" before finalizing merge.
- **Structural Merge**: Ghost overlay in 3D + Feature Tree Diff view.
- **Surgical Suite**: Node-based Dependency Graph + Collaborative Sketching with real-time locks.

### Theme 3: The "Resilience" (Operational Policy) - **PRIORITY 4**
*Focus: Enforcing connectivity and managing drift.*
- **Micro-Branching**: Allow LAN/Offline work with a lease.
- **Mutation Lease**: Drift threshold based on mutation volume (points weighted by risk).
- **Graceful Lockdown**: UI "Orange Alert" when the drift lease is near expiry.

## Action Planning

### Phase 1: Identity Foundation (High Impact)
*   **Next Steps**: Modify `Dml/property.dml` and `Dml/object.dml` to include authorship fields. Update `Manager` to handle Alias-to-NodeID mapping.
*   **Success Indicator**: Every change in the FreeCAD log shows *who* changed it at the property level.

### Phase 2: The Rebase Logic (High Feasibility)
*   **Next Steps**: Develop the headless re-computation logic for rebasing a history sequence on a new OCP state.
*   **Success Indicator**: A merge can be "tested" in memory without affecting the Main branch.

## Session Summary and Insights
**Major Breakthrough**: The transition from a "technical file merge" to a **"Social Conflict Resolution"** session where authors are automatically invited to the merge surgery based on property metadata.

**Reflection**: By choosing "Continuous Connectivity" with a "Mutation-based Drift Lease," we've found a way to bridge the gap between P2P autonomy and cloud-native reliability.
