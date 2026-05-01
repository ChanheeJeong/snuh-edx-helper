from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, 
                             QLabel, QGroupBox, QPushButton, QTextEdit,
                             QCheckBox, QRadioButton, QButtonGroup, QSizePolicy)
from PyQt6.QtCore import Qt

class JOLLY_UI(QWidget):
    def setup_ui(self):
        main_layout = QHBoxLayout(self)

        # [좌측 패널]
        left_panel = QWidget()
        left_layout = QVBoxLayout(left_panel)

        self.btn_reset = QPushButton("모두 초기화 (RESET)")
        self.btn_reset.setFixedHeight(50)
        self.btn_reset.setStyleSheet("font-size: 14px; font-weight: bold; background-color: #e74c3c; color: white; border-radius: 4px;")
        left_layout.addWidget(self.btn_reset)

        # 1. Side Selection
        side_group = QGroupBox("검사 방향 (Side)")
        side_layout = QHBoxLayout()
        side_layout.setSpacing(10)
        
        self.btn_side_left = QPushButton("Left")
        self.btn_side_right = QPushButton("Right")
        self.btn_side_left.setFixedHeight(45)
        self.btn_side_right.setFixedHeight(45)
        self.btn_side_left.setCheckable(True)
        self.btn_side_right.setCheckable(True)
        
        self.side_btn_group = QButtonGroup()
        self.side_btn_group.addButton(self.btn_side_left)
        self.side_btn_group.addButton(self.btn_side_right)
        
        side_layout.addWidget(self.btn_side_left)
        side_layout.addWidget(self.btn_side_right)
        side_group.setLayout(side_layout)
        left_layout.addWidget(side_group)

        # 폰트 스타일 정의
        giant_font = "font-size: 24px; font-weight: 900;"
        base_font = "font-size: 15px; font-weight: bold;"

        # 2. Low Frequency
        low_group = QGroupBox("Low Frequency Stimulation")
        low_main_layout = QHBoxLayout()
        
        low_left_widget = QWidget()
        low_left_layout = QVBoxLayout(low_left_widget)
        low_left_layout.setContentsMargins(0, 0, 0, 0)
        low_left_layout.setSpacing(15) # 간격 확대
        
        self.rdo_low_normal = QRadioButton(" Normal")
        self.rdo_low_abnormal = QRadioButton(" Abnormal")
        self.rdo_low_normal.setChecked(True)
        self.rdo_low_normal.setStyleSheet(f"{giant_font} color: #27ae60;")
        self.rdo_low_abnormal.setStyleSheet(f"{giant_font} color: #c0392b;")
        
        self.low_btn_group = QButtonGroup()
        self.low_btn_group.addButton(self.rdo_low_normal)
        self.low_btn_group.addButton(self.rdo_low_abnormal)
        low_left_layout.addWidget(self.rdo_low_normal)
        low_left_layout.addWidget(self.rdo_low_abnormal)

        self.chk_low_oculi = QCheckBox("Orbicularis oculi (Oculi)")
        self.chk_low_adq = QCheckBox("Abductor digiti quinti (ADQ)")
        self.chk_low_fcu = QCheckBox("Flexor carpi ulnaris (FCU)")
        self.chk_low_trap = QCheckBox("Trapezius")
        
        # 공간 유지 기능
        sp = self.chk_low_trap.sizePolicy()
        sp.setRetainSizeWhenHidden(True)
        self.chk_low_trap.setSizePolicy(sp)
        self.chk_low_trap.setVisible(False)
        
        low_chk_layout = QVBoxLayout()
        low_chk_layout.setContentsMargins(40, 0, 0, 0) # 들여쓰기 더 깊게
        low_chk_layout.setSpacing(10)
        for chk in [self.chk_low_oculi, self.chk_low_adq, self.chk_low_fcu, self.chk_low_trap]:
            chk.setStyleSheet(base_font)
            chk.setEnabled(False)
            low_chk_layout.addWidget(chk)
        low_left_layout.addLayout(low_chk_layout)
        
        low_right_widget = QWidget()
        low_right_layout = QVBoxLayout(low_right_widget)
        low_right_layout.setContentsMargins(0, 0, 0, 0)
        
        # [핵심 수정] 배경색 제거, 한 줄 배치
        self.chk_add_trapezius = QCheckBox("Trapezius 추가")
        self.chk_add_trapezius.setStyleSheet("font-weight: bold; font-size: 18px; color: #2980b9; padding: 5px;")
        low_right_layout.addWidget(self.chk_add_trapezius)
        low_right_layout.addStretch()
        
        low_main_layout.addWidget(low_left_widget, 7)
        low_main_layout.addWidget(low_right_widget, 3)
        low_group.setLayout(low_main_layout)
        left_layout.addWidget(low_group)

        # 3. High Frequency
        high_group = QGroupBox("High Frequency Stimulation")
        high_layout = QVBoxLayout()
        high_layout.setSpacing(15)
        
        self.rdo_high_normal = QRadioButton(" Normal")
        self.rdo_high_abnormal = QRadioButton(" Abnormal")
        self.rdo_high_normal.setChecked(True)
        self.rdo_high_normal.setStyleSheet(f"{giant_font} color: #27ae60;")
        self.rdo_high_abnormal.setStyleSheet(f"{giant_font} color: #c0392b;")
        
        self.high_btn_group = QButtonGroup()
        self.high_btn_group.addButton(self.rdo_high_normal)
        self.high_btn_group.addButton(self.rdo_high_abnormal)
        high_layout.addWidget(self.rdo_high_normal)
        
        # Abnormal 세부 옵션
        high_abnormal_layout = QHBoxLayout()
        high_abnormal_layout.addWidget(self.rdo_high_abnormal)
        
        self.rdo_high_dec = QRadioButton("Decremental")
        self.rdo_high_inc = QRadioButton("Incremental")
        self.rdo_high_dec.setChecked(True)
        self.rdo_high_dec.setStyleSheet("font-size: 14px; font-weight: bold; color: #8e44ad; margin-left: 20px;")
        self.rdo_high_inc.setStyleSheet("font-size: 14px; font-weight: bold; color: #8e44ad;")
        self.rdo_high_dec.setEnabled(False)
        self.rdo_high_inc.setEnabled(False)
        
        self.high_type_group = QButtonGroup()
        self.high_type_group.addButton(self.rdo_high_dec)
        self.high_type_group.addButton(self.rdo_high_inc)
        
        high_abnormal_layout.addWidget(self.rdo_high_dec)
        high_abnormal_layout.addWidget(self.rdo_high_inc)
        high_abnormal_layout.addStretch()
        high_layout.addLayout(high_abnormal_layout)

        self.chk_high_fcu = QCheckBox("Flexor carpi ulnaris (FCU)")
        self.chk_high_adq = QCheckBox("Abductor digiti quinti (ADQ)")
        
        high_chk_layout = QVBoxLayout()
        high_chk_layout.setContentsMargins(40, 0, 0, 0)
        high_chk_layout.setSpacing(10)
        for chk in [self.chk_high_fcu, self.chk_high_adq]:
            chk.setStyleSheet(base_font)
            chk.setEnabled(False)
            high_chk_layout.addWidget(chk)
        high_layout.addLayout(high_chk_layout)
        high_group.setLayout(high_layout)
        left_layout.addWidget(high_group)
        
        left_layout.addStretch()

        # [우측 패널]
        right_panel = QWidget()
        right_layout = QVBoxLayout(right_panel)
        self.group_findings = QGroupBox("Findings")
        f_lay = QVBoxLayout(); self.txt_findings = QTextEdit()
        self.txt_findings.setStyleSheet("background-color: #ffffff; border-radius: 4px; border: 1px solid #bdc3c7; padding: 10px; font-size: 13px;")
        f_lay.addWidget(self.txt_findings); self.group_findings.setLayout(f_lay)

        self.group_conclusions = QGroupBox("Conclusion")
        c_lay = QVBoxLayout(); self.txt_conclusions = QTextEdit()
        self.txt_conclusions.setStyleSheet("background-color: #ffffff; border-radius: 4px; border: 1px solid #bdc3c7; padding: 10px; font-size: 13px;")
        c_lay.addWidget(self.txt_conclusions); self.group_conclusions.setLayout(c_lay)

        right_layout.addWidget(self.group_findings, 2)
        right_layout.addWidget(self.group_conclusions, 1)

        main_layout.addWidget(left_panel, 55)
        main_layout.addWidget(right_panel, 45)