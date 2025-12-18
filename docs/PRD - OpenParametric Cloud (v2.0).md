# **Product Requirements Document: OpenParametric Cloud (v2.0)**

**Version:** 2.0 (Architecture Shift: Event Sourcing)

**Target Kernel:** FreeCAD 1.0.2 (Headless Docker Container)

**Primary Architecture:** Observer-Log-Replay (Linear Transaction Log)

**Date:** December 18, 2025

## **1\. Executive Summary**

### **1.1 Project Vision**

**OpenParametric Cloud (OPC)** is an enterprise-grade, open-source, self-hosted web application designed to replicate the core capabilities of Onshape. Unlike traditional CAD systems that rely on binary file management (.FCStd), OPC utilizes a database-centric **"Observer-Log-Replay"** architecture.

The primary goal is to provide a "Single Source of Truth" environment where the CAD model is defined not by a file, but by an immutable stream of atomic operations stored in a database. This eliminates file locking, enables real-time collaboration, and provides data sovereignty for organizations that cannot use public cloud SaaS solutions.

### **1.2 The Core Architectural Shift**

To achieve this vision using the open-source FreeCAD engine, OPC moves away from state synchronization (mirroring files) to **Event Sourcing** (syncing intent).

* **The Observer (Capture):** A client-side Python module hooks into the FreeCAD internal signaling system to intercept user actions *before* they are serialized to disk.  
* **The Log (Storage):** These intercepted actions are stored as a linear, timestamped sequence of JSON operations in MongoDB.  
* **The Replay (Regeneration):** Stateless server-side containers fetch this log and rapid-fire execute the commands to reconstruct the 3D geometry on demand.

### **1.3 Strategic Imperative: FreeCAD 1.0.2**

This project strictly targets **FreeCAD 1.0.2** (and later) to leverage the integrated **Topological Naming Algorithm (Realthunder integration)**. This ensures that the Operation Log stores stable topological hashes (e.g., Face34a...) rather than unstable integer indices, allowing operations to be replayed reliably even if upstream geometry changes slightly.

## **2\. System Architecture**

### **2.1 High-Level Data Flow**

1. **User Action:** User drags a sketch vertex or types "50mm" in the property editor.  
2. **Observer Capture:** The client-side Observer intercepts the internal onChanged signal.  
3. **Log Append:** The operation is serialized to JSON and pushed to the **Operation Log** (MongoDB).  
4. **Broadcast:** The server assigns a Sequence ID and broadcasts the new "Head" to all connected clients.  
5. **Replay Trigger:** The Geometry Service detects a change, fetches the new operations, updates its internal headless model, and regenerates the B-Rep.  
6. **Visual Update:** The Geometry Service exports a lightweight GLB mesh and sends it to the client for rendering.

### **2.2 Component Breakdown**

#### **A. The Observer (The Writer)**

* **Role:** The "Scribe" that translates user intent into database records.  
* **Location:** Runs inside the client's local session (WebAssembly or transient container).  
* **Technology:** Python module inheriting from FreeCAD.DocumentObserver.  
* **Logic:**  
  * slotCreatedObject(obj) $\\rightarrow$ **Op:** CREATE\_OBJECT  
  * slotChangedObject(obj, prop) $\\rightarrow$ **Op:** SET\_PROPERTY  
  * slotDeletedObject(obj) $\\rightarrow$ **Op:** DELETE\_OBJECT  
* **Debouncing:** Implements a "Batcher" to ensure continuous inputs (like slider dragging) only commit the final value to the log.

#### **B. The Operation Log (The Persistence)**

* **Role:** The "Single Source of Truth."  
* **Technology:** MongoDB (Time-Series Collection).  
* **Conflict Resolution:** **First-Come-First-Serve.**  
  * The database utilizes atomic auto-incrementing Sequence IDs.  
  * If User A and User B submit conflicting edits simultaneously, the database strictly orders them (e.g., SeqID 100 vs. 101). The Replayer executes them in that strict order, ensuring eventual consistency.

