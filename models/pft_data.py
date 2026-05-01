from dataclasses import dataclass
from typing import Optional, List, Dict

# --- Reference Data for Normal Ranges ---
NORMAL_RANGES = {
    "MIP": {
        "Female": {"20-39": (60.0, 21.9), "40-59": (60.4, 23.5), ">=60": (62.0, 21.9)},
        "Male": {"20-39": (88.6, 23.2), "40-59": (94.4, 25.8), ">=60": (78.6, 27.4)}
    },
    "MEP": {
        "Female": {"20-39": (63.8, 14.8), "40-59": (61.4, 13.3), ">=60": (62.6, 10.8)},
        "Male": {"20-39": (87.3, 14.0), "40-59": (93.2, 25.5), ">=60": (79.9, 30.6)}
    },
    "SNIP": {
        "Female": {"20-39": (66.6, 12.0), "40-59": (75.7, 24.8), ">=60": (71.1, 19.5)},
        "Male": {"20-39": (96.4, 23.4), "40-59": (104.4, 32.6), ">=60": (85.8, 30.2)}
    }
}

@dataclass
class PFTPatientInfo:
    age: Optional[int] = None
    sex: Optional[str] = None
    height: Optional[int] = None
    weight: Optional[int] = None

@dataclass
class PFTDataInput:
    patient: PFTPatientInfo
    # 3x4 matrix for trials: [MIP, MEP, SNIP, PEF]
    trials: List[List[Optional[int]]] 
    fvc: Optional[int] = None
    fev1: Optional[int] = None

@dataclass
class PFTAnalysisResult:
    normal_ranges: Dict[str, str] # e.g., {"MIP": "38.1 - 81.9"}
    test_status: Dict[str, str]   # e.g., {"MIP": "Normal"}
    conclusion_text: str = ""