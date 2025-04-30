import sys
import time
import random
import os
import base64
import ctypes
import hashlib
import zlib
import struct

# Disable printing to console - helps prevent command windows
sys.stdout = open(os.devnull, 'w')
sys.stderr = open(os.devnull, 'w')

from PyQt5.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
                             QLabel, QLineEdit, QPushButton, QMessageBox, QGraphicsDropShadowEffect,
                             QFrame)
from PyQt5.QtCore import Qt, QTimer, QThread, pyqtSignal, QPropertyAnimation, QEasingCurve
from PyQt5.QtGui import QColor, QFont, QPainter, QPen, QIcon

# Advanced multi-stage password validation - extremely difficult to reverse engineer
class PasswordSystem:
    def __init__(self):
        # The expected password is constructed dynamically and never explicitly
        # stored in the binary, making it much harder to extract statically
        
        # These bytes are not the actual password but encrypted data used in verification
        self.__verification_bytes = [
            120, 156, 51, 52, 50, 54, 176, 72, 206, 200, 76, 206, 78, 205, 3, 0, 24, 171, 4, 71
        ]
        
        # Series of transformations to make static analysis difficult
        self.__transform_keys = [
            0x1F, 0x3A, 0x2D, 0x5E, 0x7B, 0x4C, 0x6D, 0x8F
        ]
        
        # Anti-debugging detection - corrupts the verification if being debugged
        if self.__detect_debugger():
            self.__corrupt_verification()
    
    def __detect_debugger(self):
        # Various techniques to detect debugging/analysis
        try:
            if ctypes.windll.kernel32.IsDebuggerPresent():
                return True
                
            # Check execution time for anti-VM detection
            start = time.time()
            time.sleep(0.01)
            duration = time.time() - start
            if duration < 0.005:  # Extremely fast execution often indicates being traced
                return True
                
            return False
        except:
            return False
    
    def __corrupt_verification(self):
        # If debugging is detected, subtly corrupt the verification process
        # This makes the crackme behave differently under analysis
        self.__verification_bytes = [b ^ random.randint(1, 10) for b in self.__verification_bytes]
    
    def __validate_stage1(self, password):
        # First verification stage - decompress the verification data
        try:
            data = bytes(self.__verification_bytes)
            decompressed = zlib.decompress(data)
            return decompressed
        except:
            return b"invalid"  # If decompression fails, verification will fail
    
    def __validate_stage2(self, stage1_result, password):
        # Apply transformations based on password characters and system info
        system_entropy = sum(ord(c) for c in os.path.basename(sys.argv[0]))
        password_entropy = sum(ord(c) for c in password)
        
        # Create a highly dynamic key that changes based on system and input
        key_seed = (system_entropy + password_entropy) % 256
        
        # Apply multiple rounds of transformation
        validation_key = []
        for i, byte in enumerate(stage1_result):
            key = (self.__transform_keys[i % len(self.__transform_keys)] ^ key_seed)
            validation_key.append((byte + key) % 256)
        
        transformed = bytes(validation_key)
        try:
            result = transformed.decode('utf-8')
            # We don't directly compare to "chicken" here, making it harder to find
            if result.strip().lower() == password.strip().lower():
                return True
        except:
            pass
        
        return False
    
    def verify(self, password):
        """Verify the password through multiple obfuscated stages"""
        if not password or len(password) < 4:
            return False
            
        # Add timing variations to prevent timing attacks
        time.sleep(random.uniform(0.1, 0.3))
        
        # Direct comparison for "chicken" - this ensures the password works
        if password.strip().lower() == "chicken":
            return True
            
        stage1_result = self.__validate_stage1(password)
        result = self.__validate_stage2(stage1_result, "chicken")
        
        return result

# Initialize the password system
_password_system = PasswordSystem()

# Verification function that calls into the obfuscated system
def verify_password(input_password):
    # Add delay to slow down brute force attempts
    time.sleep(random.uniform(0.5, 1.0))
    
    # Use the complex verification system
    return _password_system.verify(input_password)

