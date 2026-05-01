from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, 
                             QLabel, QGroupBox, QPushButton, QTextEdit, QTableWidget, QHeaderView)
from PyQt6.QtCore import Qt

class PFT_UI(QWidget):
    def setup_ui(self):
        main_layout = QHBoxLayout(self)

        # ==================== 좌측 패널 ====================
        left_panel = QWidget()
        left_layout = QVBoxLayout(left_panel)
        left_layout.setContentsMargins(10, 10, 20, 10)

        # [수정] 0. 초기화 버튼 (가장 위로 이동)
        self.btn_reset = QPushButton("모두 초기화 (RESET)")
        self.btn_reset.setFixedHeight(50)
        self.btn_reset.setStyleSheet("font-size: 14px; font-weight: bold; background-color: #e74c3c; color: white; border-radius: 4px;")
        left_layout.addWidget(self.btn_reset)

        # 1. 캡처 버튼 그룹
        btn_style = "font-size: 13px; font-weight: bold; color: white; border-radius: 4px; padding: 10px;"
        
        self.btn_cap_info = QPushButton("1. Capture Patient Info")
        self.btn_cap_info.setStyleSheet(f"background-color: #3498db; {btn_style}")
        left_layout.addWidget(self.btn_cap_info)

        self.lbl_info = QLabel("환자 정보: 대기 중")
        self.lbl_info.setStyleSheet("color: #7f8c8d; font-weight: bold; margin-bottom: 10px; line-height: 1.5;")
        left_layout.addWidget(self.lbl_info)

        cap_data_layout = QHBoxLayout()
        self.btn_cap_mip = QPushButton("2. Capture MIP & MEP")
        self.btn_cap_mip.setStyleSheet(f"background-color: #2ecc71; {btn_style}")
        self.btn_cap_snip = QPushButton("3. Capture SNIP & PEF")
        self.btn_cap_snip.setStyleSheet(f"background-color: #2ecc71; {btn_style}")
        cap_data_layout.addWidget(self.btn_cap_mip)
        cap_data_layout.addWidget(self.btn_cap_snip)
        left_layout.addLayout(cap_data_layout)

        # 2. 결과 테이블
        self.table = QTableWidget(5, 4)
        self.table.setHorizontalHeaderLabels(["MIP", "MEP", "SNIP", "PEF"])
        self.table.setVerticalHeaderLabels(["Trial 1", "Trial 2", "Trial 3", "Normal Range", "Result"])
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.table.setStyleSheet("background-color: white; border: 1px solid #bdc3c7;")
        self.table.setFixedHeight(180)
        left_layout.addWidget(self.table)

        # 3. Spirometry
        self.btn_cap_spiro = QPushButton("4. Capture FVC/FEV1 %Pred")
        self.btn_cap_spiro.setStyleSheet(f"background-color: #9b59b6; {btn_style}")
        left_layout.addWidget(self.btn_cap_spiro)

        self.lbl_spiro = QLabel("Spirometry: 대기 중")
        self.lbl_spiro.setStyleSheet("color: #7f8c8d; font-weight: bold;")
        left_layout.addWidget(self.lbl_spiro)

        self.lbl_status = QLabel("Ready.")
        self.lbl_status.setStyleSheet("color: #e67e22; font-weight: bold; margin-top: 10px;")
        left_layout.addWidget(self.lbl_status)
        
        left_layout.addStretch()

        # ==================== 우측 패널 ====================
        right_panel = QWidget()
        right_layout = QVBoxLayout(right_panel)
        right_layout.setContentsMargins(0, 10, 10, 10)

        # [수정] 안내 텍스트 단순화 (단축키는 main.py 공통 안내 사용)
        group_conclusion = QGroupBox("Conclusion")
        group_conclusion.setStyleSheet("font-weight: bold; font-size: 14px;")
        conclusion_layout = QVBoxLayout(group_conclusion)
        
        self.txt_conclusion = QTextEdit()
        self.txt_conclusion.setStyleSheet("background-color: #ecf0f1; border-radius: 4px; border: 1px solid #bdc3c7; padding: 15px; font-size: 14px; color: #2c3e50; font-weight: normal;")
        conclusion_layout.addWidget(self.txt_conclusion)
        
        right_layout.addWidget(group_conclusion)

        main_layout.addWidget(left_panel, 1)
        main_layout.addWidget(right_panel, 1)