import keyboard
import time
from PyQt6.QtWidgets import QApplication
from PyQt6.QtCore import QTimer
from modules.emg_ui import EMG_UI
from models.emg_data import (
    UE_ORDER, UE_MUSCLES, UE_TABS, UE_DEFAULT,
    LE_ORDER, LE_MUSCLES, LE_TABS, LE_DEFAULT
)

class EMGWidget(EMG_UI):
    def __init__(self, main_window):
        super().__init__()
        self.main_window = main_window
        self.setup_ui()
        self.connect_events()
        self.setup_hotkeys()

    def connect_events(self):
        self.btn_reset.clicked.connect(self.reset_all)
        self.btn_ue_default.clicked.connect(self.set_ue_default)
        self.btn_le_default.clicked.connect(self.set_le_default)

    def setup_hotkeys(self):
        # [수정] 단축키를 요청하신 U와 L로 변경
        keyboard.add_hotkey('ctrl+shift+u', self.fill_ue_table)
        keyboard.add_hotkey('ctrl+shift+l', self.fill_le_table)

    def set_ue_default(self):
        for muscle, btn in self.ue_btns.items():
            btn.setChecked(muscle in UE_DEFAULT)

    def set_le_default(self):
        for muscle, btn in self.le_btns.items():
            btn.setChecked(muscle in LE_DEFAULT)

    def reset_all(self):
        for btn in self.ue_btns.values(): btn.setChecked(False)
        for btn in self.le_btns.values(): btn.setChecked(False)
        self.set_status_ready()

    def set_status_ready(self):
        self.lbl_status.setText("대기 중... (EMR에 커서를 두고 단축키를 누르세요)")
        self.lbl_status.setStyleSheet("color: #7f8c8d; font-weight: bold; font-size: 13px;")

    def _execute_macro(self, muscle_order, btn_dict, muscle_data, tab_map, limb_name):
        """선생님의 오리지널 로직을 그대로 구현한 핵심 매크로 함수"""
        self.lbl_status.setText(f"{limb_name} EMG 양식 작성 중... (키보드/마우스를 건드리지 마세요)")
        self.lbl_status.setStyleSheet("color: #e67e22; font-weight: bold; font-size: 14px;")
        QApplication.processEvents() # UI 업데이트 강제 실행
        
        # 사용자가 EMR 클릭할 시간 1초 부여 (기존 3초에서 단축, 필요시 늘리세요)
        time.sleep(1) 
        
        for muscle in muscle_order:
            tabs_total = tab_map.get(muscle, 6)
            is_checked = btn_dict[muscle].isChecked()
            
            if is_checked:
                data = muscle_data[muscle]
                keyboard.write(data.root); time.sleep(0.05); keyboard.send('tab'); time.sleep(0.05)
                keyboard.write(data.nerve); time.sleep(0.05); keyboard.send('tab'); time.sleep(0.05)
                keyboard.write("N"); time.sleep(0.05)
                
                # 이미 2번의 Tab을 썼으므로 나머지만 누름
                for _ in range(tabs_total - 2):
                    keyboard.send('tab'); time.sleep(0.05)
            else:
                # 체크 안 된 근육은 내용 없이 통째로 Tab만 눌러서 다음 줄로 점프
                for _ in range(tabs_total):
                    keyboard.send('tab'); time.sleep(0.05)
                    
        self.lbl_status.setText(f"완료! {limb_name} 양식이 입력되었습니다.")
        self.lbl_status.setStyleSheet("color: #2ecc71; font-weight: bold; font-size: 14px;")
        QTimer.singleShot(3000, self.set_status_ready) # 3초 후 상태 복귀

    def fill_ue_table(self):
        self._execute_macro(UE_ORDER, self.ue_btns, UE_MUSCLES, UE_TABS, "Upper Extremity")

    def fill_le_table(self):
        self._execute_macro(LE_ORDER, self.le_btns, LE_MUSCLES, LE_TABS, "Lower Extremity")