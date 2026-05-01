from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, 
                             QLabel, QGroupBox, QPushButton, QTextEdit,
                             QTableWidget, QHeaderView, QGridLayout, QCheckBox, QRadioButton, QButtonGroup)
from PyQt6.QtCore import Qt

class BLINK_UI(QWidget):
    def setup_ui(self):
        main_layout = QHBoxLayout(self)

        # [좌측 패널]
        left_panel = QWidget()
        left_layout = QVBoxLayout(left_panel)

        self.btn_reset = QPushButton("모두 초기화 (RESET)")
        self.btn_reset.setFixedHeight(50)
        self.btn_reset.setStyleSheet("font-size: 14px; font-weight: bold; background-color: #e74c3c; color: white; border-radius: 4px;")
        left_layout.addWidget(self.btn_reset)

        self.btn_wait_image = QPushButton("이미지 다운로드 (experimental)")
        self.btn_wait_image.setCheckable(True)
        self.btn_wait_image.setFixedHeight(45)
        self.btn_wait_image.setStyleSheet("padding: 10px; font-size: 14px; font-weight: bold; background-color: #f1c40f; color: black; border: 1px solid #f39c12; border-radius: 4px;")
        left_layout.addWidget(self.btn_wait_image)

        # 1. Excitability
        exc_group = QGroupBox("1. Facial Nerve Excitability Test")
        exc_layout = QGridLayout()
        exc_layout.setSpacing(3)
        
        self.rt_exc_btns = {}
        self.lt_exc_btns = {}
        btn_values = [str(i) for i in range(1, 20)] + [">19", "X"]
        
        lbl_rt = QLabel("Rt.")
        lbl_rt.setStyleSheet("font-weight: bold;")
        exc_layout.addWidget(lbl_rt, 0, 0)
        for i, val in enumerate(btn_values):
            btn = QPushButton(val)
            btn.setFixedSize(32, 30) if val == ">19" else btn.setFixedSize(24, 30)
            btn.setCheckable(True)
            self.rt_exc_btns[val] = btn
            exc_layout.addWidget(btn, 0, i+1)
            
        lbl_lt = QLabel("Lt.")
        lbl_lt.setStyleSheet("font-weight: bold;")
        exc_layout.addWidget(lbl_lt, 1, 0)
        for i, val in enumerate(btn_values):
            btn = QPushButton(val)
            btn.setFixedSize(32, 30) if val == ">19" else btn.setFixedSize(24, 30)
            btn.setCheckable(True)
            self.lt_exc_btns[val] = btn
            exc_layout.addWidget(btn, 1, i+1)
            
        exc_group.setLayout(exc_layout)
        left_layout.addWidget(exc_group)

        # 2. Stimulation (표 100 : 이미지 70)
        stim_group = QGroupBox("2. Facial Nerve Stimulation Test")
        stim_layout = QHBoxLayout() 
        
        self.table_stim = QTableWidget(2, 2)
        self.table_stim.setVerticalHeaderLabels(["Rt.", "Lt."])
        self.table_stim.setHorizontalHeaderLabels(["Latency (ms)", "Amplitude (mV)"])
        self.table_stim.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.table_stim.setFixedHeight(95)
        stim_layout.addWidget(self.table_stim, 100)

        self.lbl_stim_image = QLabel("FNST 원본 캡처")
        self.lbl_stim_image.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.lbl_stim_image.setStyleSheet("background-color: #ecf0f1; border: 1px solid #bdc3c7; border-radius: 4px;")
        self.lbl_stim_image.setFixedHeight(95)
        stim_layout.addWidget(self.lbl_stim_image, 100)

        stim_group.setLayout(stim_layout)
        left_layout.addWidget(stim_group)

        # 3. Reflex (표 100 : 이미지 70)
        reflex_group = QGroupBox("3. Blink Reflex Test")
        reflex_layout = QHBoxLayout() 
        
        self.table_reflex = QTableWidget(2, 3)
        self.table_reflex.setVerticalHeaderLabels(["Rt.", "Lt."])
        self.table_reflex.setHorizontalHeaderLabels(["Ipsi R1", "Ipsi R2", "Contra R2"])
        self.table_reflex.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.table_reflex.setFixedHeight(95)
        reflex_layout.addWidget(self.table_reflex, 100)

        reflex_img_container = QWidget()
        reflex_img_layout = QVBoxLayout(reflex_img_container)
        reflex_img_layout.setContentsMargins(0, 0, 0, 0)
        reflex_img_layout.setSpacing(5) 
        
        self.lbl_reflex_img_rt = QLabel("Blink Rt 캡처")
        self.lbl_reflex_img_rt.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.lbl_reflex_img_rt.setStyleSheet("background-color: #ecf0f1; border: 1px solid #bdc3c7; border-radius: 4px;")
        
        self.lbl_reflex_img_lt = QLabel("Blink Lt 캡처")
        self.lbl_reflex_img_lt.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.lbl_reflex_img_lt.setStyleSheet("background-color: #ecf0f1; border: 1px solid #bdc3c7; border-radius: 4px;")
        
        reflex_img_layout.addWidget(self.lbl_reflex_img_rt)
        reflex_img_layout.addWidget(self.lbl_reflex_img_lt)
        
        reflex_layout.addWidget(reflex_img_container, 70)

        reflex_group.setLayout(reflex_layout)
        left_layout.addWidget(reflex_group)

        # 4. LSR
        lsr_group = QGroupBox("4. Lateral Spread Response")
        lsr_layout = QVBoxLayout()
        
        self.chk_lsr_active = QCheckBox("LSR 검사 활성화")
        self.chk_lsr_active.setStyleSheet("font-weight: bold; color: #d35400;")
        lsr_layout.addWidget(self.chk_lsr_active)
        
        side_layout = QHBoxLayout()
        self.rdo_lsr_left = QRadioButton("Left")
        self.rdo_lsr_right = QRadioButton("Right")
        self.rdo_lsr_right.setChecked(True)
        self.lsr_side_group = QButtonGroup()
        self.lsr_side_group.addButton(self.rdo_lsr_left)
        self.lsr_side_group.addButton(self.rdo_lsr_right)
        side_layout.addWidget(self.rdo_lsr_left)
        side_layout.addWidget(self.rdo_lsr_right)
        side_layout.addStretch()
        lsr_layout.addLayout(side_layout)
        
        self.chk_lsr_path1 = QCheckBox("Orbicularis oculi -> Mentalis")
        self.chk_lsr_path2 = QCheckBox("Mentalis -> Orbicularis oculi")
        lsr_layout.addWidget(self.chk_lsr_path1)
        lsr_layout.addWidget(self.chk_lsr_path2)
        
        lsr_group.setLayout(lsr_layout)
        left_layout.addWidget(lsr_group)
        left_layout.addStretch()

        # [우측 패널] 55:45, 2:1 비율
        right_panel = QWidget()
        right_layout = QVBoxLayout(right_panel)

        self.group_findings = QGroupBox("Findings")
        f_lay = QVBoxLayout()
        self.txt_findings = QTextEdit()
        self.txt_findings.setStyleSheet("background-color: #ffffff; border-radius: 4px; border: 1px solid #bdc3c7; padding: 10px; font-size: 13px;")
        f_lay.addWidget(self.txt_findings)
        self.group_findings.setLayout(f_lay)

        self.group_conclusions = QGroupBox("Conclusion")
        c_lay = QVBoxLayout()
        self.txt_conclusions = QTextEdit()
        self.txt_conclusions.setStyleSheet("background-color: #ffffff; border-radius: 4px; border: 1px solid #bdc3c7; padding: 10px; font-size: 13px;")
        c_lay.addWidget(self.txt_conclusions)
        self.group_conclusions.setLayout(c_lay)

        right_layout.addWidget(self.group_findings, 2)
        right_layout.addWidget(self.group_conclusions, 1)

        main_layout.addWidget(left_panel, 55)
        main_layout.addWidget(right_panel, 45)
        
        self.toggle_lsr_controls(False)

    def toggle_lsr_controls(self, active):
        self.rdo_lsr_left.setEnabled(active)
        self.rdo_lsr_right.setEnabled(active)
        self.chk_lsr_path1.setEnabled(active)
        self.chk_lsr_path2.setEnabled(active)