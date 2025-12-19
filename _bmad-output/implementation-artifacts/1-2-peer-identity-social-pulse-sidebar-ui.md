# Story 1.2: Peer Identity & Social Pulse Sidebar (UI)

Status: done

## Story

As an engineer,
I want to see a live list of active peers in the "Social Pulse" sidebar,
so that I have instant awareness of who is present and active in the collaborative session.

## Acceptance Criteria

1. **Given** I am in an active CollaborativeFC session with other peers connected (or simulated/mocked)
2. **When** I view the "Social Pulse" sidebar
3. **Then** the sidebar must display each peer's **Avatar** and **Author ID**
4. **And** the sidebar must show a visual **heartbeat/pulse indicator** (e.g., a color-coded dot) for each peer to signify their connection health
5. **And** clicking a peer avatar must trigger a camera alignment (Observation Mode) with that peer's current 3D viewport focus (Mocked action for now)

## Tasks / Subtasks

- [x] **Infrastructure & Dependencies**
    - [x] Research and Prototype WebView2 embedding in FreeCAD PySide2 context (Critical Path)
        - *Investigate `pyside2-webview`, `pythonnet` + `Edge WebView2`, or `pywebview` as fallback if QtWebEngine is missing.*
    - [x] Add necessary libraries to `requirements.txt`
- [x] **Frontend Implementation (HTML/CSS/JS)**
    - [x] Create `Mod/CollaborativeFC/Resources/sidebar/` directory structure
    - [x] Implement `index.html` structure (Avatar list, status indicators)
    - [x] Implement `styles.css` using "Mechanical Dark" theme and Pulse animations
    - [x] Implement `logic.js` to handle data injection and click events
- [x] **Backend Implementation (Python/Qt)**
    - [x] Create `Mod/CollaborativeFC/Sidebar.py`
    - [x] Implement `PulseSidebar` class (PySide2 DockWidget wrapping the WebView)
    - [x] Implement Data Bridge (Python -> JS) to send "Peer List" updates
    - [x] Implement Event Bridge (JS -> Python) to handle "Avatar Click"
- [x] **Integration**
    - [x] Register `PulseSidebar` in `InitGui.py` on workbench initialization
    - [x] Mock "Active Peers" data source to drive the UI for verification
    - [x] Verify "Click" event prints to FreeCAD console (stub for Observation Mode)

## Dev Notes

- **Architecture Pattern**: Hybrid UI. The Sidebar is a native FreeCAD DockWidget hosting a WebView content area.
- **Technology Constraint**: FreeCAD's embedded Python on Windows often lacks `QtWebEngineWidgets`.
    - **Primary Strategy**: If `QtWebEngineWidgets` is missing, use `pip install pywebview` or `pythonnet`.
    - **Fallback**: If WebView2 integration proves too unstable in this sprint, implement a `QListWidget` native fallback temporarily to meet the "Visual List" requirement, but prioritize the Web approach per Architecture.
- **UX**:
    - **Theme**: "Mechanical Dark" (#1A1A1B).
    - **Avatars**: Use `geometric-shapes` + `color` (Amethyst, Emerald, Sapphire).
- **Mocking**: Since P2P (Epic 2) is not ready, hardcode a list of 2-3 peers in Python to send to the UI.

### Project Structure Notes

- New Directory: `Mod/CollaborativeFC/Resources/sidebar/`
- New Module: `Mod/CollaborativeFC/Sidebar.py`

### References

- [Source: _bmad-output/epics.md#Story 1.2: Peer Identity & Social Pulse Sidebar (UI)]
- [Source: _bmad-output/ux-design-specification.md#6.1 Peer Avatar "Social Pulse" (WebView)]
- [Source: _bmad-output/architecture.md#Starter Option B (Rejected) -> Hybrid UI Orchestration]

## Dev Agent Record

### Agent Model Used

BMad-BMM-Create-Story/v1.0

### Debug Log References

- Verified `QtWebEngineWidgets` is missing in current environment. Added investigation task.

### Completion Notes List

- Implemented Hybrid UI Sidebar for Peer Identity.
- Integrated `pywebview` with a reparenting strategy to embed a modern WebView2 control into FreeCAD's PySide2 DockWidget.
- Added `pythonnet` and `pywebview` to `requirements.txt` to support this architecture on Windows.
- Created "Mechanical Dark" themed frontend with pulse animations and SVG-like geometric avatars.
- Established a Python-to-JS data bridge for real-time peer updates and a JS-to-Python event bridge for interactions.
- Mocked peer data (Sarah, Alex, Leo) to demonstrate the UI.
- **Architectural Update**: Moved to a "Stable Floating Mode" for the WebView2 window. This bypasses recursion/COM errors and prevents FreeCAD 1.0 crashes associated with cross-thread HWND reparenting.
- Verified everything with a new test suite and standalone prototype.

### File List

- `Mod/CollaborativeFC/Sidebar.py`
- `Mod/CollaborativeFC/InitGui.py` (Modified)
- `Mod/CollaborativeFC/Resources/sidebar/index.html`
- `Mod/CollaborativeFC/Resources/sidebar/styles.css`
- `Mod/CollaborativeFC/Resources/sidebar/logic.js`
- `requirements.txt` (Modified)
- `tests/test_ui_dependencies.py`
- `tests/test_sidebar.py`
