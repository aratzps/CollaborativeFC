---
project_name: 'CollaborativeFC'
user_name: 'Aratz'
date: '2025-12-18'
sections_completed: ['technology_stack', 'language_rules', 'framework_rules', 'testing_rules', 'quality_rules', 'workflow_rules', 'anti_patterns']
status: 'complete'
rule_count: 24
optimized_for_llm: true
---

# Project Context for AI Agents

_This file contains critical rules and patterns that AI agents must follow when implementing code in this project. Focus on unobvious details that agents might otherwise miss._

---

## Technology Stack & Versions

- **FreeCAD Hosting**: Python 3.10+ / PySide2 (5.15.2.1)
- **Networking/P2P**: Autobahn (v25.10.2) / Twisted (v25.5.0) / Crossbar.io (v22.6.1)
- **Hybrid UI Bridge**: WebView2 (v143.0.3650.80)
- **Local Engine**: OCCT (Open CASCADE) for recompute parity (Must match FreeCAD 0.21+ exact OCCT version).

## Critical Implementation Rules

### Language-Specific Rules (Python & C++)

**Python (Main Process):**
- **Strict Main-Thread Decorator**: Any UI-interacting function MUST be decorated with `@on_main_thread` (or use `QMetaObject.invokeMethod`) to prevent segmentation faults during P2P callbacks.
- **Absolute Imports**: Always use absolute paths (e.g., `from CollaborativeFC.State import WorkbenchState`) to ensure compatibility with the FreeCAD `Mod/` loader.

**C++ (Sidecar Engine):**
- **Sovereign Memory**: Use smart pointers (`std::unique_ptr`) for all geometric buffer management.
- **Serialization Standard**: Use `nlohmann/json` for all IPC messages; do not use raw binary pointers across the socket bridge.

### Framework-Specific Rules (WAMP/WebView2)

**WAMP Protocol:**
- **Namespace Protocol**: Every topic MUST follow the `ocp.[action].[target]` identifier (e.g., `ocp.update.property`).
- **Sync Payload**: All synchronization events MUST include the `master_recompute_hash` for geometric parity verification.

**WebView2 (Surgical HUD):**
- **Transparency Mode**: Overlay windows MUST start in "Click-Through" mode (`WS_EX_TRANSPARENT`) unless the "Surgical Resolution" state is active.
- **Data Bridge**: Use the `WebChannel` bridge; direct JS injection is forbidden for performance reasons.

### Testing Rules

**Test Strategy:**
- **Co-location**: Unit tests reside in `__tests__/` subdirectories next to the source.
- **Geometric Parity Assertions**: Every synchronization test MUST assert that the `final_geometric_hash` matches exactly across local and remote peers.

**Mocking & Fixtures:**
- **Host Mocking**: Use the `freecad_test_setup` fixture to simulate the FreeCAD recompute environment.
- **P2P Isolation**: Use `OCPDiscoveryMock` to test networking logic without requiring a live Crossbar.io instance.

### Code Quality & Style Rules

**Critical Constraints:**
- **The "Fail-to-Read-Only" Gate**: Logic MUST detect Sidecar unresponsiveness and transition the UI to `Read-Only` mode automatically to prevent data loss.
- **Sidecar Lifecycle Manager**: All process creation MUST go through the `SubprocessManager` singleton; direct `os.system` or `subprocess.Popen` calls are strictly forbidden.

**Naming & Conventions:**
- **WAMP Themes**: `ocp.[action].[target]` (e.g., `ocp.dispatch.change`).
- **Python Style**: `snake_case` (vars/funcs) and `PascalCase` (classes).
- **Absolute Paths**: No relative `Mod/` paths; always use the absolute package reference.

### Development Workflow Rules
- **Sidecar Lifecycle**: Every feature branch MUST be tested with two concurrent peer instances locally to verify sync convergence.
- **Commit Pattern**: Use feature tree tags in commits: `feat(recompute): implement background OCCT loop`.

### Critical Don't-Miss Rules (Anti-Patterns)
- **❌ UI Blocking**: Never perform recomputes or networking in the main FreeCAD thread. This breaks the "Social Synergy" experience.
- **❌ Unchecked Recompute**: NEVER apply a remote mutation without first verifying local state. If recompute fails, trigger the **Surgical Resolving** state immediately.
- **❌ Global State Persistence**: Do not store transient peer state in the `.FCStd` file. All awareness must live in the `MutationStore` or the in-memory `WorkbenchState`.
- **❌ Siloed Errors**: All errors must be broadcast to the "Social Pulse" sidebar; silent failures in the background recompute loop are FORBIDDEN.

---

## Usage Guidelines

**For AI Agents:**
- Read this file before implementing any code.
- Follow ALL rules exactly as documented; do not assume "standard" patterns apply if they conflict with these project-specific rules.
- When in doubt, prefer the more restrictive/safe option (e.g., Read-Only fallback).
- Update this file if new distributed patterns emerge during implementation.

**For Humans:**
- Keep this file lean and focused on agent-facing friction points.
- Remove rules that become second nature to all contributors over time.
- Review for outdated version constraints quarterly.

Last Updated: 2025-12-18
