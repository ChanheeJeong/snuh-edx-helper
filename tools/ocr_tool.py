import cv2
import pytesseract
import re
import os
import sys

if getattr(sys, 'frozen', False):
    # PyInstaller로 빌드된 .exe 환경일 때
    base_dir = os.path.dirname(sys.executable)
else:
    # 파이썬 스크립트(.py)로 실행할 때 (modules 폴더 안이므로 한 칸 위로)
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

tesseract_path = os.path.join(base_dir, 'Tesseract-OCR', 'tesseract.exe')
pytesseract.pytesseract.tesseract_cmd = tesseract_path

class OCRTool:
    @staticmethod
    def extract_float(cv_img):
        """HRDB, Valsalva 등을 위한 소수점 숫자 추출 (이전의 안정적인 버전으로 롤백)"""
        try:
            resized = cv2.resize(cv_img, None, fx=2, fy=2, interpolation=cv2.INTER_CUBIC)
            gray = cv2.cvtColor(resized, cv2.COLOR_BGR2GRAY)
            _, thresh = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY | cv2.THRESH_OTSU)
            
            raw_text = pytesseract.image_to_string(thresh, config='--psm 6').strip()
            matches = re.findall(r'\d+\.\d+', raw_text)
            
            val = matches[0] if matches else "N/A"
            return val, raw_text
        except Exception as e:
            return "N/A", str(e)

    @staticmethod
    def extract_int(cv_img):
        """Tilt Table을 위한 정수 추출 (테두리 노이즈 제거를 위한 패딩 적용)"""
        try:
            resized = cv2.resize(cv_img, None, fx=2, fy=2, interpolation=cv2.INTER_CUBIC)
            gray = cv2.cvtColor(resized, cv2.COLOR_BGR2GRAY)
            
            # 표 테두리가 글자로 인식되지 않도록 흰색 여백(Padding)을 줍니다.
            padded = cv2.copyMakeBorder(gray, 20, 20, 20, 20, cv2.BORDER_CONSTANT, value=255)
            _, thresh = cv2.threshold(padded, 0, 255, cv2.THRESH_BINARY | cv2.THRESH_OTSU)
            
            # 따옴표 없는 안전한 화이트리스트 적용
            config = '--psm 6 -c tessedit_char_whitelist=0123456789'
            raw_text = pytesseract.image_to_string(thresh, config=config).strip()
            
            matches = re.findall(r'\d+', raw_text)
            val = int(matches[0]) if matches else 0
            return val, raw_text
        except Exception as e:
            return 0, str(e)

    @staticmethod
    def extract_date(cv_img):
        """환자 정보에서 날짜 추출"""
        try:
            resized = cv2.resize(cv_img, None, fx=2, fy=2, interpolation=cv2.INTER_CUBIC)
            gray = cv2.cvtColor(resized, cv2.COLOR_BGR2GRAY)
            _, thresh = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY | cv2.THRESH_OTSU)
            
            raw_text = pytesseract.image_to_string(thresh, config='--psm 6').strip()
            matches = re.findall(r'(\d{2})/(\d{2})/(\d{4})', raw_text)
            
            val = matches[0] if matches else None
            return val, raw_text
        except Exception as e:
            return None, str(e)