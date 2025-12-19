import FreeCAD
import FreeCADGui

class GhostManager:
    """
    Manages the creation and lifecycle of 'Ghost' objects for 3D visualization of conflicts.
    """
    def __init__(self):
        self.active_ghost = None

    def create_ghost(self, target_obj, prop_name, prop_value):
        """
        Creates a visual ghost of target_obj with the proposed property mutation applied.
        """
        # 1. Cleanup existing ghost
        self.remove_ghost()

        try:
            doc = FreeCAD.ActiveDocument
            if not doc:
                return

            # 2. Clone the object
            # copyObject returns only the objects, we need to paste them or use copyObject(obj, False) -> returns copy ??
            # doc.copyObject returns a list of objects if multiple.
            # Actually simplest is: new_obj = doc.copyObject(target_obj, False) ?? No
            # Correct API: doc.copyObject(obj) puts it in clipboard? No.
            
            # Use Part.copy? No, we want full parametric clone if possible, OR just a shape copy.
            # If we want to change property, we need a parametric clone.
            
            # Simplest Parametric Copy:
            # ghost = doc.addObject(target_obj.TypeId, f"__Ghost__{target_obj.Label}")
            # copy properties?
            
            # Relying on FreeCAD's built-in Copy:
            # ghost = doc.copyObject(target_obj, False) -> invalid syntax
            
            # Let's try:
            # 1. Get Geometry
            # 2. Create Simple Part::Feature
            # 3. Apply Shape
            # BUT we need to recompute with NEW property. A static shape copy won't reflect the change!
            # So we MUST clone the parametric object.
            
            # Strategy: Duplicate via Type
            # Determine Ghost Type
            # If target represents a Box (has L,W,H), use a simple Part::Box proxy
            # This avoids issues with PartDesign features (Body requirements) failing to compute.
            is_box_like = hasattr(target_obj, "Length") and hasattr(target_obj, "Width") and hasattr(target_obj, "Height")
            
            ghost_type = target_obj.TypeId
            if is_box_like and "PartDesign" in target_obj.TypeId:
                ghost_type = "Part::Box"
                FreeCAD.Console.PrintMessage(f"   [GHOST] Using Part::Box proxy for {target_obj.Label} ({target_obj.TypeId})\n")

            ghost = doc.addObject(ghost_type, f"Ghost_{target_obj.Label}")

            # 3. Copy Properties (Adaptive)
            if ghost.TypeId == "Part::Box":
                # Copy dims
                try:
                    ghost.Length = target_obj.Length
                    ghost.Width = target_obj.Width
                    ghost.Height = target_obj.Height
                    if hasattr(target_obj, "Placement"):
                        ghost.Placement = target_obj.Placement
                    FreeCAD.Console.PrintMessage(f"   [GHOST] Copied Dims: {ghost.Length}, {ghost.Width}, {ghost.Height}\n")
                except Exception as e:
                     FreeCAD.Console.PrintError(f"   [GHOST] Dim Copy Failed: {e}\n")

            elif target_obj.TypeId == "PartDesign::Pad":
                # Handle Pad by linking the same Profile (Safe for Length mutation)
                if hasattr(target_obj, "Profile") and target_obj.Profile:
                    ghost.Profile = target_obj.Profile
                if hasattr(target_obj, "Length"):
                    ghost.Length = target_obj.Length
                # Copy other essential Pad properties
                for p in ["Type", "UpToFace", "Reversed", "Midplane", "Offset"]:
                    if hasattr(target_obj, p) and hasattr(ghost, p):
                        setattr(ghost, p, getattr(target_obj, p))
                
                # IMPORTANT: Pad needs to be in a Body? 
                # Standalone Pads might fail if not in Body, but let's try.
                # Usually FreeCAD requires PartDesign features to have a Body ancestor.
                # If this fails, we might need to assume the visualizer works best on Primitives for now.
                # But linking Profile fixes the "No object linked" error.
            else:
                # Fallback: Just copy the shape (static ghost)
                # This won't reflect the mutation if it's parametric!
                # If we modify a generic object, we might not be able to "Ghost" it easily without full clone.
                # For this MVP, let's assume Part::Box or simple features.
                FreeCAD.Console.PrintWarning(f"[CollaborativeFC] Ghosting only fully supported for primitives. Fallback used.\n")
                if hasattr(target_obj, "Shape"):
                    ghost.Shape = target_obj.Shape
            
            # 3. Apply Mutation
            if hasattr(ghost, prop_name):
                # Handle type conversion if needed (string to float)
                # Assuming value is correct type from JSON
                try:
                    FreeCAD.Console.PrintMessage(f"   [GHOST] Applying Mutation: {prop_name} = {prop_value} (Type: {type(prop_value)})\n")
                    setattr(ghost, prop_name, prop_value)
                    
                    # Verify
                    new_val = getattr(ghost, prop_name)
                    FreeCAD.Console.PrintMessage(f"   [GHOST] Verify: {prop_name} is now {new_val}\n")
                except Exception as e:
                    FreeCAD.Console.PrintError(f"[CollaborativeFC] Failed to set ghost prop: {e}\n")
            
            # 4. Style
            doc.recompute()
            
            if hasattr(ghost, "ViewObject") and ghost.ViewObject:
                ghost.ViewObject.ShapeColor = (0.6, 0.2, 0.8) # Purple
                ghost.ViewObject.Transparency = 70
                ghost.ViewObject.LineColor = (1.0, 1.0, 1.0)
                ghost.ViewObject.LineWidth = 2.0
                
            self.active_ghost = ghost
            FreeCAD.Console.PrintMessage(f"[CollaborativeFC] Ghost created: {ghost.Label}\n")

        except Exception as e:
            FreeCAD.Console.PrintError(f"[CollaborativeFC] Create Ghost Failed: {e}\n")

    def remove_ghost(self):
        if self.active_ghost:
            try:
                doc = FreeCAD.ActiveDocument
                if doc:
                    # Verify object exists before access
                    obj = doc.getObject(self.active_ghost.Name) if hasattr(self.active_ghost, "Name") else None
                    if obj:
                        doc.removeObject(obj.Name)
                        doc.recompute()
            except Exception as e:
                FreeCAD.Console.PrintError(f"[CollaborativeFC] Remove Ghost Warning: {e}\n")
            finally:
                self.active_ghost = None

# Global Instance
_ghost_manager = GhostManager()

def get_instance():
    return _ghost_manager
