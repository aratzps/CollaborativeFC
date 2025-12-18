# Data Models - CollaborativeFC

This document describes the core data models and synchronization schemas used by the CollaborativeFC FreeCAD add-on, focusing on the DML (Data Modeling Language) definitions.

## Schema Overview (DML)
The collaboration is driven by a schema-based synchronization engine. The schemas are defined in `.dml` files located in the `Dml/` directory.

### Document (`main.dml`)
The root container for a collaborative session.
- **Properties**: A `PropertyContainer` for document-level settings.
- **Objects**: An `ObjectContainer` holding `DocumentObject` entries.
- **ViewProviders**: An `ObjectContainer` holding `ViewProvider` entries.
- **Transaction**: A recursive, automatic transaction management block that handles dependency propagation.

### Object (`object.dml`)
Represents a FreeCAD object (e.g., a Part, Sketch, or Feature).
- **Attributes**:
  - `typeid` (string): The FreeCAD Type ID (e.g., `Part::Box`).
  - `fcName` (string): The unique internal name in FreeCAD.
- **Properties**: A linked `PropertyContainer`.
- **Extensions**: A vector of strings representing FreeCAD extensions.
- **Events**:
  - `onSetupFinished`
  - `onObjectRecomputed`
  - `onExtensionCreated/Removed`

### Property (`property.dml`)
Defines the synchronization of individual object properties (parameters).
- **Attributes**:
  - `typeid`: FreeCAD Property type.
  - `group`: UI group in the Property Editor.
  - `documentation`: Help text.
  - `status`: Synchronization status (ReadOnly, Hidden, etc.).
  - `data`: The actual value (serialized).
- **Functions**: `SetValue`, `GetValue`, `GetInfo`, `SetEditorMode`.

## Application-Level Models (Python)

### Entity (`Manager/Entity.py`)
A State Machine driven model representing the collaboration state of a document.
- **States**: `Local` (Internal, Disconnected, CreateProcess), `Node` (Invited, OpenProcess, Online).
- **Online Sub-states**: `Replicate` (Observer mode), `Edit` (Interactive mode).
- **Responsibility**: Manages the lifecycle and transitions between local FreeCAD state and OCP network state.

### OnlineDocument (`Documents/OnlineDocument.py`)
The primary runtime orchestrator for document synchronization.
- **Internal Maps**:
  - `objects`: Maps object names to `OnlineObject` instances.
  - `viewproviders`: Maps object names to `OnlineViewProvider` instances.
- **Responsibility**: Handles FreeCAD document events, creates/removes online runners, and manages transactions.

### PeerView (`Interface/PeerView.py`)
Data structure for peer management.
- **Attributes**: `nodeid`, `joined`, `auth` (Read/Write rights).
