from dataclasses import dataclass

@dataclass
class MuscleData:
    root: str
    nerve: str

# --- Upper Extremity (U/E) ---
UE_MUSCLES = {
    "Biceps brachii": MuscleData("C5-6", "MC"),
    "Deltoid": MuscleData("C5-6", "Ax"),
    "Triceps brachii": MuscleData("C6-8", "R"),
    "Pronator teres": MuscleData("C6-7", "M"),
    "1st dorsal interosseous": MuscleData("C8-T1", "U"),
    "Abductor pollicis brevis": MuscleData("C8-T1", "M"),
}

UE_ORDER = [
    "Biceps brachii", "Deltoid", "Triceps brachii", 
    "Pronator teres", "1st dorsal interosseous", "Abductor pollicis brevis"
]

UE_TABS = {
    "Biceps brachii": 5, "Deltoid": 7, "Triceps brachii": 6,
    "Pronator teres": 6, "1st dorsal interosseous": 6, "Abductor pollicis brevis": 6,
}

UE_DEFAULT = ["Biceps brachii", "Pronator teres", "1st dorsal interosseous"]


# --- Lower Extremity (L/E) ---
LE_MUSCLES = {
    "Tibialis anterior": MuscleData("L4-5", "DP"),
    "Vastus lateralis": MuscleData("L2-4", "F"),
    "Peroneus longus": MuscleData("L5-S1", "SP"),
    "Gastrocnemius": MuscleData("S1-2", "T"),
    "Biceps femoris": MuscleData("L5-S2", "T"),
    "Tibialis posterior": MuscleData("L4-5", "T"),
}

LE_ORDER = [
    "Tibialis anterior", "Vastus lateralis", "Peroneus longus",
    "Gastrocnemius", "Biceps femoris", "Tibialis posterior"
]

LE_TABS = {
    "Tibialis anterior": 5, "Vastus lateralis": 7, "Peroneus longus": 6,
    "Gastrocnemius": 6, "Biceps femoris": 6, "Tibialis posterior": 6,
}

LE_DEFAULT = ["Vastus lateralis", "Tibialis anterior", "Gastrocnemius"]