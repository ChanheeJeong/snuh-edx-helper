import cv2
import numpy as np
from PyQt6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLabel, QCheckBox, QSizePolicy, QPushButton, QMessageBox
from PyQt6.QtCore import Qt, QRect
from PyQt6.QtGui import QImage, QPixmap, QPainter, QColor, QPen, QFont

class InteractiveGraphLabel(QLabel):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setMouseTracking(True)
        
        self.lines = []         
        self.phase_ids = []     
        self.dragging_idx = -1  
        self.hover_idx = -1     
        
        self.baseline_y = None 

        self.COLOR_MAP = {
            "1": QColor(41, 128, 185, 255),   
            "2E": QColor(39, 174, 96, 255),   
            "2L": QColor(192, 57, 43, 255),   
            "3": QColor(41, 128, 185, 255),   
            "4": QColor(192, 57, 43, 255)     
        }

    def set_phases(self, phase_ids, min_rx, max_rx):
        self.phase_ids = phase_ids
        n_lines = len(phase_ids) + 1
        
        if n_lines > 1:
            if not self.lines or len(self.lines) != n_lines:
                self.lines = [0.0] * n_lines
                try:
                    idx_3 = phase_ids.index("3")
                except ValueError:
                    idx_3 = len(phase_ids) // 2 
                
                self.lines[0] = min_rx
                self.lines[idx_3] = max_rx
                
                if idx_3 > 0:
                    step_inner = (max_rx - min_rx) / idx_3
                    for i in range(1, idx_3):
                        self.lines[i] = min_rx + i * step_inner
                
                post_lines = n_lines - 1 - idx_3
                if post_lines > 0:
                    step_outer = step_inner if idx_3 > 0 else 0.1
                    for i in range(idx_3 + 1, n_lines):
                        new_pos = max_rx + (i - idx_3) * step_outer
                        self.lines[i] = min(new_pos, 0.98) 
        else:
            self.lines = []
            
        self.update() 

    def set_phases_exact(self, phase_ids, saved_lines):
        self.phase_ids = phase_ids
        self.lines = list(saved_lines)
        self.baseline_y = None 
        self.update()

    def paintEvent(self, event):
        super().paintEvent(event)
        if not self.phase_ids or not self.lines: return

        painter = QPainter(self)
        w = self.width()
        h = self.height()

        y_top = int(h * (80 / 1795.0))
        y_bottom = int(h * (760 / 1795.0))
        px_lines = [int(l * w) for l in self.lines]

        if self.baseline_y is not None and "4" in self.phase_ids:
            idx_4 = self.phase_ids.index("4")
            px_start = px_lines[idx_4]
            px_end = px_lines[idx_4 + 1]
            rect_mask = QRect(px_start, y_top, px_end - px_start, self.baseline_y - y_top)
            painter.fillRect(rect_mask, QColor(0, 200, 255, 60)) 

        if self.baseline_y is not None:
            pen_base = QPen(QColor(230, 126, 34, 255)) 
            pen_base.setWidth(2)
            painter.setPen(pen_base)
            painter.drawLine(0, self.baseline_y, w, self.baseline_y)

        pen = QPen()
        for i, px in enumerate(px_lines):
            if i == self.hover_idx or i == self.dragging_idx:
                pen.setColor(QColor(231, 76, 60, 255)) 
                pen.setWidth(2) 
                pen.setStyle(Qt.PenStyle.SolidLine)
            else:
                pen.setColor(QColor(40, 40, 40, 200)) 
                pen.setWidth(1) 
                pen.setStyle(Qt.PenStyle.DashLine)
                
            painter.setPen(pen)
            painter.drawLine(px, y_top, px, y_bottom)

        font = QFont("Arial", 10, QFont.Weight.Bold)
        painter.setFont(font)
        
        for i in range(len(self.phase_ids)):
            p_id = self.phase_ids[i]
            x_start = px_lines[i]
            x_end = px_lines[i+1]
            
            painter.setPen(self.COLOR_MAP.get(p_id, QColor(0, 0, 0)))
            rect_text = QRect(x_start, y_top + 5, x_end - x_start, 20) 
            painter.drawText(rect_text, Qt.AlignmentFlag.AlignTop | Qt.AlignmentFlag.AlignHCenter, p_id)

    def get_line_near(self, x):
        w = self.width()
        threshold = 15 / w 
        rx = x / w
        for i, l in enumerate(self.lines):
            if abs(l - rx) < threshold: return i
        return -1

    def mousePressEvent(self, event):
        idx = self.get_line_near(event.pos().x())
        if idx != -1: self.dragging_idx = idx

    def mouseMoveEvent(self, event):
        w = self.width()
        rx = event.pos().x() / w
        hover = self.get_line_near(event.pos().x())
        if hover != self.hover_idx:
            self.hover_idx = hover
            self.update() 
            
        if hover != -1 or self.dragging_idx != -1:
            self.setCursor(Qt.CursorShape.SizeHorCursor)
        else:
            self.setCursor(Qt.CursorShape.ArrowCursor)

        if self.dragging_idx != -1:
            min_rx = self.lines[self.dragging_idx - 1] + 0.01 if self.dragging_idx > 0 else 0.0
            max_rx = self.lines[self.dragging_idx + 1] - 0.01 if self.dragging_idx < len(self.lines) - 1 else 1.0
            rx = max(min_rx, min(rx, max_rx)) 
            self.lines[self.dragging_idx] = rx
            
            if self.dragging_idx == 0:
                self.baseline_y = None
                
            self.update() 

    def mouseReleaseEvent(self, event):
        self.dragging_idx = -1
        self.update()


