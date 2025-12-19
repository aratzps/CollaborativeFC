# Story 1.3: Feature Tree "Glints" & Ownership Awareness

Status: done

## Story

As an engineer,
I want the FreeCAD Feature Tree items to show "Glint" indicators when a peer is editing them,
So that I can proactively avoid editing the same features and prevent immediate conflicts.

## Acceptance Criteria

1. **Given** a peer is actively editing a feature's properties (simulated via mock for now)
2. **When** I look at my local FreeCAD Feature Tree
3. **Then** the corresponding tree item must display a color-coded **"Glint" pulse or border** matching the peer's avatar color
4. **And** hovering over the "Glint" must display a **Contextual Lens** (tooltip) showing the peer's name and the last edit timestamp (FR3)
5. **And** the feature's local properties must be visually "dimmed" in the property editor to signify a peer's active "Mutation Lease" (UX constraint)

## Tasks / Subtasks

- [x] **Infrastructure: Tree View Access**
    - [x] Locate the FreeCAD Tree View widget using PySide
    - [x] Research the best way to add custom overlays or indicators to Tree View items (Delegate vs. Icon update)
- [x] **Visual Implementation: The "Glint"**
    - [x] Create a mechanism to inject "Glint" state into specific tree items based on an OCP Object ID
    - [x] Implement color-coding (Amethyst, Emerald, Sapphire) based on the editing peer
    - [x] (Progressive) Implement a subtle pulse animation if possible via QPropertyAnimation or Timer
- [x] **Contextual Awareness**
    - [x] Implement Tooltip (Contextual Lens) with "Peer Name + Last Edit"
    - [x] Implement Property Editor "Dimming" (Visual locking of properties being edited by others)
- [x] **Integration & Mocking**
    - [x] Connect the Glint system to the `PulseSidebar` state (so colors match)
    - [x] Create a mock command `CollaborativeFC.SimulatePeerEdit` to trigger a glint on selected objects

## Dev Notes

- **Tree Widget**: In FreeCAD, this is usually a `QTreeView` with the object name `TreeWidget`.
- **Property Editor**: This is a `QTreeView` with the object name `propertyEditor`.
- **Dimming**: To dim properties, we can try to set them to read-only or change their background color via the Qt model.
- **Lease Logic**: In this story, the "Lease" is purely visual/simulated. Epic 2 will handle the actual network locking.

## Completion Notes (Phase 1)
- **Infrastructure**: Successfully bypassed FreeCAD C++ encapsulation by using `QStyledItemDelegate` for the Tree View and `QIdentityProxyModel` for the Property Editor.
- **Visuals**: Implemented high-contrast "Awareness Dots" with white halos and translucent row highlights that work in both light and dark themes.
- **Fuzzy Matching**: Implemented substring label matching to ensure glints stay attached even if FreeCAD modifies item labels internally.
- **Mocking**: Added a simulation command that allow cycling through peer ownership for testing.
- **Tools used**: Sub-agent research to identify target widget names (`DocumentTreeItems`, etc.) for FreeCAD 1.0.

![Final Glint Implementation](C:/Users/aratz/.gemini/antigravity/brain/c9f80afe-27ca-40b9-a536-be06e83552b0/uploaded_image_1766098160921.png)

## Project Structure Notes

- New Module: `Mod/CollaborativeFC/GlintManager.py`
- Update: `Mod/CollaborativeFC/InitGui.py` to initialize the GlintManager

## References

- [Source: _bmad-output/epics.md#Story 1.3: Feature Tree "Glints" & Ownership Awareness]
- [Source: _bmad-output/ux-design-specification.md#6.2 Tree Glints (Qt)]
