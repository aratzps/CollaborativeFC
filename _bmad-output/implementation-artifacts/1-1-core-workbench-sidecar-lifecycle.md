# Story 1.1: Core Workbench & Sidecar Lifecycle

Status: review

<!-- Note: Validation is optional. Run validate-create-story for quality check before dev-story. -->

## Story

As an engineer,
I want the CollaborativeFC workbench to initialize and launch the OCP Sidecar,
so that I can start a collaborative session with zero manual infrastructure management.

## Acceptance Criteria

1. **Given** I have installed the CollaborativeFC add-on in `Mod/`
2. **When** I switch to the "Collaborative" workbench in FreeCAD
3. **Then** the `InitGui.py` file must register the workbench and its custom icons
4. **And** the system must launch the `src/sidecar/main.py` as a background-attached process
5. **And** the FreeCAD UI must display a "Sidecar Connected" status in the status bar

## Tasks / Subtasks

- [x] Initialize Project Structure
  - [x] Create `Mod/CollaborativeFC/` directory structure (Resources, icons, etc.)
  - [x] Create `src/sidecar/` directory structure
  - [x] Create `requirements.txt`
- [x] Implement Workbench Entry Point
  - [x] Create `Mod/CollaborativeFC/Init.py`
  - [x] Create `Mod/CollaborativeFC/InitGui.py`
  - [x] Create `Mod/CollaborativeFC/CollaborativeFC.py` class
  - [x] Implement `GetClassName`, `GetIcon`, `Activate`, `Deactivate` methods
- [x] Implement Sidecar Process Manager
  - [x] Create `src/sidecar/main.py` (skeleton)
  - [x] Implement `subprocess` launch logic in `InitGui.py` or a dedicated `SidecarManager` class
  - [x] Ensure sidecar is terminated when FreeCAD closes
- [x] Implement Status Bar Feedback
  - [x] Add `Sidecar Connected` message to FreeCAD status bar upon successful launch

## Dev Notes

- **Architecture Pattern**: Foreground-Attached Process. The Sidecar is a child process of FreeCAD.
- **Critical Lifecycle**: Ensure the sidecar is strictly tied to the workbench activation/deactivation or FreeCAD application lifecycle. Use `atexit` or `Deactivate` hook to kill the process if needed (though `subprocess` daemon usage might handle this).
- **Paths**: Use relative paths from the module root to locate `src/sidecar/main.py`.
- **Icons**: Ensure a placeholder icon exists for the workbench registration to succeed.

### Technical Requirements

- **Language**: Python 3.10+ (FreeCAD embedded)
- **Libs**: `subprocess`, `os`, `sys` for process management.
- **Structure**:
    ```
    CollaborativeFC/
    ├── Mod/CollaborativeFC/
    │   ├── Init.py
    │   ├── InitGui.py
    │   ├── CollaborativeFC.py
    └── src/sidecar/
        ├── main.py
    ```

### Architecture Compliance

- **Decision**: Custom FreeCAD Workbench Boilerplate.
- **Consistency**: Use `PascalCase` for the Workbench class `CollaborativeFC`.
- **Constraint**: Do not block the main UI thread while waiting for the sidecar. Launch it asynchronously or as a non-blocking subprocess.

### References

- [Source: _bmad-output/epics.md#Story 1.1: Core Workbench & Sidecar Lifecycle]
- [Source: _bmad-output/architecture.md#Starter Template Evaluation]

## Dev Agent Record

### Agent Model Used

BMad-BMM-Create-Story/v1.0

### Debug Log References

- None

### Completion Notes List

- Implemented standard FreeCAD Workbench structure.
- Created OCP Sidecar skeleton and process manager in `InitGui.py`.
- Rewrote `InitGui.py` path discovery to support FreeCAD's dynamic loading where `__file__` is undefined.
- Refactored `InitGui.py` to be self-contained, removing fragile imports of `CollaborativeFC.py`.
- Renamed workbench class to `CollaborativeFC` and added logging.
- Added `Initialize` and other required Workbench methods directly to `InitGui` class.
- Added properties package `__init__.py` to `Mod/CollaborativeFC`.
- Verified sidecar launch via mocks.
- Added updated unit tests for robust path finding logic.
- Removed `CollaborativeFC.py` as it was redundant; workbench definition consolidated in `InitGui.py`.

### File List

- `Mod/CollaborativeFC/Init.py`
- `Mod/CollaborativeFC/InitGui.py`
- `Mod/CollaborativeFC/__init__.py`
- `Mod/CollaborativeFC/Resources/icons/CollaborativeFC.svg`
- `src/sidecar/main.py`
- `requirements.txt`
- `tests/test_sidecar_manager.py`