class ValsalvaGraphWindow(QWidget):
    def __init__(self, cv_img, return_callback=None, saved_lines=None, saved_chk_2l=False, saved_chk_4=False, yellow_min=None, yellow_max=None, saved_chk_poor=False):
        super().__init__()
        self.setWindowTitle("Valsalva Phase 정밀 분석")
        
        orig_w = 1030
        orig_h = 897
        target_w = 850 
        factor = max(1, round(orig_w / target_w))
        self.new_w = orig_w // factor
        self.new_h = orig_h // factor
        
        self.resize(self.new_w + 40, self.new_h + 150) 
        
        self.return_callback = return_callback
        self.overshoot_state = None 
        
        self.saved_lines = saved_lines
        self.saved_chk_2l = saved_chk_2l
        self.saved_chk_4 = saved_chk_4
        self.saved_chk_poor = saved_chk_poor 
        
        if cv_img is not None:
            self.cv_img_resized = cv2.resize(cv_img, (self.new_w, self.new_h), interpolation=cv2.INTER_AREA)
            if yellow_min is None or yellow_max is None:
                self.extract_yellow_range()
            else:
                self.yellow_min_rx = yellow_min
                self.yellow_max_rx = yellow_max
        else:
            self.cv_img_resized = None
            self.yellow_min_rx = 0.35
            self.yellow_max_rx = 0.65

        self.setup_ui()

    def extract_yellow_range(self):
        lower_yellow = np.array([40, 160, 220])
        upper_yellow = np.array([75, 195, 255])
        mask = cv2.inRange(self.cv_img_resized, lower_yellow, upper_yellow)
        coords = cv2.findNonZero(mask)
        w = self.cv_img_resized.shape[1]
        
        if coords is not None and len(coords) > 50:
            x_coords = coords[:, 0, 0]
            min_x = int(np.min(x_coords))
            max_x = int(np.max(x_coords))
            if max_x - min_x > w * 0.05:
                self.yellow_min_rx = min_x / w
                self.yellow_max_rx = max_x / w
                return
        self.yellow_min_rx = 0.35
        self.yellow_max_rx = 0.65

    def detect_baseline(self):
        if not self.lbl_image.lines or self.cv_img_resized is None: return
        
        px_x = int(self.lbl_image.lines[0] * self.cv_img_resized.shape[1])
        h = self.cv_img_resized.shape[0]
        y_top = int(h * (80 / 1795.0))
        y_bottom = int(h * (760 / 1795.0))
        
        found_y = -1
        for y in range(y_top, y_bottom):
            b, g, r = self.cv_img_resized[y, px_x]
            if int(r) > int(g) + 20 and int(r) > int(b) + 20 and r > 120:
                found_y = y
                break
                
        if found_y != -1:
            self.lbl_image.baseline_y = found_y
            self.lbl_image.update()
        else:
            QMessageBox.warning(self, "경고", "Phase 1 선 위에서 SBP(분홍/붉은색)를 찾지 못했습니다.\n선을 조금 이동 후 다시 시도해보세요.")

    def apply_and_return(self):
        if self.return_callback:
            is_poor = self.chk_poor.isChecked()
            # 버튼이 체크 안 된 기본 상태면 Absent는 False (즉, 존재함)
            p2l_absent = self.btn_phase2l.isChecked() 
            p4_absent = self.btn_phase4.isChecked()
            lines = self.lbl_image.lines
            
            # 콜백 반환 (overshoot_state는 사실상 p4가 존재할 때 정상적으로 있는가에 대한 여부)
            self.return_callback(is_poor, p2l_absent, p4_absent, self.overshoot_state, lines, self.yellow_min_rx, self.yellow_max_rx)
        self.close()

    def toggle_poor_mode(self):
        is_poor = self.chk_poor.isChecked()
        self.btn_phase2l.setDisabled(is_poor)
        self.btn_phase4.setDisabled(is_poor)
        self.btn_baseline.setDisabled(is_poor)
        self.lbl_image.setDisabled(is_poor) 

    def update_button_styles(self):
        # 버튼 체크됨 = 결여(-) 상태 (비정상) -> 노란색
        # 버튼 체크안됨 = 존재(+) 상태 (정상 디폴트) -> 파란색
        if self.btn_phase2l.isChecked():
            self.btn_phase2l.setText("Phase II_late (-)")
            self.btn_phase2l.setStyleSheet("background-color: #f1c40f; color: black; font-weight: bold; border-radius: 4px; padding: 0 20px; font-size: 14px;")
        else:
            self.btn_phase2l.setText("Phase II_late (+)")
            self.btn_phase2l.setStyleSheet("background-color: #3498db; color: white; font-weight: bold; border-radius: 4px; padding: 0 20px; font-size: 14px;")
            
        if self.btn_phase4.isChecked():
            self.btn_phase4.setText("Phase IV overshoot (-)")
            self.btn_phase4.setStyleSheet("background-color: #f1c40f; color: black; font-weight: bold; border-radius: 4px; padding: 0 20px; font-size: 14px;")
            self.overshoot_state = False
        else:
            self.btn_phase4.setText("Phase IV overshoot (+)")
            self.btn_phase4.setStyleSheet("background-color: #3498db; color: white; font-weight: bold; border-radius: 4px; padding: 0 20px; font-size: 14px;")
            self.overshoot_state = True

    def on_phase_toggled(self):
        self.update_button_styles()
        self.update_phases()

    def setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(10, 10, 10, 10)

        # --- 상단 1열: Poor 체크박스, Baseline 탐지 ---
        top_bar1 = QHBoxLayout()
        self.chk_poor = QCheckBox("Poor valsalva maneuver")
        self.chk_poor.setStyleSheet("font-weight: bold; font-size: 15px; color: #c0392b;")
        self.chk_poor.stateChanged.connect(self.toggle_poor_mode)
        
        self.btn_baseline = QPushButton("Baseline Detection")
        self.btn_baseline.setFixedHeight(35)
        self.btn_baseline.setStyleSheet("background-color: #9b59b6; color: white; font-weight: bold; border-radius: 4px; padding: 0 15px;")
        self.btn_baseline.clicked.connect(self.detect_baseline)
        
        lbl_title = QLabel("세로선을 드래그하여 기준선을 설정하세요.")
        lbl_title.setStyleSheet("font-weight: bold; color: #7f8c8d; font-size: 13px;")

        top_bar1.addWidget(self.chk_poor)
        top_bar1.addSpacing(30)
        top_bar1.addWidget(self.btn_baseline)
        top_bar1.addWidget(lbl_title)
        top_bar1.addStretch()
        layout.addLayout(top_bar1)

        # --- 상단 2열: Phase 토글(2배), 완료 버튼(2배) ---
        top_bar2 = QHBoxLayout()
        top_bar2.setContentsMargins(0, 0, 0, 10)
        
        self.btn_phase2l = QPushButton("Phase II_late (+)")
        self.btn_phase2l.setCheckable(True)
        self.btn_phase2l.setFixedHeight(70) 
        self.btn_phase2l.setStyleSheet("background-color: #3498db; color: white; font-weight: bold; border-radius: 4px; padding: 0 20px; font-size: 14px;")
        self.btn_phase2l.toggled.connect(self.on_phase_toggled)
        
        self.btn_phase4 = QPushButton("Phase IV overshoot (+)")
        self.btn_phase4.setCheckable(True)
        self.btn_phase4.setFixedHeight(70) 
        self.btn_phase4.setStyleSheet("background-color: #3498db; color: white; font-weight: bold; border-radius: 4px; padding: 0 20px; font-size: 14px;")
        self.btn_phase4.toggled.connect(self.on_phase_toggled)

        self.btn_return = QPushButton("분석 완료 (나가기)")
        self.btn_return.setFixedHeight(70) 
        self.btn_return.setStyleSheet("padding: 8px; font-weight: bold; font-size: 16px; background-color: #2ecc71; color: white; border-radius: 4px;")
        self.btn_return.clicked.connect(self.apply_and_return)
        
        top_bar2.addWidget(self.btn_phase2l)
        top_bar2.addWidget(self.btn_phase4)
        top_bar2.addStretch()
        top_bar2.addWidget(self.btn_return)
        layout.addLayout(top_bar2)

        # --- 커스텀 인터랙티브 그래프 ---
        self.lbl_image = InteractiveGraphLabel()
        self.lbl_image.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.lbl_image.setStyleSheet("background-color: #ffffff; border-radius: 4px; border: 1px solid #bdc3c7;")
        self.lbl_image.setSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Fixed)
        self.lbl_image.setFixedSize(self.new_w, self.new_h) 
        
        layout.addWidget(self.lbl_image, 0, Qt.AlignmentFlag.AlignCenter)

        if self.cv_img_resized is not None:
            self.display_image()

        # [버그 수정] 저장된 값을 불러올 때 시그널을 차단하여 saved_lines가 증발하는 것을 방지합니다.
        self.btn_phase2l.blockSignals(True)
        if self.saved_chk_2l: self.btn_phase2l.setChecked(True)
        self.btn_phase2l.blockSignals(False)
        
        self.btn_phase4.blockSignals(True)
        if self.saved_chk_4: self.btn_phase4.setChecked(True)
        self.btn_phase4.blockSignals(False)

        self.chk_poor.blockSignals(True)
        self.chk_poor.setChecked(self.saved_chk_poor)
        self.chk_poor.blockSignals(False)
        
        # UI 스타일 및 모드 초기화
        self.update_button_styles()
        self.toggle_poor_mode()
        self.update_phases() # 여기서 비로소 단 한 번만 선을 그립니다.

    def update_phases(self):
        phases_ids = ["1", "2E"]
        
        # 2L 버튼이 체크 안 되어 있으면 (정상, 존재함)
        if not self.btn_phase2l.isChecked(): 
            phases_ids.append("2L")
            
        phases_ids.append("3")
        
        # [핵심 수정] 4는 항상 존재해야 하므로 무조건 추가합니다. (Overshoot 여부와 무관)
        phases_ids.append("4")

        n_req_lines = len(phases_ids) + 1
        
        # 이전에 그려둔 선의 갯수와 요구되는 선의 갯수가 같으면 선 위치를 유지합니다.
        if self.saved_lines is not None and len(self.saved_lines) == n_req_lines:
            self.lbl_image.set_phases_exact(phases_ids, self.saved_lines)
            self.saved_lines = None 
        else:
            # 갯수가 다르면 기본 비율로 재배치합니다.
            self.lbl_image.set_phases(phases_ids, self.yellow_min_rx, self.yellow_max_rx)

    def display_image(self):
        if self.cv_img_resized is None: return
        h, w, c = self.cv_img_resized.shape
        qimg = cv2.cvtColor(self.cv_img_resized, cv2.COLOR_BGR2RGB)
        q_img = QImage(qimg.data, w, h, c * w, QImage.Format.Format_RGB888)
        self.lbl_image.setPixmap(QPixmap.fromImage(q_img))