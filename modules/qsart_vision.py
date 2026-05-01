import os
import cv2
import numpy as np
import pytesseract 
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QImage, QPixmap

from tools.ocr_tool import OCRTool

class QsartVisionHandler:
    def __init__(self, controller):
        self.ctrl = controller

    def process_and_show_auto_images(self, file_list):
        img_1 = self._find_and_load_target_file(file_list, target_suffix="_1")
        img_2 = self._find_and_load_target_file(file_list, target_suffix="_2")
        img_3 = self._find_and_load_target_file(file_list, target_suffix="_3")

        if img_1 is not None:
            self._process_patient_info(img_1)
            self._process_table(img_1)
            
        self._process_graphs(img_2, img_3)

    def _find_and_load_target_file(self, file_list, target_suffix):
        target_path = None
        for f in file_list:
            name, _ = os.path.splitext(os.path.basename(f).lower())
            if name.endswith(target_suffix):
                target_path = f
                break
                
        if not target_path: 
            return None
            
        try:
            return cv2.imdecode(np.fromfile(target_path, np.uint8), cv2.IMREAD_COLOR)
        except Exception as e:
            print(f"[QSART Vision Error] 파일 로드 실패: {e}")
            return None

    def _process_patient_info(self, img):
        try:
            cropped = img[835:1035, 135:1105]
            h, w = cropped.shape[:2]
            
            row_h = int(h / 3.0)
            col_w = int(w / 2.0)
            sex_cell = cropped[row_h:row_h*2, 0:col_w] 
            
            gray = cv2.cvtColor(cv2.resize(sex_cell, None, fx=2, fy=2), cv2.COLOR_BGR2GRAY)
            _, thresh = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY | cv2.THRESH_OTSU)
            text = pytesseract.image_to_string(thresh, config='--psm 6').lower()
            
            if "female" in text or " f" in text:
                self.ctrl.set_patient_sex("Female")
            elif "male" in text or " m" in text:
                self.ctrl.set_patient_sex("Male")
            else:
                self.ctrl.set_patient_sex("N/A") 
            
            target_w, target_h = 238, 55 
            calc_h = int(target_w * (h / w))
            resized = cv2.resize(cropped, (target_w, calc_h), interpolation=cv2.INTER_AREA)
            
            final_img = np.zeros((target_h, target_w, 3), dtype=np.uint8)
            final_img[:,:] = 255 
            
            y_offset = (target_h - calc_h) // 2 if target_h > calc_h else 0
            plot_h = min(target_h, calc_h)
            final_img[y_offset : y_offset + plot_h, :] = resized[0:plot_h, :]
            
            qimg = cv2.cvtColor(final_img, cv2.COLOR_BGR2RGB)
            pixmap = QPixmap.fromImage(QImage(qimg.data, target_w, target_h, qimg.strides[0], QImage.Format.Format_RGB888))
            self.ctrl.lbl_patient_image.setPixmap(pixmap)
            
        except Exception as e:
            print(f"[QSART Vision Error] 환자 정보/성별 추출 실패: {e}")

    def _process_table(self, img):
        try:
            # 1. Left 측 데이터 크롭 및 OCR
            left_ocr_crop = img[2300:2350, 550:1550]
            h_l, w_l = left_ocr_crop.shape[:2]
            col_w_l = int(w_l / 4.0)
            
            left_vols = []
            for i in range(4):
                val, _ = OCRTool.extract_float(left_ocr_crop[:, i*col_w_l : (i+1)*col_w_l])
                left_vols.append(val)
                
            left_display_crop = img[2230:2350, 550:1550]
            qimg_l = cv2.cvtColor(left_display_crop, cv2.COLOR_BGR2RGB)
            pixmap_left = QPixmap.fromImage(QImage(qimg_l.data, qimg_l.shape[1], qimg_l.shape[0], qimg_l.shape[1] * 3, QImage.Format.Format_RGB888))

            # 2. Right 측 데이터 크롭 및 OCR
            right_ocr_crop = img[2330:2380, 550:1550]
            h_r, w_r = right_ocr_crop.shape[:2]
            col_w_r = int(w_r / 4.0)
            
            right_vols = []
            for i in range(4):
                val, _ = OCRTool.extract_float(right_ocr_crop[:, i*col_w_r : (i+1)*col_w_r])
                right_vols.append(val)
                
            right_display_crop = img[2230:2380, 550:1550]
            qimg_r = cv2.cvtColor(right_display_crop, cv2.COLOR_BGR2RGB)
            pixmap_right = QPixmap.fromImage(QImage(qimg_r.data, qimg_r.shape[1], qimg_r.shape[0], qimg_r.shape[1] * 3, QImage.Format.Format_RGB888))

            # 컨트롤러로 4개의 데이터 일괄 전달
            self.ctrl.store_table_data(left_vols, right_vols, pixmap_left, pixmap_right)
            
        except Exception as e:
            print(f"[QSART Vision Error] 표 크롭/OCR 실패: {e}")

    def _process_graphs(self, img_2, img_3):
        try:
            graphs = [None] * 4
            
            if img_2 is not None:
                graphs[0] = img_2[280:1170, 250:2260]
                graphs[1] = img_2[1170:2070, 250:2260]
                graphs[2] = img_2[2070:2970, 250:2260]
            
            if img_3 is not None:
                graphs[3] = img_3[280:1170, 250:2260]

            for i in range(4):
                if graphs[i] is not None:
                    qimg = cv2.cvtColor(graphs[i], cv2.COLOR_BGR2RGB)
                    h, w, c = qimg.shape
                    pixmap = QPixmap.fromImage(QImage(qimg.data, w, h, w * c, QImage.Format.Format_RGB888))
                    
                    lbl = self.ctrl.lbl_graphs[i]
                    lbl.setPixmap(pixmap.scaled(lbl.size(), Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation))
                    
        except Exception as e:
            print(f"[QSART Vision Error] 그래프 크롭 실패: {e}")