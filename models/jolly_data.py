from dataclasses import dataclass

@dataclass
class JollyInput:
    side: str = "Left"
    low_freq_normal: bool = True
    high_freq_normal: bool = True
    
    # Abnormalities
    low_oculi: bool = False
    low_adq: bool = False
    low_fcu: bool = False
    test_trapezius: bool = False
    low_trapezius: bool = False
    
    high_fcu: bool = False  # FCU 먼저
    high_adq: bool = False
    high_abnormal_type: str = "decremental" # "decremental" or "incremental"

@dataclass
class JollyResult:
    findings_text: str = ""
    conclusion_text: str = ""