from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, 
                             QLabel, QGroupBox, QPushButton, QFrame, QSizePolicy, QTextEdit,
                             QTableWidget, QHeaderView, QGridLayout, QLineEdit, QCheckBox) # QCheckBox 추가
from PyQt6.QtCore import Qt

class ANSFT_UI(QWidget):
    
    def setup_ui(self):
        main_layout = QHBoxLayout(self)

        left_panel = QWidget()
        left_layout = QVBoxLayout(left_panel)

        # =====================================================================
        # 1. 상단 (중복 안내 텍스트 삭제 및 Reset 버튼 확장)
        # =====================================================================
        self.btn_reset = QPushButton("모두 초기화 (RESET)")
        self.btn_reset.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        self.btn_reset.setFixedHeight(50)
        self.btn_reset.setStyleSheet("font-size: 14px; font-weight: bold; background-color: #e74c3c; color: white; border-radius: 4px;")
        left_layout.addWidget(self.btn_reset)

        # =====================================================================
        # 다운로드 대기 및 환자 정보
        # =====================================================================
        self.header_container = QWidget()
        self.header_layout = QHBoxLayout(self.header_container)
        self.header_layout.setContentsMargins(0, 0, 0, 0)
        self.header_layout.setSpacing(15) 

        self.btn_wait_image = QPushButton("이미지 다운로드 대기")
        self.btn_wait_image.setCheckable(True)
        self.btn_wait_image.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        self.btn_wait_image.setFixedHeight(45)
        self.btn_wait_image.setStyleSheet("padding: 10px; font-size: 14px; font-weight: bold; background-color: #f1c40f; color: black; border: 1px solid #f39c12; border-radius: 4px;")
        
        self.frame_patient_info = QFrame()
        self.frame_patient_info.setFrameShape(QFrame.Shape.StyledPanel)
        self.frame_patient_info.setFixedSize(238, 55)
        self.frame_patient_info.setStyleSheet("background-color: #ecf0f1; border-radius: 4px; border: 1px solid #bdc3c7;")
        
        patient_layout = QVBoxLayout(self.frame_patient_info)
        patient_layout.setContentsMargins(0, 0, 0, 0) 
        self.lbl_patient_image = QLabel("환자 정보")
        self.lbl_patient_image.setAlignment(Qt.AlignmentFlag.AlignCenter) 
        self.lbl_patient_image.setStyleSheet("color: #95a5a6; font-size: 11px; font-weight: bold;")
        patient_layout.addWidget(self.lbl_patient_image)

        self.header_layout.addWidget(self.btn_wait_image)
        self.header_layout.addWidget(self.frame_patient_info)
        left_layout.addWidget(self.header_container)

        # 2. SSR 구역
        self.ssr_group = QGroupBox("1. Sympathetic skin response")
        self.ssr_group.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        ssr_main_layout = QHBoxLayout()
        ssr_main_layout.setContentsMargins(10, 15, 10, 15)
        ssr_main_layout.setSpacing(15)

        button_container = QWidget()
        button_layout = QVBoxLayout(button_container)
        button_layout.setContentsMargins(0, 0, 0, 0)
        button_layout.setSpacing(10)

        common_btn_style = """
            QPushButton { font-weight: bold; background-color: #2ecc71; color: white; border: 1px solid #27ae60; border-radius: 4px; font-size: 13px; }
            QPushButton:checked { background-color: #e74c3c; color: white; border: 1px solid #c0392b; }
        """
        self.btn_ssr_palm = QPushButton("Palm 정상")
        self.btn_ssr_palm.setCheckable(True) 
        self.btn_ssr_palm.setFixedHeight(37) 
        self.btn_ssr_palm.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        self.btn_ssr_palm.setStyleSheet(common_btn_style)

        self.btn_ssr_sole = QPushButton("Sole 정상")
        self.btn_ssr_sole.setCheckable(True)
        self.btn_ssr_sole.setFixedHeight(37) 
        self.btn_ssr_sole.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        self.btn_ssr_sole.setStyleSheet(common_btn_style)

        button_layout.addWidget(self.btn_ssr_palm)
        button_layout.addWidget(self.btn_ssr_sole)

        self.frame_ssr_graph = QFrame()
        self.frame_ssr_graph.setFixedSize(174, 88) 
        self.frame_ssr_graph.setStyleSheet("background-color: #ecf0f1; border-radius: 4px; border: 1px solid #bdc3c7;")
        ssr_graph_layout = QVBoxLayout(self.frame_ssr_graph)
        ssr_graph_layout.setContentsMargins(0, 0, 0, 0) 
        self.lbl_ssr_graph = QLabel("SSR")
        self.lbl_ssr_graph.setAlignment(Qt.AlignmentFlag.AlignCenter) 
        ssr_graph_layout.addWidget(self.lbl_ssr_graph)

        ssr_main_layout.addWidget(button_container, 1)
        ssr_main_layout.addWidget(self.frame_ssr_graph, 0) 
        self.ssr_group.setLayout(ssr_main_layout)
        left_layout.addWidget(self.ssr_group)

        # =====================================================================
        # 3. HRDB 구역 (Arrhythmia 체크박스 추가)
        # =====================================================================
        self.hrdb_group = QGroupBox("2. Heart rate response to deep breathing")
        self.hrdb_group.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        
        hrdb_v_layout = QVBoxLayout()
        hrdb_v_layout.setContentsMargins(10, 5, 10, 15) # 상단 여백 축소
        
        # 부정맥 체크박스 (우측 정렬)
        self.chk_arrhythmia_hrdb = QCheckBox("Arrhythmia (부정맥)")
        self.chk_arrhythmia_hrdb.setStyleSheet("color: #e74c3c; font-weight: bold;")
        hrdb_v_layout.addWidget(self.chk_arrhythmia_hrdb, alignment=Qt.AlignmentFlag.AlignRight)

        hrdb_main_layout = QHBoxLayout()
        hrdb_main_layout.setContentsMargins(0, 0, 0, 0)
        hrdb_main_layout.setSpacing(15)
        
        self.txt_hrdb_ocr = QLineEdit()
        self.txt_hrdb_ocr.setPlaceholderText("OCR 결과 대기 중...")
        self.txt_hrdb_ocr.setStyleSheet("background-color: #ffffff; border-radius: 4px; border: 1px solid #bdc3c7; padding-left: 10px; font-size: 13px; color: #2c3e50;")
        self.txt_hrdb_ocr.setFixedHeight(45)
        
        self.frame_hrdb_image = QFrame()
        self.frame_hrdb_image.setFixedSize(174, 45) 
        self.frame_hrdb_image.setStyleSheet("background-color: #ecf0f1; border-radius: 4px; border: 1px solid #bdc3c7;")
        hrdb_image_layout = QVBoxLayout(self.frame_hrdb_image)
        hrdb_image_layout.setContentsMargins(0, 0, 0, 0)
        self.lbl_hrdb_image = QLabel("HRDB")
        self.lbl_hrdb_image.setAlignment(Qt.AlignmentFlag.AlignCenter)
        hrdb_image_layout.addWidget(self.lbl_hrdb_image)

        hrdb_main_layout.addWidget(self.txt_hrdb_ocr)
        hrdb_main_layout.addWidget(self.frame_hrdb_image)
        
        hrdb_v_layout.addLayout(hrdb_main_layout)
        self.hrdb_group.setLayout(hrdb_v_layout)
        left_layout.addWidget(self.hrdb_group)

        # 4. Tilt table test 구역
        self.tilt_group = QGroupBox("3. Tilt table test")
        self.tilt_group.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        tilt_main_layout = QHBoxLayout()
        tilt_main_layout.setContentsMargins(10, 15, 10, 15)
        tilt_main_layout.setSpacing(15)
        
        self.table_tilt = QTableWidget(5, 3)
        self.table_tilt.setHorizontalHeaderLabels(["SBP", "DBP", "HR"])
        self.table_tilt.setVerticalHeaderLabels(["Supine", "1 min", "3 min", "5 min", "10 min"])
        self.table_tilt.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.table_tilt.verticalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.table_tilt.verticalHeader().setMinimumWidth(55)
        self.table_tilt.verticalHeader().setMinimumSectionSize(15)
        self.table_tilt.horizontalHeader().setMinimumSectionSize(15)
        
        font_t = self.table_tilt.font()
        font_t.setPointSize(9)
        self.table_tilt.setFont(font_t)
        
        self.table_tilt.setFixedHeight(155)
        self.table_tilt.setStyleSheet("background-color: #ffffff; border-radius: 4px; border: 1px solid #bdc3c7;")
        
        self.frame_tilt_image = QFrame()
        self.frame_tilt_image.setFixedSize(174, 155) 
        self.frame_tilt_image.setStyleSheet("background-color: #ecf0f1; border-radius: 4px; border: 1px solid #bdc3c7;")
        tilt_image_layout = QVBoxLayout(self.frame_tilt_image)
        tilt_image_layout.setContentsMargins(0, 0, 0, 0)
        self.lbl_tilt_image = QLabel("Tilt")
        self.lbl_tilt_image.setAlignment(Qt.AlignmentFlag.AlignCenter)
        tilt_image_layout.addWidget(self.lbl_tilt_image)

        tilt_main_layout.addWidget(self.table_tilt)
        tilt_main_layout.addWidget(self.frame_tilt_image)
        self.tilt_group.setLayout(tilt_main_layout)
        left_layout.addWidget(self.tilt_group)

        # =====================================================================
        # 5. Valsalva test 구역 (Arrhythmia 체크박스 추가)
        # =====================================================================
        self.valsalva_group = QGroupBox("4. Valsalva test")
        self.valsalva_group.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)
        
        valsalva_v_layout = QVBoxLayout()
        valsalva_v_layout.setContentsMargins(10, 5, 10, 15) # 상단 여백 축소
        valsalva_v_layout.setSpacing(12) 
        
        # 부정맥 체크박스 (우측 정렬)
        self.chk_arrhythmia_val = QCheckBox("Arrhythmia (부정맥)")
        self.chk_arrhythmia_val.setStyleSheet("color: #e74c3c; font-weight: bold;")
        valsalva_v_layout.addWidget(self.chk_arrhythmia_val, alignment=Qt.AlignmentFlag.AlignRight)

        # --- 1층: 표와 기존 이미지 ---
        row1_layout = QHBoxLayout()
        row1_layout.setSpacing(15)
        
        self.table_valsalva = QTableWidget(1, 3)
        self.table_valsalva.setHorizontalHeaderLabels(["HR Valsalva ratio", "HR Ratio 5%ile", "PRT(sec)"])
        self.table_valsalva.verticalHeader().setVisible(False)
        self.table_valsalva.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.table_valsalva.verticalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.table_valsalva.verticalHeader().setMinimumSectionSize(15)
        self.table_valsalva.horizontalHeader().setMinimumSectionSize(15)
        font_v = self.table_valsalva.font()
        font_v.setPointSize(8) 
        self.table_valsalva.setFont(font_v)
        self.table_valsalva.horizontalHeader().setFont(font_v)
        self.table_valsalva.setFixedHeight(65)
        self.table_valsalva.setStyleSheet("background-color: #ffffff; border-radius: 4px; border: 1px solid #bdc3c7;")
        
        self.frame_valsalva_image = QFrame()
        self.frame_valsalva_image.setFixedSize(174, 65) 
        self.frame_valsalva_image.setStyleSheet("background-color: #ecf0f1; border-radius: 4px; border: 1px solid #bdc3c7;")
        valsalva_image_layout = QVBoxLayout(self.frame_valsalva_image)
        valsalva_image_layout.setContentsMargins(0, 0, 0, 0)
        self.lbl_valsalva_image = QLabel("Valsalva") 
        self.lbl_valsalva_image.setAlignment(Qt.AlignmentFlag.AlignCenter)
        valsalva_image_layout.addWidget(self.lbl_valsalva_image)

        row1_layout.addWidget(self.table_valsalva, stretch=1)
        row1_layout.addWidget(self.frame_valsalva_image, stretch=0)

        # --- 2층: 분석 버튼과 새로운 Norm Ratio 이미지 ---
        row2_layout = QHBoxLayout()
        row2_layout.setSpacing(15)

        self.btn_valsalva_graph = QPushButton("Valsalva 그래프 분석 (대기)")
        self.btn_valsalva_graph.setFixedHeight(35)
        self.btn_valsalva_graph.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        self.btn_valsalva_graph.setStyleSheet("padding: 5px; font-weight: bold; background-color: #f1c40f; color: black; border-radius: 4px;")

        self.frame_norm_ratio_image = QFrame()
        self.frame_norm_ratio_image.setFixedSize(174, 35) 
        self.frame_norm_ratio_image.setStyleSheet("background-color: #ecf0f1; border-radius: 4px; border: 1px solid #bdc3c7;")
        norm_ratio_layout = QVBoxLayout(self.frame_norm_ratio_image)
        norm_ratio_layout.setContentsMargins(0, 0, 0, 0)
        self.lbl_norm_ratio_image = QLabel("Norm Ratio")
        self.lbl_norm_ratio_image.setAlignment(Qt.AlignmentFlag.AlignCenter)
        norm_ratio_layout.addWidget(self.lbl_norm_ratio_image)

        row2_layout.addWidget(self.btn_valsalva_graph, stretch=1)
        row2_layout.addWidget(self.frame_norm_ratio_image, stretch=0)

        # --- 3층: 요약 텍스트 박스 ---
        self.txt_valsalva_summary = QTextEdit()
        self.txt_valsalva_summary.setFixedHeight(65) 
        self.txt_valsalva_summary.setStyleSheet("background-color: #f8f9fa; border-radius: 4px; border: 1px solid #bdc3c7; padding: 5px;")
        self.txt_valsalva_summary.setReadOnly(True)
        self.txt_valsalva_summary.setPlaceholderText("그래프 분석 전입니다. 버튼을 클릭해주세요.")

        # 레이아웃을 순서대로 쌓기
        valsalva_v_layout.addLayout(row1_layout)
        valsalva_v_layout.addLayout(row2_layout)
        valsalva_v_layout.addWidget(self.txt_valsalva_summary) 
        
        self.valsalva_group.setLayout(valsalva_v_layout)
        left_layout.addWidget(self.valsalva_group)
        left_layout.addStretch()

        # 오른쪽 패널 레이아웃
        right_panel = QWidget()
        right_layout = QVBoxLayout(right_panel)

        self.group_findings = QGroupBox("Findings")
        findings_layout = QVBoxLayout()
        self.txt_findings = QTextEdit()
        self.txt_findings.setStyleSheet("background-color: #ffffff; border-radius: 4px; border: 1px solid #bdc3c7; padding: 10px;")
        findings_layout.addWidget(self.txt_findings)
        self.group_findings.setLayout(findings_layout)

        self.group_analysis = QGroupBox("Analysis")
        analysis_layout = QVBoxLayout()
        self.txt_analysis = QTextEdit()
        self.txt_analysis.setStyleSheet("background-color: #ffffff; border-radius: 4px; border: 1px solid #bdc3c7; padding: 10px;")
        analysis_layout.addWidget(self.txt_analysis)
        self.group_analysis.setLayout(analysis_layout)

        self.group_conclusions = QGroupBox("Conclusion")
        conclusions_layout = QVBoxLayout()
        self.txt_conclusions = QTextEdit()
        self.txt_conclusions.setStyleSheet("background-color: #ffffff; border-radius: 4px; border: 1px solid #bdc3c7; padding: 10px;")
        conclusions_layout.addWidget(self.txt_conclusions)
        self.group_conclusions.setLayout(conclusions_layout)

        right_layout.addWidget(self.group_findings, 4)
        right_layout.addWidget(self.group_analysis, 4)
        right_layout.addWidget(self.group_conclusions, 3)

        main_layout.addWidget(left_panel, 1)
        main_layout.addWidget(right_panel, 1)