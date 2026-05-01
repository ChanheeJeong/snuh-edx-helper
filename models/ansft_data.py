from dataclasses import dataclass, field
from typing import List

# ==========================================
# 1. 입력 데이터 모델 (UI -> Engine)
# ==========================================
@dataclass
class PatientInfo:
    age: int = 0

@dataclass
class SSRData:
    palm_normal: bool = True
    sole_normal: bool = True

@dataclass
class HRDBData:
    is_arrhythmia: bool = False
    val1: str = "N/A"
    val2: str = "N/A"

@dataclass
class TiltData:
    # 5 rows (Supine, 1m, 3m, 5m, 10m), 3 cols (SBP, DBP, HR)
    records: List[List[int]] = field(default_factory=lambda: [[0,0,0] for _ in range(5)])

@dataclass
class ValsalvaData:
    is_arrhythmia: bool = False
    is_analyzed: bool = False
    is_poor: bool = False
    val_ratio: str = "N/A"
    normal_val_ratio: str = "N/A"
    prt_sec: str = "N/A"
    p2l_exists: bool = True
    p4_exists: bool = True
    overshoot_state: bool = True

@dataclass
class ANSFTInput:
    patient: PatientInfo
    ssr: SSRData
    hrdb: HRDBData
    tilt: TiltData
    valsalva: ValsalvaData


# ==========================================
# 2. 진단 결과 모델 (Engine -> Formatter)
# ==========================================
@dataclass
class ANSFTResult:
    # SSR Result
    ssr_finding: str = ""
    ssr_analysis_plain: str = ""
    ssr_status: str = "normal"  # 'normal', 'abnormal', 'pending'
    is_sudo: bool = False

    # HRDB Result
    hrdb_finding: str = ""
    hrdb_analysis_plain: str = ""
    hrdb_status: str = "pending"
    is_cv_hrdb: bool = False

    # Tilt Result
    tilt_finding: str = ""
    tilt_analysis_plains: List[str] = field(default_factory=list)
    tilt_statuses: List[str] = field(default_factory=list)
    oh_found: bool = False
    delayed_oh_found: bool = False
    pots_found: bool = False

    # Valsalva Result
    val_finding: str = ""
    val_analysis_plains: List[str] = field(default_factory=list)
    val_statuses: List[str] = field(default_factory=list)
    is_val_adr_abnormal: bool = False
    is_cv_val_severe: bool = False
    is_cv_val_mild: bool = False