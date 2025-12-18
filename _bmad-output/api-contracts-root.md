# API Contracts - CollaborativeFC

This document catalogs the WAMP (Web Application Messaging Protocol) API contracts used to communicate between the CollaborativeFC FreeCAD add-on and the OCP (Open Collaboration Platform) node.

## Connection Details
- **Protocol**: WAMP over WebSockets
- **Serializer**: msgpack
- **Realm**: `ocp`
- **Default Endpoint**: `ws://localhost:8080/ws` (configurable via P2P/API settings)

## Document Management (`ocp.documents.*`)

| Procedure | Parameters | Description |
|-----------|------------|-------------|
| `create` | `dmlPath` | Creates a new shared document using the provided DML schema. Returns `docId`. |
| `open` | `docId` | Opens an existing shared document on the node. |
| `close` | `docId` | Closes the document on the node. |
| `list` | None | Returns a list of all documents currently open on the node. |
| `invitations` | None | Returns a list of document IDs the node has been invited to. |
| `status` | `docId` | Returns current status of a document (`open`, `invited`, `closed`). |
| `view` | `bool` | Toggles the node's "view" mode (prevents synchronization interruptions). |
| `listPeers` | `docId` | Returns a list of peers currently collaborating on the document. |

## Content Synchronization (`ocp.documents.{docId}.content.*`)

| Procedure | Parameters | Description |
|-----------|------------|-------------|
| `Transaction.IsOpen` | None | Checks if a synchronization transaction is currently open. |
| `Transaction.Close` | None | Closes the current transaction, committing changes to all peers. |
| `Document.Objects.GetObjectTypes` | None | Returns a map of object names to their FreeCAD Type IDs. |

## Events (Subscriptions)

| Topic | Data | Description |
|-------|------|-------------|
| `ocp.documents.created` | `docId` | Emitted when a new document is created on the node. |
| `ocp.documents.opened` | `docId` | Emitted when a document is opened. |
| `ocp.documents.closed` | `docId` | Emitted when a document is closed. |
| `ocp.documents.invited` | `docId`, `added` | Emitted when an invitation is received or revoked. |

## Node Configuration (`config.*`)

The node lifecycle is managed via CLI-style calls to the `ocp` binary:
- `config [key]`: Read configuration.
- `config write [key] [value]`: Update configuration.
- `stop`: Shutdown the node.
- `init`: Initialize the node directory.