#### **C. The Replayer (The Reader/Geometry Service)**

* **Role:** The "Engine" that turns the log back into geometry.  
* **Location:** Stateless Docker Container (freecad-daily-cmd base).  
* **Checkpointing Optimization:**  
  * To avoid replaying 10,000 operations for every view, the system implements **Checkpoints**.  
  * Every 100 operations, a snapshot (.FCStd file) is saved to Object Storage (MinIO).  
  * The Replayer loads the nearest Checkpoint and only replays the subsequent $\\Delta$ operations.

## **3\. Data Structures & Schema**

### **3.1 The Atomic Operation Schema**

Every entry in the MongoDB log represents a discrete FreeCAD state change.

{  
  "sequence\_id": 1054,             // Global strict ordering key  
  "document\_id": "uuid-550e",      // The document this applies to  
  "user\_id": "user\_A",             // Who made the change  
  "timestamp": 1709340000,         // When it happened  
  "type": "SET\_PROPERTY",          // Operation Type (CREATE, SET, DELETE, RECOMPUTE)  
  "target": {  
    "object\_uuid": "pad\_001\_uuid", // Stable internal name (not Label)  
    "sub\_element": null            // Used for sub-object properties  
  },  
  "payload": {  
    "property": "Length",  
    "value": 50.0,  
    "unit": "mm",  
    "data\_type": "Float"  
  },  
  "metadata": {  
    "client\_version": "1.0.2",     // Critical for deterministic replay  
    "feature\_hash": "a1b2c3..."    // Optional integrity check  
  }  
}

### **3.2 Assembly Schema**

Assemblies are not FreeCAD files; they are JSON definitions stored in the database.

{  
  "assembly\_id": "asm\_root",  
  "instances": \[  
    {  
      "instance\_id": "inst\_1",  
      "source\_doc\_id": "bolt\_v2",  
      "version\_tag": "release\_1.0",  
      "transform\_matrix": \[1, 0, 0, 0, 0, 1, 0, 0, 0, 0, 1, 0, 10, 20, 0, 1\],  
      "mates": \[\]  
    }  
  \]  
}

## **4\. Functional Requirements**

### **4.1 Part Studio (Modeling)**

**Constraint:** The backend must never execute arbitrary user Python code. It must only execute "Whitelisted" commands via the Replayer.

#### **4.1.1 Sketching**

* **Interaction:** Client-side WebAssembly constraint solver (PlaneGCS port).  
* **Visuals:** Real-time updates at 60fps using local Three.js lines.  
* **Commit:** On MouseUp, the client sends a batched SET\_PROPERTY operation containing the final constraints and geometry to the server.  
* **Replay:** The server updates the Sketch object's internal geometry list and calls solve() to ensure the server-side B-Rep matches the client visual.

#### **4.1.2 Modeling Features**

* **Extrude/Revolve/Loft:** The UI sends high-level intents which map directly to PartDesign features.  
* **TNP Handling:**  
  * When a user references a face for a sketch or fillet, the log stores the **Topological Hash** (Face34a...) provided by FreeCAD 1.0.2.  
  * During replay, the Geometry Service queries the model for the element matching that hash, ensuring robust regeneration even if the upstream geometry index has shifted.

### **4.2 Assemblies**

* **Visualization:** The client loads GLB files for individual parts.  
* **Positioning:** The client applies the transformation matrices defined in the Assembly JSON.  
* **Mates:** High-level constraints (Planar, Revolute, Fastened) are solved by a backend solver (or client-side WASM solver) which updates the transformation matrices in the database.

## **5\. Conflict Resolution & Consistency**

### **5.1 The "First-Come-First-Serve" Rule**

1. **User A** changes Pad.Length to 50mm.  
2. **User B** (with 100ms latency) changes Pad.Length to 60mm.  
3. **Database Action:**  
   * Receives User A $\\rightarrow$ Assigns SeqID: 50\.  
   * Receives User B $\\rightarrow$ Assigns SeqID: 51\.  
