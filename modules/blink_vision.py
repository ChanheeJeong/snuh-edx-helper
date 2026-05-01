import os
import cv2
import numpy as np
import pytesseract
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QImage, QPixmap

from tools.ocr_tool import OCRTool

class BlinkVisionHandler:
    def __init__(self, controller):
        self.ctrl = controller

    # =====================================================================
    # [핵심 로직] 해상도 판별 및 크롭 좌표 딕셔너리 반환
    # =====================================================================
    def _get_crop_coords(self, h, w):
        # 1. 신규 포맷 (1557 x 2272 내외)
        if 1500 <= w <= 1600 and 2200 <= h <= 2300:
            return {
                "fnet_rt": (1698, 1722, 735, 755), 
                "fnet_lt": (1808, 1832, 735, 755),
                "fnst_disp": (1412, 1558, 428, 756),
                # 선생님께서 측정해주신 정확한 소수점 좌표(700, 743) 반영 완료
                "fnst_rt_lat": (1446, 1471, 684, 710, 700), 
                "fnst_rt_amp": (1446, 1472, 729, 755, 743),
                "fnst_lt_lat": (1528, 1553, 684, 710, 700),
                "fnst_lt_amp": (1528, 1553, 729, 755, 743),
                "reflex_rt": (480, 512, 134, 288),
                "reflex_lt": (480, 512, 861, 1015)
            }
        # 2. 기존 포맷 (1600 x 2128) - 기본값
        else:
            return {
                "fnet_rt": (1596, 1618, 749, 777),
                "fnet_lt": (1699, 1721, 749, 777),
                "fnst_disp": (1327, 1465, 441, 779),
                "fnst_rt_lat": (1359, 1382, 699, 732, 721),
                "fnst_rt_amp": (1359, 1382, 750, 777, 766),
                "fnst_lt_lat": (1436, 1459, 699, 732, 721),
                "fnst_lt_amp": (1436, 1459, 750, 777, 766),
                "reflex_rt": (453, 483, 139, 297),
                "reflex_lt": (453, 483, 887, 1045)
            }

    def process_and_show_auto_images(self, file_list):
        target_path = None
        
        for f in file_list:
            name, _ = os.path.splitext(os.path.basename(f).lower())
            if name.endswith("_1"):
                target_path = f
                break
                
        if not target_path: 
            return
            
        try:
            img_array = np.fromfile(target_path, np.uint8)
            img = cv2.imdecode(img_array, cv2.IMREAD_COLOR)
            
            if img is not None:
                h, w = img.shape[:2]
                coords = self._get_crop_coords(h, w)
                
                self._process_fnet(img, coords)
                self._process_fnst(img, coords)
                self._process_reflex(img, coords)
                
                self.ctrl.analyze_and_update()
        except Exception as e:
            print(f"[Blink Vision Error] 파일 로드 실패: {e}")

    def _add_padding(self, img, pad_size=5):
        return cv2.copyMakeBorder(img, pad_size, pad_size, pad_size, pad_size, cv2.BORDER_CONSTANT, value=[255, 255, 255])

    def _process_fnet(self, img, coords):
        try:
            y1, y2, x1, x2 = coords["fnet_rt"]
            rt_crop = img[y1:y2, x1:x2]
            
            y1, y2, x1, x2 = coords["fnet_lt"]
            lt_crop = img[y1:y2, x1:x2]
            
            rt_val, _ = OCRTool.extract_int(rt_crop)
            lt_val, _ = OCRTool.extract_int(lt_crop)
            
            rt_str = str(rt_val) if 0 < rt_val <= 19 else (">19" if rt_val > 19 else "X")
            lt_str = str(lt_val) if 0 < lt_val <= 19 else (">19" if lt_val > 19 else "X")
            
            self.ctrl.update_fnet(rt_str, lt_str)
        except Exception as e:
            print(f"[Blink Vision Error] FNET 처리 실패: {e}")

    def _process_fnst(self, img, coords):
        try:
            dy1, dy2, dx1, dx2 = coords["fnst_disp"]
            display_crop = img[dy1:dy2, dx1:dx2]
            qimg = cv2.cvtColor(display_crop, cv2.COLOR_BGR2RGB)
            pixmap = QPixmap.fromImage(QImage(qimg.data, qimg.shape[1], qimg.shape[0], qimg.shape[1] * 3, QImage.Format.Format_RGB888))
            self.ctrl.lbl_stim_image.setPixmap(pixmap.scaled(self.ctrl.lbl_stim_image.size(), Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation))

            def split_and_extract(coord_tuple):
                y1, y2, x1, x2, x_dot = coord_tuple
                
                left_crop = img[y1:y2, x1:x_dot]
                right_crop = img[y1:y2, x_dot+1:x2]
                
                def ocr_int(crop):
                    enlarged = cv2.resize(crop, None, fx=2.0, fy=2.0, interpolation=cv2.INTER_CUBIC)
                    gray = cv2.cvtColor(enlarged, cv2.COLOR_BGR2GRAY)
                    blur = cv2.GaussianBlur(gray, (3, 3), 0)
                    _, thresh = cv2.threshold(blur, 0, 255, cv2.THRESH_BINARY | cv2.THRESH_OTSU)
                    padded = cv2.copyMakeBorder(thresh, 10, 10, 10, 10, cv2.BORDER_CONSTANT, value=255)
                    
                    custom_config = r'--oem 3 --psm 8 -c tessedit_char_whitelist=0123456789'
                    return pytesseract.image_to_string(padded, config=custom_config).strip()
                    
                l_str = ocr_int(left_crop)
                r_str = ocr_int(right_crop)
                
                try:
                    if l_str and r_str:
                        return float(f"{l_str}.{r_str}")
                    elif l_str:
                        return float(l_str)
                except ValueError:
                    pass
                return None

            rt_lat = split_and_extract(coords["fnst_rt_lat"])
            rt_amp = split_and_extract(coords["fnst_rt_amp"])
            lt_lat = split_and_extract(coords["fnst_lt_lat"])
            lt_amp = split_and_extract(coords["fnst_lt_amp"])

            self.ctrl.update_fnst(rt_lat, rt_amp, lt_lat, lt_amp)
        except Exception as e:
            print(f"[Blink Vision Error] FNST 처리 실패: {e}")

    def _process_reflex(self, img, coords):
        try:
            ry1, ry2, rx1, rx2 = coords["reflex_rt"]
            rt_crop = img[ry1:ry2, rx1:rx2]
            
            ly1, ly2, lx1, lx2 = coords["reflex_lt"]
            lt_crop = img[ly1:ly2, lx1:lx2]

            def set_image(crop, label_widget):
                qimg = cv2.cvtColor(crop, cv2.COLOR_BGR2RGB)
                pixmap = QPixmap.fromImage(QImage(qimg.data, qimg.shape[1], qimg.shape[0], qimg.shape[1] * 3, QImage.Format.Format_RGB888))
                label_widget.setPixmap(pixmap.scaled(label_widget.size(), Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation))
            
            set_image(rt_crop, self.ctrl.lbl_reflex_img_rt)
            set_image(lt_crop, self.ctrl.lbl_reflex_img_lt)

            def extract_cells(crop):
                h, w = crop.shape[:2]
                cw = w / 3.0
                vals = []
                for i in range(3):
                    x1 = int(i * cw) + 2
                    x2 = int((i + 1) * cw) - 2
                    y1 = 2
                    y2 = h - 2
                    
                    cell = crop[y1:y2, x1:x2]
                    val, _ = OCRTool.extract_float(cell)
                    vals.append(val)
                return vals

            rt_vals = extract_cells(rt_crop)
            lt_vals = extract_cells(lt_crop)

            self.ctrl.update_reflex(rt_vals, lt_vals)
        except Exception as e:
            print(f"[Blink Vision Error] Reflex 처리 실패: {e}")