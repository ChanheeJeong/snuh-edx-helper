# ⚡ SNUH EDX Helper

![Python](https://img.shields.io/badge/Python-3.10+-blue.svg?logo=python&logoColor=white)
![PyQt6](https://img.shields.io/badge/PyQt6-GUI-brightgreen.svg?logo=qt&logoColor=white)
![OpenCV](https://img.shields.io/badge/OpenCV-Vision-red.svg?logo=opencv&logoColor=white)
![Tesseract](https://img.shields.io/badge/Tesseract-OCR-orange.svg)
![License](https://img.shields.io/badge/License-MIT-lightgrey.svg)

> **서울대학교병원 신경과 전공의를 위한 근전도(EMG/NCS) 및 자율신경검사(ANSFT) 스마트 판독 보조 & EMR 자동화 솔루션**

**SNUH EDX Helper**는 외래 및 병동에서 반복적으로 발생하는 검사 결과 입력과 판독문 작성 시간을 획기적으로 단축하기 위해 개발된 윈도우용 데스크톱 애플리케이션입니다. 직관적인 UI, 화면 캡처 기반의 OCR 기술, 그리고 강력한 키보드 매크로를 결합하여 의료진의 업무 피로도를 낮추고 판독의 정확성을 높입니다.

---

## ✨ 핵심 기능 (Key Features)

### 🗂️ 1. 통합 검사 모듈 (All-in-one Dashboard)
- **NCS, EMG, EP, ANS, PFT** 등 다양한 신경계 검사 모듈을 탭(Tab) 형식으로 통합 제공.
- **Splash Screen**: 실행 시 판독자(Resident) 이름을 선택/기록하여 모든 판독문 서명에 자동 반영.

### 📝 2. 질환별 스마트 판독문 생성 (NCS Simple)
- 직관적인 **2x2 사지(Limb) 토글 UI** 제공.
- 정상(Normal), 다발신경병증(SMPN), 수근관증후군(CTS), 족저신경병증(Plantar) 등 선택된 패턴과 검사 부위에 맞춰 영문 판독문 자동 조합 및 생성.

### 🤖 3. EMR 표 자동 채우기 매크로 (EMG Automation)
- 상지(U/E) 및 하지(L/E) 근육별 Spontaneous Activity 테이블 자동 완성.
- 검사한 근육을 체크하고 단축키를 누르면, EMR 양식에 맞춰 `Root`, `Nerve`, `N(정상)` 값들을 자동으로 타이핑하며 Tab 키로 칸을 이동.

### 👁️ 4. 화면 캡처 & OCR 자동 계산 (PFT & ANS)
- **반투명 오버레이 캡처**: 모니터 화면의 검사 결과표를 마우스로 드래그하여 즉시 캡처.
- **Tesseract OCR 연동**: 캡처된 이미지에서 환자 나이/성별/신장, MIP/MEP 수치 등을 추출.
- **정상 범위(Normal Range) 자동 계산**: 추출된 환자 정보를 바탕으로 폐기능검사 및 자율신경검사의 정상 범위를 자동으로 계산하고 비정상 소견(Abnormal) 판별.

---

## ⌨️ 단축키 가이드 (Hotkeys)

프로그램이 백그라운드에 켜져 있는 상태에서 EMR 입력란에 커서를 두고 아래 단축키를 누르면 즉시 작동합니다.

| 단축키 | 기능 설명 | 적용 모듈 |
| :--- | :--- | :--- |
| `Ctrl + Shift + Q` | **종합 판독문 입력**: 완성된 판독 결론과 가판독 안내 문구, 서명을 EMR에 한 번에 붙여넣기 | NCS, PFT, ANSFT 등 |
| `Ctrl + Shift + U` | **상지(U/E) 근전도 입력**: 선택된 상지 근육들의 EMG 소견을 표에 자동 타이핑 | EMG |
| `Ctrl + Shift + L` | **하지(L/E) 근전도 입력**: 선택된 하지 근육들의 EMG 소견을 표에 자동 타이핑 | EMG |
| `Ctrl + Q` | **서명(Signature) 입력**: 현재 설정된 판독자/교수님 서명을 즉시 붙여넣기 | 전역(Global) |

---

## 📂 프로젝트 구조 (Architecture)

확장성과 유지보수를 고려하여 `MVC (Model-View-Controller)` 패턴을 차용해 구조화되었습니다.
```text
snuh-edx-helper/
│
├── main.py                     # 메인 애플리케이션 진입점 및 탭 라우팅
├── user_config.json            # 사용자(판독자) 히스토리 저장 파일
│
├── models/                     # 데이터 구조 (Data Classes) 및 상수
│   ├── ansft_data.py
│   ├── emg_data.py
│   ├── ncs_simple_data.py
│   └── pft_data.py
│
├── engine/                     # 의학적 논리, 수치 계산, 판독문 생성 로직
│   ├── ansft_engine.py
│   ├── ncs_simple_engine.py
│   └── pft_engine.py
│
├── modules/                    # UI 레이아웃 및 이벤트 컨트롤러
│   ├── splash_screen.py        # 시작 화면 (사용자 선택)
│   ├── emg_ui.py / emg_controller.py
│   ├── ncs_simple_ui.py / ncs_simple_controller.py
│   ├── pft_ui.py / pft_controller.py / pft_vision.py
│   └── ansft_ui.py / ansft_controller.py
│
└── tools/                      # 공통 유틸리티 툴
    ├── signature_tool.py       # 서명 관리 및 단축키 모듈
    ├── preliminary_tool.py     # 가판독 안내 문구 모듈
    └── path_clear_tool.py      # 이미지 모니터링 폴더 비우기 툴