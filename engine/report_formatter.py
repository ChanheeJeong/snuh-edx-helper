from models.ansft_data import ANSFTInput, ANSFTResult

class ReportFormatter:
    @staticmethod
    def format_report(inp: ANSFTInput, res: ANSFTResult):
        def colorize(text, status):
            if status == 'normal': return f"<span style='color: #27ae60; font-weight: bold;'>{text}</span>"
            elif status == 'abnormal': return f"<span style='color: #e74c3c; font-weight: bold;'>{text}</span>"
            elif status == 'pending': return f"<span style='color: #d35400; font-weight: bold;'>{text}</span>"
            return text

        # 1. Findings 텍스트
        f_text = f"1. Sympathetic skin response\n{res.ssr_finding}\n\n"
        f_text += f"2. Heart rate response to deep breathing\n{res.hrdb_finding}\n\n"
        f_text += f"3. Tilt table test\n{res.tilt_finding}\n\n"
        f_text += f"4. Valsalva maneuver test\n{res.val_finding}"

        # 2. Analysis 텍스트 (HTML 색상 적용)
        a_text = f"* Age: {inp.patient.age}\n\n"
        a_text += f"1. Sympathetic skin response\n{colorize(res.ssr_analysis_plain, res.ssr_status)}\n\n"
        a_text += f"2. Heart rate response to deep breathing\n{colorize(res.hrdb_analysis_plain, res.hrdb_status)}\n\n"
        
        tilt_analysis_html = "\n".join([colorize(txt, st) for txt, st in zip(res.tilt_analysis_plains, res.tilt_statuses)])
        a_text += f"3. Tilt table test\n{tilt_analysis_html}\n\n"
        
        val_analysis_html = "\n".join([colorize(txt, st) for txt, st in zip(res.val_analysis_plains, res.val_statuses)])
        a_text += f"4. Valsalva maneuver test\n{val_analysis_html}"

        # 3. Conclusion 로직 조립
        if not inp.valsalva.is_analyzed and not inp.valsalva.is_arrhythmia:
            c_text = "** Valsalva 그래프 분석이 필요합니다. 좌측의 분석 버튼을 눌러주세요. **"
        else:
            is_cardiovagal = res.is_cv_hrdb or res.is_cv_val_severe
            cv_str = "cardiovagal dysfunction"

            is_adrenergic = res.pots_found or res.oh_found or res.delayed_oh_found or res.is_val_adr_abnormal
            adr_str = ""
            if res.pots_found:
                adr_str = "sympathetic overactivity"
            elif res.oh_found and res.is_val_adr_abnormal:
                adr_str = "sympathetic adrenergic failure"
            elif res.oh_found or res.delayed_oh_found:
                adr_str = "sympathetic adrenergic dysfunction"
            elif res.is_val_adr_abnormal:
                adr_str = "mild sympathetic adrenergic dysfunction"

            abnormal_list = []
            if is_adrenergic: abnormal_list.append(adr_str)
            if is_cardiovagal: abnormal_list.append(cv_str)
            if res.is_sudo: abnormal_list.append("sudomotor dysfunction")

            normal_list = []
            is_cv_evaluable = not (inp.hrdb.is_arrhythmia and inp.valsalva.is_arrhythmia)
            is_adr_evaluable = not inp.valsalva.is_arrhythmia

            if not is_cardiovagal and is_cv_evaluable: 
                normal_list.append("cardiovagal")
            if not is_adrenergic and is_adr_evaluable: 
                normal_list.append("sympathetic adrenergic")
            if not res.is_sudo: 
                normal_list.append("sudomotor")

            if len(abnormal_list) == 0:
                c_text = "Normal autonomic function for age. No evidence of significant cardiovagal, adrenergic, or sudomotor dysfunction. Clinical correlation is recommended."
            else:
                if len(abnormal_list) == 1:
                    sug_str = abnormal_list[0]
                elif len(abnormal_list) == 2:
                    sug_str = f"{abnormal_list[0]} and {abnormal_list[1]}"
                else:
                    sug_str = f"{abnormal_list[0]}, {abnormal_list[1]}, and {abnormal_list[2]}"
                
                c_text = f"- Suggestive of {sug_str}.\n"

                if len(normal_list) > 0:
                    if len(normal_list) == 1:
                        no_str = normal_list[0]
                    elif len(normal_list) == 2:
                        no_str = f"{normal_list[0]} or {normal_list[1]}"
                    else:
                        no_str = f"{normal_list[0]}, {normal_list[1]}, or {normal_list[2]}"
                    c_text += f"- No evidence of significant {no_str} dysfunction.\n"
                
                c_text += "- Clinical correlation is recommended."

            c_text += "\n\n**현재 가판독 상태이며 추후 정식 판독을 참조하기 바람."

        return f_text, a_text, c_text