# tools/preliminary_tool.py
from PyQt6.QtWidgets import QWidget, QHBoxLayout, QLabel, QLineEdit
import keyboard

class PreliminaryTool(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.default_text = "**현재 가판독 상태이며 추후 정식 판독을 참조하기 바람."
        self.current_preliminary = self.default_text
        self.setup_ui()
        self.setup_global_shortcut()

    def setup_ui(self):
        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0) 
        
        # 라벨에 단축키 명시
        label = QLabel("가판 (Ctrl+W):")
        label.setStyleSheet("font-weight: normal; font-size: 12px;") 
        
        self.preliminary_input = QLineEdit()
        # [핵심 수정] 가로 폭을 140에서 260으로 넉넉하게 확장했습니다.
        self.preliminary_input.setFixedWidth(260)
        # padding-left: 5px 를 추가하여 내부 좌측 여백 생성
        self.preliminary_input.setStyleSheet("font-size: 12px; padding-left: 4px;")
        
        # 디폴트 텍스트 세팅
        self.preliminary_input.setText(self.default_text)
        # 긴 텍스트의 경우, 커서를 맨 앞으로 옮겨 문구의 시작(**현재 가판독...)이 보이게 함
        self.preliminary_input.setCursorPosition(0)
        
        self.preliminary_input.textChanged.connect(self.on_text_changed)
        
        layout.addWidget(label)
        layout.addSpacing(3)
        layout.addWidget(self.preliminary_input)

    def on_text_changed(self, text):
        self.current_preliminary = text

    def setup_global_shortcut(self):
        # 단축키를 Ctrl+W로 변경
        keyboard.add_hotkey('ctrl+w', self.paste_preliminary)

    def paste_preliminary(self):
        if self.current_preliminary:
            keyboard.write(self.current_preliminary)