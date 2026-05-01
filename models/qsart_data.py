from dataclasses import dataclass, field
from typing import List

@dataclass
class QsartSiteData:
    volume_str: str = "N/A"
    volume_float: float = 0.0
    is_valid: bool = False
    is_persistent: bool = False

@dataclass
class QSARTInput:
    sex: str = "Male"
    side: str = "left" 
    volumes: List[QsartSiteData] = field(default_factory=lambda: [QsartSiteData() for _ in range(4)])

@dataclass
class QsartSiteResult:
    status: str = "Pending"
    norm_range_str: str = ""

@dataclass
class QSARTResult:
    site_results: List[QsartSiteResult] = field(default_factory=lambda: [QsartSiteResult() for _ in range(4)])
    findings_text: str = ""
    conclusion_text: str = ""