# AgileClaw — 요구사항 (Re-baseline)

## 1. 목표

AgileClaw는 요청 목표마다 Agile Team을 생성하고 KPI 기반 자율 루프를 안정적으로 실행해야 한다.

## 2. 기능 요구사항

### F0. 코어 (필수)

1. 대화 채널
- Telegram 또는 CLI로 메시지 송수신 가능

2. 에이전트 실행
- Claude API 호출
- tool_use 루프 처리

3. 도구 실행
- 기본 도구: `shell`, `read_file`, `write_file`, `web_fetch`, browser 계열
- 도구 플러그인 자동 로딩 지원

4. 메모리
- 대화 히스토리 저장/조회
- 전역 컨텍스트(`CONTEXT.md`) 로드
- goals 로드 및 로그 기록

5. 스케줄러
- cron/every 스케줄 지원
- `chat`, `agile_review`, `daily_report`, `weekly_report`, `run_skill` 액션 라우팅

6. 에자일 루프
- goals 기반 리뷰 프롬프트 생성
- KPI 측정/격차/다음 액션 제안

7. Goal Team 관리
- 목표 요청이 들어오면 팀 차터를 생성 (`memory/teams/team-*.md`)
- 팀별 KPI 측정 방법을 먼저 정의하고 실행

8. 스킬 카탈로그
- `skills/*/SKILL.md` 자동 탐색
- 채팅 시스템 프롬프트에 스킬 인덱스 주입

### F1. 확장 (우선순위 높음)

1. KPI 도구 계층
- 범용 KPI 도구 (`kpi_upsert_metric`, `kpi_log_measurement`, `kpi_list_metrics`)
- 플랫폼 선택 도구 (Threads/Reddit 등)

2. 자동 리포트
- 일일/주간 리포트 템플릿
- 지정 채널로 송신

## 3. 비기능 요구사항

1. 단순성
- 핵심 코드 1,500줄 내 유지

2. 신뢰성
- 도구 실패가 전체 프로세스를 중단시키지 않아야 함
- API 오류 재시도(백오프) 필요

3. 운영성
- 설정 파일 단순화 (`config.yaml`)
- 파일 기반 상태로 디버깅 가능해야 함

4. 확장성
- 도구 추가가 단일 파일 단위여야 함
- 스킬 추가가 `SKILL.md` 추가만으로 가능해야 함

## 4. 수용 기준

1. 최소 수용 기준
- `/agile` 실행 성공
- 크론에서 `agile_review` 자동 실행 성공
- `skills` 목록 조회 가능
- 도구 자동 로딩 정상 동작

2. 확장 수용 기준
- 새 도구 파일 추가 후 코드 수정 없이 로딩됨
- 새 스킬 폴더 추가 후 `/skills` 목록에 반영됨
