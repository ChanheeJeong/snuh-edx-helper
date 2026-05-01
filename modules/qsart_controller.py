import os
import traceback
import time
import keyboard 
import pyperclip
from datetime import datetime
from PyQt6.QtCore import QTimer, Qt
from PyQt6.QtGui import QPixmap, QColor, QBrush
from PyQt6.QtWidgets import QTableWidgetItem

from models.qsart_data import QSARTInput, QsartSiteData
from engine.qsart_engine import QSARTEngine
from modules.qsart_ui import QSART_UI
from modules.qsart_vision import QsartVisionHandler

class QSARTWidget(QSART_UI):
    def __init__(self, main_window): 
        super().__init__()
        self.main_window = main_window # [추가] 메인 윈도우 참조 저장
        
        self.base_path = r"C:\HIS_Image"
        self.previous_files = set()
        self.session_new_files = set()
        
        self.vision_handler = QsartVisionHandler(self)
        
        self.patient_sex = "N/A"
        
        self.left_volumes = ["N/A"] * 4
        self.right_volumes = ["N/A"] * 4
        self.left_pixmap = QPixmap()
        self.right_pixmap = QPixmap()
        
        self.volumes_data = ["N/A"] * 4 
        self._is_updating_table = False
        
        self.current_findings_text = ""
        self.current_conclusion_text = ""
        
        self.setup_ui()

        self.btn_reset.clicked.connect(self.reset_all) 
        self.btn_wait_image.clicked.connect(self.toggle_watch)
        self.btn_sex_toggle.clicked.connect(self.on_sex_toggled)
        self.table_qsart.itemChanged.connect(self.on_table_changed)

        self.btn_side_left.clicked.connect(self.on_side_left_clicked)
        self.btn_side_right.clicked.connect(self.on_side_right_clicked)
        self.set_side("left") 

        for chk in self.chk_persistent:
            chk.stateChanged.connect(self.analyze_and_render_table)

        self.watch_timer = QTimer()
        self.watch_timer.timeout.connect(self.check_for_new_files)

        self.txt_findings.clear()
        self.txt_conclusions.clear()

    def macro_type_conclusion(self):
        if not self.current_findings_text or not self.current_conclusion_text:
            return
            
        # [추가] 메인 윈도우에서 현재 탭에 맞는 서명 가져오기
        signature = self.main_window.signature_tool.get_signature()
            
        pyperclip.copy(self.current_findings_text)
        time.sleep(0.2); keyboard.send('ctrl+v'); time.sleep(0.2); keyboard.send('tab'); time.sleep(0.2) 
        
        pyperclip.copy(self.current_conclusion_text)
        time.sleep(0.2); keyboard.send('ctrl+v'); time.sleep(0.2); keyboard.send('tab'); time.sleep(0.2)

        # [수정] 고정 문자열 대신 가져온 서명 변수(signature) 사용
        pyperclip.copy(signature)
        time.sleep(0.2); keyboard.send('ctrl+v')

    def set_side(self, side_str):
        self.btn_side_left.blockSignals(True)
        self.btn_side_right.blockSignals(True)
        
        uncheck_css = "font-weight: bold; background-color: #ecf0f1; color: #7f8c8d; border-radius: 4px;"
        check_css = "font-weight: bold; background-color: #9b59b6; color: white; border-radius: 4px;"
        
        if side_str == "left":
            self.btn_side_left.setChecked(True)
            self.btn_side_left.setStyleSheet(check_css)
            self.btn_side_right.setChecked(False)
            self.btn_side_right.setStyleSheet(uncheck_css)
        else:
            self.btn_side_right.setChecked(True)
            self.btn_side_right.setStyleSheet(check_css)
            self.btn_side_left.setChecked(False)
            self.btn_side_left.setStyleSheet(uncheck_css)
            
        self.btn_side_left.blockSignals(False)
        self.btn_side_right.blockSignals(False)
        
        self._apply_side_data()

    def on_side_left_clicked(self):
        self.set_side("left")

    def on_side_right_clicked(self):
        self.set_side("right")

    def set_patient_sex(self, sex_str):
        self.patient_sex = sex_str
        self.btn_sex_toggle.blockSignals(True)
        
        if sex_str == "N/A":
            self.btn_sex_toggle.setChecked(False)
            self.btn_sex_toggle.setText("성별: N/A")
            self.btn_sex_toggle.setStyleSheet("font-weight: bold; background-color: #95a5a6; color: white; border-radius: 4px;")
        elif sex_str == "Female":
            self.btn_sex_toggle.setChecked(True)
            self.btn_sex_toggle.setText("성별: Female")
            self.btn_sex_toggle.setStyleSheet("font-weight: bold; background-color: #e74c3c; color: white; border-radius: 4px;")
        else:
            self.btn_sex_toggle.setChecked(False)
            self.btn_sex_toggle.setText("성별: Male")
            self.btn_sex_toggle.setStyleSheet("font-weight: bold; background-color: #3498db; color: white; border-radius: 4px;")
            
        self.btn_sex_toggle.blockSignals(False)
        self.analyze_and_render_table()

    def on_sex_toggled(self):
        if self.patient_sex == "Male":
            self.set_patient_sex("Female")
        else:
            self.set_patient_sex("Male")

    def store_table_data(self, left_vols, right_vols, left_pix, right_pix):
        self.left_volumes = left_vols
        self.right_volumes = right_vols
        
        target_width = self.frame_table_image.width() or 600
        self.left_pixmap = left_pix.scaledToWidth(target_width, Qt.TransformationMode.SmoothTransformation)
        self.right_pixmap = right_pix.scaledToWidth(target_width, Qt.TransformationMode.SmoothTransformation)
        
        # =====================================================================
        # [자동 스위칭 로직] OCR 데이터 검증
        # =====================================================================
        def count_valid(vols):
            count = 0
            for v in vols:
                v_str = str(v).replace(" ", "")
                if v_str != "N/A" and v_str != "":
                    count += 1
            return count
            
        left_valid_count = count_valid(self.left_volumes)
        right_valid_count = count_valid(self.right_volumes)
        
        # 둘 중 한쪽만 제대로 인식이 되었다면 그 방향으로 자동 전환
        if left_valid_count == 0 and right_valid_count > 0:
            self.set_side("right")
        elif right_valid_count == 0 and left_valid_count > 0:
            self.set_side("left")
        else:
            self._apply_side_data()

    def _apply_side_data(self):
        side = "left" if self.btn_side_left.isChecked() else "right"
        
        if side == "left":
            self.volumes_data = list(self.left_volumes)
            if not self.left_pixmap.isNull():
                self.lbl_table_image.setPixmap(self.left_pixmap)
        else:
            self.volumes_data = list(self.right_volumes)
            if not self.right_pixmap.isNull():
                self.lbl_table_image.setPixmap(self.right_pixmap)
                
        self.analyze_and_render_table()

    def on_table_changed(self, item):
        if self._is_updating_table:
            return
            
        if item.column() == 0:
            new_val = item.text().strip()
            row = item.row()
            
            self.volumes_data[row] = new_val
            
            # 수정한 방향의 원본 배열도 업데이트하여 왔다갔다 해도 유지되게 함
            side = "left" if self.btn_side_left.isChecked() else "right"
            if side == "left":
                self.left_volumes[row] = new_val
            else:
                self.right_volumes[row] = new_val
                
            self.analyze_and_render_table()

    def analyze_and_render_table(self):
        self._is_updating_table = True
        
        side = "left" if self.btn_side_left.isChecked() else "right"
        q_inp = QSARTInput(sex=self.patient_sex, side=side)
        
        for i in range(4):
            v_str = self.volumes_data[i]
            site = QsartSiteData(volume_str=v_str, is_persistent=self.chk_persistent[i].isChecked())
            try:
                if v_str and v_str != "N/A":
                    site.volume_float = float(v_str)
                    site.is_valid = True
            except ValueError:
                pass
            q_inp.volumes[i] = site

        res = QSARTEngine.analyze(q_inp)
        
        for i in range(4):
            r = res.site_results[i]
            
            item_vol = QTableWidgetItem(self.volumes_data[i])
            item_vol.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            self.table_qsart.setItem(i, 0, item_vol)
            
            item_range = QTableWidgetItem(r.norm_range_str)
            item_range.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            item_range.setFlags(item_range.flags() & ~Qt.ItemFlag.ItemIsEditable)
            self.table_qsart.setItem(i, 1, item_range)
            
            stat_item = QTableWidgetItem(r.status)
            stat_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            stat_item.setFlags(stat_item.flags() & ~Qt.ItemFlag.ItemIsEditable)
            
            font = stat_item.font()
            font.setBold(True)
            stat_item.setFont(font)
            
            color_hex = "#2c3e50" 
            if r.status == "Normal":
                color_hex = "#27ae60" 
            elif r.status in ["Reduced", "Increased"]:
                color_hex = "#e74c3c" 
            
            stat_item.setForeground(QBrush(QColor(color_hex)))
            self.table_qsart.setItem(i, 2, stat_item)
            
            self.group_boxes[i].setStyleSheet(f"QGroupBox {{ font-weight: bold; color: {color_hex}; }}")

        if res.findings_text:
            self.current_findings_text = res.findings_text
            self.txt_findings.setText(res.findings_text)
        else:
            self.current_findings_text = ""
            self.txt_findings.clear()
        
        if res.conclusion_text:
            self.current_conclusion_text = f"{res.conclusion_text}\n\n**현재 가판독 상태이며 추후 정식 판독을 참조하기 바람."
            self.txt_conclusions.setText(self.current_conclusion_text)
        else:
            self.current_conclusion_text = ""
            self.txt_conclusions.clear()
            
        self._is_updating_table = False

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
        today = datetime.now().strftime("%Y-%m-%d")
        target_dir = os.path.join(self.base_path, today)
        
        if not os.path.exists(target_dir):
            return
        
        try:
            current_files = self.get_all_files(self.base_path)
            new_files = current_files - self.previous_files
            
            if new_files:
                for f in new_files:
                    if today in f:
                        self.session_new_files.add(f)
                
                self.previous_files = current_files
                
                if len(self.session_new_files) >= 3:
                    self.watch_timer.stop()
                    
                    self.btn_wait_image.blockSignals(True)
                    self.btn_wait_image.setChecked(False)
                    self.btn_wait_image.blockSignals(False)
                    
                    self.btn_wait_image.setStyleSheet("padding: 10px; font-size: 14px; font-weight: bold; background-color: #009688; color: white; border: 1px solid #00796B; border-radius: 4px;")
                    self.btn_wait_image.setText("다운로드 완료")
                    
                    self.vision_handler.process_and_show_auto_images(list(self.session_new_files))
                    
        except Exception as e:
            print(f"\n[QSART Error] {traceback.format_exc()}")
            self.watch_timer.stop()
            self.btn_wait_image.setText("오류 발생 (콘솔 확인)")

    def get_all_files(self, path):
        file_set = set()
        for r, d, f in os.walk(path):
            for file in f:
                file_set.add(os.path.join(r, file))
        return file_set

    def reset_all(self):
        self.watch_timer.stop()
        
        self.btn_wait_image.blockSignals(True)
        self.btn_wait_image.setChecked(False)
        self.btn_wait_image.blockSignals(False)
        
        self.btn_wait_image.setStyleSheet("padding: 10px; font-size: 14px; font-weight: bold; background-color: #f1c40f; color: black; border: 1px solid #f39c12; border-radius: 4px;")
        self.btn_wait_image.setText("이미지 다운로드 대기")
        self.session_new_files = set()
        
        self.lbl_patient_image.setPixmap(QPixmap())
        self.lbl_patient_image.setText("환자 정보")
        self.lbl_table_image.setPixmap(QPixmap())
        self.lbl_table_image.setText("표 대기 중")
        
        self.set_patient_sex("N/A")
        
        self.left_volumes = ["N/A"] * 4
        self.right_volumes = ["N/A"] * 4
        self.left_pixmap = QPixmap()
        self.right_pixmap = QPixmap()
        self.volumes_data = ["N/A"] * 4
        
        self.set_side("left")
        
        for i, lbl in enumerate(self.lbl_graphs):
            lbl.setPixmap(QPixmap())
            lbl.setText("그래프 대기중")
            self.group_boxes[i].setStyleSheet("QGroupBox { font-weight: bold; color: #2c3e50; }")
            self.chk_persistent[i].setChecked(False)
            
        self.table_qsart.clearContents()
        self.current_findings_text = ""
        self.current_conclusion_text = ""
        self.txt_findings.clear()
        self.txt_conclusions.clear()
        
        self.previous_files = self.get_all_files(self.base_path) if os.path.exists(self.base_path) else set()