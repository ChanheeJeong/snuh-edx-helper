import keyboard
import time
import re
from datetime import datetime
from PyQt6.QtWidgets import QTableWidgetItem, QApplication
from PyQt6.QtCore import Qt

from models.pft_data import PFTPatientInfo, PFTDataInput
from engine.pft_engine import PFTEngine
from modules.pft_ui import PFT_UI
from modules.pft_vision import PFTVisionHandler

class PFTWidget(PFT_UI):
    def __init__(self, main_window):
        super().__init__()
        self.main_window = main_window
        self.DISCLAIMER = "**현재 가판독 상태이며 추후 정식 판독을 참조하기 바람."
        
        self.patient = PFTPatientInfo()
        self.trials = [[None] * 4 for _ in range(3)]
        self.fvc = None
        self.fev1 = None
        self.current_result = None

        self.setup_ui()
        self.connect_events()

    def connect_events(self):
        self.btn_reset.clicked.connect(self.reset_all)
        self.btn_cap_info.clicked.connect(self.capture_info)
        self.btn_cap_mip.clicked.connect(self.capture_mip)
        self.btn_cap_snip.clicked.connect(self.capture_snip)
        self.btn_cap_spiro.clicked.connect(self.capture_spiro)

    def update_table(self):
        # 1. 3x4 시행 데이터 채우기 및 중앙 정렬
        for r in range(3):
            for c in range(4):
                val = self.trials[r][c]
                item = QTableWidgetItem(str(val) if val is not None else "")
                item.setTextAlignment(Qt.AlignmentFlag.AlignCenter) # [수정] 중앙 정렬
                self.table.setItem(r, c, item)
        
        # 2. 결과가 있으면 정상 범위 및 판정 결과 채우기
        if self.current_result:
            keys = ["MIP", "MEP", "SNIP", "PEF"]
            for c, key in enumerate(keys):
                # 정상 범위 중앙 정렬
                item_norm = QTableWidgetItem(self.current_result.normal_ranges.get(key, ""))
                item_norm.setTextAlignment(Qt.AlignmentFlag.AlignCenter) # [수정] 중앙 정렬
                self.table.setItem(3, c, item_norm)
                
                # 결과(Normal/Abnormal) 중앙 정렬 및 색상
                item_status = QTableWidgetItem(self.current_result.test_status.get(key, ""))
                item_status.setTextAlignment(Qt.AlignmentFlag.AlignCenter) # [수정] 중앙 정렬
                if item_status.text() == "Abnormal": 
                    item_status.setForeground(Qt.GlobalColor.red)
                elif item_status.text() == "Normal": 
                    item_status.setForeground(Qt.GlobalColor.darkGreen)
                self.table.setItem(4, c, item_status)

    def analyze_and_update(self):
        input_data = PFTDataInput(patient=self.patient, trials=self.trials, fvc=self.fvc, fev1=self.fev1)
        self.current_result = PFTEngine.analyze(input_data)
        
        self.update_table()
        if self.current_result.conclusion_text:
            display_text = f"{self.current_result.conclusion_text}\n\n{self.DISCLAIMER}"
            self.txt_conclusion.setText(display_text)

    def capture_info(self):
        text = PFTVisionHandler.capture_and_ocr(clean_lines=False, is_info=True)
        if not text: return
        
        dob_match = re.search(r'Birth Date:\s*(\d{4})-(\d{2})-(\d{2})', text)
        if dob_match:
            y, m, d = map(int, dob_match.groups())
            today = datetime.today()
            self.patient.age = today.year - y - ((today.month, today.day) < (m, d))
        
        sex_match = re.search(r'Sex:\s*(\w)', text)
        if sex_match: self.patient.sex = "Male" if sex_match.group(1).upper() == 'M' else "Female"
        
        h_match = re.search(r'Height:\s*(\d+)', text)
        if h_match: self.patient.height = int(h_match.group(1))
        
        w_match = re.search(r'Weight:\s*(\d+)', text)
        if w_match: self.patient.weight = int(w_match.group(1))

        self.lbl_info.setText(f"Age: {self.patient.age}, Sex: {self.patient.sex}\nHeight: {self.patient.height}, Weight: {self.patient.weight}")
        self.btn_cap_info.setStyleSheet("background-color: #f1c40f; color: black; font-weight: bold; border-radius: 4px; padding: 10px;")
        self.lbl_status.setText("Patient Info Captured.")
        self.analyze_and_update()

    def capture_mip(self):
        text = PFTVisionHandler.capture_and_ocr(clean_lines=True)
        nums = PFTVisionHandler.extract_numbers(text)
        if len(nums) == 6:
            rows = [nums[i:i + 2] for i in range(0, 6, 2)]
            for i in range(3): self.trials[i][0], self.trials[i][1] = rows[i][0], rows[i][1]
            self.btn_cap_mip.setStyleSheet("background-color: #f1c40f; color: black; font-weight: bold; border-radius: 4px; padding: 10px;")
            self.lbl_status.setText("MIP/MEP Captured.")
            self.analyze_and_update()
        else: self.lbl_status.setText(f"OCR Error: Expected 6 numbers, found {len(nums)}")

    def capture_snip(self):
        text = PFTVisionHandler.capture_and_ocr(clean_lines=True)
        nums = PFTVisionHandler.extract_numbers(text)
        if len(nums) == 6:
            rows = [nums[i:i + 2] for i in range(0, 6, 2)]
            for i in range(3): self.trials[i][2], self.trials[i][3] = rows[i][0], rows[i][1]
            self.btn_cap_snip.setStyleSheet("background-color: #f1c40f; color: black; font-weight: bold; border-radius: 4px; padding: 10px;")
            self.lbl_status.setText("SNIP/PEF Captured.")
            self.analyze_and_update()
        else: self.lbl_status.setText(f"OCR Error: Expected 6 numbers, found {len(nums)}")

    def capture_spiro(self):
        text = PFTVisionHandler.capture_and_ocr(clean_lines=False)
        nums = PFTVisionHandler.extract_numbers(text)
        if len(nums) == 2:
            self.fvc, self.fev1 = nums[0], nums[1]
            self.lbl_spiro.setText(f"FVC %Pred: {self.fvc}%\nFEV1 %Pred: {self.fev1}%")
            self.btn_cap_spiro.setStyleSheet("background-color: #f1c40f; color: black; font-weight: bold; border-radius: 4px; padding: 10px;")
            self.lbl_status.setText("Spirometry Captured.")
            self.analyze_and_update()
        else: self.lbl_status.setText(f"OCR Error: Expected 2 numbers, found {len(nums)}")

    def macro_type_conclusion(self):
        """Ctrl+Shift+Q 매크로 로직"""
        if any(v is None for v in [self.patient.height, self.patient.weight]) or any(None in row for row in self.trials):
            self.lbl_status.setText("Incomplete data for macro.")
            return

        self.lbl_status.setText("PFT 양식 입력 중... (키보드/마우스를 건드리지 마세요)")
        QApplication.processEvents() # UI 강제 업데이트

        time.sleep(1.0)
        
        def pt(count=1):
            for _ in range(count): 
                keyboard.send('tab')
                time.sleep(0.08)
        
        # 1. 3x4 = 12개의 시행 데이터 타이핑
        for row in self.trials:
            for val in row:
                keyboard.write(str(val)); time.sleep(0.05); pt()
        
        # 2. 정상 범위 및 키/몸무게 타이핑
        pt(5)
        keyboard.write(str(self.current_result.normal_ranges.get("MIP", ""))); time.sleep(0.05); pt(2)
        keyboard.write(str(self.current_result.normal_ranges.get("MEP", ""))); time.sleep(0.05); pt(2)
        keyboard.write(str(self.current_result.normal_ranges.get("SNIP", ""))); time.sleep(0.05); pt(2)
        keyboard.write(str(self.current_result.normal_ranges.get("PEF", ""))); time.sleep(0.05); pt(1)
        keyboard.write(str(self.patient.height)); time.sleep(0.05); pt(2)
        keyboard.write(str(self.patient.weight)); time.sleep(0.05); pt(6)
        
        # 3. [수정] 서명 제외, 결론 + 가판 문구를 하나로 묶어서 붙여넣기
        if self.current_result.conclusion_text:
            import pyperclip
            text_to_paste = f"{self.current_result.conclusion_text}\n\n{self.DISCLAIMER}"
            pyperclip.copy(text_to_paste)
            time.sleep(0.2)
            keyboard.send('ctrl+v')
            time.sleep(0.2)
            # 서명 탭 이동 및 붙여넣기 로직 삭제됨
            
        self.lbl_status.setText("PFT 매크로 입력 완료!")
        self.lbl_status.setStyleSheet("color: #2ecc71; font-weight: bold; margin-top: 10px;")

    def reset_all(self):
        self.patient = PFTPatientInfo()
        self.trials = [[None] * 4 for _ in range(3)]
        self.fvc = self.fev1 = None
        self.current_result = None
        
        btn_style = "font-size: 13px; font-weight: bold; color: white; border-radius: 4px; padding: 10px;"
        self.btn_cap_info.setStyleSheet(f"background-color: #3498db; {btn_style}")
        self.btn_cap_mip.setStyleSheet(f"background-color: #2ecc71; {btn_style}")
        self.btn_cap_snip.setStyleSheet(f"background-color: #2ecc71; {btn_style}")
        self.btn_cap_spiro.setStyleSheet(f"background-color: #9b59b6; {btn_style}")
        
        self.lbl_info.setText("환자 정보: 대기 중")
        self.lbl_spiro.setText("Spirometry: 대기 중")
        self.lbl_status.setText("Ready.")
        self.lbl_status.setStyleSheet("color: #e67e22; font-weight: bold; margin-top: 10px;")
        
        self.txt_conclusion.clear()
        self.table.clearContents()