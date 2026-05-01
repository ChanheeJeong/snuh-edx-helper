from PyQt6.QtWidgets import QApplication
from models.ncs_simple_data import NCSSimpleInput
from engine.ncs_simple_engine import NCSSimpleEngine
from modules.ncs_simple_ui import NCSSimple_UI
import time
import keyboard
import pyperclip

class NCSSimpleWidget(NCSSimple_UI):
    def __init__(self, main_window):
        super().__init__()
        self.main_window = main_window
        self.current_conclusion_text = ""
        self._is_updating = False
        
        # [추가] 가판 문구 상수
        self.DISCLAIMER = "**현재 가판독 상태이며 추후 정식 판독을 참조하기 바람."
        
        self.setup_ui()
        self.connect_events()
        self.analyze_and_update()

    def connect_events(self):
        self.btn_reset.clicked.connect(self.reset_all)
        
        # 검사 부위 버튼
        for btn in [self.btn_eval_lue, self.btn_eval_rue, self.btn_eval_lle, self.btn_eval_rle]:
            btn.toggled.connect(self.on_eval_changed)
            
        # 패턴 변경
        self.rdo_group.buttonClicked.connect(self.on_pattern_changed)
        self.chk_demyelinating.stateChanged.connect(self.analyze_and_update)
        
        # 이상 부위 버튼
        for btn in [self.btn_abnorm_lue, self.btn_abnorm_rue, self.btn_abnorm_lle, self.btn_abnorm_rle]:
            btn.toggled.connect(self.analyze_and_update)

    def on_eval_changed(self):
        if self._is_updating: return
        self._is_updating = True
        if not self.btn_eval_lue.isChecked(): self.btn_abnorm_lue.setChecked(False); self.btn_abnorm_lue.setEnabled(False)
        if not self.btn_eval_rue.isChecked(): self.btn_abnorm_rue.setChecked(False); self.btn_abnorm_rue.setEnabled(False)
        if not self.btn_eval_lle.isChecked(): self.btn_abnorm_lle.setChecked(False); self.btn_abnorm_lle.setEnabled(False)
        if not self.btn_eval_rle.isChecked(): self.btn_abnorm_rle.setChecked(False); self.btn_abnorm_rle.setEnabled(False)
        self._is_updating = False
        self.on_pattern_changed(None)

    def on_pattern_changed(self, btn):
        if self._is_updating: return
        self._is_updating = True
        
        self.chk_demyelinating.setEnabled(False)
        for b in [self.btn_abnorm_lue, self.btn_abnorm_rue, self.btn_abnorm_lle, self.btn_abnorm_rle]:
            b.setEnabled(False)
            b.setChecked(False)
            
        if self.rdo_smpn.isChecked():
            self.chk_demyelinating.setEnabled(True)
        elif self.rdo_cts.isChecked():
            if self.btn_eval_lue.isChecked(): self.btn_abnorm_lue.setEnabled(True)
            if self.btn_eval_rue.isChecked(): self.btn_abnorm_rue.setEnabled(True)
        elif self.rdo_plantar.isChecked():
            if self.btn_eval_lle.isChecked(): self.btn_abnorm_lle.setEnabled(True)
            if self.btn_eval_rle.isChecked(): self.btn_abnorm_rle.setEnabled(True)

        self._is_updating = False
        self.analyze_and_update()

    def analyze_and_update(self, *args):
        if self._is_updating: return
        
        pattern_str = "Normal"
        if self.rdo_smpn.isChecked(): pattern_str = "SMPN"
        elif self.rdo_cts.isChecked(): pattern_str = "CTS"
        elif self.rdo_plantar.isChecked(): pattern_str = "Plantar"
        
        input_data = NCSSimpleInput(
            eval_lue=self.btn_eval_lue.isChecked(),
            eval_rue=self.btn_eval_rue.isChecked(),
            eval_lle=self.btn_eval_lle.isChecked(),
            eval_rle=self.btn_eval_rle.isChecked(),
            pattern=pattern_str,
            is_demyelinating=self.chk_demyelinating.isChecked(),
            abnorm_lue=self.btn_abnorm_lue.isChecked(),
            abnorm_rue=self.btn_abnorm_rue.isChecked(),
            abnorm_lle=self.btn_abnorm_lle.isChecked(),
            abnorm_rle=self.btn_abnorm_rle.isChecked()
        )
        
        res = NCSSimpleEngine.analyze(input_data)
        self.current_conclusion_text = res.conclusion_text
        
        # [수정] 화면 표출 시 서명 대신 가판 문구(Disclaimer) 사용
        display_text = f"{self.current_conclusion_text}\n\n{self.DISCLAIMER}"
        self.txt_conclusion.setText(display_text)

    def macro_type_conclusion(self):
        """EMR 입력 매크로 (결론 -> Tab -> 서명)"""
        if not self.current_conclusion_text: return
        signature = self.main_window.signature_tool.get_signature()
        
        # 1. 결론 붙여넣기 (가판 문구 제외 순수 결론)
        pyperclip.copy(self.current_conclusion_text)
        time.sleep(0.2); keyboard.send('ctrl+v'); time.sleep(0.2)
        
        # 2. 다음 칸(서명란)으로 이동
        keyboard.send('tab'); time.sleep(0.2)
        
        # 3. 서명 붙여넣기
        pyperclip.copy(signature)
        time.sleep(0.2); keyboard.send('ctrl+v')

    def reset_all(self):
        self._is_updating = True
        
        # [수정] 리셋 시 모두 선택 해제
        for btn in [self.btn_eval_lue, self.btn_eval_rue, self.btn_eval_lle, self.btn_eval_rle]:
            btn.setChecked(False) 
            
        self.rdo_normal.setChecked(True)
        self.chk_demyelinating.setChecked(False); self.chk_demyelinating.setEnabled(False)
        
        for btn in [self.btn_abnorm_lue, self.btn_abnorm_rue, self.btn_abnorm_lle, self.btn_abnorm_rle]:
            btn.setChecked(False); btn.setEnabled(False)
            
        self._is_updating = False
        self.analyze_and_update()