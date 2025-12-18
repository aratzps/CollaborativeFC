# Development and Operations Info - CollaborativeFC

This document provides information on how to develop, test, and deploy the CollaborativeFC add-on.

## Development Environment
- **Prerequisites**:
  - [FreeCAD](https://www.freecad.org/) (tested with 0.19 and later).
  - Python 3.x (as used by FreeCAD).
  - `ocp` command-line tool (Open Collaboration Platform).
- **Dependencies**:
  - `ocp` (Python binding)
  - `autobahn` (WAMP client)
  - `msgpack` (serialization)
  - `aiofiles` (async file IO)
  - `qasync` (asyncio/Qt integration)

## Installation
The add-on can be installed by placing the repository folder into the FreeCAD `Mod` directory.
Missing Python dependencies can be installed directly from the UI using the built-in `Installer` component (`Interface/Installer.py`), which executes `pip install -r requirements.txt` in a subprocess.

## Running the Application
1. Start FreeCAD.
2. Select the "Collaborate" workbench.
3. Use the popup UI to:
   - **Startup** the OCP node (managing the local P2P node).
   - **Connect** to the node via the WAMP API.
   - **Share** or **Join** documents.

## Testing
The project includes an automated test system in `Test.py`.
- **Test Server**: Requires a WAMP server running on the `ocptest` realm.
- **Environment Variables**:
  - `OCP_TEST_RUN=1`: Enables the test handler.
  - `OCP_TEST_SERVER_URI`: WebSocket URI for the test server (e.g., `ws://127.0.0.1:8081/ws`).
  - `OCP_TEST_RPC_ADDRESS`: Unique RPC address for the current instance (e.g., `ocp.test.instance1`).
  - `OCP_TEST_LOG_LEVEL`: Configures logging verbosity during tests (`Debug`, `Info`, `Warn`, `Error`).

## Observability and Logging
- **In-App Logs**: The `OCP node running` tab in the UI allows viewing logs from the `ocp` subprocess.
- **Python Console**: Detailed synchronization logs are printed to the FreeCAD Python console (Report View).
- **Error Handling**: Uses a custom state-machine-aware error handler (`Utils/Errorhandling.py`) that captures stack traces and associates errors with specific collaborative entities.
