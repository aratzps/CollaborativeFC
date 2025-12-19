import os
import logging
try:
    from PySide6 import QtCore, QtGui, QtWidgets
except ImportError:
    from PySide2 import QtCore, QtGui, QtWidgets

# RECURSION SHIELD: Same as Sidebar for consistency
import sys
sys.setrecursionlimit(10000)

class GlintItemDelegate(QtWidgets.QStyledItemDelegate):
    """
    Draws over the FreeCAD Tree View without replacing the model.
    This bypasses the 'setModel is private' error.
    """
    def __init__(self, manager, parent=None):
        super().__init__(parent)
        self.manager = manager
        self.colors = {
            "p1": QtGui.QColor("#A855F7"), # Amethyst
            "p2": QtGui.QColor("#10B981"), # Emerald
            "p3": QtGui.QColor("#3B82F6"), # Sapphire
            "default": QtGui.QColor("#94A3B8")
        }

    def paint(self, painter, option, index):
        # 1. Let FreeCAD draw the item first (so we can draw ON TOP)
        super().paint(painter, option, index)

        # 2. Get the item text (Label)
        item_text = str(index.data(QtCore.Qt.DisplayRole)).strip()
        peer_id = None
        
        # Fuzzy match to find if this item is being glinted
        # We check if the glinted key is inside the tree text (e.g., 'Body001' in 'Body001')
        for key, pid in self.manager.active_glints.items():
            if key and key in item_text:
                peer_id = pid
                break

        if peer_id:
            color = self.colors.get(peer_id, self.colors["default"])
            
            painter.save()
            painter.setRenderHint(QtGui.QPainter.Antialiasing)
            
            # 3. Draw a glow OVER the icon area (usually on the left)
            # We use a semi-transparent overlay
            glow_rect = QtCore.QRect(option.rect)
            glow_color = QtGui.QColor(color)
            glow_color.setAlpha(40)
            painter.fillRect(glow_rect, glow_color)
            
            # 4. Draw the awareness dot (Strong visibility)
            # Position it slightly to the left of the text
            dot_size = 10
            dot_x = option.rect.left() + 4
            dot_y = option.rect.top() + (option.rect.height() - dot_size) // 2
            
            # White halo for contrast
            painter.setBrush(QtGui.QBrush(QtCore.Qt.white))
            painter.setPen(QtCore.Qt.NoPen)
            painter.drawEllipse(dot_x-1, dot_y-1, dot_size+2, dot_size+2)
            
            # The actual peer color
            painter.setBrush(QtGui.QBrush(color))
            painter.drawEllipse(dot_x, dot_y, dot_size, dot_size)
            
            painter.restore()

    def helpEvent(self, event, view, option, index):
        """Show the 'Contextual Lens' tooltip on hover."""
        if event.type() == QtCore.Qt.ToolTip:
            item_text = str(index.data(QtCore.Qt.DisplayRole)).strip()
            peer_id = None
            for key, pid in self.manager.active_glints.items():
                if key and key in item_text:
                    peer_id = pid
                    break
            if peer_id:
                peer_name = "Peer"
                if peer_id == "p1": peer_name = "Sarah"
                elif peer_id == "p2": peer_name = "Alex"
                elif peer_id == "p3": peer_name = "Leo"
                QtWidgets.QToolTip.showText(event.globalPos(), 
                                          f"Currently editing by {peer_name}\n(CollaborativeFC Ownership)", 
                                          view)
                return True
        return super().helpEvent(event, view, option, index)

class GlintPropProxyModel(QtCore.QIdentityProxyModel):
    """
    Intercepts PropertyEditor calls to dim properties of 'Leased' objects.
    """
    def __init__(self, manager, parent=None):
        super().__init__(parent)
        self.manager = manager

    def data(self, index, role=QtCore.Qt.DisplayRole):
        import FreeCADGui
        import LockManager
        
        # PRIORITY: If the entire workbench is locked (Protocol Mismatch), dim EVERYTHING
        is_locked = LockManager.LockManager.get_instance().check_lock()
        
        selection = FreeCADGui.Selection.getSelection()
        peer_id = None
        
        if selection:
            obj = selection[0]
            peer_id = self.manager.active_glints.get(obj.Name) or self.manager.active_glints.get(obj.Label)
        
        try:
            val = super().data(index, role)
        except RuntimeError as e:
            # Catch "Can't find converter" for custom FreeCAD types like QList<Base::Quantity>
            if "converter" in str(e):
                return None
            raise e

        if peer_id or is_locked:
            if role == QtCore.Qt.BackgroundRole:
                # Darker background for locked/leased items
                return QtGui.QBrush(QtGui.QColor(45, 45, 55)) 
            if role == QtCore.Qt.ForegroundRole:
                # Dimmed text
                return QtGui.QBrush(QtGui.QColor(150, 150, 160))
            if role == QtCore.Qt.FontRole:
                if not val or not isinstance(val, QtGui.QFont):
                    val = QtGui.QFont()
                val.setItalic(True)
                return val
        return val

