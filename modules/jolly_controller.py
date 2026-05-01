import time
import keyboard
import pyperclip
from modules.jolly_ui import JOLLY_UI
from models.jolly_data import JollyInput
from engine.jolly_engine import JollyEngine

class JOLLYWidget(JOLLY_UI):
    def __init__(self, main_window):
        super().__init__()
        self.main_window = main_window 
        self._is_updating = False
        self.current_findings_text = ""
        self.current_conclusion_text = ""
        
        self.setup_ui()
        self.connect_events()
        
        # 초기화 시 좌측 버튼 활성화
        self.btn_side_left.setChecked(True)
        self.on_side_changed() 

    def connect_events(self):
        self.btn_reset.clicked.connect(self.reset_all)
        
        self.side_btn_group.buttonClicked.connect(self.on_side_changed)
        self.chk_add_trapezius.stateChanged.connect(self.on_add_trapezius_changed)
        
        self.rdo_low_normal.toggled.connect(self.on_low_mode_changed)
        self.rdo_high_normal.toggled.connect(self.on_high_mode_changed)
        
        self.rdo_high_dec.toggled.connect(self.analyze_and_update)
        self.rdo_high_inc.toggled.connect(self.analyze_and_update)
        
        for chk in [self.chk_low_oculi, self.chk_low_adq, self.chk_low_fcu, self.chk_low_trap, self.chk_high_adq, self.chk_high_fcu]:
            chk.stateChanged.connect(self.analyze_and_update)

    def on_side_changed(self):
        if self.btn_side_left.isChecked():
            self.btn_side_left.setStyleSheet("background-color: #3498db; color: white; font-weight: bold; font-size: 15px;")
            self.btn_side_right.setStyleSheet("background-color: #ecf0f1; color: #7f8c8d; font-weight: bold; font-size: 15px;")
        else:
            self.btn_side_right.setStyleSheet("background-color: #3498db; color: white; font-weight: bold; font-size: 15px;")
            self.btn_side_left.setStyleSheet("background-color: #ecf0f1; color: #7f8c8d; font-weight: bold; font-size: 15px;")
        self.analyze_and_update()

    def on_add_trapezius_changed(self):
        is_checked = self.chk_add_trapezius.isChecked()
        self.chk_low_trap.setVisible(is_checked)
        
        if not is_checked:
            self._is_updating = True
            self.chk_low_trap.setChecked(False)
            self._is_updating = False
            
        self.analyze_and_update()

    def on_low_mode_changed(self):
        if self._is_updating: return
        is_normal = self.rdo_low_normal.isChecked()
        for chk in [self.chk_low_oculi, self.chk_low_adq, self.chk_low_fcu, self.chk_low_trap]:
            chk.setEnabled(not is_normal)
            if is_normal: 
                self._is_updating = True
                chk.setChecked(False)
                self._is_updating = False
        self.analyze_and_update()

    def on_high_mode_changed(self):
        if self._is_updating: return
        is_normal = self.rdo_high_normal.isChecked()
        
        self.rdo_high_dec.setEnabled(not is_normal)
        self.rdo_high_inc.setEnabled(not is_normal)
        
        for chk in [self.chk_high_adq, self.chk_high_fcu]:
            chk.setEnabled(not is_normal)
            if is_normal:
                self._is_updating = True
                chk.setChecked(False)
                self._is_updating = False
        self.analyze_and_update()

    def analyze_and_update(self, *args):
        if self._is_updating: return
        
        high_type = "decremental" if self.rdo_high_dec.isChecked() else "incremental"
        
        j_input = JollyInput(
            side="Left" if self.btn_side_left.isChecked() else "Right",
            low_freq_normal=self.rdo_low_normal.isChecked(),
            high_freq_normal=self.rdo_high_normal.isChecked(),
            low_oculi=self.chk_low_oculi.isChecked(),
            low_adq=self.chk_low_adq.isChecked(),
            low_fcu=self.chk_low_fcu.isChecked(),
            test_trapezius=self.chk_add_trapezius.isChecked(),
            low_trapezius=self.chk_low_trap.isChecked(),
            high_fcu=self.chk_high_fcu.isChecked(),
            high_adq=self.chk_high_adq.isChecked(),
            high_abnormal_type=high_type
        )
        res = JollyEngine.analyze(j_input)
        self.current_findings_text = res.findings_text
        self.current_conclusion_text = res.conclusion_text
        self.txt_findings.setText(self.current_findings_text)
        self.txt_conclusions.setText(self.current_conclusion_text)

    def macro_type_conclusion(self):
        if not self.current_findings_text or not self.current_conclusion_text: return
        
        signature = self.main_window.signature_tool.get_signature()

        pyperclip.copy(self.current_findings_text)
        time.sleep(0.2); keyboard.send('ctrl+v'); time.sleep(0.2); keyboard.send('tab'); time.sleep(0.2) 
        pyperclip.copy(self.current_conclusion_text)
        time.sleep(0.2); keyboard.send('ctrl+v'); time.sleep(0.2); keyboard.send('tab'); time.sleep(0.2)
        pyperclip.copy(signature)
        time.sleep(0.2); keyboard.send('ctrl+v')

    def reset_all(self):
        self._is_updating = True
        
        self.btn_side_left.setChecked(True)
        self.on_side_changed()
        
        self.rdo_low_normal.setChecked(True)
        self.rdo_high_normal.setChecked(True)
        self.chk_add_trapezius.setChecked(False)
        self.rdo_high_dec.setChecked(True)
        
        for chk in [self.chk_low_oculi, self.chk_low_adq, self.chk_low_fcu, self.chk_low_trap, self.chk_high_adq, self.chk_high_fcu]:
            chk.setChecked(False); chk.setEnabled(False)
            
        self._is_updating = False
        self.analyze_and_update()