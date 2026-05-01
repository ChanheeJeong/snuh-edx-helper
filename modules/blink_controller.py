import os
import traceback
import time
import keyboard 
import pyperclip
from datetime import datetime
from PyQt6.QtCore import QTimer, Qt
from PyQt6.QtGui import QPixmap
from PyQt6.QtWidgets import QTableWidgetItem

from models.blink_data import BlinkInput, ExcitabilityData, StimulationData, ReflexData, LSRData
from engine.blink_engine import BlinkEngine
from modules.blink_ui import BLINK_UI
from modules.blink_vision import BlinkVisionHandler

class BLINKWidget(BLINK_UI):
    def __init__(self, main_window): 
        super().__init__()
        self.main_window = main_window # [추가] 메인 윈도우 참조 저장
        
        self.base_path = r"C:\HIS_Image"
        self.previous_files = set()
        self.session_new_files = set()
        
        self.vision_handler = BlinkVisionHandler(self)
        
        self._is_updating = False
        self.current_findings_text = ""
        self.current_conclusion_text = ""
        
        self.setup_ui()
        self.connect_events()

    def connect_events(self):
        self.btn_reset.clicked.connect(self.reset_all)
        self.btn_wait_image.clicked.connect(self.toggle_watch)
        
        for val, btn in self.rt_exc_btns.items():
            btn.clicked.connect(lambda checked, v=val: self.on_exc_btn_clicked("rt", v))
        for val, btn in self.lt_exc_btns.items():
            btn.clicked.connect(lambda checked, v=val: self.on_exc_btn_clicked("lt", v))
            
        self.table_stim.itemChanged.connect(self.analyze_and_update)
        self.table_reflex.itemChanged.connect(self.analyze_and_update)
        
        self.chk_lsr_active.stateChanged.connect(self.on_lsr_active_changed)
        self.rdo_lsr_left.toggled.connect(self.analyze_and_update)
        self.rdo_lsr_right.toggled.connect(self.analyze_and_update)
        self.chk_lsr_path1.stateChanged.connect(self.analyze_and_update)
        self.chk_lsr_path2.stateChanged.connect(self.analyze_and_update)

        self.watch_timer = QTimer()
        self.watch_timer.timeout.connect(self.check_for_new_files)

    def update_fnet(self, rt_str, lt_str):
        self._is_updating = True
        for k, b in self.rt_exc_btns.items():
            b.setChecked(k == rt_str)
            b.setStyleSheet("background-color: #f1c40f; color: black; font-weight: bold;" if k == rt_str else "")
        for k, b in self.lt_exc_btns.items():
            b.setChecked(k == lt_str)
            b.setStyleSheet("background-color: #f1c40f; color: black; font-weight: bold;" if k == lt_str else "")
        self._is_updating = False

    def update_fnst(self, rt_lat, rt_amp, lt_lat, lt_amp):
        self._is_updating = True
        def set_item(r, c, val):
            item = QTableWidgetItem(str(val))
            item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            self.table_stim.setItem(r, c, item)
        set_item(0, 0, rt_lat)
        set_item(0, 1, rt_amp)
        set_item(1, 0, lt_lat)
        set_item(1, 1, lt_amp)
        self._is_updating = False

    def update_reflex(self, rt_vals, lt_vals):
        self._is_updating = True
        def set_item(r, c, val):
            item = QTableWidgetItem(str(val))
            item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            self.table_reflex.setItem(r, c, item)
        for i in range(3):
            set_item(0, i, rt_vals[i])
            set_item(1, i, lt_vals[i])
        self._is_updating = False

    def on_exc_btn_clicked(self, side, value):
        if self._is_updating: return
        self._is_updating = True
        btns = self.rt_exc_btns if side == "rt" else self.lt_exc_btns
        for k, b in btns.items():
            if k != value:
                b.setChecked(False)
                b.setStyleSheet("")
            else:
                b.setStyleSheet("background-color: #f1c40f; color: black; font-weight: bold;")
        self._is_updating = False
        self.analyze_and_update()

    def on_lsr_active_changed(self):
        is_active = self.chk_lsr_active.isChecked()
        self.toggle_lsr_controls(is_active)
        self.analyze_and_update()

    def _get_float_from_table(self, table, row, col):
        item = table.item(row, col)
        if item and item.text().strip():
            try: return float(item.text().strip())
            except ValueError: return None
        return None

    def analyze_and_update(self, *args):
        if self._is_updating: return
        
        b_input = BlinkInput()
        rt_exc = next((k for k, b in self.rt_exc_btns.items() if b.isChecked()), None)
        lt_exc = next((k for k, b in self.lt_exc_btns.items() if b.isChecked()), None)
        b_input.excitability = ExcitabilityData(rt_val=rt_exc, lt_val=lt_exc)
        
        b_input.rt_stim = StimulationData(lat=self._get_float_from_table(self.table_stim, 0, 0), amp=self._get_float_from_table(self.table_stim, 0, 1))
        b_input.lt_stim = StimulationData(lat=self._get_float_from_table(self.table_stim, 1, 0), amp=self._get_float_from_table(self.table_stim, 1, 1))
        
        b_input.rt_reflex = ReflexData(r1=self._get_float_from_table(self.table_reflex, 0, 0), r2i=self._get_float_from_table(self.table_reflex, 0, 1), r2c=self._get_float_from_table(self.table_reflex, 0, 2))
        b_input.lt_reflex = ReflexData(r1=self._get_float_from_table(self.table_reflex, 1, 0), r2i=self._get_float_from_table(self.table_reflex, 1, 1), r2c=self._get_float_from_table(self.table_reflex, 1, 2))
        
        side_str = "Left" if self.rdo_lsr_left.isChecked() else "Right"
        b_input.lsr = LSRData(
            active=self.chk_lsr_active.isChecked(),
            side=side_str,
            oculi_to_mentalis=self.chk_lsr_path1.isChecked(),
            mentalis_to_oculi=self.chk_lsr_path2.isChecked()
        )
        
        res = BlinkEngine.analyze(b_input)
        
        self.current_findings_text = res.findings_text
        self.txt_findings.setText(res.findings_text)
        
        if res.conclusion_text:
            self.current_conclusion_text = f"{res.conclusion_text}\n\n**현재 가판독 상태이며 추후 정식 판독을 참조하기 바람."
            self.txt_conclusions.setText(self.current_conclusion_text)
        else:
            self.current_conclusion_text = ""
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
        if not os.path.exists(target_dir): return
            
        try:
            current_files = self.get_all_files(self.base_path)
            new_files = current_files - self.previous_files
            
            if new_files:
                for f in new_files:
                    if today in f: self.session_new_files.add(f)
                        
                self.previous_files = current_files
                has_target = any(name.endswith("_1.png") or name.endswith("_1.jpg") or name.endswith("_1") or "_1." in name for name in [f.lower() for f in self.session_new_files])
                
                if has_target:
                    self.watch_timer.stop()
                    self.btn_wait_image.blockSignals(True)
                    self.btn_wait_image.setChecked(False)
                    self.btn_wait_image.blockSignals(False)
                    self.btn_wait_image.setStyleSheet("padding: 10px; font-size: 14px; font-weight: bold; background-color: #009688; color: white; border: 1px solid #00796B; border-radius: 4px;")
                    self.btn_wait_image.setText("다운로드 완료")
                    
                    self.vision_handler.process_and_show_auto_images(list(self.session_new_files))
        except Exception as e:
            print(f"\n[Blink Error] {traceback.format_exc()}")
            self.watch_timer.stop()
            self.btn_wait_image.setText("오류 발생 (콘솔 확인)")

    def get_all_files(self, path):
        file_set = set()
        for r, d, f in os.walk(path):
            for file in f: file_set.add(os.path.join(r, file))
        return file_set

    def reset_all(self):
        self._is_updating = True
        self.watch_timer.stop()
        
        self.btn_wait_image.blockSignals(True)
        self.btn_wait_image.setChecked(False)
        self.btn_wait_image.blockSignals(False)
        self.btn_wait_image.setStyleSheet("padding: 10px; font-size: 14px; font-weight: bold; background-color: #f1c40f; color: black; border: 1px solid #f39c12; border-radius: 4px;")
        self.btn_wait_image.setText("이미지 다운로드 대기")
        self.session_new_files = set()
        
        for btn in self.rt_exc_btns.values(): btn.setChecked(False); btn.setStyleSheet("")
        for btn in self.lt_exc_btns.values(): btn.setChecked(False); btn.setStyleSheet("")
        
        self.lbl_stim_image.setPixmap(QPixmap()); self.lbl_stim_image.setText("FNST 원본 캡처")
        self.lbl_reflex_img_rt.setPixmap(QPixmap()); self.lbl_reflex_img_rt.setText("Blink Rt 캡처")
        self.lbl_reflex_img_lt.setPixmap(QPixmap()); self.lbl_reflex_img_lt.setText("Blink Lt 캡처")
        
        self.table_stim.clearContents()
        self.table_reflex.clearContents()
        
        self.chk_lsr_active.setChecked(False)
        self.chk_lsr_path1.setChecked(False)
        self.chk_lsr_path2.setChecked(False)
        self.rdo_lsr_right.setChecked(True)
        
        self.txt_findings.clear()
        self.txt_conclusions.clear()
        self.current_findings_text = ""
        self.current_conclusion_text = ""
        
        self.previous_files = self.get_all_files(self.base_path) if os.path.exists(self.base_path) else set()
        self._is_updating = False
        self.toggle_lsr_controls(False)