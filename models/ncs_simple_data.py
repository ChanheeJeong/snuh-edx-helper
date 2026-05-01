from dataclasses import dataclass, field
from typing import List, Optional

@dataclass
class NCSSimpleInput:
    # 1. 검사한 사지 (True/False)
    eval_lue: bool = False
    eval_rue: bool = False
    eval_lle: bool = False
    eval_rle: bool = False
    
    # 2. 질환 선택 (Normal, SMPN, CTS, Plantar)
    pattern: str = "Normal" 
    
    # 3. 추가 옵션
    is_demyelinating: bool = False # SMPN 전용
    
    # 4. 병이 있는 사지 (CTS, Plantar 전용)
    abnorm_lue: bool = False # CTS 선택 시 활성화
    abnorm_rue: bool = False # CTS 선택 시 활성화
    abnorm_lle: bool = False # Plantar 선택 시 활성화
    abnorm_rle: bool = False # Plantar 선택 시 활성화

@dataclass
class NCSSimpleResult:
    conclusion_text: str = ""