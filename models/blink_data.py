from dataclasses import dataclass, field

@dataclass
class ExcitabilityData:
    rt_val: str = None
    lt_val: str = None

@dataclass
class StimulationData:
    lat: float = None
    amp: float = None

@dataclass
class ReflexData:
    r1: float = None
    r2i: float = None
    r2c: float = None

@dataclass
class LSRData:
    active: bool = False
    side: str = "Right"
    oculi_to_mentalis: bool = False
    mentalis_to_oculi: bool = False

@dataclass
class BlinkInput:
    excitability: ExcitabilityData = field(default_factory=ExcitabilityData)
    rt_stim: StimulationData = field(default_factory=StimulationData)
    lt_stim: StimulationData = field(default_factory=StimulationData)
    rt_reflex: ReflexData = field(default_factory=ReflexData)
    lt_reflex: ReflexData = field(default_factory=ReflexData)
    lsr: LSRData = field(default_factory=LSRData)

@dataclass
class BlinkResult:
    findings_text: str = ""
    conclusion_text: str = ""