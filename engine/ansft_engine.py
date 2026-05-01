from models.ansft_data import ANSFTInput, ANSFTResult

class ANSFTEngine:
    @staticmethod
    def analyze(data: ANSFTInput) -> ANSFTResult:
        res = ANSFTResult()
        
        # 1. SSR 논리
        p_norm, s_norm = data.ssr.palm_normal, data.ssr.sole_normal
        if p_norm and s_norm:
            res.ssr_finding = "- Normal SSRs in both palms and soles"
            res.ssr_analysis_plain = "- sudomotor function is within normal limits"
            res.ssr_status = "normal"
        elif not p_norm and not s_norm:
            res.ssr_finding = "- Absent SSRs in both palms and soles"
            res.ssr_analysis_plain = "- sudomotor dysfunction is suggested"
            res.ssr_status = "abnormal"
            res.is_sudo = True
        elif p_norm and not s_norm:
            res.ssr_finding = "- Normal SSRs in both palms but absent in both soles"
            if data.patient.age >= 65:
                res.ssr_analysis_plain = "- sudomotor function is within normal limits"
                res.ssr_status = "normal"
            else:
                res.ssr_analysis_plain = "- sudomotor dysfunction is suggested"
                res.ssr_status = "abnormal"
                res.is_sudo = True
        else:
            res.ssr_finding = "- Abnormal SSRs in palms but normal in soles"
            res.ssr_analysis_plain = "- sudomotor dysfunction is suggested"
            res.ssr_status = "abnormal"
            res.is_sudo = True

        # 2. HRDB 논리
        if data.hrdb.is_arrhythmia:
            res.hrdb_finding = "- Not interpretable due to arrhythmia"
            res.hrdb_analysis_plain = "- Analysis skipped due to arrhythmia"
            res.hrdb_status = "pending"
        else:
            res.hrdb_finding = f"- E/I ratio: {data.hrdb.val1} (Normal average E/I ratio: >{data.hrdb.val2})"
            try:
                if float(data.hrdb.val1) >= float(data.hrdb.val2):
                    res.hrdb_analysis_plain = "- cardiovagal function is within normal limits"
                    res.hrdb_status = "normal"
                else:
                    res.hrdb_analysis_plain = "- cardiovagal dysfunction is suggested"
                    res.hrdb_status = "abnormal"
                    res.is_cv_hrdb = True
            except:
                res.hrdb_analysis_plain = "- cardiovagal function analysis pending (OCR error)"
                res.hrdb_status = "pending"

        # 3. Tilt Table 논리
        res.tilt_finding = "- No significant change of BP and HR on orthostatic challenge"
        records = data.tilt.records
        if len(records) == 5:
            oh_text, hr_comp_text, pots_text = "", "", ""
            baseline_sbp, baseline_dbp, baseline_hr = records[0]

            for i in range(1, 5):
                t_min = {1:1, 2:3, 3:5, 4:10}[i]
                t_str = f"within {3 if t_min <=3 else t_min} minutes"

                sbp, dbp, hr = records[i]
                if sbp == 0 or dbp == 0 or hr == 0: continue
                if baseline_sbp == 0 or baseline_dbp == 0 or baseline_hr == 0: continue

                drop_sbp = baseline_sbp - sbp
                drop_dbp = baseline_dbp - dbp
                d_hr = hr - baseline_hr

                is_sbp_drop = drop_sbp >= 20
                is_dbp_drop = drop_dbp >= 10

                if (is_sbp_drop or is_dbp_drop) and not res.oh_found and not res.delayed_oh_found:
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
                        res.oh_found = True
                        hr_comp_text = ", without HR compensation."
                    else:
                        if t_min <= 3:
                            prefix = "Classic OH"
                            res.oh_found = True
                        else:
                            prefix = "Delayed OH"
                            res.delayed_oh_found = True
                        hr_comp_text = ", with HR compensation."

                    oh_text = f"- {prefix}: {cause} {t_str}"
                    break 

            if not res.oh_found and not res.delayed_oh_found:
                max_d_hr = max([records[i][2] - baseline_hr for i in range(1, 5) if records[i][2] != 0]) if any(records[i][2] != 0 for i in range(1,5)) else 0
                cutoff = 40 if 12 <= data.patient.age <= 19 else 30
                if max_d_hr >= cutoff:
                    res.pots_found = True
                    pots_text = f"- POTS: Heart rate increased by more than {cutoff} bpm"
                    if cutoff == 40: pots_text += " (ages 12-19)"
                    pots_text += " within 10 minutes of head-up tilt, in the absence of OH."

            if res.oh_found or res.delayed_oh_found: res.tilt_finding = oh_text + hr_comp_text
            elif res.pots_found: res.tilt_finding = pots_text

            if res.pots_found:
                res.tilt_analysis_plains.append("- sympathetic overactivity")
                res.tilt_statuses.append("abnormal")
            if res.oh_found or res.delayed_oh_found:
                res.tilt_analysis_plains.append("- sympathetic adrenergic dysfunction")
                res.tilt_statuses.append("abnormal")
                
            if not res.oh_found and not res.delayed_oh_found and not res.pots_found:
                res.tilt_analysis_plains.append("- sympathetic adrenergic and cardiovagal functions are within normal limits")
                res.tilt_statuses.append("normal")
        else:
            res.tilt_analysis_plains.append("- Analysis pending")
            res.tilt_statuses.append("pending")

        # 4. Valsalva 논리
        v_data = data.valsalva
        if v_data.is_arrhythmia:
            res.val_finding = "- Not interpretable due to arrhythmia"
            res.val_analysis_plains.append("- Analysis skipped due to arrhythmia")
            res.val_statuses.append("pending")
        elif not v_data.is_analyzed:
            res.val_finding = "- Analysis pending (그래프 분석 대기 중)"
            res.val_analysis_plains.append("- Analysis pending")
            res.val_statuses.append("pending")
        elif v_data.is_poor:
            res.val_finding = "- Poor valsalva maneuver"
            res.val_analysis_plains.append("- Analysis pending due to poor maneuver")
            res.val_statuses.append("pending")
        else:
            res.val_finding = f"- Valsalva ratio: {v_data.val_ratio} (Normal Valsalva phase and ratio: {v_data.normal_val_ratio})\n"
            res.val_finding += f"- Pressure recovery time: {v_data.prt_sec} sec (PRT normal range <5.00 sec)\n"

            if v_data.p2l_exists and v_data.p4_exists:
                adr_str = "Absence of Phase II_late & Phase IV overshoot"
                res.is_val_adr_abnormal = True
            elif v_data.p2l_exists:
                adr_str = "Absence of Phase II_late"
                res.is_val_adr_abnormal = True
            elif v_data.p4_exists:
                adr_str = "Absence of Phase IV overshoot"
                res.is_val_adr_abnormal = True
            else:
                adr_str = "Normal"
            
            res.val_finding += f"- Adrenergic Response (Finapres): {adr_str}"

            try:
                vr = float(v_data.val_ratio)
                nvr = float(v_data.normal_val_ratio)
                if vr < nvr:
                    if vr <= nvr * 0.5 or res.is_cv_hrdb:
                        res.is_cv_val_severe = True
                        res.val_analysis_plains.append("- cardiovagal dysfunction is suggested")
                        res.val_statuses.append("abnormal")
                    else:
                        res.is_cv_val_mild = True
                        res.val_analysis_plains.append("- mild cardiovagal dysfunction is suggested")
                        res.val_statuses.append("abnormal")
                else:
                    res.val_analysis_plains.append("- cardiovagal function is within normal limits")
                    res.val_statuses.append("normal")
            except:
                res.val_analysis_plains.append("- cardiovagal function analysis pending (OCR error)")
                res.val_statuses.append("pending")

            if adr_str == "Normal":
                res.val_analysis_plains.append("- sympathetic adrenergic function is within normal limits")
                res.val_statuses.append("normal")
            else:
                res.val_analysis_plains.append("- mild sympathetic adrenergic dysfunction")
                res.val_statuses.append("abnormal")

        return res