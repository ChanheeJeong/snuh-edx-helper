from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, 
                             QLabel, QGroupBox, QPushButton, QSizePolicy)
from PyQt6.QtCore import Qt
from models.emg_data import UE_ORDER, LE_ORDER

class EMG_UI(QWidget):
    def setup_ui(self):
        main_layout = QHBoxLayout(self)

        # ==================== 좌측 패널 (입력 및 매크로 구역) ====================
        left_panel = QWidget()
        left_layout = QVBoxLayout(left_panel)
        left_layout.setContentsMargins(10, 10, 20, 10)
        left_layout.setSpacing(15)

        # 공통 토글 버튼 스타일
        self.toggle_btn_style = """
            QPushButton {
                background-color: #ecf0f1; border: 1px solid #bdc3c7; border-radius: 4px; padding: 10px; font-weight: bold; font-size: 14px; color: #2c3e50; text-align: left; padding-left: 15px;
            }
            QPushButton:checked {
                background-color: #f1c40f; color: black; border: 1px solid #d4ac0d;
            }
            QPushButton:hover {
                background-color: #d5dbdb;
            }
        """

        # --- 상지 (U/E) 그룹 ---
        group_ue = QGroupBox("Upper Extremity (U/E) Spontaneous Activity")
        group_ue.setStyleSheet("font-weight: bold; font-size: 14px;")
        ue_layout = QVBoxLayout(group_ue)
        
        ue_header_layout = QHBoxLayout()
        lbl_ue_macro = QLabel("매크로 단축키: Ctrl+Shift+U")
        lbl_ue_macro.setStyleSheet("color: #e74c3c; font-weight: bold;")
        self.btn_ue_default = QPushButton("Default 선택")
        self.btn_ue_default.setStyleSheet("background-color: #3498db; color: white; font-weight: bold; padding: 5px; border-radius: 4px;")
        ue_header_layout.addWidget(lbl_ue_macro)
        ue_header_layout.addStretch()
        ue_header_layout.addWidget(self.btn_ue_default)
        ue_layout.addLayout(ue_header_layout)

        self.ue_btns = {}
        for muscle in UE_ORDER:
            btn = QPushButton(muscle)
            btn.setCheckable(True)
            btn.setStyleSheet(self.toggle_btn_style)
            self.ue_btns[muscle] = btn
            ue_layout.addWidget(btn)
            
        left_layout.addWidget(group_ue)

        # --- 하지 (L/E) 그룹 ---
        group_le = QGroupBox("Lower Extremity (L/E) Spontaneous Activity")
        group_le.setStyleSheet("font-weight: bold; font-size: 14px;")
        le_layout = QVBoxLayout(group_le)
        
        le_header_layout = QHBoxLayout()
        lbl_le_macro = QLabel("매크로 단축키: Ctrl+Shift+L")
        lbl_le_macro.setStyleSheet("color: #e74c3c; font-weight: bold;")
        self.btn_le_default = QPushButton("Default 선택")
        self.btn_le_default.setStyleSheet("background-color: #3498db; color: white; font-weight: bold; padding: 5px; border-radius: 4px;")
        le_header_layout.addWidget(lbl_le_macro)
        le_header_layout.addStretch()
        le_header_layout.addWidget(self.btn_le_default)
        le_layout.addLayout(le_header_layout)

        self.le_btns = {}
        for muscle in LE_ORDER:
            btn = QPushButton(muscle)
            btn.setCheckable(True)
            btn.setStyleSheet(self.toggle_btn_style)
            self.le_btns[muscle] = btn
            le_layout.addWidget(btn)
            
        left_layout.addWidget(group_le)
        
        # --- 리셋 및 상태 라벨 ---
        self.btn_reset = QPushButton("모두 초기화 (RESET)")
        self.btn_reset.setFixedHeight(45)
        self.btn_reset.setStyleSheet("font-size: 14px; font-weight: bold; background-color: #e74c3c; color: white; border-radius: 4px;")
        left_layout.addWidget(self.btn_reset)
        
        self.lbl_status = QLabel("대기 중... (EMR에 커서를 두고 단축키를 누르세요)")
        self.lbl_status.setStyleSheet("color: #7f8c8d; font-weight: bold; font-size: 13px;")
        left_layout.addWidget(self.lbl_status)
        
        left_layout.addStretch()

        # ==================== 우측 패널 (빈 공간, 추후 확장용) ====================
        right_panel = QWidget()
        right_layout = QVBoxLayout(right_panel)
        
        lbl_placeholder = QLabel("EMG 판독문 및 추가 기능\n(To be developed...)")
        lbl_placeholder.setAlignment(Qt.AlignmentFlag.AlignCenter)
        lbl_placeholder.setStyleSheet("font-size: 20px; color: #bdc3c7; font-weight: bold;")
        right_layout.addWidget(lbl_placeholder)

        main_layout.addWidget(left_panel, 1)
        main_layout.addWidget(right_panel, 1)