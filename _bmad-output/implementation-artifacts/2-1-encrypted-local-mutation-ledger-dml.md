# Story 2.1: Encrypted Local Mutation Ledger (DML)

Status: in-progress

## Story

As an engineer,
I want my parametric edits to be stored in a local, append-only encrypted ledger (%AppData%),
So that my work is cryptographically secure and I maintain full data sovereignty.

## Acceptance Criteria

- [ ] **Mutation Recording**: The system must record (ID, Author, Value, Timestamp) for every property change committed.
- [ ] **AES-256-GCM Encryption**: The ledger file on disk must be fully encrypted using AES-256-GCM.
- [ ] **AppData Persistence**: The ledger must be stored in `%AppData%/CollaborativeFC/mutation_ledger.db` (or similar).
- [ ] **Debug Audit View**: A command to view the local ledger contents (decrypted for the user) must be available.

## Tasks / Subtasks

- [ ] **Ledger Engine (Sidecar)**
    - [ ] Implement the `LedgerManager` in the Sidecar (Python).
    - [ ] Choose a lightweight storage engine (SQLite with SQLCipher or simple append-only JSON/MessagePack).
    - [ ] Implement AES-256-GCM encryption/decryption logic.
- [ ] **Property Change Capture**
    - [ ] Hook into FreeCAD property changes (from Story 1.3 infrastructure).
    - [ ] Forward mutations from the Workbench (Qt) to the Sidecar (IPC).
- [ ] **Persistence Layer**
    - [ ] Ensure the `%AppData%/CollaborativeFC` directory exists.
    - [ ] Implement rotation/compaction for the ledger file.
- [ ] **Workbench Integration**
    - [ ] Create a "View Ledger" command in the Collaborative workbench.
    - [ ] Implement a basic UI (Qt or WebView2) to list recent mutations.

## Dev Notes

- **Encryption**: Use `cryptography` library for AES-GCM.
- **Storage**: Given the "Append-only" requirement, a simple sqlite database or an encrypted flat file is ideal.
- **Author ID**: Use the local user's Author ID from Story 1.2.

## References

- [Source: _bmad-output/epics.md#Story 2.1: Encrypted Local Mutation Ledger (DML)]
- [NFR7: Persistent mutation ledger in %AppData% must be encrypted using AES-256.]
