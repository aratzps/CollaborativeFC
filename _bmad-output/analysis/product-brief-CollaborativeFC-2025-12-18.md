---
stepsCompleted: [1, 2, 3, 4, 5, 6]
inputDocuments:
  - '_bmad-output/analysis/brainstorming-session-2025-12-18.md'
  - '_bmad-output/master-index.md'
  - '_bmad-output/source-tree-analysis.md'
  - '_bmad-output/api-contracts-root.md'
  - '_bmad-output/data-models-root.md'
  - '_bmad-output/ui-components-root.md'
  - '_bmad-output/dev-ops-info-root.md'
  - '_bmad-output/project-scan-report.json'
  - 'README.md'
  - 'docs/PRD - OpenParametric Cloud (v2.0).md'
workflowType: 'product-brief'
lastStep: 6
project_name: 'CollaborativeFC'
user_name: 'Aratz'
date: '2025-12-18'
---

# Product Brief: CollaborativeFC

**Date:** 2025-12-18
**Author:** Aratz

---

## Executive Summary

CollaborativeFC is a revolutionary open-source framework for FreeCAD that provides real-time multi-user synergy and professional version control features currently exclusive to high-end cloud-native platforms like Onshape. By implementing a Distributed Parametric Protocol and a "Social Merge" workflow, it enables engineering teams to work concurrently on complex models without "Merge Hell," while maintaining full sovereignty over their data through a P2P architecture.

---

## Core Vision

### Problem Statement
Most CAD systems (with the exception of Onshape) are built on a "Single-User, Single-File" paradigm. This creates "Desktop CAD Islands" where collaboration requires clunky check-in/check-out systems, manual file sharing, or fragile branching that is nearly impossible to merge once geometries drift. This lack of real-time synergy slows down engineering cycles and introduces significant human error during integration.

### Problem Impact
- **Productivity Loss**: Teams cannot work on the same part or assembly simultaneously, leading to sequential bottlenecks.
- **Merge Fatigue**: Branching a complex parametric model often leads to unresolvable topological conflicts, forcing engineers to manually rebuild work.
- **Opaque History**: Standard version control doesn't track *who* changed *which* variable, making it difficult to understand the intent behind model changes.

### Why Existing Solutions Fall Short
- **File-based PDM**: Only manages files, not the data *inside* the files. It handles "versions" but fails at "concurrent edits."
- **Proprietary Cloud CAD**: Provides features (Onshape) but at the cost of data sovereignty, high subscription fees, and "walled garden" lock-in.
- **Screen Sharing**: Primitive and non-interactive; only one person has control.

### Proposed Solution
An open-source, OCP-integrated FreeCAD workbench that treats the CAD model as a **Distributed Parametric Protocol.** It moves beyond "file-sync" to facilitate a **Social Recompute** where every feature addition and variable change is tracked, owner-attributed, and negotiated in real-time. This allows teams to treat their shared model as a living recipe of collaborative engineering intents.

### Key Differentiators
- **Human-Centric Conflict Resolution**: A groundbreaking protocol where merge conflicts automatically trigger a **Live Surgery Session.** Affected "Authors"—identified by DML metadata—are invited into a shared workspace to reconcile their geometric intents.
- **The Merge Workbench**: A specialized CAD environment featuring **Interactive Dependency Graphs** (Logic), **3D Ghost Overlays** (Space), and **Collaborative Sketchers** (Geometry) where multiple users collaboratively "untie knots" in real-time.
- **Variable-Level Sovereignty**: Full version control and authorship tracked at the **Atomic Variable level** (Parameters), allowing for a 100% transparent audit trail of design decisions.
- **Resilient Mutation Leases**: A "Local-First" architecture featuring a **Drift-Lease Safety Valve** that monitors mutation volume during offline work and ensures synchronization before merge stability is compromised.

---

