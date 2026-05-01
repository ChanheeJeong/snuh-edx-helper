import cv2
import numpy as np
import os
from PIL import Image

class ImageProcessor:
    @staticmethod
    def get_image_size_pil(file_path):
        if not os.path.exists(file_path): return None, None
        try:
            with Image.open(file_path) as img: return img.width, img.height
        except Exception:
            return None, None

    @staticmethod
    def _group_files_by_timestamp(file_list):
        groups = {}
        for file_path in file_list:
            filename = os.path.basename(file_path)
            timestamp = filename.split('_')[0]
            if timestamp not in groups: groups[timestamp] = []
            groups[timestamp].append(file_path)
        return groups

    @staticmethod
    def find_target_hrdb_file(file_list):
        if len(file_list) != 5: return None
        groups = ImageProcessor._group_files_by_timestamp(file_list)
        pair_files = []
        for timestamp, files in groups.items():
            if len(files) == 2:
                pair_files = files
                break
        if not pair_files: return None
        for file_path in pair_files:
            w, h = ImageProcessor.get_image_size_pil(file_path)
            if w == 4800 and h == 6480: return file_path
        return None

    @staticmethod
    def crop_patient_info(file_list):
        if len(file_list) != 5: return None
        groups = ImageProcessor._group_files_by_timestamp(file_list)
        new_report_files = []
        for timestamp, files in groups.items():
            if len(files) == 3:
                new_report_files = files
                break
        if not new_report_files: return None
        target_path = None
        for file_path in new_report_files:
            if os.path.splitext(os.path.basename(file_path))[0].endswith('_1'):
                target_path = file_path
                break
        if not target_path: return None
        try:
            img_array = np.fromfile(target_path, np.uint8)
            img = cv2.imdecode(img_array, cv2.IMREAD_COLOR)
            if img is None: return None
            cropped_img = img[829:1030, 129:1080]
            return cropped_img
        except Exception: return None

    @staticmethod
    def crop_ssr_graph(file_list):
        if len(file_list) != 5: return None
        groups = ImageProcessor._group_files_by_timestamp(file_list)
        old_report_files = []
        for timestamp, files in groups.items():
            if len(files) == 2:
                old_report_files = files
                break
        if not old_report_files: return None
        target_path = None
        for file_path in old_report_files:
            if os.path.splitext(os.path.basename(file_path))[0].endswith('_1'):
                target_path = file_path
                break
        if not target_path: return None
        try:
            img_array = np.fromfile(target_path, np.uint8)
            img = cv2.imdecode(img_array, cv2.IMREAD_COLOR)
            if img is None: return None
            cropped_img = img[325:1025, 102:1497]
            return cropped_img
        except Exception: return None

    @staticmethod
    def crop_unique_green_box(target_image_path):
        img_array = np.fromfile(target_image_path, np.uint8)
        img = cv2.imdecode(img_array, cv2.IMREAD_COLOR)
        if img is None: return None
        lower_green = np.array([35, 222, 18]) 
        upper_green = np.array([39, 226, 22])
        mask = cv2.inRange(img, lower_green, upper_green)
        contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        if not contours: return None
        cnt = max(contours, key=cv2.contourArea)
        x, y, w, h = cv2.boundingRect(cnt)
        cropped_img = img[y:y+h, x:x+w]
        return cropped_img

    @staticmethod
    def crop_tilt_table(file_list):
        if len(file_list) != 5: return None
        groups = ImageProcessor._group_files_by_timestamp(file_list)
        old_report_files = []
        for timestamp, files in groups.items():
            if len(files) == 2:
                old_report_files = files
                break
        if not old_report_files: return None
        target_path = None
        for file_path in old_report_files:
            if os.path.splitext(os.path.basename(file_path))[0].endswith('_2'):
                target_path = file_path
                break
        if not target_path: return None
        try:
            img_array = np.fromfile(target_path, np.uint8)
            img = cv2.imdecode(img_array, cv2.IMREAD_COLOR)
            if img is None: return None
            cropped_img = img[2077:3067, 649:3087]
            return cropped_img
        except Exception: return None

    @staticmethod
    def crop_valsalva_boxes(file_list):
        if len(file_list) != 5: return None

        groups = ImageProcessor._group_files_by_timestamp(file_list)
        old_report_files = []
        for timestamp, files in groups.items():
            if len(files) == 2:
                old_report_files = files
                break
        if not old_report_files: return None

        target_path = None
        for file_path in old_report_files:
            if os.path.splitext(os.path.basename(file_path))[0].endswith('_2'):
                target_path = file_path
                break
        if not target_path: return None

        try:
            img_array = np.fromfile(target_path, np.uint8)
            img = cv2.imdecode(img_array, cv2.IMREAD_COLOR)
            if img is None: return None

            lower_gray = np.array([235, 225, 215])
            upper_gray = np.array([245, 235, 225])
            mask = cv2.inRange(img, lower_gray, upper_gray)

            contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
            contours = sorted(contours, key=cv2.contourArea, reverse=True)
            if len(contours) < 2: return None
            
            target_contours = contours[:2]
            rects = [cv2.boundingRect(c) for c in target_contours]
            rects.sort(key=lambda r: r[0])
            
            left_rect = rects[0]
            right_rect = rects[1]

            a = left_rect[0]
            b = left_rect[1]
            c = right_rect[0] + right_rect[2] 
            d = max(left_rect[1] + left_rect[3], right_rect[1] + right_rect[3]) 

            img_h, img_w = img.shape[:2]

            crop_x_start = max(0, a - 10)
            crop_y_start = max(0, b - 10)
            crop_x_end = min(img_w, c + 10)
            
            # [수정] 아래쪽 패딩을 +300에서 +280으로 축소
            crop_y_end = min(img_h, d + 280)

            cropped_img = img[crop_y_start:crop_y_end, crop_x_start:crop_x_end]
            
            print(f"[processor success] Valsalva 크롭 완료 (크기: {cropped_img.shape[1]}x{cropped_img.shape[0]})")
            return cropped_img

        except Exception as e:
            print(f"[processor error] Valsalva 크롭 중 오류: {e}")
            return None
        
    # =========================================================================
    # [새로운 기능] Valsalva 세부 그래프 분석용 크롭 (newreport_2)
    # =========================================================================
    @staticmethod
    def crop_valsalva_graph(file_list):
        """
        3개짜리 리포트 세트에서 '_2' 파일을 찾아
        지정된 좌표 (240, 280) ~ (2300, 2075)을 크롭합니다.
        numpy 슬라이싱: y=[280:2075], x=[240:2300]
        """
        if len(file_list) != 5: return None

        groups = ImageProcessor._group_files_by_timestamp(file_list)
        new_report_files = []
        for timestamp, files in groups.items():
            if len(files) == 3:
                new_report_files = files
                break
        
        if not new_report_files: return None

        target_path = None
        for file_path in new_report_files:
            if os.path.splitext(os.path.basename(file_path))[0].endswith('_2'):
                target_path = file_path
                break
        
        if not target_path: return None

        try:
            img_array = np.fromfile(target_path, np.uint8)
            img = cv2.imdecode(img_array, cv2.IMREAD_COLOR)
            if img is None: return None

            # [핵심] 지정된 거대 좌표 크롭 (크기: 2060x1795)
            cropped_img = img[280:2075, 240:2300]
            print(f"[processor success] Valsalva 그래프 크롭 완료 (크기: {cropped_img.shape[1]}x{cropped_img.shape[0]})")
            return cropped_img

        except Exception as e:
            print(f"[processor error] Valsalva 그래프 크롭 중 오류: {e}")
            return None