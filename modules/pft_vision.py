import cv2
import pytesseract
import re
import os
import sys
from PIL import Image
from PyQt6.QtWidgets import QDialog, QApplication, QRubberBand
from PyQt6.QtCore import Qt, QRect, QPoint
from PyQt6.QtGui import QScreen, QPainter, QColor

# [주의] 대상 PC의 Tesseract 경로에 맞게 수정 필요
if getattr(sys, 'frozen', False):
    # PyInstaller로 빌드된 .exe 환경일 때
    base_dir = os.path.dirname(sys.executable)
else:
    # 파이썬 스크립트(.py)로 실행할 때 (modules 폴더 안이므로 한 칸 위로)
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

tesseract_path = os.path.join(base_dir, 'Tesseract-OCR', 'tesseract.exe')
pytesseract.pytesseract.tesseract_cmd = tesseract_path

class SnippingTool(QDialog):
    """반투명 전체 화면 오버레이에서 드래그하여 화면을 캡처하는 도구 (프리징 해결 버젼)"""
    def __init__(self):
        super().__init__()
        
        # [핵심 수정 1] 윈도우 플래그 최적화: 최상단, 프레임 없음, 툴 팁 속성으로 포커스 문제 해결
        self.setWindowFlags(
            Qt.WindowType.FramelessWindowHint | 
            Qt.WindowType.WindowStaysOnTopHint |
            Qt.WindowType.ToolTip 
        )
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.setCursor(Qt.CursorShape.CrossCursor)

        # 다중 모니터 환경까지 커버하기 위해 가상 데스크톱 전체 영역을 잡음
        screen_geometry = QApplication.primaryScreen().virtualGeometry()
        self.setGeometry(screen_geometry)

        self.rubber_band = QRubberBand(QRubberBand.Shape.Rectangle, self)
        self.origin = QPoint()
        self.selected_rect = QRect()
        self.captured_pixmap = None
        
        self.is_drawing = False # 마우스 드래그 상태 관리 변수

    # [핵심 수정 2] 배경을 투명하게 칠하기 위한 paintEvent 추가 (CSS 대신 QPainter 사용이 더 안정적)
    def paintEvent(self, event):
        painter = QPainter(self)
        painter.fillRect(self.rect(), QColor(0, 0, 0, 80)) # 반투명 검은색 (알파 80)

    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            self.origin = event.pos()
            self.rubber_band.setGeometry(QRect(self.origin, self.origin))
            self.rubber_band.show()
            self.is_drawing = True

    def mouseMoveEvent(self, event):
        if self.is_drawing and not self.origin.isNull():
            # 사용자가 드래그하는 방향에 상관없이 사각형 영역을 정상적으로 잡기 위해 normalized() 사용
            self.rubber_band.setGeometry(QRect(self.origin, event.pos()).normalized())

    def mouseReleaseEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton and self.is_drawing:
            self.is_drawing = False
            self.selected_rect = self.rubber_band.geometry()
            self.rubber_band.hide()
            self.hide() # 캡처 전 오버레이 창을 숨겨서 오버레이 자체가 캡처되는 것을 방지
            
            # [핵심 수정 3] QTimer나 지연 없이 즉각적으로 화면 캡처 수행
            # 화면이 너무 작게 캡처되는 것을 막기 위해 최소 10x10 픽셀 이상 드래그했을 때만 작동
            if self.selected_rect.width() > 10 and self.selected_rect.height() > 10:
                screen = QApplication.primaryScreen()
                self.captured_pixmap = screen.grabWindow(
                    0, 
                    self.selected_rect.x(), self.selected_rect.y(), 
                    self.selected_rect.width(), self.selected_rect.height()
                )
                self.accept()
            else:
                self.reject() # 너무 작게 그렸으면 취소 처리

    # [핵심 수정 4] ESC 키를 누르면 프로그램이 멈추지 않고 안전하게 캡처 모드를 취소
    def keyPressEvent(self, event):
        if event.key() == Qt.Key.Key_Escape:
            self.reject()

class PFTVisionHandler:
    @staticmethod
    def capture_and_ocr(clean_lines=False, is_info=False) -> str:
        # SnippingTool은 한 번 쓰고 버리는 것이 안전함 (메모리 릭 방지)
        snipper = SnippingTool()
        result = snipper.exec()
        
        if result == QDialog.DialogCode.Accepted and snipper.captured_pixmap:
            img_path = "temp_pft_capture.png"
            snipper.captured_pixmap.save(img_path)
            
            if clean_lines:
                image = cv2.imread(img_path)
                gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
                thresh = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU)[1]
                
                # 수평선 제거
                h_kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (40, 1))
                d_lines = cv2.morphologyEx(thresh, cv2.MORPH_OPEN, h_kernel, iterations=1)
                cnts = cv2.findContours(d_lines, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)[-2]
                for c in cnts: cv2.drawContours(image, [c], -1, (255, 255, 255), 2)
                
                # 수직선 제거
                v_kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (1, 40))
                d_lines = cv2.morphologyEx(thresh, cv2.MORPH_OPEN, v_kernel, iterations=1)
                cnts = cv2.findContours(d_lines, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)[-2]
                for c in cnts: cv2.drawContours(image, [c], -1, (255, 255, 255), 2)
                
                cv2.imwrite(img_path, image)

            config = '--psm 6' if is_info else '--psm 6 -c tessedit_char_whitelist=0123456789'
            text = pytesseract.image_to_string(Image.open(img_path), config=config).strip()
            return text
        return ""

    @staticmethod
    def extract_numbers(text: str) -> list:
        return [int(n) for n in re.findall(r'\b(\d+)\b', text)]