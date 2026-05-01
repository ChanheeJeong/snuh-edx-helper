import os
import traceback
import time
import keyboard 
import pyperclip
from datetime import datetime
from PyQt6.QtCore import QTimer
from PyQt6.QtGui import QPixmap

from models.ansft_data import PatientInfo, SSRData, HRDBData, TiltData, ValsalvaData, ANSFTInput
from engine.ansft_engine import ANSFTEngine
from engine.report_formatter import ReportFormatter
from tools.image_processor import ImageProcessor
from modules.ansft_valsalva import ValsalvaGraphWindow 
from modules.ansft_ui import ANSFT_UI

# 분리된 비전 핸들러 임포트
from modules.ansft_vision import AnsftVisionHandler

class ANSFTWidget(ANSFT_UI):
    def __init__(self, main_window): 
        super().__init__()
        self.main_window = main_window 
        
        self.base_path = r"C:\HIS_Image"
        self.previous_files = set()
        self.session_new_files = set()
        
        # Vision 로직 위임 객체 생성
        self.vision_handler = AnsftVisionHandler(self)
        
        self.valsalva_window = None 
        self.val_saved_lines, self.val_yellow_min, self.val_yellow_max = None, None, None
        self.val_saved_chk_2l, self.val_saved_chk_4, self.val_saved_chk_poor, self.val_saved_overshoot_state = False, False, False, False
        
        self.patient_age = 0
        self.hrdb_val1, self.hrdb_val2 = "N/A", "N/A"
        self.tilt_data = [] 
        self.val_ratio, self.prt_sec, self.normal_val_ratio = "N/A", "N/A", "N/A"
        
        self._is_updating_table = False
        self.is_valsalva_analyzed = False 
        self.current_findings_text, self.current_conclusion_text = "", ""

        self.setup_ui()

        # UI 이벤트 연결
        self.btn_reset.clicked.connect(self.reset_all) 
        self.btn_wait_image.clicked.connect(self.toggle_watch)
        self.btn_ssr_palm.clicked.connect(self.update_findings_and_analysis)
        self.btn_ssr_sole.clicked.connect(self.update_findings_and_analysis)
        self.btn_valsalva_graph.clicked.connect(self.open_valsalva_graph_window)
        
        self.table_tilt.itemChanged.connect(self.on_table_changed)
        self.table_valsalva.itemChanged.connect(self.on_table_changed)
        
        self.chk_arrhythmia_hrdb.toggled.connect(self.update_arrhythmia_ui)
        self.chk_arrhythmia_val.toggled.connect(self.update_arrhythmia_ui)

        self.watch_timer = QTimer()
        self.watch_timer.timeout.connect(self.check_for_new_files)

    def macro_type_conclusion(self):
        if not self.current_findings_text or not self.current_conclusion_text:
            return
            
        signature = self.main_window.signature_tool.get_signature()
            
        pyperclip.copy(self.current_findings_text)
        time.sleep(0.2); keyboard.send('ctrl+v'); time.sleep(0.2); keyboard.send('tab'); time.sleep(0.2) 
        
        pyperclip.copy(self.current_conclusion_text)
        time.sleep(0.2); keyboard.send('ctrl+v'); time.sleep(0.2); keyboard.send('tab'); time.sleep(0.2)

        pyperclip.copy(signature)
        time.sleep(0.2); keyboard.send('ctrl+v')

    def on_table_changed(self, item):
        if self._is_updating_table: return 
        
        new_tilt_data = []
        for r in range(5):
            row_vals = []
            for c in range(3):
                cell_item = self.table_tilt.item(r, c)
                val = 0
                if cell_item and cell_item.text().strip():
                    try:
                        clean_text = "".join(filter(lambda x: x.isdigit() or x=='-', cell_item.text().strip()))
                        val = int(clean_text) if clean_text else 0
                    except ValueError: val = 0
                row_vals.append(val)
            new_tilt_data.append(row_vals)
            
        self.tilt_data = new_tilt_data
        
        item_ratio, item_norm_ratio, item_prt = self.table_valsalva.item(0, 0), self.table_valsalva.item(0, 1), self.table_valsalva.item(0, 2)
        self.val_ratio = item_ratio.text().strip() if item_ratio else "N/A"
        self.normal_val_ratio = item_norm_ratio.text().strip() if item_norm_ratio else "N/A"
        self.prt_sec = item_prt.text().strip() if item_prt else "N/A"
        
        self.update_findings_and_analysis()

    def update_arrhythmia_ui(self):
        is_hrdb_arr = self.chk_arrhythmia_hrdb.isChecked()
        self.txt_hrdb_ocr.setEnabled(not is_hrdb_arr)
        
        if is_hrdb_arr:
            self.txt_hrdb_ocr.setText("Arrhythmia (분석 불가)")
            self.txt_hrdb_ocr.setStyleSheet("background-color: #ecf0f1; border-radius: 4px; border: 1px solid #bdc3c7; padding-left: 10px; font-size: 13px; color: #7f8c8d; font-weight: bold;")
        else:
            self.txt_hrdb_ocr.setText(f"E/I ratio '{self.hrdb_val1}' (normal range >'{self.hrdb_val2}')")
            self.txt_hrdb_ocr.setStyleSheet("background-color: #ffffff; border-radius: 4px; border: 1px solid #bdc3c7; padding-left: 10px; font-size: 13px; color: #2c3e50;")

        is_val_arr = self.chk_arrhythmia_val.isChecked()
        self.table_valsalva.setEnabled(not is_val_arr)
        self.btn_valsalva_graph.setEnabled(not is_val_arr)
        self.txt_valsalva_summary.setEnabled(not is_val_arr)
        
        if is_val_arr:
            self.txt_valsalva_summary.setText("Arrhythmia (분석 불가)")
        elif not self.is_valsalva_analyzed:
            self.txt_valsalva_summary.setText("그래프 분석 전입니다. 버튼을 클릭해주세요.")
        else:
            p2l_mark = "(+)" if self.val_saved_chk_2l else "(-)"
            p4over_mark = "(+)" if self.val_saved_chk_4 else "(-)"
            self.txt_valsalva_summary.setText(f"Absence of Phase II_late {p2l_mark}\nAbsence of Phase IV overshoot {p4over_mark}")

        self.update_findings_and_analysis()

    def update_findings_and_analysis(self):
        if self.btn_ssr_palm.isChecked(): self.btn_ssr_palm.setText("Palm 비정상")
        else: self.btn_ssr_palm.setText("Palm 정상")
        
        if self.btn_ssr_sole.isChecked(): self.btn_ssr_sole.setText("Sole 비정상")
        else: self.btn_ssr_sole.setText("Sole 정상")

        input_data = ANSFTInput(
            patient=PatientInfo(age=self.patient_age),
            ssr=SSRData(palm_normal=not self.btn_ssr_palm.isChecked(), sole_normal=not self.btn_ssr_sole.isChecked()),
            hrdb=HRDBData(is_arrhythmia=self.chk_arrhythmia_hrdb.isChecked(), val1=self.hrdb_val1, val2=self.hrdb_val2),
            tilt=TiltData(records=self.tilt_data),
            valsalva=ValsalvaData(
                is_arrhythmia=self.chk_arrhythmia_val.isChecked(), is_analyzed=self.is_valsalva_analyzed,
                is_poor=self.val_saved_chk_poor, val_ratio=self.val_ratio, normal_val_ratio=self.normal_val_ratio,
                prt_sec=self.prt_sec, p2l_exists=self.val_saved_chk_2l, p4_exists=self.val_saved_chk_4, overshoot_state=self.val_saved_overshoot_state
            )
        )

        result_data = ANSFTEngine.analyze(input_data)
        f_text, a_text, c_text = ReportFormatter.format_report(input_data, result_data)
        
        self.txt_findings.setText(f_text)
        self.txt_analysis.setHtml(f"<div style='font-family: sans-serif; font-size: 13px; color: #2c3e50;'>{a_text.replace(chr(10), '<br>')}</div>")
        self.txt_conclusions.setText(c_text)
        
        self.current_findings_text, self.current_conclusion_text = f_text, c_text

    def toggle_watch(self):
        if self.btn_wait_image.isChecked():
            self.reset_all()
            self.btn_wait_image.setStyleSheet("padding: 10px; font-size: 14px; font-weight: bold; background-color: #f39c12; color: white; border: 1px solid #d68910; border-radius: 4px;")
            self.btn_wait_image.setText("다운로드 대기 중... (취소)")
            self.btn_wait_image.setChecked(True)
            self.watch_timer.start(3000) 
        else:
            self.watch_timer.stop()
            self.btn_wait_image.setStyleSheet("padding: 10px; font-size: 14px; font-weight: bold; background-color: #f1c40f; color: black; border: 1px solid #f39c12; border-radius: 4px;")
            self.btn_wait_image.setText("이미지 다운로드 대기")

    def check_for_new_files(self):
        today_str = datetime.now().strftime("%Y-%m-%d")
        target_dir = os.path.join(self.base_path, today_str)
        if not os.path.exists(target_dir): return
        try:
            current_files = self.get_all_files(self.base_path)
            new_files = current_files - self.previous_files
            if new_files:
                for f in new_files:
                    if today_str in f: self.session_new_files.add(f)
                self.previous_files = current_files
                if len(self.session_new_files) >= 5:
                    self.watch_timer.stop()
                    self.btn_wait_image.blockSignals(True); self.btn_wait_image.setChecked(False); self.btn_wait_image.blockSignals(False)
                    self.btn_wait_image.setStyleSheet("padding: 10px; font-size: 14px; font-weight: bold; background-color: #009688; color: white; border: 1px solid #00796B; border-radius: 4px;")
                    self.btn_wait_image.setText("다운로드 완료")
                    self.vision_handler.process_and_show_auto_images(list(self.session_new_files))
        except Exception as e:
            print(f"\n[Error] {traceback.format_exc()}"); self.watch_timer.stop()
            self.btn_wait_image.setText("오류 발생 (콘솔 확인)")

    def get_all_files(self, path):
        file_set = set()
        for root, dirs, files in os.walk(path):
            for file in files: file_set.add(os.path.join(root, file))
        return file_set

    def reset_all(self):
        self.watch_timer.stop()
        self.btn_wait_image.blockSignals(True); self.btn_wait_image.setChecked(False); self.btn_wait_image.blockSignals(False)
        self.btn_wait_image.setStyleSheet("padding: 10px; font-size: 14px; font-weight: bold; background-color: #f1c40f; color: black; border: 1px solid #f39c12; border-radius: 4px;")
        self.btn_wait_image.setText("이미지 다운로드 대기")
        self.session_new_files = set()
        self.val_saved_lines, self.val_yellow_min, self.val_yellow_max = None, None, None
        self.val_saved_chk_2l, self.val_saved_chk_4, self.val_saved_chk_poor, self.val_saved_overshoot_state = False, False, False, False 
        self.normal_val_ratio, self.is_valsalva_analyzed = "N/A", False 
        self.current_findings_text, self.current_conclusion_text = "", ""
        self.chk_arrhythmia_hrdb.setChecked(False); self.chk_arrhythmia_val.setChecked(False)
        self.btn_valsalva_graph.setStyleSheet("padding: 5px; font-weight: bold; background-color: #f1c40f; color: black; border-radius: 4px;")
        self.btn_valsalva_graph.setText("Valsalva 그래프 분석 (대기)")
        self.txt_valsalva_summary.clear()
        
        # [핵심 수정] SSR 버튼 상태 및 텍스트 초기화
        self.btn_ssr_palm.setChecked(False)
        self.btn_ssr_sole.setChecked(False)
        self.btn_ssr_palm.setText("Palm 정상")
        self.btn_ssr_sole.setText("Sole 정상")

        self.lbl_patient_image.setPixmap(QPixmap()); self.lbl_patient_image.setText("환자 정보")
        self.lbl_ssr_graph.setPixmap(QPixmap()); self.lbl_ssr_graph.setText("SSR")
        self.lbl_hrdb_image.setPixmap(QPixmap()); self.lbl_hrdb_image.setText("HRDB")
        self.lbl_tilt_image.setPixmap(QPixmap()); self.lbl_tilt_image.setText("Tilt")
        self.lbl_valsalva_image.setPixmap(QPixmap()); self.lbl_valsalva_image.setText("Valsalva")
        self.lbl_norm_ratio_image.setPixmap(QPixmap()); self.lbl_norm_ratio_image.setText("Norm Ratio")
        self.txt_hrdb_ocr.clear(); self.table_tilt.clearContents(); self.table_valsalva.clearContents()
        self.txt_findings.clear(); self.txt_analysis.clear(); self.txt_conclusions.clear()
        self.previous_files = self.get_all_files(self.base_path) if os.path.exists(self.base_path) else set()

    def open_valsalva_graph_window(self):
        if len(self.session_new_files) < 5: return
        cropped_cv_graph = ImageProcessor.crop_valsalva_graph(list(self.session_new_files))
        if cropped_cv_graph is None: return
        self.valsalva_window = ValsalvaGraphWindow(
            cv_img=cropped_cv_graph, return_callback=self.on_valsalva_analysis_done,
            saved_lines=self.val_saved_lines, saved_chk_2l=self.val_saved_chk_2l, saved_chk_4=self.val_saved_chk_4,
            yellow_min=self.val_yellow_min, yellow_max=self.val_yellow_max, saved_chk_poor=self.val_saved_chk_poor
        )
        self.valsalva_window.show()

    def on_valsalva_analysis_done(self, is_poor, p2_absent, p4_absent, overshoot_state, lines, y_min, y_max):
        self.val_saved_chk_poor, self.val_saved_chk_2l, self.val_saved_chk_4 = is_poor, p2_absent, p4_absent
        self.val_saved_lines, self.val_yellow_min, self.val_yellow_max = lines, y_min, y_max
        self.val_saved_overshoot_state = overshoot_state 
        self.is_valsalva_analyzed = True
        self.btn_valsalva_graph.setStyleSheet("padding: 5px; font-weight: bold; background-color: #3498db; color: white; border-radius: 4px;")
        self.btn_valsalva_graph.setText("Valsalva 그래프 분석 완료")
        if not self.chk_arrhythmia_val.isChecked():
            if is_poor: self.txt_valsalva_summary.setText("Poor valsalva maneuver")
            else:
                self.txt_valsalva_summary.setText(f"Absence of Phase II_late {'(+)' if p2_absent else '(-)'}\nAbsence of Phase IV overshoot {'(+)' if p4_absent else '(-)'}")
        self.update_findings_and_analysis()