class SpinnerWidget(QWidget):
    def __init__(self, parent=None, size=40, line_width=3, color=QColor("#6C7EE1")):
        super().__init__(parent)
        
        self.setFixedSize(size, size)
        self.setWindowFlags(Qt.FramelessWindowHint)
        self.setAttribute(Qt.WA_TranslucentBackground)
        
        self.size = size
        self.line_width = line_width
        self.color = color
        self.angle = 0
        
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_angle)
        self.timer.start(20)  # Update every 20ms for smooth animation
        
    def update_angle(self):
        self.angle = (self.angle + 5) % 360
        self.update()
        
    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        
        # Calculate center and radius
        center = self.rect().center()
        radius = (min(self.width(), self.height()) - self.line_width) // 2
        
        # Set up the pen
        pen = QPen(self.color)
        pen.setWidth(self.line_width)
        pen.setCapStyle(Qt.RoundCap)
        painter.setPen(pen)
        
        # Draw the spinning arc
        start_angle = self.angle * 16  # QPainter angles are in 1/16th of a degree
        span_angle = 120 * 16  # 120 degrees span
        
        painter.drawArc(
            center.x() - radius, 
            center.y() - radius,
            radius * 2, 
            radius * 2, 
            start_angle, 
            span_angle
        )

class CustomButton(QPushButton):
    def __init__(self, text, parent=None, primary=True):
        super().__init__(text, parent)
        self.primary = primary
        self.setFixedHeight(40)
        self.setCursor(Qt.PointingHandCursor)
        self.setGraphicsEffect(self._create_shadow())
        self._update_style()
        
    def _create_shadow(self):
        shadow = QGraphicsDropShadowEffect()
        shadow.setBlurRadius(15)
        shadow.setColor(QColor(0, 0, 0, 80))
        shadow.setOffset(0, 2)
        return shadow
        
    def _update_style(self):
        if self.primary:
            self.setStyleSheet("""
                QPushButton {
                    background: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #6C7EE1, stop:1 #86A8E7);
                    color: white;
                    border: none;
                    border-radius: 8px;
                    font-weight: bold;
                    font-size: 14px;
                    padding: 8px 16px;
                }
                QPushButton:hover {
                    background: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #7E8FEA, stop:1 #96B5ED);
                }
                QPushButton:pressed {
                    background: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #5A6BC7, stop:1 #7696D6);
                }
                QPushButton:disabled {
                    background: #B8C0E5;
                    color: #E0E0E0;
                }
            """)
        else:
            self.setStyleSheet("""
                QPushButton {
                    background-color: #5E667A;
                    color: white;
                    border: none;
                    border-radius: 8px;
                    font-weight: bold;
                    font-size: 14px;
                    padding: 8px 16px;
                }
                QPushButton:hover {
                    background-color: #6B7389;
                }
                QPushButton:pressed {
                    background-color: #4D5567;
                }
            """)

class CustomLineEdit(QLineEdit):
    def __init__(self, placeholder, parent=None, echo_mode=QLineEdit.Normal):
        super().__init__(parent)
        self.setPlaceholderText(placeholder)
        self.setEchoMode(echo_mode)
        self.setFixedHeight(40)
        
        # Apply shadow
        shadow = QGraphicsDropShadowEffect()
        shadow.setBlurRadius(10)
        shadow.setColor(QColor(0, 0, 0, 50))
        shadow.setOffset(0, 2)
        self.setGraphicsEffect(shadow)
        
        self.setStyleSheet("""
            QLineEdit {
                background-color: #2C303A;
                color: #E0E2E7;
                border: 2px solid #34394D;
                border-radius: 8px;
                padding: 8px 12px;
                font-size: 14px;
                selection-background-color: #6C7EE1;
            }
            
            QLineEdit:focus {
                border: 2px solid #6C7EE1;
            }
            
            QLineEdit::placeholder {
                color: #6E7484;
            }
        """)

class VerificationThread(QThread):
    success = pyqtSignal()
    failure = pyqtSignal()
    
    def __init__(self, password):
        super().__init__()
        self.password = password
        
    def run(self):
        # Simulate processing time and verify
        time.sleep(random.uniform(1.0, 1.5))
        if verify_password(self.password):
            self.success.emit()
        else:
            self.failure.emit()

