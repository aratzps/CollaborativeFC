# Source Tree Analysis - CollaborativeFC

This document provides a breakdown of the source code structure for the CollaborativeFC FreeCAD add-on.

## Root Directory
- `Collaboration.py`: The main entry point for the collaboration infrastructure. It handles dependency checks, initializes the `OCPConnection`, `Manager`, and `UIWidget`, and hooks them together.
- `InitGui.py`: Standard FreeCAD entry point for UI initialization. Registers the workbench and sets up the `qasync` event loop.
- `Init.py`: FreeCAD entry point for console mode or early initialization.
- `Test.py`: A specialized test handler that connects to a WAMP test server to automate UI and synchronization tests.
- `requirements.txt`: Python package dependencies (`ocp`, `msgpack`, `autobahn`, `aiofiles`).
- `LICENSE`: The project is licensed under the GNU Library General Public License (LGPL) v2.0 or later.

## Sub-packages

### `/Documents`
Core logic for mirroring FreeCAD document state to the OCP node.
- `OnlineDocument.py`: Manages the lifecycle of a collaborative document.
- `OnlineObject.py`, `OnlineViewProvider.py`: Mirrors specific FreeCAD objects and their visual properties.
- `Observer.py`, `OnlineObserver.py`: Watches for local and remote changes.
- `Syncer.py`, `Batcher.py`: Manages synchronization flow and batches updates for performance.
- `AsyncRunner.py`: Custom runner for handling async operations on FreeCAD objects.

### `/Interface`
The presentation layer and UI logic.
- `Widget.py`: The main GUI frame.
- `DocView.py`, `DocEdit.py`, `PeerView.py`: Specific views for document and peer management.
- `Installer.py`: Guided installation for dependencies.
- `AsyncSlotWidget.py`: Bridge utilities for Qt signals and asyncio.

### `/Manager`
High-level orchestration of collaboration entities.
- `Manager.py`: The global registry of all collaborative documents (entities).
- `Entity.py`: A State Machine driven model representing a single collaborative document.
- `NodeDocument.py`: Handles peer management and document-level metadata on the OCP node.

### `/OCP`
Low-level communication with the Open Collaboration Platform node.
- `API.py`: WAMP client implementation for the OCP realm.
- `Node.py`: Subprocess management for the `ocp` executable.
- `Network.py`: Network topology and connectivity monitoring.
- `Connection.py`: Orchestrates the `API` and `Node` lifecycle.

### `/Dml`
Data Modeling Language schemas that define the synchronization structure of the document, objects, and properties.

### `/Utils`
General utility modules.
- `StateMachine.py`: A comprehensive hierarchical state machine implementation.
- `Errorhandling.py`: Standardized error catching and reporting.
- `AsyncSlot.py`: Utilities for connecting Qt slots to async functions.

### `/Resources`
Static assets like icons (`.svg`) and UI definition files (`.ui`).
