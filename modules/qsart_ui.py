from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, 
                             QLabel, QGroupBox, QPushButton, QFrame, QSizePolicy, QTextEdit,
                             QTableWidget, QHeaderView, QGridLayout, QCheckBox)
from PyQt6.QtCore import Qt

class QSART_UI(QWidget):
    def setup_ui(self):
        main_layout = QHBoxLayout(self)

        # =====================================================================
        # [좌측 패널]
        # =====================================================================
        left_panel = QWidget()
        left_layout = QVBoxLayout(left_panel)

        # 1. 모두 초기화 버튼
        self.btn_reset = QPushButton("모두 초기화 (RESET)")
        self.btn_reset.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        self.btn_reset.setFixedHeight(50)
        self.btn_reset.setStyleSheet("font-size: 14px; font-weight: bold; background-color: #e74c3c; color: white; border-radius: 4px;")
        left_layout.addWidget(self.btn_reset)

        # 2. 상단 컨트롤 컨테이너 (대기 버튼, 성별 토글, 환자 정보)
        self.header_container = QWidget()
        self.header_layout = QHBoxLayout(self.header_container)
        self.header_layout.setContentsMargins(0, 0, 0, 0)
        self.header_layout.setSpacing(10) 

        self.btn_wait_image = QPushButton("이미지 다운로드 대기")
        self.btn_wait_image.setCheckable(True)
        self.btn_wait_image.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        self.btn_wait_image.setFixedHeight(45)
        self.btn_wait_image.setStyleSheet("padding: 10px; font-size: 14px; font-weight: bold; background-color: #f1c40f; color: black; border: 1px solid #f39c12; border-radius: 4px;")
        
        self.btn_sex_toggle = QPushButton("성별: N/A")
        self.btn_sex_toggle.setCheckable(True)
        self.btn_sex_toggle.setFixedSize(100, 45)
        self.btn_sex_toggle.setStyleSheet("font-weight: bold; background-color: #95a5a6; color: white; border-radius: 4px;")

        self.frame_patient_info = QFrame()
        self.frame_patient_info.setFixedSize(238, 55)
        self.frame_patient_info.setStyleSheet("background-color: #ecf0f1; border-radius: 4px; border: 1px solid #bdc3c7;")
        
        patient_layout = QVBoxLayout(self.frame_patient_info)
        patient_layout.setContentsMargins(0, 0, 0, 0) 
        
        self.lbl_patient_image = QLabel("환자 정보")
        self.lbl_patient_image.setAlignment(Qt.AlignmentFlag.AlignCenter) 
        patient_layout.addWidget(self.lbl_patient_image)

        self.header_layout.addWidget(self.btn_wait_image)
        self.header_layout.addWidget(self.btn_sex_toggle) 
        self.header_layout.addWidget(self.frame_patient_info)
        
        left_layout.addWidget(self.header_container)

        # 3. QSART Results 그룹박스
        self.qsart_group = QGroupBox("QSART Results")
        self.qsart_group.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        
        qsart_v_layout = QVBoxLayout()
        qsart_v_layout.setContentsMargins(10, 15, 10, 15)
        qsart_v_layout.setSpacing(15)
        
        # --- 3-1. 표 영역 ---
        table_container_layout = QVBoxLayout()
        image_and_side_layout = QHBoxLayout()
        
        side_btn_layout = QVBoxLayout()
        self.btn_side_left = QPushButton("Left")
        self.btn_side_left.setCheckable(True)
        self.btn_side_left.setFixedSize(60, 35)
        
        self.btn_side_right = QPushButton("Right")
        self.btn_side_right.setCheckable(True)
        self.btn_side_right.setFixedSize(60, 35)
        
        side_btn_layout.addWidget(self.btn_side_left)
        side_btn_layout.addWidget(self.btn_side_right)
        side_btn_layout.addStretch() 
        
        self.frame_table_image = QFrame()
        self.frame_table_image.setFixedHeight(90) 
        self.frame_table_image.setStyleSheet("background-color: #ecf0f1; border-radius: 4px; border: 1px solid #bdc3c7;")
        
        table_img_layout = QVBoxLayout(self.frame_table_image)
        table_img_layout.setContentsMargins(0, 0, 0, 0)
        
        self.lbl_table_image = QLabel("표 대기 중")
        self.lbl_table_image.setAlignment(Qt.AlignmentFlag.AlignCenter)
        table_img_layout.addWidget(self.lbl_table_image)

        image_and_side_layout.addLayout(side_btn_layout, stretch=0)
        image_and_side_layout.addWidget(self.frame_table_image, stretch=1) 

        self.table_qsart = QTableWidget(4, 3) 
        self.table_qsart.setVerticalHeaderLabels(["Forearm", "Proximal Leg", "Distal Leg", "Foot"])
        self.table_qsart.setHorizontalHeaderLabels(["Volume (uL)", "Normal Range", "Status"])
        self.table_qsart.setStyleSheet("background-color: #ffffff; border-radius: 4px; border: 1px solid #bdc3c7;")
        self.table_qsart.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.table_qsart.verticalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.table_qsart.setFixedHeight(144) 
        
        table_container_layout.addLayout(image_and_side_layout)
        table_container_layout.addWidget(self.table_qsart)
        
        qsart_v_layout.addLayout(table_container_layout, stretch=0)

        # --- 3-2. 그래프 영역 ---
        grid_layout = QGridLayout()
        grid_layout.setSpacing(10)
        
        self.lbl_graphs = []
        self.group_boxes = [] 
        self.chk_persistent = [] 
        titles = ["1. Forearm", "2. Proximal Leg", "3. Distal Leg", "4. Foot"]
        
        for i in range(4):
            group_box = QGroupBox(titles[i])
            group_box.setStyleSheet("QGroupBox { font-weight: bold; color: #2c3e50; }")
            group_box.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
            
            l_layout = QVBoxLayout(group_box)
            l_layout.setContentsMargins(5, 18, 5, 5) 
            
            chk = QCheckBox("Persistent production")
            chk.setStyleSheet("font-size: 11px; color: #7f8c8d;")
            l_layout.addWidget(chk)
            self.chk_persistent.append(chk)
            
            lbl = QLabel(f"그래프 대기중")
            lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
            lbl.setStyleSheet("background-color: #ecf0f1; border: 1px dashed #bdc3c7;")
            l_layout.addWidget(lbl)
            
            self.lbl_graphs.append(lbl)
            self.group_boxes.append(group_box)
            
            grid_layout.addWidget(group_box, i // 2, i % 2)

        qsart_v_layout.addLayout(grid_layout, stretch=1)
        self.qsart_group.setLayout(qsart_v_layout)
        left_layout.addWidget(self.qsart_group)

        # =====================================================================
        # [우측 패널] Findings와 Conclusion
        # =====================================================================
        right_panel = QWidget()
        right_layout = QVBoxLayout(right_panel)

        self.group_findings = QGroupBox("Findings")
        findings_layout = QVBoxLayout()
        self.txt_findings = QTextEdit()
        self.txt_findings.setStyleSheet("background-color: #ffffff; border-radius: 4px; border: 1px solid #bdc3c7; padding: 10px; font-size: 13px;")
        findings_layout.addWidget(self.txt_findings)
        self.group_findings.setLayout(findings_layout)

        self.group_conclusions = QGroupBox("Conclusion")
        conclusions_layout = QVBoxLayout()
        self.txt_conclusions = QTextEdit()
        self.txt_conclusions.setStyleSheet("background-color: #ffffff; border-radius: 4px; border: 1px solid #bdc3c7; padding: 10px; font-size: 13px;")
        conclusions_layout.addWidget(self.txt_conclusions)
        self.group_conclusions.setLayout(conclusions_layout)

        right_layout.addWidget(self.group_findings, 1)
        right_layout.addWidget(self.group_conclusions, 1)

        main_layout.addWidget(left_panel, 1)
        main_layout.addWidget(right_panel, 1)