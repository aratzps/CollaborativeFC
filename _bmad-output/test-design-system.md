# System-Level Test Design

## Testability Assessment

### Controllability: PASS with Recommendations
- **Sidecar Lifecycle**: The architecture defines the Sidecar as a foreground-attached process managed by `InitGui.py`. This allows test harnesses to programmatically start/stop the sidecar to simulate crashes or restarts (supporting NFR6).
- **State Injection**: The "Local-first" nature with `MutationStore` in `%AppData%` allows tests to "seed" the state by simply writing pre-calculated DML files before starting the workbench.
- **Network Isolation**: Use of WAMP implies we can mock the router or peer messages easily in integration tests without needing actual internet connectivity.
- **Recommendation**: Ensure the `WorkbenchState` singleton has a "Test Mode" flag to redirect `%AppData%` paths to a temporary directory for isolation during parallel test execution.

### Observability: PASS
- **Ledger Transparency**: Story 2.1 requires a "View Local Ledger" debug view. This provides a direct window into the system's state for verification, bypassing complex UI scraping.
- **Deterministic State**: NFR5 (Geometric Hashing) provides a perfect "Oracle" for correctness. Tests can simply assert `current_hash == expected_hash` rather than inspecting complex 3D geometry.
- **Status Signals**: The "Fail-to-Read-Only" gate provides a clear binary state (Edit vs. Read-Only) that is easily readable by UI automation tools.

### Reliability: CONCERNS
- **Real-time Dependency**: NFR1 requires <200ms latency. Flaky network conditions in CI could lead to non-deterministic E2E failures.
- **Process Management**: Testing "Crash Recovery" (Sidecar death) requires robust OS-level process management in the test harness, which can be brittle on different CI runners (Windows vs Linux if applicable, though this is Windows-native).
- **Mitigation**: Heavily rely on "Network-First" testing by mocking WAMP messages rather than spinning up full peer swarms for every test.

## Architecturally Significant Requirements (ASRs)

| ASR ID | Requirement | Risk Score (P×I) | Testability Challenge |
| :--- | :--- | :--- | :--- |
| **ASR-1** | **Distributed Parametric Protocol (DPP)**: State-based CRDTs for deterministic property merging. | **9** (3×3) | Requires verifying eventual consistency across multiple nodes. Hard to debug race conditions. |
| **ASR-2** | **Geometric Parity (NFR4)**: 0.0% geometric deviation between peers. | **9** (3×3) | "Floating point drift" is notorious. Requires strict environment control (same OCCT version) in CI. |
| **ASR-3** | **Fail-to-Read-Only (Safety)**: Lock UI if Sidecar fails. | **6** (2×3) | Requires fault injection (killing subprocesses) during active UI sessions. |
| **ASR-4** | **Surgical Suite HUD**: WebView2 overlay > 1s load. | **4** (2×2) | Testing hybrid UI (Qt + WebView2) effectively requires specialized tooling (Playwright for web, something else for Qt?). |

## Test Levels Strategy

### Unit Tests: 40%
- **Focus**: CRDT Merge Logic, Geometric Hashing Algorithms, DML Ledger Parsing/Writing.
- **Rationale**: The core "truth" is mathematical (hashes and CRDTs). These can be tested in pure isolation without FreeCAD or Network.

### Integration Tests: 40%
- **Focus**: IPC (Socket) communication, Sidecar Lifecycle, "Fail-to-Read-Only" triggers, WAMP message dispatch/handling.
- **Rationale**: Verifying the loop between the FreeCAD Python wrapper and the C++ Sidecar is critical. We can mock the "Network" side of the Sidecar to test just the local integration.

### E2E Tests: 20%
- **Focus**: "Sarah's Midnight Integration" (Full collaborative flows), Surgical Suite UI interaction, Multi-node sync simulation.
- **Rationale**: High cost to setup (requires multiple FreeCAD instances or "Shadow Peers"). Reserve for critical user journeys and "Smoke Tests".

## NFR Testing Approach

### Security (SEC)
- **Peer Auth**: Unit test the PKI handshake logic.
- **Ledger Encryption**: Verify `MutationStore` writes ciphertext to disk (never plaintext).
- **Tooling**: Python `cryptography` libs for verification.

### Performance (PERF)
- **Sync Latency (NFR1)**: Instrument the Sidecar to log `timestamp_in` vs `timestamp_out`. Run benchmarks with mock WAMP router.
- **Recompute Overhead (NFR2)**: Use OS-level monitors (e.g., `psutil`) in integration tests to verify Sidecar stays under 30% CPU cap during heavy recomputes.

### Reliability (REL)
- **Recovery (NFR6)**: "Chaos Monkey" style tests: Kill the WAMP router, verify 5s reconnect. Kill the Sidecar, verify FreeCAD locks UI.

### Maintainability (MAINT)
- **Strict Versioning**: Automated check in CI to ensure Sidecar and Workbench protocols match.
- **Code Coverage**: Enforce high coverage on CRDT logic.

## Test Environment Requirements

- **OS**: Windows (Primary target). CI must run Windows runners.
- **FreeCAD Headless**: CI environment needs a "Headless FreeCAD" installation for running the Python tests.
- **WAMP Router**: A lightweight WAMP router (e.g., Crossbar.io) instance for Integration/E2E testing.

## Testability Concerns (Blockers)

- **WebView2 Automation**: Standard FreeCAD test frameworks don't easily support driving WebView2 content.
    - *Mitigation*: Use Playwright to test the Surgical Suite web app *in isolation* (mocking the `window.pywebview` bridge), then just smoke-test the loading in FreeCAD.
- **OCCT Parity in CI**: CI runners might use software rendering or different OCCT builds than user desktops.
    - *Mitigation*: Dockerize the build environment with exact version pinning, or stick to "Tier 1: Basic Regeneration" tests in CI and leave "Tier 3: Mass Props" for specific heavy-check pipelines.

## Recommendations for Sprint 0

1.  **Harness Setup**: Create a `TestWorkbenchState` that mocks the `Sidecar` for pure UI testing.
2.  **Bridge Mock**: Create a TypeScript mock of the FreeCAD<->WebView2 bridge to allow Playwright testing of the Surgical Suite.
3.  **Fixture Data**: Generate a library of "Standard Conflict Scenarios" (DML files) to seed tests for the Surgical Suite.