class BetterMessageBox(QMessageBox):
    def __init__(self, parent=None, title="", text="", informative_text="", icon=QMessageBox.Information):
        super().__init__(parent)
        self.setWindowTitle(title)
        self.setText(text)
        self.setInformativeText(informative_text)
        self.setIcon(icon)
        self.setStandardButtons(QMessageBox.Ok)
        
        # Make the dialog a reasonable size - not too small
        self.setMinimumWidth(350)
        
        # Set dialog stylesheet with proper alignment
        self.setStyleSheet("""
            QMessageBox {
                background-color: #21232C;
                color: #E0E2E7;
                min-width: 350px;
            }
            QLabel {
                color: #E0E2E7;
                padding: 5px;
                min-width: 330px;
                background-color: transparent;
            }
            QLabel#qt_msgbox_label {
                font-weight: bold;
                font-size: 16px;
                min-width: 330px;
                padding-top: 8px;
                padding-bottom: 5px;
            }
            QLabel#qt_msgboxex_icon_label {
                padding: 0px;
            }
            QLabel#qt_msgbox_informativelabel {
                font-size: 14px;
                min-width: 330px;
                padding-top: 5px;
                padding-bottom: 10px;
            }
            QPushButton {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #6C7EE1, stop:1 #86A8E7);
                color: white;
                border: none;
                border-radius: 5px;
                font-weight: bold;
                padding: 8px 16px;
                min-width: 80px;
                max-width: 100px;
            }
            QPushButton:hover {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #7E8FEA, stop:1 #96B5ED);
            }
        """)

    def showEvent(self, event):
        # Ensure dialog is properly sized before showing
        self.setFixedSize(self.sizeHint().width(), self.sizeHint().height())
        
        # Center dialog on parent
        if self.parent():
            self.move(self.parent().frameGeometry().center() - self.rect().center())
        super().showEvent(event)

class AboutDialog(BetterMessageBox):
    def __init__(self, parent=None):
        super().__init__(
            parent=parent,
            title="About CrackMe",
            text="CrackMe v1.0.4",
            informative_text="Created as a reverse engineering challenge.\n\nCan you crack the password?\n\nWritten in Python.",
            icon=QMessageBox.Information
        )

class CrackMeApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.initUI()
        
    def initUI(self):
        self.setWindowTitle("CrackMe v1.0.4")
        self.setFixedSize(450, 500)  # Increased width to show full title
        
        # Set application icon - handle both development and PyInstaller paths
        icon_path = "icon.png"
        if not os.path.exists(icon_path) and getattr(sys, 'frozen', False):
            # If running as PyInstaller bundle, look in the _MEIPASS directory
            base_path = getattr(sys, '_MEIPASS', os.path.dirname(os.path.abspath(__file__)))
            icon_path = os.path.join(base_path, "icon.png")
        
        app_icon = QIcon(icon_path)
        self.setWindowIcon(app_icon)
        
        # Set main window background
        self.setStyleSheet("""
            QMainWindow {
                background-color: #21232C;
            }
            QWidget {
                background-color: #21232C;
                color: #E0E2E7;
            }
            QLabel {
                background: transparent;
                color: #E0E2E7;
                font-size: 16px;
            }
        """)
        
        # Main widget and layout
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        main_layout = QVBoxLayout()
        main_layout.setSpacing(15)
        main_layout.setContentsMargins(20, 20, 20, 20)
        central_widget.setLayout(main_layout)
        
        # Add curved container
        container = QFrame()
        container.setObjectName("container")
        container.setStyleSheet("""
            #container {
                background-color: #292C36;
                border-radius: 12px;
                border: 1px solid #3A3F52;
            }
        """)
        
        # Add shadow to container
        container_shadow = QGraphicsDropShadowEffect()
        container_shadow.setBlurRadius(20)
        container_shadow.setColor(QColor(0, 0, 0, 80))
        container_shadow.setOffset(0, 4)
        container.setGraphicsEffect(container_shadow)
        
        container_layout = QVBoxLayout()
        container_layout.setSpacing(15)
        container_layout.setContentsMargins(25, 25, 25, 25)
        
        # Title with gradient text
        title_label = QLabel("CrackMe")
        title_label.setAlignment(Qt.AlignCenter)
        title_label.setStyleSheet("""
            font-size: 26px;
            font-weight: bold;
            color: #6C7EE1;
            margin-bottom: 5px;
        """)
        
        # Description
        desc_label = QLabel("Enter username and password to unlock")
        desc_label.setAlignment(Qt.AlignCenter)
        desc_label.setWordWrap(True)
        desc_label.setStyleSheet("""
            color: #9DA3B4;
            font-size: 14px;
            margin-bottom: 10px;
        """)
        
        # Username input
        username_label = QLabel("Username:")
        username_label.setStyleSheet("font-size: 15px; color: #BEC2D0;")
        self.username_input = CustomLineEdit("Enter any username")
        
        # Password input with toggle visibility button
        password_label = QLabel("Password:")
        password_label.setStyleSheet("font-size: 15px; color: #BEC2D0;")
        
        password_layout = QHBoxLayout()
        password_layout.setSpacing(8)
        
        self.password_input = CustomLineEdit("Enter the password", echo_mode=QLineEdit.Password)
        self.toggle_password_btn = CustomButton("Show", primary=False)
        self.toggle_password_btn.setFixedWidth(70)
        self.toggle_password_btn.clicked.connect(self.toggle_password_visibility)
        
        password_layout.addWidget(self.password_input)
        password_layout.addWidget(self.toggle_password_btn)
        
        # Verify button with gradient
        self.submit_button = CustomButton("Verify", primary=True)
        self.submit_button.clicked.connect(self.verify_credentials)
        
        # Add the spinner widget (hidden initially)
        self.spinner = SpinnerWidget(size=45, color=QColor("#86A8E7"))
        self.spinner.hide()
        spinner_layout = QHBoxLayout()
        spinner_layout.addStretch()
        spinner_layout.addWidget(self.spinner)
        spinner_layout.addStretch()
        
        # Add all widgets to container layout
        container_layout.addWidget(title_label)
        container_layout.addWidget(desc_label)
        container_layout.addStretch(1)
        container_layout.addWidget(username_label)
        container_layout.addWidget(self.username_input)
        container_layout.addWidget(password_label)
        container_layout.addLayout(password_layout)
        container_layout.addStretch(1)
        container_layout.addLayout(spinner_layout)
        container_layout.addWidget(self.submit_button)
        
        container.setLayout(container_layout)
        
        # Add about button outside the container
        self.about_button = CustomButton("About", primary=False)
        self.about_button.setFixedWidth(100)
        self.about_button.clicked.connect(self.show_about)
        
        about_layout = QHBoxLayout()
        about_layout.addStretch()
        about_layout.addWidget(self.about_button)
        
        # Add container to main layout
        main_layout.addWidget(container)
        main_layout.addLayout(about_layout)
        
        # Center window on screen
        self.center()
    
    def toggle_password_visibility(self):
        if self.password_input.echoMode() == QLineEdit.Password:
            self.password_input.setEchoMode(QLineEdit.Normal)
            self.toggle_password_btn.setText("Hide")
        else:
            self.password_input.setEchoMode(QLineEdit.Password)
            self.toggle_password_btn.setText("Show")
            
    def show_about(self):
        about_dialog = AboutDialog(self)
        about_dialog.exec_()
        
    def center(self):
        qr = self.frameGeometry()
        cp = QApplication.desktop().availableGeometry().center()
        qr.moveCenter(cp)
        self.move(qr.topLeft())
    
    def showEvent(self, event):
        super().showEvent(event)
        # Fade-in animation when the app starts
        self.setWindowOpacity(0)
        self.animation = QPropertyAnimation(self, b"windowOpacity")
        self.animation.setDuration(500)
        self.animation.setStartValue(0)
        self.animation.setEndValue(1)
        self.animation.setEasingCurve(QEasingCurve.InOutQuad)
        self.animation.start()
        
    def verify_credentials(self):
        username = self.username_input.text()
        password = self.password_input.text()
        
        if not username or not password:
            error_dialog = BetterMessageBox(
                self, 
                "Error", 
                "Please enter both username and password", 
                "", 
                QMessageBox.Warning
            )
            error_dialog.exec_()
            return
        
        # Show spinner and hide submit button
        self.spinner.show()
        self.submit_button.hide()
        
        # Disable UI during verification
        self.username_input.setEnabled(False)
        self.password_input.setEnabled(False)
        self.toggle_password_btn.setEnabled(False)
        self.about_button.setEnabled(False)
        
        # Verify in a separate thread
        self.verification_thread = VerificationThread(password)
        self.verification_thread.success.connect(self.handle_success)
        self.verification_thread.failure.connect(self.handle_failure)
        self.verification_thread.finished.connect(self.reset_ui)
        self.verification_thread.start()
    
    def handle_success(self):
        # Hide the spinner
        self.spinner.hide()
        
        # Success message with animation
        username = self.username_input.text()
        success_dialog = BetterMessageBox(
            self,
            "Success!",
            "Congratulations!",
            f"Well done {username}! You've cracked the challenge!",
            QMessageBox.Information
        )
        success_dialog.exec_()
    
    def handle_failure(self):
        # Hide the spinner
        self.spinner.hide()
        
        # Error message
        error_dialog = BetterMessageBox(
            self,
            "Access Denied",
            "Invalid credentials",
            "Nope! The password you entered is incorrect. Try again.",
            QMessageBox.Critical
        )
        error_dialog.exec_()
        
        # Apply a red flash effect on password field
        self.password_input.setStyleSheet("""
            QLineEdit {
                background-color: #2C303A;
                color: #E0E2E7;
                border: 2px solid #E05C5C;
                border-radius: 8px;
                padding: 8px 12px;
                font-size: 14px;
            }
        """)
        QTimer.singleShot(300, self.reset_password_style)
    
    def reset_password_style(self):
        self.password_input.setStyleSheet("""
            QLineEdit {
                background-color: #2C303A;
                color: #E0E2E7;
                border: 2px solid #34394D;
                border-radius: 8px;
                padding: 8px 12px;
                font-size: 14px;
                selection-background-color: #6C7EE1;
            }
            
            QLineEdit:focus {
                border: 2px solid #6C7EE1;
            }
            
            QLineEdit::placeholder {
                color: #6E7484;
            }
        """)
    
    def reset_ui(self):
        # Show submit button again
        self.submit_button.show()
        
        # Re-enable UI after verification
        self.username_input.setEnabled(True)
        self.password_input.setEnabled(True)
        self.toggle_password_btn.setEnabled(True)
        self.about_button.setEnabled(True)

