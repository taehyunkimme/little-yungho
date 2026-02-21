---
name: phase0-ra-project-setup
description: BCG RA 채용 프로젝트 초기 설정. 프로젝트 정보, 케이스 정보, 채용 인원을 한 번에 수집하여 project_settings.json에 저장.
user_invocable: true
---

# RA 채용 프로젝트 초기 설정 (Phase 0)

이 스킬은 RA 채용 프로세스를 시작하기 전에 프로젝트 정보, 케이스 정보, 채용 인원을 한 번에 수집하여 `data/project_settings.json`에 저장합니다.

## 워크플로우

### Step 1: 기존 설정 확인

1. `data/project_settings.json` 파일이 존재하면 Read 도구로 로드하여 기존 값을 표시합니다.
2. 존재하지 않으면 빈 상태에서 시작합니다.

### Step 2: 프로젝트 정보 수집 (AskUserQuestion 배치)

AskUserQuestion을 활용하여 아래 정보를 수집합니다 (최대 4개 질문씩 배치):

**배치 1:**
1. **프로젝트 주제** (`project_topic`) — 예: "국내 금융 지주사 성장 전략"
2. **근무 기간 시작일** (`work_start`) — 예: "2026-02-27"
3. **근무 기간 종료일** (`work_end`) — 예: "2026-04-03"
4. **지원 마감일** (`application_due`) — 예: "2026-02-18"

**배치 2:**
1. **채용 RA 인원** (`ra_count`) — 예: "2명"
2. **Client 명** (`client_name`) — 예: "KB금융지주"
3. **Case 명** (`case_name`) — 예: "KB Financial Group Growth Strategy"
4. **Case code** (`case_code`) — 예: "SEO-2026-001"

**배치 3:**
1. **P/PL** (`partner_pl`) — 예: "홍길동 Partner / 김철수 PL"
2. **지원 이메일 주소** (`email_addresses`) — To 주소 (CC는 항상 Seoul.RAApplication@bcg.com)

### Step 3: 확인 및 저장

1. 수집된 정보를 표 형태로 사용자에게 보여주고 AskUserQuestion으로 확인합니다.
2. 수정 필요 시 해당 항목만 재수집합니다.
3. `data/project_settings.json`에 저장합니다.

### project_settings.json 스키마

```json
{
  "project_topic": "프로젝트 주제",
  "application_due": "YYYY-MM-DD",
  "work_start": "YYYY-MM-DD",
  "work_end": "YYYY-MM-DD",
  "email_addresses": "[이메일1], [이메일2]",
  "ra_count": 2,
  "client_name": "Client명",
  "case_name": "Case명",
  "case_code": "Case code",
  "partner_pl": "P/PL"
}
```

## 주의사항

- 기존 `project_settings.json`이 있으면 기존 값을 기본값으로 표시하여 수정 편의를 제공합니다.
- 모든 필드가 수집된 후 최종 확인을 반드시 받습니다.
- 이 스킬은 다른 Phase를 실행하기 전에 먼저 실행해야 합니다.
