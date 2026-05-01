from models.ncs_simple_data import NCSSimpleInput, NCSSimpleResult

class NCSSimpleEngine:
    @staticmethod
    def _format_limb_list(limbs: list) -> str:
        if not limbs: return ""
        
        has_left_arm = "left arm" in limbs
        has_right_arm = "right arm" in limbs
        has_left_leg = "left leg" in limbs
        has_right_leg = "right leg" in limbs
        
        formatted = []
        if has_left_arm and has_right_arm: formatted.append("bilateral arms")
        elif has_left_arm: formatted.append("left arm")
        elif has_right_arm: formatted.append("right arm")
        
        if has_left_leg and has_right_leg: formatted.append("bilateral legs")
        elif has_left_leg: formatted.append("left leg")
        elif has_right_leg: formatted.append("right leg")
        
        if len(formatted) == 1: return formatted[0]
        if len(formatted) == 2: return " and ".join(formatted)
        return ", ".join(formatted[:-1]) + ", and " + formatted[-1]

    @staticmethod
    def analyze(data: NCSSimpleInput) -> NCSSimpleResult:
        eval_limbs = []
        if data.eval_lue: eval_limbs.append("left arm")
        if data.eval_rue: eval_limbs.append("right arm")
        if data.eval_lle: eval_limbs.append("left leg")
        if data.eval_rle: eval_limbs.append("right leg")

        if not eval_limbs:
            return NCSSimpleResult(conclusion_text="Please select at least one evaluated limb.")

        eval_str = NCSSimpleEngine._format_limb_list(eval_limbs)
        conclusion = ""

        # 1. Normal
        if data.pattern == "Normal":
            conclusion = f"Normal study. There is no definite electrophysiologic evidence of peripheral neuropathy in the {eval_str}. Clinical correlation is recommended."
        
        # 2. SMPN
        elif data.pattern == "SMPN":
            demyel_str = " (demyelinating type)" if data.is_demyelinating else ""
            conclusion = f"Abnormal study. There is electrophysiologic evidence of sensorimotor polyneuropathy{demyel_str} in the {eval_str}. Clinical correlation is recommended."
            
        # 3. CTS
        elif data.pattern == "CTS":
            abnorm_arms = []
            if data.abnorm_lue: abnorm_arms.append("left")
            if data.abnorm_rue: abnorm_arms.append("right")
            
            if not abnorm_arms:
                return NCSSimpleResult(conclusion_text="Please select at least one abnormal arm for CTS.")
            
            cts_side = "bilateral" if len(abnorm_arms) == 2 else abnorm_arms[0]
            cts_plural = "syndromes" if cts_side == "bilateral" else "syndrome"
            
            conclusion = f"Abnormal study. There is electrophysiologic evidence of the {cts_side} carpal tunnel {cts_plural}."
            
            # [수정된 핵심 로직] 검사했지만 병변으로 체크되지 않은 모든 사지 추출
            normal_limbs = []
            if data.eval_lue and not data.abnorm_lue: normal_limbs.append("left arm")
            if data.eval_rue and not data.abnorm_rue: normal_limbs.append("right arm")
            if data.eval_lle and not data.abnorm_lle: normal_limbs.append("left leg")
            if data.eval_rle and not data.abnorm_rle: normal_limbs.append("right leg")
            
            if normal_limbs:
                norm_limb_str = NCSSimpleEngine._format_limb_list(normal_limbs)
                conclusion += f" There is no definite electrophysiologic evidence of peripheral neuropathy in the {norm_limb_str}."
                
            conclusion += " Clinical correlation is recommended."
            
        # 4. Plantar Sensory Neuropathy
        elif data.pattern == "Plantar":
            abnorm_legs = []
            if data.abnorm_lle: abnorm_legs.append("left")
            if data.abnorm_rle: abnorm_legs.append("right")
            
            if not abnorm_legs:
                return NCSSimpleResult(conclusion_text="Please select at least one abnormal leg for Plantar neuropathy.")
            
            plantar_side = "bilateral" if len(abnorm_legs) == 2 else abnorm_legs[0]
            
            conclusion = f"Abnormal study. There is electrophysiologic evidence of {plantar_side} plantar sensory neuropathy."
            
            # [수정된 핵심 로직] 검사했지만 병변으로 체크되지 않은 모든 사지 추출
            normal_limbs = []
            if data.eval_lue and not data.abnorm_lue: normal_limbs.append("left arm")
            if data.eval_rue and not data.abnorm_rue: normal_limbs.append("right arm")
            if data.eval_lle and not data.abnorm_lle: normal_limbs.append("left leg")
            if data.eval_rle and not data.abnorm_rle: normal_limbs.append("right leg")
            
            if normal_limbs:
                norm_limb_str = NCSSimpleEngine._format_limb_list(normal_limbs)
                conclusion += f" There is no definite electrophysiologic evidence of peripheral neuropathy in the {norm_limb_str}."
                
            conclusion += " Clinical correlation is recommended."

        return NCSSimpleResult(conclusion_text=conclusion)