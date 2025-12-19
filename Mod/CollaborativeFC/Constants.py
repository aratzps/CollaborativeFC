import FreeCAD

# CollaborativeFC Protocol Constants
PROTOCOL_VERSION = "0.1.0" # Experimental version for Story 1.4

def get_freecad_build_id():
    """Returns a string representation of the FreeCAD/OCCT build version."""
    ver = FreeCAD.Version()
    # Format: 1.0.0-git-rev (BuildDate)
    return f"{ver[0]}.{ver[1]}.{ver[2]}-{ver[4]}"

def verify_protocol(remote_version, remote_build_id):
    """
    Verifies if a remote peer is compatible with the local node.
    Returns (is_compatible, message)
    """
    local_build = get_freecad_build_id()
    
    if remote_version != PROTOCOL_VERSION:
        return False, f"Protocol Mismatch: Local={PROTOCOL_VERSION}, Remote={remote_version}"
    
    if remote_build_id != local_build:
        return False, f"Build ID Mismatch: Local={local_build}, Remote={remote_build_id}"
        
    return True, "Compatible"
