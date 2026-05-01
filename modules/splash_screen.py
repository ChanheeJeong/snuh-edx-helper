import os
import json
from PyQt6.QtWidgets import (QDialog, QVBoxLayout, QLabel, QComboBox, 
                             QLineEdit, QPushButton, QMessageBox)
from PyQt6.QtCore import Qt

CONFIG_FILE = "user_config.json"

class SplashScreen(QDialog):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("SNUH EDX Helper - Welcome")
        self.setFixedSize(450, 300)
        
        self.setWindowFlags(self.windowFlags() & ~Qt.WindowType.WindowContextHelpButtonHint)
        
        self.selected_name = "R3 정찬희" # 기본값
        self.saved_users = self.load_users()
        self.setup_ui()

    def load_users(self):
        if os.path.exists(CONFIG_FILE):
            try:
                with open(CONFIG_FILE, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    return data.get("users", ["R3 정찬희"])
            except Exception:
                pass
        return ["R3 정찬희"]

    def save_user(self, name):
        if not name: return
        
        # 중복 제거 및 가장 최근 이름을 최상단으로 올리기
        if name in self.saved_users:
            self.saved_users.remove(name)
        self.saved_users.insert(0, name)
        
        # 최대 10명까지만 기억하도록 제한
        self.saved_users = self.saved_users[:10]
            
        with open(CONFIG_FILE, 'w', encoding='utf-8') as f:
            json.dump({"users": self.saved_users}, f, ensure_ascii=False, indent=4)

    def setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(40, 40, 40, 40)
        layout.setSpacing(20)

        # 타이틀
        lbl_title = QLabel("SNUH EDX Helper")
        lbl_title.setStyleSheet("font-size: 26px; font-weight: 900; color: #2c3e50;")
        lbl_title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(lbl_title)

        lbl_desc = QLabel("판독자(Resident) 이름을 선택하거나 입력하세요.")
        lbl_desc.setStyleSheet("font-size: 13px; color: #7f8c8d;")
        lbl_desc.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(lbl_desc)

        # 사용자 선택 콤보박스
        self.combo_users = QComboBox()
        self.combo_users.addItems(self.saved_users)
        self.combo_users.addItem("+ 새 판독자 입력...")
        self.combo_users.setFixedHeight(40) # 콤보박스도 넉넉하게 키움
        self.combo_users.setStyleSheet("font-size: 15px; padding: 5px; font-weight: bold;")
        self.combo_users.currentTextChanged.connect(self.on_combo_changed)
        layout.addWidget(self.combo_users)

        # [수정] 새 사용자 입력창 (한글 잘림 방지를 위해 높이 명시적 지정)
        self.input_new_user = QLineEdit()
        self.input_new_user.setPlaceholderText("예: R2 홍길동")
        self.input_new_user.setFixedHeight(40) 
        self.input_new_user.setStyleSheet("font-size: 15px; padding: 5px;")
        self.input_new_user.setVisible(False)
        layout.addWidget(self.input_new_user)

        layout.addStretch()

        # START 버튼 (크고 중앙에)
        self.btn_start = QPushButton("START")
        self.btn_start.setFixedHeight(60)
        self.btn_start.setStyleSheet("""
            QPushButton {
                background-color: #3498db; 
                color: white; 
                font-size: 22px; 
                font-weight: bold; 
                border-radius: 8px;
            }
            QPushButton:hover {
                background-color: #2980b9;
            }
        """)
        self.btn_start.clicked.connect(self.on_start_clicked)
        layout.addWidget(self.btn_start)

    def on_combo_changed(self, text):
        if text == "+ 새 판독자 입력...":
            self.input_new_user.setVisible(True)
            self.input_new_user.setFocus()
        else:
            self.input_new_user.setVisible(False)

    def on_start_clicked(self):
        if self.combo_users.currentText() == "+ 새 판독자 입력...":
            name = self.input_new_user.text().strip()
            if not name:
                QMessageBox.warning(self, "입력 오류", "새 판독자 이름을 입력해주세요!")
                self.input_new_user.setFocus()
                return
        else:
            name = self.combo_users.currentText()
        
        self.selected_name = name
        self.save_user(name)
        self.accept()