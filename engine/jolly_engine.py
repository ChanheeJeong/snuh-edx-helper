from models.jolly_data import JollyInput, JollyResult

class JollyEngine:
    @staticmethod
    def analyze(data: JollyInput) -> JollyResult:
        res = JollyResult()
        findings = []
        
        side = data.side.lower()
        any_low_abnormal = data.low_oculi or data.low_adq or data.low_fcu or (data.test_trapezius and data.low_trapezius)
        any_high_abnormal = data.high_fcu or data.high_adq
        is_abnormal = any_low_abnormal or any_high_abnormal

        def _format_muscles(muscles):
            if not muscles: return ""
            if len(muscles) == 1:
                return f"{muscles[0]} muscle"
            return ", ".join(muscles[:-1]) + f" and {muscles[-1]} muscles"

        # 검사한 근육 목록 취합
        tested_muscles = ["orbicularis oculi", "abductor digiti quinti", "flexor carpi ulnaris"]
        if data.test_trapezius:
            tested_muscles.append("trapezius")

        findings.append(f"<Jolly Test Findings>\nJolly test was performed at the {side} {_format_muscles(tested_muscles)}.")
        
        idx = 1
        
        # ==========================================
        # 1. Low Frequency Stimulation (LFS)
        # ==========================================
        lfs_all = [("orbicularis oculi", data.low_oculi), 
                   ("abductor digiti quinti", data.low_adq), 
                   ("flexor carpi ulnaris", data.low_fcu)]
        if data.test_trapezius:
            lfs_all.append(("trapezius", data.low_trapezius))
            
        if data.low_freq_normal:
            normals = [m[0] for m in lfs_all]
            findings.append(f"{idx}) No abnormal decremental responses at low rate stimulations (2, 3, 5Hz) in {side} {_format_muscles(normals)}.")
            idx += 1
        else:
            abnormals = [m[0] for m in lfs_all if m[1]]
            normals = [m[0] for m in lfs_all if not m[1]]
            
            if abnormals:
                findings.append(f"{idx}) Abnormal decremental responses occurred at low rate stimulations (2, 3, 5Hz) in {side} {_format_muscles(abnormals)}.")
                idx += 1
            if normals:
                findings.append(f"{idx}) No abnormal decremental responses at low rate stimulations (2, 3, 5Hz) in {side} {_format_muscles(normals)}.")
                idx += 1

        # ==========================================
        # 2. High Frequency Stimulation (HFS)
        # ==========================================
        hfs_all = [("flexor carpi ulnaris", data.high_fcu), 
                   ("abductor digiti quinti", data.high_adq)]
                   
        if data.high_freq_normal:
            normals = [m[0] for m in hfs_all]
            findings.append(f"{idx}) No abnormal decremental responses or abnormal incremental responses at high rate stimulations (30Hz) in {side} {_format_muscles(normals)}.")
        else:
            abnormals = [m[0] for m in hfs_all if m[1]]
            normals = [m[0] for m in hfs_all if not m[1]]
            
            if abnormals:
                findings.append(f"{idx}) Abnormal {data.high_abnormal_type} responses at high rate stimulations (30Hz) in {side} {_format_muscles(abnormals)}.")
                idx += 1
            if normals:
                findings.append(f"{idx}) No abnormal decremental responses or abnormal incremental responses at high rate stimulations (30Hz) in {side} {_format_muscles(normals)}.")

        res.findings_text = "\n".join(findings)

        # ==========================================
        # 3. Conclusion 생성
        # ==========================================
        if not is_abnormal:
            conclusion = "Normal study. There is no electrophysiologic evidence of abnormality in neuromuscular junction transmission. Clinical correlation is recommended."
        else:
            # Incremental 이상 소견이 메인이라면 LEMS로 멘트 변경
            if any_high_abnormal and data.high_abnormal_type == "incremental":
                conclusion = "Abnormal study. There is electrophysiologic evidence of abnormality in neuromuscular junction transmission as seen in LEMS. Clinical correlation is recommended."
            else:
                conclusion = "Abnormal study. There is electrophysiologic evidence of abnormality in neuromuscular junction transmission as seen in MG. Clinical correlation is recommended."
            
        conclusion += "\n\n**현재 가판독 상태이며 추후 정식 판독을 참조하기 바람."
        res.conclusion_text = conclusion
        
        return res