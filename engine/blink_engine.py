from models.blink_data import BlinkInput, BlinkResult

class BlinkEngine:
    @staticmethod
    def analyze(data: BlinkInput) -> BlinkResult:
        res = BlinkResult()
        findings = []
        conclusion = ""

        # 1) Excitability
        rt_val, lt_val = data.excitability.rt_val, data.excitability.lt_val
        findings.append("Facial Nerve Excitability Test Findings")
        findings.append(f"Right ( {rt_val or '*'} mA ) Left ( {lt_val or '*'} mA )")
        
        if rt_val and lt_val:
            rt_norm = rt_val not in ['>19', 'X']
            lt_norm = lt_val not in ['>19', 'X']
            findings.append(f"- Bilateral facial nerve excitability thresholds were {'normal' if rt_norm and lt_norm else 'abnormal'}.")
            if rt_norm and lt_norm: 
                diff_norm = abs(int(rt_val) - int(lt_val)) < 4
                findings.append(f"- The difference of Bilateral facial nerve excitability thresholds was {'normal' if diff_norm else 'abnormal'}.")
            else: 
                findings.append("- The difference of Bilateral facial nerve excitability thresholds could not be assessed.")

        # 2) Stimulation
        rt_lat, rt_amp = data.rt_stim.lat, data.rt_stim.amp
        lt_lat, lt_amp = data.lt_stim.lat, data.lt_stim.amp
        stim_ok = all(v is not None for v in [rt_lat, rt_amp, lt_lat, lt_amp])
        
        if stim_ok:
            findings.append("\nFacial Nerve Stimulation Test Findings")
            findings.append(f"Right (latency : {rt_lat} ms ; amplitude : {rt_amp} mV)")
            findings.append(f"Left (latency : {lt_lat} ms ; amplitude : {lt_amp} mV)")
            lat_norm = (rt_lat < 3.08 and lt_lat < 3.08)
            amp_norm = (rt_amp >= 1.1 and lt_amp >= 1.1)
            findings.append(f"- On direct facial nerve stimulation, the facial nerves showed {'normal' if lat_norm else 'abnormal'} terminal latencies and {'normal' if amp_norm else 'abnormal'} CMAP amplitudes.")
            findings.append(f"- In side-to-side comparisons, the difference between CMAP amplitudes was {'normal' if abs(rt_amp - lt_amp) < 1.257 else 'abnormal'} (<1.257mV).")

        # 3) Blink Reflex
        rt_r1, rt_r2i, rt_r2c = data.rt_reflex.r1, data.rt_reflex.r2i, data.rt_reflex.r2c
        lt_r1, lt_r2i, lt_r2c = data.lt_reflex.r1, data.lt_reflex.r2i, data.lt_reflex.r2c
        reflex_ok = all(v is not None for v in [rt_r1, rt_r2i, rt_r2c, lt_r1, lt_r2i, lt_r2c])

        if reflex_ok:
            findings.append("\nBlink Reflex Test Findings")
            findings.append(f"1. RSRR (R1 : {rt_r1} ms, R2: {rt_r2i} ms) RSLR (R2 : {rt_r2c} ms)")
            findings.append(f"2. LSLR (R1 : {lt_r1} ms, R2: {lt_r2i} ms) LSRR (R2 : {lt_r2c} ms)")
            
            rt_norm = (rt_r1 < 12.2 and rt_r2i < 37.9 and rt_r2c < 39.2)
            lt_norm = (lt_r1 < 12.2 and lt_r2i < 37.9 and lt_r2c < 39.2)
            findings.append(f"- Stimulation of right supraorbital nerve resulted in {'normal' if rt_norm else 'abnormal'} ipsilateral R1, ipsilateral R2 and contralateral R2 latencies.")
            findings.append(f"- Stimulation of left supraorbital nerve resulted in {'normal' if lt_norm else 'abnormal'} ipsilateral R1, ipsilateral R2 and contralateral R2 latencies.")
            
            if abs(rt_r1 - lt_r1) < 1.2 and abs(rt_r2i - lt_r2i) < 5.0 and abs(rt_r2c - lt_r2c) < 7.0: 
                findings.append("- Side-to-side comparisons of all latencies were normal.")
            else:
                abnormal_diffs = [d for d, ok in [("R1", abs(rt_r1-lt_r1)<1.2), ("ipsi R2", abs(rt_r2i-lt_r2i)<5.0), ("contra R2", abs(rt_r2c-lt_r2c)<7.0)] if not ok]
                findings.append(f"- Side-to-side comparisons showed abnormal differences in {', '.join(abnormal_diffs)} latencies.")

        # 4) LSR
        if data.lsr.active:
            findings.append("\nLateral Spread Response Test Findings")
            side = data.lsr.side.lower()
            
            if data.lsr.oculi_to_mentalis: 
                findings.append(f"- Stimulation of the zygomatic branch of the {side} facial nerve resulted in an abnormal delayed response of the mandibular branch of the {side} facial nerve.")
            else: 
                findings.append(f"- Stimulation of the zygomatic branch of the {side} facial nerve resulted in normal response (no response) of the mandibular branch of the {side} facial nerve.")
                
            if data.lsr.mentalis_to_oculi: 
                findings.append(f"- Stimulation of the mandibular branch of the {side} facial nerve resulted in an abnormal delayed response of the zygomatic branch of the {side} facial nerve.")
            else: 
                findings.append(f"- Stimulation of the mandibular branch of the {side} facial nerve resulted in normal response (no response) of the zygomatic branch of the {side} facial nerve.")
                
        res.findings_text = "\n".join(findings)

        is_lsr_abnormal = data.lsr.active and (data.lsr.oculi_to_mentalis or data.lsr.mentalis_to_oculi)

        if is_lsr_abnormal:
            side = data.lsr.side.lower()
            conclusion = f"Abnormal study. There is electrophysiologic evidence of {side} lateral spread responses as can be seen in {side} hemifacial spasm. "
            if stim_ok and reflex_ok: 
                conclusion += "There is no definite electrophysiologic abnormality of bilateral blink reflex system and facial nerve conduction study. "
            conclusion += "Clinical correlation is recommended."
            
        elif stim_ok and reflex_ok:
            rt_amp_low, lt_amp_low = rt_amp < 1.1, lt_amp < 1.1
            rt_r1_ab, rt_r2i_ab, rt_r2c_ab = rt_r1 >= 12.2, rt_r2i >= 37.9, rt_r2c >= 39.2
            lt_r1_ab, lt_r2i_ab, lt_r2c_ab = lt_r1 >= 12.2, lt_r2i >= 37.9, lt_r2c >= 39.2
            is_normal = not (rt_amp_low or lt_amp_low or rt_r1_ab or rt_r2i_ab or rt_r2c_ab or lt_r1_ab or lt_r2i_ab or lt_r2c_ab)
            
            if is_normal:
                conclusion = "Normal study. There is no definite electrophysiologic abnormality of bilateral blink reflex system and facial nerve conduction study. "
                if data.lsr.active:
                    conclusion += "There is no definite electrophysiologic abnormality of lateral spread responses. "
                conclusion += "Clinical correlation is recommended."
            elif rt_r1_ab and rt_r2i_ab and rt_r2c_ab and not(lt_r1_ab or lt_r2i_ab or lt_r2c_ab): 
                conclusion = "Abnormal study. There is an electrophysiologic evidence for abnormality in the afferent pathway of the right blink reflex system. Clinical correlation is recommended."
            elif lt_r1_ab and lt_r2i_ab and lt_r2c_ab and not(rt_r1_ab or rt_r2i_ab or rt_r2c_ab): 
                conclusion = "Abnormal study. There is an electrophysiologic evidence for abnormality in the afferent pathway of the left blink reflex system. Clinical correlation is recommended."
            elif lt_amp_low or (rt_r2c_ab and lt_r2i_ab): 
                conclusion = "Abnormal study. There is electrophysiologic evidence for the left facial neuropathy. Clinical correlation is recommended."
            elif rt_amp_low or (lt_r2c_ab and rt_r2i_ab): 
                conclusion = "Abnormal study. There is electrophysiologic evidence for the right facial neuropathy. Clinical correlation is recommended."
            elif rt_r2i_ab and lt_r2i_ab: 
                conclusion = "Abnormal study. There is electrophysiologic abnormality in a ponto-medullary lesion. Clinical correlation is recommended."
            else: 
                conclusion = "Abnormal study. The findings suggest a complex pattern of facial and/or trigeminal nerve involvement. Clinical correlation is recommended."
        else:
            conclusion = "" 

        res.conclusion_text = conclusion
        return res