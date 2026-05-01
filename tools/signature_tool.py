import keyboard
import pyperclip
import time
from PyQt6.QtWidgets import QWidget, QHBoxLayout, QLabel, QLineEdit
from PyQt6.QtCore import Qt

class SignatureTool(QWidget):
    def __init__(self, parent=None, resident_name="R3 정찬희"):
        super().__init__(parent)
        self.resident_name = resident_name
        self.setup_ui()
        keyboard.add_hotkey('ctrl+q', self.macro_type_signature)

    def setup_ui(self):
        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        
        lbl = QLabel("서명 (Ctrl+Q):")
        lbl.setStyleSheet("font-weight: bold; color: #2c3e50;")
        
        self.edit_sig = QLineEdit()
        self.edit_sig.setFixedWidth(160)
        # [수정] font-weight: bold; 속성 제거
        self.edit_sig.setStyleSheet("background-color: #fdfefe; border: 1px solid #bdc3c7; border-radius: 4px; padding: 2px;")
        
        layout.addWidget(lbl)
        layout.addWidget(self.edit_sig)

    def update_signature(self, tab_name):
        """탭 이름에 따라 서명을 자동으로 변경합니다."""
        
        if tab_name in ["ANSFT", "QSART"]:
            sig_text = f"{self.resident_name} / Pf. 최석진"
        else:
            sig_text = f"{self.resident_name} / Pf. 성정준"
            
        self.edit_sig.setText(sig_text)

    def get_signature(self):
        return self.edit_sig.text()

    def macro_type_signature(self):
        signature = self.get_signature()
        if signature:
            pyperclip.copy(signature)
            time.sleep(0.2)
            keyboard.send('ctrl+v')