![Status](https://img.shields.io/badge/Status-Rule--Based%20Heuristic-yellowgreen "Status") ![Python](https://img.shields.io/badge/Python-3.12%2B-blue "Python") ![Backend](https://img.shields.io/badge/Backend-OpenCV%20PCA%20Geometry-blue "Backend") ![License](https://img.shields.io/badge/License-MIT-green "License") ![CI/CD Pipeline](https://img.shields.io/badge/CI%2FCD%20Pipeline-passing-brightgreen?logo=github "CI/CD Pipeline")

# Dental_009: Impacted Tooth Detailed Analysis (매복 제3대구치 기하학적 난이도 분석)

## 개요

`Dental_009`는 파노라마 방사선 영상에서 선행 치아 분할 모듈(`Dental_008`)이 식별한 제3대구치(사랑니, FDI `#18, #28, #38, #48`)와 인접 제2대구치(`#17, #27, #37, #47`)의 폴리곤 마스크 좌표를 입력받아, 기하학적 장축 각도(Winter's Classification) 및 맹출 깊이(Pell & Gregory Level A/B/C 프록시)를 규칙 기반으로 산출하는 후처리 모듈입니다.

---

## 주요 기능 및 아키텍처

### 1. 알고리즘 명세 (Algorithm Specification)
1. [PCA 주성분 장축 추정 (`get_long_axis_vector`)]:
   - OpenCV `cv2.PCACompute`를 사용하여 제3대구치 및 인접 제2대구치 컨투어의 제1주성분(Long Axis) 단위 벡터를 추출합니다.
2. [Winter's Classification 각도 분류 (`evaluate_winters_classification`)]:
   - 제2대구치 장축 벡터 대비 제3대구치 장축 벡터의 사잇각($\theta$)을 계산하여 분류합니다 (참고 문헌: Winter, 1926; Quek et al., Int J Oral Maxillofac Surg 2003):
     - `Vertical`: $|\theta| \le 10^\circ$
     - `Mesioangular` / `Distoangular`: $10^\circ < |\theta| \le 75^\circ$ (악궁 사분면 Q1~Q4 방향에 따른 부호 판별)
     - `Horizontal`: $75^\circ < |\theta| \le 105^\circ$
     - `Distoangular/Inverted`: $|\theta| > 105^\circ$
3. [맹출 상태 및 Pell & Gregory 깊이 분류 (`evaluate_eruption_status`, `evaluate_pell_gregory_level`)]:
   - 인접 제2대구치의 교합면(Occlusal plane)과 치경부 중간선(Cervical midpoint)을 기준으로 제3대구치 최고점의 수직 위치를 비교하여 `Fully Erupted` (`Level A`), `Partially Erupted` (`Level B`), `Fully Impacted` (`Level C`)로 분류합니다.
   - [탐색적 엔지니어링 휴리스틱 고지 (`88%` Height-Ratio Heuristic)]: `target_h < adj_h * 0.88` 조건은 2D 파노라마 투영에서 협설측 경사나 부분 맹출로 인해 치관-치근 수직 바운딩 박스 길이가 짧아지는 현상을 보완하기 위한 탐색적 엔지니어링 휴리스틱(Exploratory Engineering Heuristic)이며, 단독 임상 확진 기준이 아닙니다.

### 2. 입력 데이터 구조 및 가중치 안내
- 필수 입력값: 제3대구치(`#18, #28, #38, #48`) 및 인접 제2대구치(`#17, #27, #37, #47`) 픽셀 폴리곤 마스크 좌표.
- [가중치 파일 안내]: 본 모듈은 별도의 딥러닝 가중치 파일이 불필요한 규칙 기반 기하학 모듈입니다.

---

## 벤치마크 및 검증 성능

- [10-Case 정량 벤치마크 (`10_cases_quantitative_benchmark.json`)]:
  - 복합 파노라마 골드 어노테이션(`panoramic-x-ray-thegem-blog-default.jpg`) 내 4개 사랑니 매복(`#18, #28, #38, #48`) 구간 평가 결과 (`IoU >= 0.25` 매칭 기준):
    - `#18`: `IoU = 0.288`, FDI 일치 (`TP`)
    - `#28`: `IoU = 0.583`, FDI 일치 (`TP`)
    - `#38`: `IoU = 0.577`, FDI 일치 (`TP`)
    - `#48`: `IoU = 0.624`, FDI 일치 (`TP`)
  - 매복 제3대구치 4/4건 검출 (`Recall = 100.0%`, `Precision = 100.0%`, `FDI_Match = 100.0%`).
- [단위 테스트 (`tests/test_analyzer.py`)]:
  - 사분면별 Winter 각도 분류(`Vertical`, `Mesioangular`, `Distoangular`, `Horizontal`, `Distoangular/Inverted`), Pell & Gregory 깊이(`Level A/B/C`), 88% 높이비 휴리스틱, TheGem 4개 사랑니 골드 케이스 정합성을 검증합니다.
- [한계점 (Limitations)]:
  - 치아의 장축을 2D 컨투어의 PCA(주성분 분석)로 추정하므로, 치근 만곡(Dilaceration)이 심하거나 치관-치근 비례가 정방형에 가까운 경우 주축 각도 오차가 발생할 수 있습니다.
  - 하악관(Mandibular canal)과의 3차원적 접촉 여부 및 치근 개수는 2D 파노라마 한계상 CBCT 없이 확정할 수 없습니다.

---

## 데이터셋 출처 및 라이선스

- 본 모듈은 선행 `Dental_008` 분할 마스크 기하 좌표를 입력으로 사용하며 별도의 원본 환자 데이터셋을 재배포하지 않습니다.
- [소스 코드 라이선스]: 본 프로젝트의 소스 코드는 `MIT License` ([LICENSE](LICENSE), `Copyright (c) 2026 Hyunchan An`) 하에 배포됩니다.

---

## 설치 및 실행 방법

```bash
pip install -r requirements.txt
pytest tests/test_analyzer.py -v
python scripts/run_visualization_demo.py
```

---

## 참고 문헌 및 연구용 실행 주의사항

- Winter, G. B. (1926). Principles of Exodontia as Applied to the Impacted Mandibular Third Molar. American Medical Book Company.
- Pell, G. J., & Gregory, B. T. (1933). Impacted mandibular third molars: classification and modified techniques for removal. Dental Digest, 39, 330-338.
- Quek, S. L. et al. (2003). Pattern of third molar impaction in a Singapore Chinese population: a retrospective radiographic survey. International Journal of Oral and Maxillofacial Surgery, 32(5), 548-552.
- [연구용 실행 주의사항]:
  - 기본 실행 주소: `127.0.0.1` (로컬 전용)
  - 외부 공개/상용 배포 금지 및 오픈 데이터셋 외 민감 의료데이터 사용 금지
  - API 키·토큰은 환경변수로만 관리하며, 외부 접근이 필요하면 `ALLOW_EXTERNAL_ACCESS=true`로만 명시적 허용
