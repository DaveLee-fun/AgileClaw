# AgileClaw — 아키텍처 (NanoCore 스타일)

## 1. 설계 원칙

1. 코어 최소화: 실행에 필수인 컴포넌트만 유지
2. 확장 외부화: 새 기능은 스킬/도구 플러그인으로 분리
3. 운영 단순성: 단일 프로세스 + 파일 기반 상태
4. KPI 중심: 목표 요청마다 Agile Team 단위로 운영

## 2. 시스템 구성

```
Telegram/CLI
    ↓
channels/telegram.py
    ↓
core/agent.py
    ├── core/claude.py         # Claude tool_use 루프
    ├── core/memory.py         # 파일 기반 메모리/로그/teams
    ├── core/skills.py         # skills/* 카탈로그
    └── tools/__init__.py      # tools/*.py 자동 로딩
             ↓
      tools/*.py (shell/files/web/browser/kpi/+custom)

scheduler/cron.py              # action 기반 잡 실행
agile/loop.py                  # 목표 리뷰 프롬프트
agile/report.py                # 일일/주간 KPI 리포트 프롬프트
```

## 3. 데이터 경로

### 3.1 채팅 경로

1. Telegram 메시지 수신
2. `Agent.chat()` 호출
3. 에이전트가 메모리 + 스킬 카탈로그를 시스템 프롬프트에 반영
4. 목표 요청이면 Agile Team 차터 자동 생성
5. Claude가 필요 시 tool_use 호출
6. 도구 실행 결과를 Claude에 반환
7. 최종 답변 저장 후 사용자에게 송신

### 3.2 스케줄 경로

1. `cron_jobs.json`에서 잡 로딩
2. 스케줄 시점 도달 시 잡 객체 전달
3. `action` 값에 따라 라우팅
- `chat`: 일반 메시지 실행
- `agile_review`: KPI 리뷰 실행
- `daily_report`: 일일 KPI 리포트
- `weekly_report`: 주간 KPI 리포트
- `run_skill`: 특정 스킬 기반 실행
4. 결과는 로그 저장

## 4. 확장 포인트

## 4.1 도구 플러그인

경로: `tools/*.py`

필수 규약:
- 모듈은 `get_tool_specs()`를 제공
- 반환값은 아래 형식의 리스트

```python
[
  {
    "definition": { ...Claude tool schema... },
    "handler": callable,  # (tool_input: dict, context: dict) -> str
  }
]
```

이 규약만 지키면 `tools/__init__.py`가 자동 로드한다.

## 4.2 스킬

경로: `skills/<skill_name>/SKILL.md`

목적:
- 반복 업무 프로토콜을 문서로 캡슐화
- 에이전트가 스킬 설명을 보고 적절한 도구를 조합해 실행

## 5. 상태 저장

```
memory/
├── CONTEXT.md
├── goals.md
├── teams/team-*.md
├── history-<chat_id>.json
└── log-YYYY-MM-DD.md

cron_jobs.json
skills/
```

## 6. 비목표 (명시)

현재 리베이스 단계에서 아래는 코어 비포함:
- 멀티 플랫폼 게이트웨이
- 분산 멀티에이전트 런타임
- 복잡한 UI/대시보드
- 무거운 권한/페어링 계층

필요 시 스킬/도구로 단계적으로 추가한다.
