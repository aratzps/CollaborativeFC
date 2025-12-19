try:
    from PySide6 import QtCore, QtGui, QtWidgets
except ImportError:
    from PySide2 import QtCore, QtGui, QtWidgets
import FreeCAD
import FreeCADGui

class VersionMismatchOverlay(QtWidgets.QDialog):
    """
    A high-visibility modal overlay that prevents interaction when versions mismatch.
    """
    def __init__(self, message, parent=None):
        super().__init__(parent or FreeCADGui.getMainWindow())
        self.setWindowFlags(QtCore.Qt.Window | QtCore.Qt.WindowStaysOnTopHint | QtCore.Qt.FramelessWindowHint)
        self.setModal(True)
        
        self.setStyleSheet("""
            QDialog {
                background-color: #111827;
                border: 2px solid #EF4444;
                border-radius: 8px;
            }
            QLabel {
                color: #F9FAFB;
                font-family: 'Segoe UI', sans-serif;
            }
            .error-title {
                color: #EF4444;
                font-size: 24px;
                font-weight: bold;
            }
            .error-msg {
                font-size: 14px;
                line-height: 1.5;
            }
            QPushButton {
                background-color: #EF4444;
                color: white;
                border: none;
                padding: 10px 20px;
                border-radius: 4px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #DC2626;
            }
        """)
        
        layout = QtWidgets.QVBoxLayout(self)
        layout.setContentsMargins(40, 40, 40, 40)
        layout.setSpacing(20)
        
        title = QtWidgets.QLabel("⚠️ PROTOCOL MISMATCH")
        title.setProperty("class", "error-title")
        title.setAlignment(QtCore.Qt.AlignCenter)
        layout.addWidget(title)
        
        msg = QtWidgets.QLabel(message)
        msg.setProperty("class", "error-msg")
        msg.setAlignment(QtCore.Qt.AlignCenter)
        msg.setWordWrap(True)
        layout.addWidget(msg)
        
        info = QtWidgets.QLabel("Collaboration and editing have been LOCKED to prevent data corruption. Please update your CollaborativeFC workbench.")
        info.setAlignment(QtCore.Qt.AlignCenter)
        info.setWordWrap(True)
        info.setStyleSheet("color: #94A3B8; font-style: italic;")
        layout.addWidget(info)
        
        btn = QtWidgets.QPushButton("Exit Workbench")
        btn.clicked.connect(self.evict_user)
        layout.addWidget(btn, 0, QtCore.Qt.AlignCenter)

    def evict_user(self):
        """Forces the user out of the Collaborative workbench."""
        import FreeCADGui
        FreeCAD.Console.PrintMessage("[CollaborativeFC] User evicted due to protocol mismatch.\n")
        # Switch to a safe workbench (Part)
        FreeCADGui.activateWorkbench("PartWorkbench")
        self.accept()

class LockManager:
    _instance = None
    
    def __init__(self):
        self.is_locked = False
        self.lock_message = ""
        self.overlay = None

    @classmethod
    def get_instance(cls):
        if not cls._instance:
            cls._instance = LockManager()
        return cls._instance

    def lock_workbench(self, message):
        """Locks the workbench and shows the critical overlay."""
        self.is_locked = True
        self.lock_message = message
        FreeCAD.Console.PrintError(f"[CollaborativeFC] WORKBENCH LOCKED: {message}\n")
        
        # In a real environment, we would trigger the Qt dialog here
        # or disable the Command handlers.
        
        # Intercepting property editor via GlintManager (dimming everything)
        # and disabling simulation commands.
        
        # For now, we'll just store the state. The Commands will check this.
        
    def show_overlay(self):
        """Displays the high-visibility overlay."""
        try:
            self.overlay = VersionMismatchOverlay(self.lock_message)
            self.overlay.show()
        except Exception as e:
            FreeCAD.Console.PrintError(f"[CollaborativeFC] Failed to show overlay: {e}\n")

    def check_lock(self):
        """Returns True if the workbench is locked."""
        return self.is_locked
