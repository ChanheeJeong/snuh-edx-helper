import os
from datetime import datetime
from PyQt6.QtWidgets import QWidget, QHBoxLayout, QLabel, QPushButton, QMessageBox
from PyQt6.QtCore import Qt

class PathClearTool(QWidget):
    def __init__(self, base_path=r"C:\HIS_Image", parent=None):
        super().__init__(parent)
        self.base_path = base_path
        self.setup_ui()

    def setup_ui(self):
        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 5, 0)
        layout.setSpacing(10)

        # 오늘 날짜를 기준으로 감시 폴더 타겟팅
        today_str = datetime.now().strftime("%Y-%m-%d")
        self.target_dir = os.path.join(self.base_path, today_str)

        # 1. 모니터링 경로 표시 라벨
        self.lbl_path = QLabel(f"모니터링: {self.target_dir}")
        self.lbl_path.setStyleSheet("color: #7f8c8d; font-size: 12px; font-weight: bold; font-family: Consolas, monospace;")
        self.lbl_path.setAlignment(Qt.AlignmentFlag.AlignVCenter | Qt.AlignmentFlag.AlignRight)
        layout.addWidget(self.lbl_path)

        # 2. [추가] 폴더 열기 버튼
        self.btn_open = QPushButton("폴더 열기")
        self.btn_open.setFixedHeight(26)
        self.btn_open.setStyleSheet("""
            QPushButton {
                background-color: #3498db; 
                color: white; 
                font-size: 12px; 
                font-weight: bold; 
                border-radius: 4px; 
                padding: 0px 10px;
            }
            QPushButton:hover {
                background-color: #2980b9;
            }
        """)
        self.btn_open.clicked.connect(self.open_folder)
        layout.addWidget(self.btn_open)

        # 3. 폴더 비우기 버튼
        self.btn_clear = QPushButton("이미지 비우기")
        self.btn_clear.setFixedHeight(26)
        self.btn_clear.setStyleSheet("""
            QPushButton {
                background-color: #e74c3c; 
                color: white; 
                font-size: 12px; 
                font-weight: bold; 
                border-radius: 4px; 
                padding: 0px 10px;
            }
            QPushButton:hover {
                background-color: #c0392b;
            }
        """)
        self.btn_clear.clicked.connect(self.clear_folder)
        layout.addWidget(self.btn_clear)

    def open_folder(self):
        """윈도우 탐색기로 모니터링 폴더를 엽니다."""
        if os.path.exists(self.target_dir):
            os.startfile(self.target_dir)
        elif os.path.exists(self.base_path):
            os.startfile(self.base_path)
        else:
            QMessageBox.warning(self, "오류", f"경로를 찾을 수 없습니다.\n{self.base_path}")

    def clear_folder(self):
        if not os.path.exists(self.target_dir):
            QMessageBox.information(self, "알림", f"아직 경로가 생성되지 않았습니다.\n({self.target_dir})")
            return

        reply = QMessageBox.question(
            self,
            "폴더 비우기",
            f"현재 모니터링 중인 경로의 모든 파일을 삭제하시겠습니까?\n\n경로: {self.target_dir}",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )

        if reply == QMessageBox.StandardButton.Yes:
            count = 0
            try:
                for filename in os.listdir(self.target_dir):
                    file_path = os.path.join(self.target_dir, filename)
                    if os.path.isfile(file_path):
                        os.remove(file_path)
                        count += 1
                QMessageBox.information(self, "완료", f"총 {count}개의 이미지/파일을 삭제했습니다.")
            except Exception as e:
                QMessageBox.critical(self, "오류", f"파일 삭제 중 오류가 발생했습니다:\n{str(e)}")