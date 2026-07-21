![Status](https://img.shields.io/badge/Status-v1.0%20Release-brightgreen) ![Python](https://img.shields.io/badge/Python-3.12%2B-blue) ![Backend](https://img.shields.io/badge/Backend-YOLOv8-red) ![UI](https://img.shields.io/badge/UI-Streamlit-orange) ![CI/CD Pipeline](https://img.shields.io/badge/CI%2FCD%20Pipeline-passing-brightgreen?logo=github)

# Dental_009 (Impacted Tooth Detailed Analysis)

이 모듈은 파노라마 X-ray에서 식별된 매복치(Impacted Tooth, 주로 제3대구치)의 발치 난이도 및 기하학적 형태를 상세 분석하는 후처리 모듈입니다.

## 기능 (Features)
- **Winter's Classification 판별**: 인접 제2대구치의 장축(Long axis)을 기준으로 매복치의 경사도를 수치화하여 4가지 클래스(Mesioangular, Distoangular, Vertical, Horizontal) 중 하나로 판별합니다.
- **맹출 상태(Eruption Status) 평가**: 제2대구치의 교합면 및 치경부 높이를 기준으로 매복치의 최고점 높이를 비교하여 완전맹출, 부분맹출, 완전매복으로 분류합니다.

## 입력 데이터 구조
- 본 모듈은 원본 이미지가 아닌, 선행 AI 모델들의 결과값을 기하학적으로 처리하는 룰 기반 모듈입니다.
- **필수 입력값**:
  - 매복치의 픽셀 폴리곤 마스크 좌표 (008 모듈 등에서 획득)
  - 인접치(제2대구치)의 픽셀 폴리곤 마스크 좌표 (008 모듈 등에서 획득)
  
## Limitations
- 치아의 장축은 PCA(주성분 분석)를 통해 추정하므로, 치근이 심하게 휘어있거나(Dilaceration) 폴리곤의 형태가 비정상적인 경우 각도 오차가 발생할 수 있습니다.
- 하악관(Mandibular canal)과의 겹침이나 3차원적인 뿌리 갯수는 파노라마 2D 한계상 정확하게 측정할 수 없습니다.

## 학습 환경 (Training Environment)
> **[학습 환경 사양]** 실질적 모델 학습은 **RTX 5080 + 라이젠9-6 9900x** 환경에서 진행되었습니다.

## 개요
이 레포지토리는 치과 AI 모듈러 시스템의 일부입니다.

## 설치 및 실행 방법
```bash
pip install -r requirements.txt
```


## 가중치 파일 안내
본 모듈은 가중치 모델이 불필요한 룰베이스/인프라/기하학 모듈이므로, 별도의 딥러닝 가중치 파일이 요구되지 않습니다.
