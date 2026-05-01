import os
import cv2
import numpy as np
from datetime import datetime
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QImage, QPixmap, QColor, QBrush
from PyQt6.QtWidgets import QTableWidgetItem

from tools.image_processor import ImageProcessor
from tools.ocr_tool import OCRTool

class AnsftVisionHandler:
    def __init__(self, controller):
        """컨트롤러의 UI 요소들에 직접 접근하기 위해 참조(reference)를 받습니다."""
        self.ctrl = controller

    def process_and_show_auto_images(self, file_list):
        self._process_patient_info(file_list)
        self._process_ssr(file_list)
        self._process_hrdb(file_list)
        
        self.ctrl._is_updating_table = True 
        self._process_tilt(file_list)
        self._process_valsalva(file_list)
        self.ctrl._is_updating_table = False
        
        self.ctrl.update_findings_and_analysis()

    def _process_tilt(self, file_list):
        cropped = ImageProcessor.crop_tilt_table(file_list)
        if cropped is not None:
            h, w = cropped.shape[:2]
            ch, cw = h / 5.0, w / 3.0
            self.ctrl.tilt_data = []
            
            for r in range(5):
                row_data = []
                for c in range(3):
                    y1, y2 = int(r * ch + 15), int((r + 1) * ch - 15)
                    x1, x2 = int(c * cw + 30), int((c + 1) * cw - 30)
                    val, _ = OCRTool.extract_int(cropped[y1:y2, x1:x2])
                    
                    # =========================================================
                    # [개선] OCR 생리학적 휴리스틱(Heuristic) 자동 교정
                    # =========================================================
                    if val > 300: 
                        val_str = str(val)
                        if len(val_str) == 3 and val_str[1] == '3':
                            val = int(val_str[0] + val_str[2])
                    
                    # 11~19 범위의 값이 나오면 71~79로 일괄 교정 (7을 1로 오인하는 오류 방어)
                    if 10 <= val <= 19:
                        val += 60
                    # =========================================================

                    row_data.append(val)
                    
                    item = QTableWidgetItem(str(val))
                    item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
                    
                    # 생리학적으로 의심스러운 범위는 빨간색으로 경고 (육안 검수 유도)
                    if (val > 200 or val < 40) and val != 0:
                        item.setForeground(QBrush(QColor("#c0392b")))
                        item.setToolTip("OCR 오인식 의심 수치입니다. 우측 원본을 반드시 확인하세요.")
                        
                    self.ctrl.table_tilt.setItem(r, c, item)
                    
                self.ctrl.tilt_data.append(row_data)

            cw_int = int(w / 3.0)
            c1 = cropped[:, int(cw_int*0.25) : int(cw_int*0.75)]
            c2 = cropped[:, cw_int + int(cw_int*0.25) : cw_int + int(cw_int*0.75)]
            c3 = cropped[:, 2*cw_int + int(cw_int*0.25) : 2*cw_int + int(cw_int*0.75)]
            stitched = cv2.hconcat([c1, c2, c3])
            
            resized = cv2.resize(stitched, (174, 155), interpolation=cv2.INTER_AREA)
            qimg = cv2.cvtColor(resized, cv2.COLOR_BGR2RGB)
            self.ctrl.lbl_tilt_image.setPixmap(QPixmap.fromImage(QImage(qimg.data, 174, 155, qimg.strides[0], QImage.Format.Format_RGB888)))

    def _process_patient_info(self, file_list):
        cropped = ImageProcessor.crop_patient_info(file_list)
        if cropped is not None:
            orig_h, orig_w = cropped.shape[:2]
            target_w, target_h = 238, 55 
            calc_h = int(target_w * (orig_h / orig_w))
            resized = cv2.resize(cropped, (target_w, calc_h), interpolation=cv2.INTER_AREA)
            final_img = np.zeros((target_h, target_w, 3), dtype=np.uint8) 
            final_img[:,:] = cropped[0,0] 
            y_offset = (target_h - calc_h) // 2 if target_h > calc_h else 0
            plot_h = min(target_h, calc_h)
            final_img[y_offset : y_offset + plot_h, :] = resized[0:plot_h, :]
            qimg = cv2.cvtColor(final_img, cv2.COLOR_BGR2RGB)
            pixmap = QPixmap.fromImage(QImage(qimg.data, target_w, target_h, qimg.strides[0], QImage.Format.Format_RGB888))
            self.ctrl.lbl_patient_image.setPixmap(pixmap)
            cell_date = cropped[int(orig_h/3):int(2*orig_h/3), int(orig_w/2):orig_w]
            bday_tuple, _ = OCRTool.extract_date(cell_date)
            if bday_tuple:
                m, d, y = map(int, bday_tuple)
                today = datetime.now()
                self.ctrl.patient_age = today.year - y - ((today.month, today.day) < (m, d))

    def _process_ssr(self, file_list):
        cropped = ImageProcessor.crop_ssr_graph(file_list)
        if cropped is not None:
            resized = cv2.resize(cropped, (174, 88), interpolation=cv2.INTER_AREA)
            qimg = cv2.cvtColor(resized, cv2.COLOR_BGR2RGB)
            self.ctrl.lbl_ssr_graph.setPixmap(QPixmap.fromImage(QImage(qimg.data, 174, 88, qimg.strides[0], QImage.Format.Format_RGB888)))

    def _process_hrdb(self, file_list):
        target_path = ImageProcessor.find_target_hrdb_file(file_list)
        if target_path:
            cropped = ImageProcessor.crop_unique_green_box(target_path)
            if cropped is not None:
                h, w = cropped.shape[:2]
                self.ctrl.hrdb_val1, _ = OCRTool.extract_float(cropped[:, :w//2])
                self.ctrl.hrdb_val2, _ = OCRTool.extract_float(cropped[:, w//2:])
                if not self.ctrl.chk_arrhythmia_hrdb.isChecked():
                    self.ctrl.txt_hrdb_ocr.setText(f"E/I ratio '{self.ctrl.hrdb_val1}' (normal range >'{self.ctrl.hrdb_val2}')")
                resized = cv2.resize(cropped, (174, 45), interpolation=cv2.INTER_AREA)
                qimg = cv2.cvtColor(resized, cv2.COLOR_BGR2RGB)
                self.ctrl.lbl_hrdb_image.setPixmap(QPixmap.fromImage(QImage(qimg.data, 174, 45, qimg.strides[0], QImage.Format.Format_RGB888)))

    def _process_valsalva(self, file_list):
        cropped = ImageProcessor.crop_valsalva_boxes(file_list)
        if cropped is not None:
            h, w = cropped.shape[:2]
            ratio_img = cropped[h//2:, :w//2]
            prt_img = cropped[h//2:, w//2:]
            ratio_img_2x = cv2.resize(ratio_img, None, fx=2, fy=2, interpolation=cv2.INTER_CUBIC)
            prt_img_2x = cv2.resize(prt_img, None, fx=2, fy=2, interpolation=cv2.INTER_CUBIC)
            self.ctrl.val_ratio, _ = OCRTool.extract_float(ratio_img_2x)
            self.ctrl.prt_sec, _ = OCRTool.extract_float(prt_img_2x)
            qimg = cv2.cvtColor(cropped, cv2.COLOR_BGR2RGB)
            pix = QPixmap.fromImage(QImage(qimg.data, w, h, qimg.strides[0], QImage.Format.Format_RGB888))
            scaled = pix.scaled(174, 60, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation)
            self.ctrl.lbl_valsalva_image.setPixmap(scaled)

        img1 = None
        for f in file_list:
            fname = os.path.basename(f).lower()
            name, ext = os.path.splitext(fname)
            if name.endswith("_1") or name.endswith("-1") or name.endswith(" 1") or name == "1" or name == "newreport_1":
                temp_img = cv2.imdecode(np.fromfile(f, dtype=np.uint8), cv2.IMREAD_COLOR)
                if temp_img is not None:
                    h, w = temp_img.shape[:2]
                    if h >= 3000 and w >= 2400:
                        img1 = temp_img
                        break
        if img1 is not None:
            norm_ratio_img = img1[2140:2205, 1370:1460]
            norm_ratio_img_2x = cv2.resize(norm_ratio_img, None, fx=2, fy=2, interpolation=cv2.INTER_CUBIC)
            self.ctrl.normal_val_ratio, _ = OCRTool.extract_float(norm_ratio_img_2x)
            pix_n = QPixmap.fromImage(QImage(cv2.cvtColor(norm_ratio_img, cv2.COLOR_BGR2RGB).data, norm_ratio_img.shape[1], norm_ratio_img.shape[0], norm_ratio_img.shape[1]*3, QImage.Format.Format_RGB888))
            self.ctrl.lbl_norm_ratio_image.setPixmap(pix_n.scaled(174, 35, Qt.AspectRatioMode.KeepAspectRatio))
        else:
            self.ctrl.normal_val_ratio = "N/A"
            self.ctrl.lbl_norm_ratio_image.setText("Norm Ratio N/A")

        self.ctrl.table_valsalva.setItem(0, 0, QTableWidgetItem(str(self.ctrl.val_ratio)))
        self.ctrl.table_valsalva.setItem(0, 1, QTableWidgetItem(str(self.ctrl.normal_val_ratio)))
        self.ctrl.table_valsalva.setItem(0, 2, QTableWidgetItem(str(self.ctrl.prt_sec)))
        for i in range(3): self.ctrl.table_valsalva.item(0, i).setTextAlignment(Qt.AlignmentFlag.AlignCenter)