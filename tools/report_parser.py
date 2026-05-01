class ReportParser:
    @staticmethod
    def generate_text(age, palm_normal, sole_normal, hrdb_val1, hrdb_val2, tilt_data, 
                      val_ratio, normal_val_ratio, prt_sec, 
                      is_poor, p2l_exists, p4_exists, overshoot_state, 
                      is_valsalva_analyzed, is_hrdb_arrhythmia=False, is_val_arrhythmia=False):
        
        # 색상 태그 함수
        def colorize(text, status):
            if status == 'normal': return f"<span style='color: #27ae60; font-weight: bold;'>{text}</span>"
            elif status == 'abnormal': return f"<span style='color: #e74c3c; font-weight: bold;'>{text}</span>"
            elif status == 'pending': return f"<span style='color: #d35400; font-weight: bold;'>{text}</span>"
            return text

        # ==========================================
        # 1. SSR 논리 (Sudomotor)
        # ==========================================
        is_sudo = False
        if palm_normal and sole_normal:
            ssr_finding = "- Normal SSRs in both palms and soles"
            ssr_analysis = colorize("- sudomotor function is within normal limits", "normal")
        elif not palm_normal and not sole_normal:
            ssr_finding = "- Absent SSRs in both palms and soles"
            ssr_analysis = colorize("- sudomotor dysfunction is suggested", "abnormal")
            is_sudo = True
        elif palm_normal and not sole_normal:
            ssr_finding = "- Normal SSRs in both palms but absent in both soles"
            if age >= 65:
                ssr_analysis = colorize("- sudomotor function is within normal limits", "normal")
            else:
                ssr_analysis = colorize("- sudomotor dysfunction is suggested", "abnormal")
                is_sudo = True
        else:
            ssr_finding = "- Abnormal SSRs in palms but normal in soles"
            ssr_analysis = colorize("- sudomotor dysfunction is suggested", "abnormal")
            is_sudo = True

        # ==========================================
        # 2. HRDB 논리 (Cardiovagal 파트 1)
        # ==========================================
        is_cv_hrdb = False
        if is_hrdb_arrhythmia:
            hrdb_finding = "- Not interpretable due to arrhythmia"
            hrdb_analysis = colorize("- Analysis skipped due to arrhythmia", "pending")
        else:
            hrdb_finding = f"- E/I ratio: {hrdb_val1} (Normal average E/I ratio: >{hrdb_val2})"
            try:
                if float(hrdb_val1) >= float(hrdb_val2):
                    hrdb_analysis = colorize("- cardiovagal function is within normal limits", "normal")
                else:
                    hrdb_analysis = colorize("- cardiovagal dysfunction is suggested", "abnormal")
                    is_cv_hrdb = True
            except:
                hrdb_analysis = colorize("- cardiovagal function analysis pending (OCR error)", "pending")

        # ==========================================
        # 3. Tilt Table 논리 (Adrenergic 파트 1)
        # ==========================================
        tilt_finding = "- No significant change of BP and HR on orthostatic challenge"
        tilt_analysis = []
        oh_found, delayed_oh_found, pots_found = False, False, False

        if len(tilt_data) == 5:
            oh_text, hr_comp_text, pots_text = "", "", ""
            baseline_sbp, baseline_dbp, baseline_hr = tilt_data[0]

            for i in range(1, 5): 
                t_min = {1:1, 2:3, 3:5, 4:10}[i]
                t_str = f"within {3 if t_min <=3 else t_min} minutes"

                sbp, dbp, hr = tilt_data[i]
                if sbp == 0 or dbp == 0 or hr == 0: continue 
                if baseline_sbp == 0 or baseline_dbp == 0 or baseline_hr == 0: continue 

                drop_sbp = baseline_sbp - sbp
                drop_dbp = baseline_dbp - dbp
                d_hr = hr - baseline_hr

                is_sbp_drop = drop_sbp >= 20
                is_dbp_drop = drop_dbp >= 10

                if (is_sbp_drop or is_dbp_drop) and not oh_found and not delayed_oh_found:
                    rounded_sbp = (drop_sbp // 10) * 10 if drop_sbp >= 0 else 0
                    rounded_dbp = (drop_dbp // 10) * 10 if drop_dbp >= 0 else 0

                    if is_sbp_drop and is_dbp_drop: 
                        cause = f"Systolic/diastolic BP decreased by {rounded_sbp}/{rounded_dbp} mmHg"
                    elif is_sbp_drop: 
                        cause = f"Systolic BP decreased by {rounded_sbp} mmHg"
                    else: 
                        cause = f"Diastolic BP decreased by {rounded_dbp} mmHg"

                    if drop_sbp != 0:
                        hr_comp = abs(d_hr / drop_sbp) > 0.5
                    else:
                        hr_comp = (d_hr > 10)

                    if not hr_comp:
                        prefix = "Neurogenic OH"
                        oh_found = True
                        hr_comp_text = ", without HR compensation."
                    else:
                        if t_min <= 3:
                            prefix = "Classic OH"
                            oh_found = True
                        else:
                            prefix = "Delayed OH"
                            delayed_oh_found = True
                        hr_comp_text = ", with HR compensation."

                    oh_text = f"- {prefix}: {cause} {t_str}"
                    break 

            if not oh_found and not delayed_oh_found:
                max_d_hr = max([tilt_data[i][2] - baseline_hr for i in range(1, 5) if tilt_data[i][2] != 0]) if any(tilt_data[i][2] != 0 for i in range(1,5)) else 0
                cutoff = 40 if 12 <= age <= 19 else 30
                if max_d_hr >= cutoff:
                    pots_found = True
                    pots_text = f"- POTS: Heart rate increased by more than {cutoff} bpm"
                    if cutoff == 40: pots_text += " (ages 12-19)"
                    pots_text += " within 10 minutes of head-up tilt, in the absence of OH."

            if oh_found or delayed_oh_found: tilt_finding = oh_text + hr_comp_text
            elif pots_found: tilt_finding = pots_text

            if pots_found:
                tilt_analysis.append(colorize("- sympathetic overactivity", "abnormal"))
            if oh_found or delayed_oh_found:
                tilt_analysis.append(colorize("- sympathetic adrenergic dysfunction", "abnormal"))
                
            if not oh_found and not delayed_oh_found and not pots_found:
                tilt_analysis.append(colorize("- sympathetic adrenergic and cardiovagal functions are within normal limits", "normal"))
        else:
            tilt_analysis.append(colorize("- Analysis pending", "pending"))

        tilt_analysis_text = "\n".join(tilt_analysis)

        # ==========================================
        # 4. Valsalva 논리 (Adrenergic & Cardiovagal 2)
        # ==========================================
        val_analysis_list = []
        is_val_adr_abnormal = False
        is_cv_val_severe = False
        is_cv_val_mild = False

        if is_val_arrhythmia:
            val_finding = "- Not interpretable due to arrhythmia"
            val_analysis_text = colorize("- Analysis skipped due to arrhythmia", "pending")
            is_valsalva_analyzed = True 
        
        elif not is_valsalva_analyzed:
            val_finding = "- Analysis pending (그래프 분석 대기 중)"
            val_analysis_text = colorize("- Analysis pending", "pending")
            
        elif is_poor:
            val_finding = "- Poor valsalva maneuver"
            val_analysis_list.append(colorize("- Analysis pending due to poor maneuver", "pending"))
            val_analysis_text = "\n".join(val_analysis_list)
        else:
            val_finding = f"- Valsalva ratio: {val_ratio} (Normal Valsalva phase and ratio: {normal_val_ratio})\n"
            val_finding += f"- Pressure recovery time: {prt_sec} sec (PRT normal range <5.00 sec)\n"

            if p2l_exists and p4_exists:
                adr_str = "Absence of Phase II_late & Phase IV overshoot"
                is_val_adr_abnormal = True
            elif p2l_exists:
                adr_str = "Absence of Phase II_late"
                is_val_adr_abnormal = True
            elif p4_exists:
                adr_str = "Absence of Phase IV overshoot"
                is_val_adr_abnormal = True
            else:
                adr_str = "Normal"
            
            val_finding += f"- Adrenergic Response (Finapres): {adr_str}"

            try:
                vr = float(val_ratio)
                nvr = float(normal_val_ratio)
                if vr < nvr:
                    if vr <= nvr * 0.5 or is_cv_hrdb:
                        is_cv_val_severe = True
                        val_analysis_list.append(colorize("- cardiovagal dysfunction is suggested", "abnormal"))
                    else:
                        is_cv_val_mild = True
                        val_analysis_list.append(colorize("- mild cardiovagal dysfunction is suggested", "abnormal"))
                else:
                    val_analysis_list.append(colorize("- cardiovagal function is within normal limits", "normal"))
            except:
                val_analysis_list.append(colorize("- cardiovagal function analysis pending (OCR error)", "pending"))

            if adr_str == "Normal":
                val_analysis_list.append(colorize("- sympathetic adrenergic function is within normal limits", "normal"))
            else:
                val_analysis_list.append(colorize("- mild sympathetic adrenergic dysfunction", "abnormal"))
                
            val_analysis_text = "\n".join(val_analysis_list)

        # ==========================================
        # 5. Conclusion 논리 조립
        # ==========================================
        if not is_valsalva_analyzed and not is_val_arrhythmia:
            conclusion_text = "** Valsalva 그래프 분석이 필요합니다. 좌측의 분석 버튼을 눌러주세요. **"
        else:
            is_cardiovagal = is_cv_hrdb or is_cv_val_severe
            cv_str = "cardiovagal dysfunction"

            is_adrenergic = pots_found or oh_found or delayed_oh_found or is_val_adr_abnormal
            adr_str = ""
            if pots_found:
                adr_str = "sympathetic overactivity"
            elif oh_found and is_val_adr_abnormal:
                adr_str = "sympathetic adrenergic failure"
            elif oh_found or delayed_oh_found:
                adr_str = "sympathetic adrenergic dysfunction"
            elif is_val_adr_abnormal:
                adr_str = "mild sympathetic adrenergic dysfunction"

            abnormal_list = []
            if is_adrenergic: abnormal_list.append(adr_str)
            if is_cardiovagal: abnormal_list.append(cv_str)
            if is_sudo: abnormal_list.append("sudomotor dysfunction")

            normal_list = []
            is_cv_evaluable = not (is_hrdb_arrhythmia and is_val_arrhythmia)
            is_adr_evaluable = not is_val_arrhythmia

            if not is_cardiovagal and is_cv_evaluable: 
                normal_list.append("cardiovagal")
            if not is_adrenergic and is_adr_evaluable: 
                normal_list.append("sympathetic adrenergic")
            if not is_sudo: 
                normal_list.append("sudomotor")

            # [핵심 수정] 이상 소견이 0개일 때 무조건 선생님이 지정해주신 Full Text 고정 출력!
            if len(abnormal_list) == 0:
                conclusion_text = "Normal autonomic function for age. No evidence of significant cardiovagal, adrenergic, or sudomotor dysfunction. Clinical correlation is recommended."
            else:
                if len(abnormal_list) == 1:
                    sug_str = abnormal_list[0]
                elif len(abnormal_list) == 2:
                    sug_str = f"{abnormal_list[0]} and {abnormal_list[1]}"
                else:
                    sug_str = f"{abnormal_list[0]}, {abnormal_list[1]}, and {abnormal_list[2]}"
                
                conclusion_text = f"- Suggestive of {sug_str}.\n"

                if len(normal_list) > 0:
                    if len(normal_list) == 1:
                        no_str = normal_list[0]
                    elif len(normal_list) == 2:
                        no_str = f"{normal_list[0]} or {normal_list[1]}"
                    else:
                        no_str = f"{normal_list[0]}, {normal_list[1]}, or {normal_list[2]}"
                    conclusion_text += f"- No evidence of significant {no_str} dysfunction.\n"
                
                conclusion_text += "- Clinical correlation is recommended."

            conclusion_text += "\n\n**현재 가판독 상태이며 추후 정식 판독을 참조하기 바람."

        findings_text = f"1. Sympathetic skin response\n{ssr_finding}\n\n2. Heart rate response to deep breathing\n{hrdb_finding}\n\n3. Tilt table test\n{tilt_finding}\n\n4. Valsalva maneuver test\n{val_finding}"
        analysis_text = f"* Age: {age}\n\n1. Sympathetic skin response\n{ssr_analysis}\n\n2. Heart rate response to deep breathing\n{hrdb_analysis}\n\n3. Tilt table test\n{tilt_analysis_text}\n\n4. Valsalva maneuver test\n{val_analysis_text}"

        return findings_text, analysis_text, conclusion_text