<!-- Next section: Target Users -->

 ## Target Users
 
 ### Primary Users
 
 #### **1. Sarah, CTO of a Hardware Startup**
 - **Role**: Lead engineer/decision-maker in a remote-first hardware company.
 - **Incentive**: Data sovereignty combined with Onshape-level collaborative speed.
 - **Pain Point**: "Merge Hell" and link management in distributed FreeCAD projects.
 - **Value**: The **Live Surgery Session** resolves weeks of integration work in minutes.
 
 #### **2. Alex, Open Source Project Maintainer**
 - **Role**: Coordinator of high-complexity global hardware projects (e.g., Open EV).
 - **Incentive**: Scalable contribution review without local recompute bottlenecks.
 - **Pain Point**: Rejecting valid contributions due to opaque dependency risks.
 - **Value**: **Peer Review through Collaborative Sketching** with clear property authorship.
 
 ### Secondary Users
 - **Stakeholders/Viewers**: Non-CAD users needing "Live BOMs" or status checks via P2P nodes.
 - **Simulation Engineers**: Needing to pull live, owner-attributed variables into analysis scripts.
 
 ### User Journey: The "Emergency Rebase"
 1. **Discovery**: Startup team adopts CollabFC to regain data sovereignty from expensive cloud CAD.
 2. **Trigger**: Two engineers reconnect after a LAN session with overlapping property mutations.
 3. **The Alert**: **Mutation-based Drift Lease** triggers an "Orange Alert" in the UI.
 4. **The Surgery**: Sarah initiates a **Live Surgery Session**; authors are auto-invited.
 5. **Success**: Team unties the dependency knot in the **Interactive Graph**, saves hours of manual rework, and the assembly recomputes for all peers.
 
 ---
 
 ## Success Metrics
 
 ### User Success Metrics
 - **Speed to Integrated State**: 90% of multi-branch merges involving >2 authors are resolved and recomputed in **under 15 minutes**.
 - **The Resilience Ratio**: Tracking "Mutation Volume vs. Conflict-Free Merges"—measuring how much parametric work can be performed "offline" while still maintaining an automatic rebase compatibility.
 - **Graph Scalability**: Continuous growth of the **Dependency Graph** complexity (nodes/edges) without a linear increase in sync latency or recompute failures.
 
 ### Business Objectives
 - **Short-Term (Prototype Phase)**: Enable a distributed team of 3+ engineers to concurrently design a multi-part assembly with zero manual file transfers over a 1-week sprint.
 - **Strategic Goal**: Become the default "Collaboration Protocol" for major Open Source Hardware projects, replacing clunky Git-for-CAD workarounds.
 - **Market Impact**: Demonstrate a **50% reduction in "Integration Day" overhead** for small hardware startups compared to standard file-based FreeCAD workflows.
 
 ### Key Performance Indicators (KPIs)
 - **Mean Time to Merge (MTTM)**: Average time spent in the "Surgical Suite" per conflict.
 - **Drift Tolerance**: The average "Mutation Volume" a branch can sustain before a rebase requires a "Surgery Session."
 - **Social Participation Rate**: Percentage of "Surgery Sessions" that successfully include the original property authors (verifying the effectiveness of the Auto-Invite protocol).
 
 ---
 
 ## MVP Scope
 
 ### Core Features
 - **The Identity Foundation**: Implementation of property-level authorship (`author_id`) and `timestamp` fields within the DML schemas.
 - **Headless Rebase Validation**: A background engine that runs dry-run rebases of mutation sequences to verify model integrity before a merge.
 - **"Social Merge" Invitations**: Automatic identification of conflicting authors, triggered by the `author_id` in the DML metadata.
 - **The "Drift Lease" Monitor**: Mutation volume counter with a graceful "UI Warning" when local drift exceeds the compatibility threshold.
 - **Basic 3D Ghosting**: Simple spatial overlay showing the "Proposed" vs. "Current" geometry during a conflict.
 
 ### Out of Scope for MVP
 - **Collaborative Sketcher**: Live multi-user drawing and constraint manipulation (V2.0).
 - **Interactive Dependency Graph**: The logic-layer visualization of the assembly links (V2.0).
 - **Automated Parameter Optimization**: AI-assisted suggested fixes for conflicts.
 - **Built-in Chat/Voice**: Relying on external communication tools (Zoom, Slack, Discord) for social negotiation.
 
 ### MVP Success Criteria
 - **Merge Integrity**: 100% of validated merges result in a recomputed model that matches the designer's intent.
 - **Drift Awareness**: Users reported "no surprises" during merges because the Mutation Lease notified them of drift early.
 - **Setup Speed**: A team can set up a shared OCP node and begin property-level tracking in under 10 minutes.
 
 ### Future Vision
 - **The All-In-One Engineering OS**: Evolving into a full-featured "Onshape for Open Source" with native communication, advanced dependency graph surgery, and integrated simulation feedback.
 - **Global Design Marketplace**: Allowing users to "Branch" public parts and contribute back with verified histories.
 
 ---
 
 <!-- Workflow Complete -->
