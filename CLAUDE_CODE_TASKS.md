# Claude Code 작업 계획 (AgileClaw Re-baseline)

## 작업 원칙

- 코어는 작게 유지하고 확장은 스킬/도구로 분리
- 문서와 구현을 항상 동기화
- 한 번에 큰 기능을 넣지 않고 루프 단위로 검증

## Phase 0 — 리베이스 (완료)

- [x] 문서 재정렬
  - `OVERVIEW.md`, `ARCHITECTURE.md`, `REQUIREMENTS.md` 동기화
  - `MIGRATION_PLAN.md`로 단계별 일정/리스크 명시

- [x] 코어 리팩터링
  - 도구 자동 로더
  - 스킬 카탈로그 로더
  - 액션 기반 크론(`chat/agile_review/run_skill`)

- [x] 운영 명령 보강
  - Telegram `/skills` 지원

## Phase 1 — KPI 자동화 (완료)

- [x] Threads/Reddit 도구 구현
- [x] goals 템플릿에 KPI 측정 명세 고정 (metric-agnostic로 일반화)
- [x] 일일 KPI 점검 스킬 작성

## Phase 2 — 리포트 자동화 (진행 중)

- [x] 일일/주간 KPI 리포트 프롬프트 모듈 추가 (`agile/report.py`)
- [x] 크론 잡 템플릿 제공 (`cron_jobs.example.json`)
- [x] 크론 액션 추가 (`daily_report`, `weekly_report`)
- [ ] 실운영 Telegram 왕복 테스트
- [ ] 실패 재시도/오류 알림 정책 고도화

## Phase 3 — 확장 검토

1. 다채널(필요 시)
2. 샌드박스 실행 격리(필요 시)
3. 웹 UI (필요 시)

## 체크리스트

- [x] 단위 테스트 통과 (`python3 -m unittest discover -s tests -v`)
- [x] `compileall` 통과
- [ ] `python main.py` 실운영 실행
- [ ] 목표 요청 메시지 자동 Agile Team 셋업 확인
- [ ] `/agile` Telegram 실응답 확인
- [ ] `/skills` Telegram 실응답 확인
- [ ] `/report daily` Telegram 실응답 확인
- [ ] 크론 `chat/agile_review/daily_report/weekly_report/run_skill` 실운영 실행
