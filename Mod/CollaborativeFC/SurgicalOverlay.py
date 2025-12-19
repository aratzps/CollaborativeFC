try:
    from PySide6 import QtCore, QtGui, QtWidgets
except ImportError:
    from PySide2 import QtCore, QtGui, QtWidgets

class SurgicalOverlay(QtWidgets.QWidget):
    # Signal to notify parent logic: "accept" or "reject"
    decision_made = QtCore.Signal(str)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setAttribute(QtCore.Qt.WA_TransparentForMouseEvents, False) # Should intercept clicks on itself
        self.setAttribute(QtCore.Qt.WA_TranslucentBackground) # Essential for glass look
        self.setWindowFlags(QtCore.Qt.FramelessWindowHint | QtCore.Qt.WindowStaysOnTopHint | QtCore.Qt.SubWindow)
        
        # Stylesheet for Glassmorphism
        self.setStyleSheet("""
            QWidget {
                background: transparent;
            }
            QFrame#ConflictCard {
                background-color: rgba(30, 30, 40, 220);
                border: 1px solid rgba(255, 255, 255, 40);
                border-radius: 12px;
            }
            QLabel {
                color: #E2E8F0;
                font-family: 'Segoe UI', sans-serif;
            }
            QPushButton {
                background-color: rgba(255, 255, 255, 20);
                border: 1px solid rgba(255, 255, 255, 30);
                border-radius: 6px;
                color: white;
                padding: 6px 12px;
            }
            QPushButton:hover {
                background-color: rgba(255, 255, 255, 40);
            }
            QPushButton#RejectBtn {
                background-color: rgba(239, 68, 68, 60); /* Red */
            }
            QPushButton#AcceptBtn {
                background-color: rgba(34, 197, 94, 60); /* Green */
            }
        """)

        # Layout
        self.layout_main = QtWidgets.QVBoxLayout(self)
        self.layout_main.setAlignment(QtCore.Qt.AlignTop | QtCore.Qt.AlignHCenter)
        self.layout_main.setContentsMargins(20, 60, 20, 20) # Top margin to avoid toolbar overlap

        # Mock Conflict Card
        self.card = self.create_conflict_card("Conflict Detected", "User 'Sarah' modified 'Part::Box' Length to 50.0")
        self.layout_main.addWidget(self.card)
        
        # Geometry Sync (needs to be hooked to resize events later)
        if parent:
            self.resize(parent.width(), parent.height())

    def create_conflict_card(self, title, description):
        card = QtWidgets.QFrame()
        card.setObjectName("ConflictCard")
        card.setFixedWidth(400)
        
        vbox = QtWidgets.QVBoxLayout(card)
        
        # Header
        lbl_title = QtWidgets.QLabel(f"⚠️ {title}")
        lbl_title.setStyleSheet("font-weight: bold; font-size: 14px; color: #FCD34D;") # Amber
        vbox.addWidget(lbl_title)
        
        # Desc
        lbl_desc = QtWidgets.QLabel(description)
        lbl_desc.setWordWrap(True)
        vbox.addWidget(lbl_desc)
        
        vbox.addWidget(lbl_desc)
        
        # Timeline Scrubber (Story 4.2)
        lbl_time = QtWidgets.QLabel("Evolution History:")
        lbl_time.setStyleSheet("font-size: 10px; color: #94A3B8; margin-top: 10px;")
        vbox.addWidget(lbl_time)
        
        slider = QtWidgets.QSlider(QtCore.Qt.Horizontal)
        slider.setObjectName("MutationSlider")
        slider.setRange(0, 100)
        slider.setValue(100)
        slider.setStyleSheet("""
            QSlider::groove:horizontal {
                border: 1px solid #374151;
                height: 4px;
                background: #1F2937;
                margin: 2px 0;
                border-radius: 2px;
            }
            QSlider::handle:horizontal {
                background: #A855F7;
                border: 1px solid #A855F7;
                width: 14px;
                height: 14px;
                margin: -6px 0;
                border-radius: 7px;
            }
        """)
        vbox.addWidget(slider)
        slider.valueChanged.connect(self.update_ghost_opacity)
        
        # Diff View Toggle (Story 4.2)
        chk_diff = QtWidgets.QCheckBox("Show Geometric Diff (Faces)")
        chk_diff.setObjectName("DiffToggle")
        chk_diff.setStyleSheet("""
            QCheckBox { color: #E2E8F0; font-size: 11px; margin-top: 5px; }
            QCheckBox::indicator { width: 14px; height: 14px; }
        """)
        vbox.addWidget(chk_diff)
        
        # Buttons
        hbox_btn = QtWidgets.QHBoxLayout()
        btn_reject = QtWidgets.QPushButton("Reject")
        btn_reject.setObjectName("RejectBtn")
        btn_reject.clicked.connect(self.on_reject)
        
        btn_accept = QtWidgets.QPushButton("Accept")
        btn_accept.setObjectName("AcceptBtn")
        btn_accept.clicked.connect(self.on_accept)
        
        hbox_btn.addWidget(btn_reject)
        hbox_btn.addStretch()
        hbox_btn.addWidget(btn_accept)
        vbox.addLayout(hbox_btn)
        
        return card

    def update_geometry(self):
        if self.parent():
            self.resize(self.parent().size())

    def resizeEvent(self, event):
        super().resizeEvent(event)
        # Updates the mask so only the card captures mouse events (and is visible)
        # This restores interaction with the 3D Viewport in empty space
        if hasattr(self, 'card'):
            self.setMask(QtGui.QRegion(self.card.geometry()))

    def update_ghost_opacity(self, value):
        import FreeCAD
        try:
            import GhostManager
            gm = GhostManager.get_instance()
            if gm and gm.active_ghost and hasattr(gm.active_ghost, "ViewObject"):
                 # Value 0-100 map to Transparency 100-0 (inverted) or just direct?
                 # FreeCAD Transparency is 0 (opaque) to 100 (invisible)
                 # Slider is 0 to 100.
                 # Let's say Slider 100 = Full Visibility (Trans=0)
                 # Slider 0 = Invisible (Trans=100)
                 trans = 100 - value
                 gm.active_ghost.ViewObject.Transparency = trans
        except Exception: pass

    def on_reject(self):
        print("[CollaborativeFC] User Rejected Conflict")
        self.decision_made.emit("reject")
        self.hide()

    def on_accept(self):
        print("[CollaborativeFC] User Accepted Conflict")
        self.decision_made.emit("accept")
        self.hide()
