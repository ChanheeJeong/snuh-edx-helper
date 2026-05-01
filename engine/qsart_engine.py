from models.qsart_data import QSARTInput, QSARTResult, QsartSiteResult

class QSARTEngine:
    NORMS = {
        "Male": [(0.06, 2.62), (0.31, 3.09), (0.17, 3.37), (0.08, 1.26)],
        "Female": [(0.08, 1.38), (0.15, 1.66), (0.10, 1.73), (0.05, 0.84)]
    }

    @staticmethod
    def _format_list(items: list) -> str:
        """리스트를 영어 문법에 맞게 쉼표와 and로 묶어줍니다."""
        if not items:
            return ""
        if len(items) == 1:
            return items[0]
        if len(items) == 2:
            return f"{items[0]} and {items[1]}"
        return ", ".join(items[:-1]) + f", and {items[-1]}"

    @staticmethod
    def analyze(data: QSARTInput) -> QSARTResult:
        res = QSARTResult()
        norms_for_sex = QSARTEngine.NORMS.get(data.sex, QSARTEngine.NORMS["Male"])
        
        names = ["forearm", "proximal leg", "distal leg", "foot"]
        reduced_sites = []
        increased_sites = []
        normal_sites = []
        persistent_sites = []

        for i in range(4):
            site_in = data.volumes[i]
            min_val, max_val = norms_for_sex[i]
            res.site_results[i].norm_range_str = f"{min_val:.2f} - {max_val:.2f}"

            if not site_in.is_valid:
                res.site_results[i].status = "Pending"
                continue
                
            val = site_in.volume_float
            if val < min_val:
                res.site_results[i].status = "Reduced"
                reduced_sites.append(names[i])
            elif val > max_val:
                res.site_results[i].status = "Increased"
                increased_sites.append(names[i])
            else:
                res.site_results[i].status = "Normal"
                normal_sites.append(names[i])

            if site_in.is_persistent:
                persistent_sites.append(names[i])

        # 모든 수치가 입력되었는지 확인 (하나라도 Pending이면 빈 텍스트 반환)
        is_all_valid = (len(reduced_sites) + len(increased_sites) + len(normal_sites) == 4)

        if not is_all_valid:
            res.findings_text = ""
            res.conclusion_text = ""
            return res

        # =========================================================
        # 1. Findings 텍스트 조립 (복합 소견 완벽 대응)
        # =========================================================
        
        # 1-1. Sweat Volume
        vol_sentences = []
        
        if len(reduced_sites) == 4:
            vol_sentences.append("Markedly reduced sweat volumes across all tested sites (forearm, proximal leg, distal leg, and foot).")
        elif len(reduced_sites) > 0:
            vol_sentences.append(f"Significant reduction in sweat volume at the {data.side} {QSARTEngine._format_list(reduced_sites)}.")

        if len(increased_sites) == 4:
            vol_sentences.append("Total sweat volumes are significantly increased across all tested sites (forearm, proximal leg, distal leg, and foot).")
        elif len(increased_sites) > 0:
            vol_sentences.append(f"Total sweat volume is significantly increased at the {data.side} {QSARTEngine._format_list(increased_sites)}.")

        if len(normal_sites) == 4:
            vol_sentences.append("Total sweat volumes at all tested sites (forearm, proximal leg, distal leg, and foot) are within normal limits.")
        elif len(normal_sites) > 0:
            # 감소 소견만 있을 때는 preserved를, 증가나 복합 소견일 때는 within normal limits를 사용합니다.
            norm_verb = "preserved" if len(reduced_sites) > 0 and len(increased_sites) == 0 else "within normal limits"
            norm_str = QSARTEngine._format_list(normal_sites)
            vol_sentences.append(f"{norm_str[0].upper() + norm_str[1:]} sweat volumes are {norm_verb}.")

        vol_text = "- Sweat Volume: " + " ".join(vol_sentences)

        # 1-2. Sweat Pattern
        if len(persistent_sites) > 0:
            persistent_str = QSARTEngine._format_list(persistent_sites)
            pat_text = f"- Sweat Pattern: Persistent sweat production is observed at the {data.side} {persistent_str} after the cessation of iontophoresis."
        else:
            pat_text = "- Sweat Pattern: The sweat response appropriately returned to baseline following the cessation of iontophoresis."

        res.findings_text = f"{vol_text}\n{pat_text}"

        # =========================================================
        # 2. Conclusion 구조식(Bullet) 조립
        # =========================================================
        
        # 완전 정상인 경우
        if len(reduced_sites) == 0 and len(increased_sites) == 0 and len(persistent_sites) == 0:
            res.conclusion_text = "Normal QSART study. Clinical correlation is recommended."
        else:
            statements = []
            
            # (1) 감소 (Reduced) 판단
            if len(reduced_sites) == 4:
                statements.append("Generalized sudomotor dysfunction.")
            elif len(reduced_sites) > 0:
                reduced_set = set(reduced_sites)
                is_length_dependent = reduced_set in [{"foot"}, {"distal leg", "foot"}, {"proximal leg", "distal leg", "foot"}]
                if is_length_dependent:
                    statements.append("Length-dependent pattern of sudomotor neuropathy.")
                else:
                    reduced_str = QSARTEngine._format_list(reduced_sites)
                    statements.append(f"Focal/segmental sudomotor dysfunction at the {data.side} {reduced_str}.")

            # (2) 증가 (Increased) 판단
            if len(increased_sites) > 0:
                prefix = "Generalized" if len(increased_sites) == 4 else "Focal"
                site_str = "" if len(increased_sites) == 4 else f" at the {data.side} {QSARTEngine._format_list(increased_sites)}"
                statements.append(f"{prefix} sudomotor hyper-reactivity{site_str}.")

            # (3) 지속적 반응 (Persistent) 판단
            if len(persistent_sites) > 0:
                prefix = "Generalized" if len(persistent_sites) == 4 else "Focal"
                site_str = "" if len(persistent_sites) == 4 else f" at the {data.side} {QSARTEngine._format_list(persistent_sites)}"
                statements.append(f"{prefix} sudomotor hyperexcitability{site_str}.")

            # 마무리 문구 추가 및 구조식(\n-) 병합
            statements.append("Clinical correlation is recommended.")
            res.conclusion_text = "\n".join([f"- {s}" for s in statements])

        return res