class GlintManager(QtCore.QObject):
    """
    Manages visual 'Glints' in the FreeCAD Tree View and Property Editor.
    Provides ownership awareness by highlighting features being edited by peers.
    """
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.tree_view = None
        self.prop_editor = None
        self.tree_delegate = None
        self.prop_proxy = None
        self.active_glints = {} # map of object_name -> peer_id
        
        # Peer Colors (Matching Sidebar)
        # self.colors is now handled by GlintItemDelegate

    def init_ui_hooks(self):
        """Aggressive hooking using Delegate for Tree and Proxy for Prop Editor."""
        import FreeCADGui, FreeCAD
        mw = FreeCADGui.getMainWindow()
        if not mw: return False
            
        all_views = mw.findChildren(QtWidgets.QTreeView)
        hooked_names = []
        
        # We hook ALL trees we find, just in case
        for v in all_views:
            name = v.objectName()
            
            # Use Delegate for Tree (Safe for any TreeView)
            # In FreeCAD 1.0, the main tree is 'DocumentTreeItems'
            if name in ["TreeWidget", "DocumentTreeItems"] or "Tree" in name or name == "":
                # Don't double-hook
                if not v.itemDelegate() or not isinstance(v.itemDelegate(), GlintItemDelegate):
                    delegate = GlintItemDelegate(self, v)
                    v.setItemDelegate(delegate)
                    self.tree_delegate = delegate
                    self.tree_view = v
                    hooked_names.append(f"Tree({name or 'unnamed'})")
            
            # Use Proxy for Property Editor
            if name in ["propertyEditorData", "propertyEditorView", "propertyEditor"]:
                model = v.model()
                if model and not isinstance(model, GlintPropProxyModel):
                    try:
                        self.prop_proxy = GlintPropProxyModel(self)
                        self.prop_proxy.setSourceModel(model)
                        v.setModel(self.prop_proxy)
                        self.prop_editor = v
                        hooked_names.append(f"Prop({name})")
                    except Exception:
                        pass
            
        if hooked_names:
            FreeCAD.Console.PrintMessage(f"[CollaborativeFC] Successfully hooked: {', '.join(hooked_names)}\n")
            
        # Start a refresh timer to keep glints updated
        if not hasattr(self, 'timer'):
            self.timer = QtCore.QTimer(self)
            self.timer.timeout.connect(self.update_ui)
            self.timer.start(2000) # Every 2 seconds
            
        return len(hooked_names) > 0

    def update_ui(self):
        """Forces repaints if there are active glints."""
        if self.active_glints:
            if self.tree_view: self.tree_view.viewport().update()
            if self.prop_editor: self.prop_editor.viewport().update()

    def set_glint(self, obj_name, peer_id, is_editing=True):
        if is_editing:
            self.active_glints[obj_name] = peer_id
        else:
            self.active_glints.pop(obj_name, None)
            
        if self.tree_view:
            self.tree_view.viewport().update()
        if self.prop_editor:
            self.prop_editor.viewport().update()

    def create_mock_glint(self):
        """Toggle a mock glint on the first selected object."""
        import FreeCAD, FreeCADGui
        if not FreeCAD.ActiveDocument:
            FreeCAD.Console.PrintError("[CollaborativeFC] Please open a document and create a part first!\n")
            return

        selection = FreeCADGui.Selection.getSelection()
        if not selection:
            FreeCAD.Console.PrintWarning("[CollaborativeFC] Select an object in the tree to simulate a glint.\n")
            return

        obj = selection[0]
        # Store glints by both Name and Label to ensure the ProxyModel finds it
        names_to_try = [obj.Name, obj.Label]
        
        current = self.active_glints.get(obj.Name) or self.active_glints.get(obj.Label)
        
        if not current: next_peer = "p1"
        elif current == "p1": next_peer = "p2"
        elif current == "p2": next_peer = "p3"
        else: next_peer = None
        
        if next_peer:
            self.set_glint(obj.Name, next_peer, True)
            self.set_glint(obj.Label, next_peer, True)
            FreeCAD.Console.PrintMessage(f"[CollaborativeFC] Glint ON for {obj.Label} ({obj.Name}) -> Peer: {next_peer}\n")
        else:
            self.set_glint(obj.Name, None, False)
            self.set_glint(obj.Label, None, False)
            FreeCAD.Console.PrintMessage(f"[CollaborativeFC] Glint OFF for {obj.Label}\n")
