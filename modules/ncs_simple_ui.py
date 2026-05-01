from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QGridLayout,
                             QLabel, QGroupBox, QPushButton, QCheckBox, 
                             QRadioButton, QButtonGroup, QTextEdit, QSizePolicy)
from PyQt6.QtCore import Qt

class NCSSimple_UI(QWidget):
    def setup_ui(self):
        main_layout = QHBoxLayout(self)

        # ==================== 좌측 패널 (입력부) ====================
        left_panel = QWidget()
        left_layout = QVBoxLayout(left_panel)
        left_layout.setContentsMargins(10, 10, 20, 10)

        # 1. 초기화 버튼
        self.btn_reset = QPushButton("모두 초기화 (RESET)")
        self.btn_reset.setFixedHeight(50)
        self.btn_reset.setStyleSheet("font-size: 14px; font-weight: bold; background-color: #e74c3c; color: white; border-radius: 4px;")
        left_layout.addWidget(self.btn_reset)

        # [핵심] 사지(Limb) 선택용 토글 버튼 스타일 (선택 시 금색 적용)
        limb_btn_style = """
            QPushButton {
                background-color: #ecf0f1; border: 1px solid #bdc3c7; border-radius: 6px; padding: 12px; font-weight: bold; font-size: 14px; color: #2c3e50;
            }
            QPushButton:checked {
                background-color: #f1c40f; color: black; border: 1px solid #d4ac0d;
            }
            QPushButton:hover:!disabled {
                background-color: #d5dbdb;
            }
            QPushButton:disabled {
                background-color: #e0e0e0; color: #a0a0a0; border: 1px solid #d0d0d0;
            }
            QPushButton:disabled:checked {
                background-color: #f9e79f; color: #7d6608;
            }
        """

        # 2. Evaluated Limbs - 2x2 버튼 (괄호 한글 삭제)
        group_eval = QGroupBox("Evaluated Limbs")
        group_eval.setStyleSheet("font-weight: bold;")
        eval_layout = QGridLayout(group_eval)
        eval_layout.setSpacing(10)
        
        self.btn_eval_lue = QPushButton("LUE"); self.btn_eval_lue.setCheckable(True)
        self.btn_eval_rue = QPushButton("RUE"); self.btn_eval_rue.setCheckable(True)
        self.btn_eval_lle = QPushButton("LLE"); self.btn_eval_lle.setCheckable(True)
        self.btn_eval_rle = QPushButton("RLE"); self.btn_eval_rle.setCheckable(True)
        
        for btn in [self.btn_eval_lue, self.btn_eval_rue, self.btn_eval_lle, self.btn_eval_rle]:
            btn.setStyleSheet(limb_btn_style)
            # [수정] 초기값: 모두 선택 해제
            btn.setChecked(False) 
            
        eval_layout.addWidget(self.btn_eval_lue, 0, 0)
        eval_layout.addWidget(self.btn_eval_rue, 0, 1)
        eval_layout.addWidget(self.btn_eval_lle, 1, 0)
        eval_layout.addWidget(self.btn_eval_rle, 1, 1)
        left_layout.addWidget(group_eval)

        # 3. Conclusion Pattern
        group_pattern = QGroupBox("Conclusion Pattern")
        group_pattern.setStyleSheet("font-weight: bold;")
        pattern_layout = QVBoxLayout(group_pattern)
        pattern_layout.setSpacing(12)
        
        self.rdo_group = QButtonGroup(self)
        self.rdo_normal = QRadioButton("Normal Study")
        self.rdo_smpn = QRadioButton("Sensorimotor Polyneuropathy (SMPN)")
        self.rdo_cts = QRadioButton("Carpal Tunnel Syndrome (CTS)")
        self.rdo_plantar = QRadioButton("Plantar Sensory Neuropathy")
        
        smpn_layout = QHBoxLayout()
        self.rdo_smpn_btn = self.rdo_smpn # 참조용
        self.chk_demyelinating = QCheckBox("Demyelinating type")
        self.chk_demyelinating.setStyleSheet("color: #2980b9; font-weight: bold;")
        self.chk_demyelinating.setEnabled(False)
        
        smpn_layout.addWidget(self.rdo_smpn)
        smpn_layout.addWidget(self.chk_demyelinating)
        smpn_layout.addStretch()

        self.rdo_normal.setChecked(True)
        
        for rdo in [self.rdo_normal, self.rdo_smpn, self.rdo_cts, self.rdo_plantar]:
            self.rdo_group.addButton(rdo)
            
        pattern_layout.addWidget(self.rdo_normal)
        pattern_layout.addLayout(smpn_layout)
        pattern_layout.addWidget(self.rdo_cts)
        pattern_layout.addWidget(self.rdo_plantar)
        
        left_layout.addWidget(group_pattern)

        # 4. Abnormal Limbs - 2x2 버튼 (괄호 한글 삭제)
        self.group_abnorm = QGroupBox("Abnormal Limbs")
        self.group_abnorm.setStyleSheet("font-weight: bold;")
        abnorm_layout = QGridLayout(self.group_abnorm)
        abnorm_layout.setSpacing(10)
        
        self.btn_abnorm_lue = QPushButton("LUE"); self.btn_abnorm_lue.setCheckable(True)
        self.btn_abnorm_rue = QPushButton("RUE"); self.btn_abnorm_rue.setCheckable(True)
        self.btn_abnorm_lle = QPushButton("LLE"); self.btn_abnorm_lle.setCheckable(True)
        self.btn_abnorm_rle = QPushButton("RLE"); self.btn_abnorm_rle.setCheckable(True)
        
        for btn in [self.btn_abnorm_lue, self.btn_abnorm_rue, self.btn_abnorm_lle, self.btn_abnorm_rle]:
            btn.setStyleSheet(limb_btn_style)
            btn.setEnabled(False)
            
        abnorm_layout.addWidget(self.btn_abnorm_lue, 0, 0)
        abnorm_layout.addWidget(self.btn_abnorm_rue, 0, 1)
        abnorm_layout.addWidget(self.btn_abnorm_lle, 1, 0)
        abnorm_layout.addWidget(self.btn_abnorm_rle, 1, 1)
            
        left_layout.addWidget(self.group_abnorm)
        left_layout.addStretch()

        # ==================== 우측 패널 (출력부) ====================
        right_panel = QWidget()
        right_layout = QVBoxLayout(right_panel)
        right_layout.setContentsMargins(0, 10, 10, 10)

        # [수정] Conclusion 그룹박스 및 텍스트 박스 Bold 제거
        group_conclusion = QGroupBox("Conclusion")
        group_conclusion.setStyleSheet("font-weight: normal; font-size: 14px;") # Bold 해제
        conclusion_layout = QVBoxLayout(group_conclusion)
        
        self.txt_conclusion = QTextEdit()
        # [수정] font-weight: bold 제거
        self.txt_conclusion.setStyleSheet("background-color: #ecf0f1; border-radius: 4px; border: 1px solid #bdc3c7; padding: 15px; font-size: 16px; color: #2c3e50; font-weight: normal;")
        conclusion_layout.addWidget(self.txt_conclusion)
        
        right_layout.addWidget(group_conclusion)

        main_layout.addWidget(left_panel, 1)
        main_layout.addWidget(right_panel, 1)