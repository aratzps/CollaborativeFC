# Story 4.1: Surgical Suite HUD (Qt Overlay)

**Status:** Ready for Dev
**Epic:** Epic 4: The Surgical Suite (Conflict Resolution)

## Description
As a user,
I want a transparent "Heads Up Display" (HUD) overlay on the 3D Viewport,
So that I can see conflict alerts and accept/reject proposals without leaving the 3D context.

## Acceptance Criteria
- [ ] **Given** the CollaborativeFC Workbench is active
- [ ] **When** a `SHOW_HUD` signal is triggered (e.g. conflict detected)
- [ ] **Then** a transparent overlay widget must appear over the 3D Canvas.
- [ ] **And** this overlay must allow clicking "through" it to rotate the model (where no buttons exist).
- [ ] **And** clicking a HUD button (Accept/Reject) must trigger the corresponding event.
- [ ] **And** the aesthetic must use "Glassmorphism" (semi-transparent dark mode).

## Implementation Plan
- **Technology:** Native `PySide` (`QWidget`).
- **Parenting:** `FreeCADGui.getMainWindow()` -> Find `MDIClient` or Active View.
- **Styling:**
    ```css
    QWidget#SurgicalHUD {
        background-color: rgba(20, 20, 30, 180);
        border-radius: 10px;
        border: 1px solid rgba(255, 255, 255, 30);
    }
    ```
- **Structure:**
    - `SurgicalOverlay(QWidget)`: The main container.
    - `ConflictCard(QFrame)`: The popup alert.

## Risks
- **Event Trapping:** Transparent widgets sometimes block mouse events for the 3D view. Need `setAttribute(Qt.WA_TransparentForMouseEvents, False)` but selectively enable it for children? Or manual event forwarding.
    - *Plan:* Use a "Click-Through" container that only blocks clicks on its visible children.