4. **Replay Action:** Sets Length to 50, then immediately overwrites it to 60\.  
5. **Client Outcome:** User A receives the SeqID: 51 update, and their UI updates to 60mm. (Standard collaborative document behavior).

### **5.2 The "Broken History" Rule (TNP Scenario)**

1. **User A** deletes Sketch1.  
2. **User B** creates Pad1 using Sketch1.  
3. **Replay Action:**  
   * Executes DELETE(Sketch1).  
   * Executes CREATE(Pad1, Profile=Sketch1).  
   * **Failure:** The Replayer catches the "Object not found" exception.  
4. **Outcome:** The Replayer marks Pad1 as **"Error: Broken Reference"** in the feature tree. The document replay continues for subsequent valid features. The server does *not* crash.

## **6\. Development Roadmap**

### **Phase 1: The "Logger" (Months 1-2)**

**Goal:** Prove the capability to record and reproduce a FreeCAD session without .FCStd files.

* **Observer Module:** Port CollaborativeFC/Documents/OnlineObserver.py to a standalone Python script running in FreeCAD 1.0.2 Cmd.  
* **Filter Logic:** Implement "Debouncing" to handle high-frequency inputs (sliders).  
* **Local Test:** Run two local FreeCAD instances. Instance A writes to a JSON file; Instance B polls the file and replays commands to verify exact geometric replication.

### **Phase 2: The "Replayer" Service (Months 3-4)**

**Goal:** Reliable headless regeneration in Docker.

* **Containerization:** Build opc-worker image with FreeCAD 1.0.2 \+ FastAPI.  
* **API Implementation:** POST /regenerate { operations: \[...\] } $\\rightarrow$ Returns GLB.  
* **Checkpoint System:** Implement the logic to save/load .FCStd snapshots every N operations.

### **Phase 3: The Cloud Integration (Months 5-6)**

**Goal:** Multi-user synchronization over the web.

* **Gateway:** Node.js WebSocket server to route traffic between Client $\\leftrightarrow$ MongoDB $\\leftrightarrow$ Geometry Service.  
* **Frontend:** React/Three.js viewer that optimizes the "Optimistic UI" updates (showing the user a preview while waiting for server confirmation).

## **7\. Infrastructure Requirements**

| Component | Technology | Responsibility |
| :---- | :---- | :---- |
| **Persistence** | **MongoDB** | Stores the Operation Log (Write-Heavy). |
| **Object Storage** | **MinIO (S3)** | Stores Checkpoints (.FCStd) and GLB caches. |
| **Caching** | **Redis** | Stores the latest "State Hash" to prevent re-computing unchanged models. |
| **Compute** | **Docker/K8s** | Auto-scaling pool of Geometry Workers (opc-worker). |
| **Client** | **Three.js \+ WASM** | Visualizes GLB; Solves 2D constraints locally. |
| **Gateway** | **Nginx \+ Node.js** | Handles WebSockets and SSL termination. |

## **8\. Risk Management**

| Risk | Impact | Mitigation Strategy |
| :---- | :---- | :---- |
| **Floating Point Drift** | Model inconsistency between Client prediction and Server truth. | **Single Source of Truth:** The Server's GLB output is authoritative. The Client is merely a "Viewer." Strict version matching between Observer and Replayer Docker containers. |
| **Infinite Log Growth** | Slow load times for mature documents. | **Checkpoints:** The system never replays more than \~100 operations. It always loads the nearest snapshot. |
| **Python Injection** | Security vulnerability via malicious payloads. | **Sanitized Ops:** The Replayer *only* executes specific, whitelisted commands (Create, SetProp, Delete). It never executes raw Python strings sent from the client. |
| **Latency** | "Laggy" feel compared to desktop CAD. | **Optimistic UI:** The client uses WebAssembly (OpenCascade.js) to generate a rough approximation immediately while the server generates the high-fidelity mesh in the background. |

