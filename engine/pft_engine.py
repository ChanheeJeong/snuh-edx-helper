from models.pft_data import PFTDataInput, PFTAnalysisResult, NORMAL_RANGES

class PFTEngine:
    @staticmethod
    def calculate_normal_ranges(patient) -> dict:
        if not all([patient.age, patient.sex, patient.height]): return {}
        
        age, sex, height_cm = patient.age, patient.sex, patient.height
        if 20 <= age <= 39: age_group = "20-39"
        elif 40 <= age <= 59: age_group = "40-59"
        else: age_group = ">=60"

        ranges = {}
        for test in ["MIP", "MEP", "SNIP"]:
            mean, std_dev = NORMAL_RANGES[test][sex][age_group]
            ranges[test] = f"{round(mean - std_dev, 1)} - {round(mean + std_dev, 1)}"
        
        height_m = height_cm / 100.0
        pef = (((height_m * (5.48 if sex == "Male" else 3.72)) + (1.58 if sex == "Male" else 2.24)) - (age * (0.041 if sex == "Male" else 0.03))) * 60
        ranges["PEF"] = str(round(pef, 1))
        
        return ranges

    @staticmethod
    def analyze(data: PFTDataInput) -> PFTAnalysisResult:
        res = PFTAnalysisResult(normal_ranges={}, test_status={}, conclusion_text="")
        
        # [핵심 수정 1] 환자 정보만 있어도 정상 범위(Normal Range)는 우선적으로 계산하여 반환
        if data.patient.age is not None and data.patient.sex is not None and data.patient.height is not None:
            res.normal_ranges = PFTEngine.calculate_normal_ranges(data.patient)
            
        # [핵심 수정 2] 시행 데이터가 다 채워지지 않았다면 결론(Conclusion) 생성은 보류
        if any(v is None for v in [data.patient.age, data.patient.sex, data.patient.height]) or \
           any(None in row for row in data.trials):
            return res
        
        abnormal_tests, normal_tests = [], []
        test_keys = ["MIP", "MEP", "SNIP", "PEF"]
        
        for i, key in enumerate(test_keys):
            max_val = max(data.trials[row][i] for row in range(3))
            range_val = res.normal_ranges[key]
            lower_bound = float(range_val.split(' - ')[0]) if ' - ' in range_val else float(range_val)
            
            if max_val < lower_bound:
                abnormal_tests.append(key); res.test_status[key] = "Abnormal"
            else:
                normal_tests.append(key); res.test_status[key] = "Normal"

        conclusion_parts = []
        if not abnormal_tests:
            conclusion_parts.append("1. All tests are within normal limits.")
        else:
            abnormal_str = ", ".join(abnormal_tests)
            normal_str = ", ".join(normal_tests)
            line1 = f"1. There are abnormal findings in {abnormal_str} tests"
            if normal_tests: line1 += f", but normal findings in {normal_str} tests."
            else: line1 += "."
            conclusion_parts.append(line1)
        
        fvc, fev1 = data.fvc, data.fev1
        if fvc is not None and fev1 is not None:
            if fvc < 75 or fev1 < 75:
                conclusion_parts.append(f"2. Possible restriction suggested by spirometry (FVC %pred: {fvc}%, FEV1 %pred: {fev1}%)")
            else:
                conclusion_parts.append(f"2. Normal spirometry (FVC %pred: {fvc}%, FEV1 %pred: {fev1}%)")

        conclusion_parts.append("3. Clinical correlation is recommended.")
        res.conclusion_text = "\n".join(conclusion_parts)
        
        return res