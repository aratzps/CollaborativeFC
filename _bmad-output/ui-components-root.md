# UI Components - CollaborativeFC

This document catalogs the UI components of the CollaborativeFC add-on, implemented using PySide2 and integrated into the FreeCAD environment.

## Main Interface

### `UIWidget` (`Interface/Widget.py`)
The primary entry point for the user, implemented as a frameless popup window.
- **Features**:
  - P2P/API connection status indicators.
  - Tabs for Node Management and Document Management.
  - Log viewer for the OCP node.
  - Integration with the `Installer` for initial setup.
- **Design**: Uses `.ui` files loaded via `FreeCADGui.PySideUic`.

## Document Management UI

### `DocView` (`Interface/DocView.py`)
A scrollable list of collaborative entities.
- **Component**: `DocWidget`
  - Displays document name and connection status.
  - Buttons: `Share`/`Join`, `Open`/`Close`, `Edit`.
  - Synchronization: Uses `StateMachineProcessWidget` to automatically reflect the state of the `Entity` state machine.

### `DocEdit` (`Interface/DocEdit.py`)
Detail view for configuring a specific document.
- **Features**:
  - Rename document (on the node).
  - Add/Remove peers by Node ID.
  - Toggle peer permissions (Read/Write).
  - Contains an embedded `PeerView`.

### `PeerView` (`Interface/PeerView.py`)
Manages the list of collaborators within a document.
- **Component**: `PeerWidget`
  - Shows Peer ID (Node ID), joined status, and current rights.
  - Functional buttons for permission toggling and removal.

## Utility UI

### `InstallView` (`Interface/Installer.py`)
Guided setup for Python dependencies.
- **Features**:
  - Displays contents of `requirements.txt`.
  - One-click installation using a background `pip` process.
  - Real-time output logging of the installation process.

### `AsyncSlotPromoter` (`Interface/AsyncSlotWidget.py`)
A utility wrapper that enables Qt controls to interact with asynchronous Python objects seamlessly, handling the bridge between Qt's signals/slots and Python's `asyncio`.

## FreeCAD Integration (`InitGui.py`)
- **Workbench**: Registers the "Collaborate" command.
- **Toolbar/Menu**: Adds the collaboration icon to the FreeCAD interface.
- **Lifecycle**: Initializes the `Qasync` event loop and hooks into FreeCAD document events (`DocumentOpened`, `DocumentClosed`).
