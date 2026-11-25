# [ 261125 1530 랩탑 개발팀 ] (Dental_009#4 Winter's Classification 부호 오류 수정 및 임계값 정규화 계획서)

## 1. 대상 이슈 및 위치

- 대상 이슈: [Dental_009#4](https://github.com/HyunchanAn/Dental_009/issues/4) (`[P1][임상] Winter's Classification 좌우 사분면 부호 오류 및 해상도 의존 임계값 수정`)
- 상위 Umbrella: [Dental_000#18](https://github.com/HyunchanAn/Dental_000/issues/18) (`Dental_000/plans_replies_walkthrough/261125_1530_Dental_Series_Remediation_Umbrella_Plan.md` Track 2)
- 주의: `Dental_000#17`에서 동결 스코프에 포함되어 있으므로, 수정 착수 전 동결 예외 승인 여부 확인 권장.

---

## 2. 즉시 실행 가능 작업 (`[READY]`)

### 2.1 `src/analyzer.py:65` 좌우 사분면 부호 오류 수정
- 현상: Q1/Q4(파노라마 우측, 근심 방향 `+x`)와 Q2/Q3(파노라마 좌측, 근심 방향 `-x`)의 부호 분리가 누락되어 한쪽 사분면에서 `Mesioangular`와 `Distoangular`가 반대로 판정되는 명백한 기하학적 버그 존재.
- 작업 내용:
  - 사분면(`quadrant` 또는 FDI 번호)에 따라 근심 방향 벡터 부호를 명시적으로 분리.
  - Q1(`18`), Q2(`28`), Q3(`38`), Q4(`48`) 대칭 케이스에 대한 단위 테스트를 추가하여 좌우 반전 대칭성을 자동 검증.

### 2.2 `README.md` 버전 배지 정합화
- 상단 `Python-3.12+` 배지와 CI(`3.10`) 버전 표기 정합화.

---

## 3. `[FREEZE]` 보류 항목 (치과의사 임상 판단 및 오너 승인 필요)

| 항목 | 상태 | 동결 사유 및 역할 |
| :--- | :--- | :--- |
| `src/analyzer.py:100,102,113,115` 픽셀 임계값(`10` px, `adj_h > 20`)의 치아 높이 비율 기반 정규화 임계치 확정 | `[FREEZE / 임상 판단 필요]` | 해상도 독립성을 위한 비율식 구조 초안은 작성 가능하나, 실제 매복치 판정(Vertical / Mesioangular / Distoangular / Horizontal 및 매복 깊이 경계)에 적용할 임상 비율 임계값과 증례 판정 결과는 치과의사(안현찬)가 직접 검토·확정해야 함. |
| `Dental_000#17` 동결 스코프 예외 수정 허용 | `[FREEZE / 오너 승인 필요]` | `Dental_009`가 `#17` 동결 목록에 포함되어 있으므로, 버그픽스 브랜치/커밋 반영에 대한 오너 승인이 필요함. |

---

## 4. 검증 기준

- 좌우 사분면(`#18`, `#28`, `#38`, `#48`) 대칭 각도 입력 시 동일한 Winter's Classification 결과 반환 확인 (`pytest tests -v`).
- 비율 기반 임계값은 치과의사 승인 후 회귀 테스트에 고정.
