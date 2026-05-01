import sys
import keyboard 
from PyQt6.QtWidgets import (QApplication, QMainWindow, QWidget, 
                             QVBoxLayout, QHBoxLayout, QTabWidget, QLabel, QDialog) # QDialog 추가
from PyQt6.QtCore import Qt

from modules.ncs_simple_controller import NCSSimpleWidget
from modules.emg_controller import EMGWidget
from modules.ansft_controller import ANSFTWidget
from modules.qsart_controller import QSARTWidget
from modules.blink_controller import BLINKWidget
from modules.jolly_controller import JOLLYWidget
from modules.pft_controller import PFTWidget
from tools.signature_tool import SignatureTool
from tools.preliminary_tool import PreliminaryTool 
from tools.path_clear_tool import PathClearTool

# [추가] Splash Screen 임포트
from modules.splash_screen import SplashScreen

class ANSFTWindow(QMainWindow):
    # [수정] 초기화 시 resident_name 파라미터 추가
    def __init__(self, resident_name="R3 정찬희"):
        super().__init__()
        self.resident_name = resident_name
        
        self.setWindowTitle("SNUH EDX Helper")
        self.setGeometry(100, 100, 1250, 950)
        self.setMinimumSize(1250, 950)

        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)
        self.layout = QVBoxLayout()
        self.central_widget.setLayout(self.layout)

        self.main_tabs = QTabWidget()
        self.layout.addWidget(self.main_tabs)

        self.corner_widget_container = QWidget()
        self.corner_layout = QHBoxLayout(self.corner_widget_container)
        
        self.corner_layout.setContentsMargins(0, 0, 10, 0) 
        self.corner_layout.setSpacing(10) 
        
        self.lbl_macro_guide = QLabel("종합 (Ctrl+Shift+Q): Findings + Conclusion + Signature")
        self.lbl_macro_guide.setStyleSheet("color: #2980b9; font-weight: bold; font-size: 13px; padding-right: 15px;")

        self.preliminary_tool = PreliminaryTool(self)
        
        # [수정] SignatureTool에 선택된 사용자 이름 넘겨주기
        self.signature_tool = SignatureTool(self, resident_name=self.resident_name)
        
        self.corner_layout.addWidget(self.lbl_macro_guide)
        self.corner_layout.addWidget(self.preliminary_tool)
        self.corner_layout.addWidget(self.signature_tool)
        
        self.main_tabs.setCornerWidget(self.corner_widget_container)

        self.setup_tabs()
        self.main_tabs.currentChanged.connect(self.on_main_tab_changed)

        self.signature_tool.update_signature("NCS")

        keyboard.add_hotkey('ctrl+shift+q', self.execute_active_macro)

    def execute_active_macro(self):
        main_index = self.main_tabs.currentIndex()
        current_sub_tab_widget = self.main_tabs.widget(main_index)
        
        if isinstance(current_sub_tab_widget, QTabWidget):
            sub_index = current_sub_tab_widget.currentIndex()
            active_widget = current_sub_tab_widget.widget(sub_index)
            
            if hasattr(active_widget, 'macro_type_conclusion'):
                active_widget.macro_type_conclusion()

    def setup_tabs(self):
        emg_sub_menus = ["NCS", "EMG", "Blink", "Jolly", "PFT"]
        emg_tab_widget = self.create_sub_tab_widget(emg_sub_menus)
        self.main_tabs.addTab(emg_tab_widget, "EMG")

        ep_sub_menus = ["SSEP", "MEP", "VEP", "BAEP"]
        ep_tab_widget = self.create_sub_tab_widget(ep_sub_menus)
        self.main_tabs.addTab(ep_tab_widget, "EP")

        ans_sub_menus = ["ANSFT", "QSART", "QST"]
        ans_tab_widget = self.create_sub_tab_widget(ans_sub_menus)
        self.main_tabs.addTab(ans_tab_widget, "ANS")

    def create_sub_tab_widget(self, sub_menu_names: list) -> QTabWidget:
        sub_tab_widget = QTabWidget()
        
        for name in sub_menu_names:
            if name == "NCS":
                tab = NCSSimpleWidget(self)
            elif name == "EMG":
                tab = EMGWidget(self)
            elif name == "ANSFT":
                tab = ANSFTWidget(self)
            elif name == "QSART":
                tab = QSARTWidget(self)
            elif name == "Blink":       
                tab = BLINKWidget(self)
            elif name == "Jolly":
                tab = JOLLYWidget(self)
            elif name == "PFT":
                tab = PFTWidget(self)
            else:
                tab = QWidget()
                layout = QVBoxLayout()
                placeholder_label = QLabel(f"{name} 화면\n(To be developed...)")
                placeholder_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
                placeholder_label.setStyleSheet("font-size: 24px; color: #7f8c8d; font-weight: bold;")
                layout.addWidget(placeholder_label)
                tab.setLayout(layout)
                
            sub_tab_widget.addTab(tab, name)
            
        path_tool = PathClearTool(base_path=r"C:\HIS_Image", parent=sub_tab_widget)
        sub_tab_widget.setCornerWidget(path_tool, Qt.Corner.TopRightCorner)
        sub_tab_widget.currentChanged.connect(self.on_sub_tab_changed)
        return sub_tab_widget

    def on_main_tab_changed(self, index):
        current_sub_tab_widget = self.main_tabs.widget(index)
        if isinstance(current_sub_tab_widget, QTabWidget):
            sub_index = current_sub_tab_widget.currentIndex()
            tab_name = current_sub_tab_widget.tabText(sub_index)
            self.signature_tool.update_signature(tab_name)

    def on_sub_tab_changed(self, index):
        sender_tab = self.sender()
        tab_name = sender_tab.tabText(index)
        self.signature_tool.update_signature(tab_name)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    
    # [추가] Splash 화면을 먼저 띄움
    splash = SplashScreen()
    if splash.exec() == QDialog.DialogCode.Accepted:
        # 사용자가 START를 눌렀을 때만 메인 윈도우 실행 (이름 전달)
        window = ANSFTWindow(resident_name=splash.selected_name)
        window.show()
        sys.exit(app.exec())
    else:
        # Splash 화면에서 X 버튼을 눌러 그냥 껐을 때 프로그램 종료
        sys.exit()