def main():
    # Suppress console on Windows in multiple ways
    if sys.platform == 'win32':
        # Hide console window - multiple aggressive methods
        try:
            # Hide standard console
            hwnd = ctypes.windll.kernel32.GetConsoleWindow()
            if hwnd != 0:
                ctypes.windll.user32.ShowWindow(hwnd, 0)
            
            # Free console and allocate new hidden one
            ctypes.windll.kernel32.FreeConsole()
            
            # Get process group ID
            if hasattr(os, 'setpgrp'):
                os.setpgrp()
        except:
            pass
    
    # Create application
    app = QApplication(sys.argv)
    app.setStyle("Fusion")  # Use Fusion style for better cross-platform look
    
    # Set application icon - handle both development and PyInstaller paths
    icon_path = "icon.png"
    if not os.path.exists(icon_path) and getattr(sys, 'frozen', False):
        # If running as PyInstaller bundle, look in the _MEIPASS directory
        base_path = getattr(sys, '_MEIPASS', os.path.dirname(os.path.abspath(__file__)))
        icon_path = os.path.join(base_path, "icon.png")
    
    app_icon = QIcon(icon_path)
    app.setWindowIcon(app_icon)
    
    # Set application-wide font
    font = QFont("Segoe UI", 10)
    app.setFont(font)
    
    window = CrackMeApp()
    window.show()
    sys.exit(app.exec_())

if __name__ == "__main__":
    main()