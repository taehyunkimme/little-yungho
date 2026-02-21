---
name: ra-recruiting
description: BCG RA 채용 프로세스 전체 실행. 공고 포스팅 → 이력서 스크리닝 → 면접 일정 조율 → 최종 합격 통보를 단계별로 진행하며, 각 Phase 사이에 진행 여부를 확인합니다.
user_invocable: true
---

# RA 채용 프로세스 전체 실행

이 스킬은 BCG RA 채용의 4개 Phase를 직접 실행합니다.
개별 Phase 스킬을 Skill 도구로 호출하지 않고, 아래 워크플로우를 인라인으로 수행합니다.

## 전체 흐름

```
Phase 0 (프로젝트 설정) → 배치 확인 → Phase 1 (공고 포스팅) → 배치 확인 → Phase 2 (이력서 스크리닝) → 배치 확인 → Phase 3 (면접 일정 조율) → 배치 확인 → Phase 4 (최종 합격 통보)
```

## 실행 규칙

- **Skill 도구를 호출하지 않습니다.** 모든 Phase를 이 스킬 내에서 직접 수행합니다.
- Phase 간 전환 시 배치화된 AskUserQuestion으로 효율적으로 확인합니다.
- 사용자가 중단을 선택하면 현재까지의 진행 상황을 요약하고 종료합니다.
- 이전 Phase의 산출물(`data/` 디렉토리)이 다음 Phase의 입력이 됩니다.
- Phase 2 Stage 2에서는 Task 도구로 병렬 에이전트를 띄워 이력서를 동시 평가합니다.

---

# Phase 0: 프로젝트 초기 설정

## Step 1: 기존 설정 확인

1. `data/project_settings.json` 파일이 존재하면 Read 도구로 로드하여 기존 값을 표시합니다.
2. 존재하지 않으면 빈 상태에서 시작합니다.

## Step 2: 프로젝트 정보 수집 (AskUserQuestion 배치)

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

## Step 3: 확인 및 저장

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

---

# Phase 0 → Phase 1 전환: 배치 확인

Phase 0 완료 후, 다음 사항을 **하나의 AskUserQuestion**으로 통합하여 확인합니다:

1. **텍스트로 Phase 0 결과 요약**을 보여줍니다:
   - 저장된 프로젝트 설정 요약 (주제, 기간, 케이스 정보, 채용 인원)

2. **AskUserQuestion** (하나의 질문):
   - "Phase 1 (채용 공고 포스팅)으로 진행할까요?"
   - 옵션: "Phase 1로 진행" / "여기서 중단"
   - 중단 선택 시: 진행 상황 요약 후 종료. 나중에 `/phase1-ra-job-posting`으로 이어서 가능함을 안내.

---

# Phase 1: 채용 공고 포스팅

## Step 1: 프로젝트 설정 로드

1. `data/project_settings.json`을 Read 도구로 로드합니다.
   - Phase 0에서 이미 저장했으므로 파일이 반드시 존재합니다.
2. 로드된 프로젝트 설정을 표시합니다 (주제, 근무 기간, 마감일, 이메일 등)

## Step 2: 채용 공고 생성

1. `.claude/skills/phase1-ra-job-posting/assets/job-posting-template.md` 파일을 읽습니다.
2. 템플릿의 placeholder를 치환합니다:
   - `{{project_topic}}` → 프로젝트 주제
   - `{{work_period}}` → 근무 기간 (예: "2026.02.27 ~ 2026.04.03")
   - `{{application_due}}` → 지원 마감일 (예: "2026.02.18")
   - `{{email_addresses}}` → 이메일 주소
3. 완성된 공고를 사용자에게 미리보기로 보여주고 확인을 받습니다.

## Step 3: 채널별 포스팅

포스팅 채널 정보는 `.claude/skills/phase1-ra-job-posting/references/posting-channels.md`를 참조합니다.

### 3-1. 네이버 카페 포스팅

1. `data/naver_cookies.json` 존재 여부 확인
   - 없으면: `.claude/skills/phase1-ra-job-posting/scripts/naver_login.py`를 실행하여 네이버 로그인 세션을 저장
2. 포스팅 제목 생성: `[BCG] Research Analyst 채용 (~{마감일})`
3. `.claude/skills/phase1-ra-job-posting/scripts/naver_cafe_writer.py`를 실행:
   ```bash
   python .claude/skills/phase1-ra-job-posting/scripts/naver_cafe_writer.py \
     --title "포스팅 제목" \
     --content "채용 공고 본문" \
     --cookie-path data/naver_cookies.json \
     --prefix "긴급"
   ```
4. 스크립트가 브라우저를 열고 글쓰기 페이지를 준비합니다. 사용자가 본문을 Cmd+V로 붙여넣고 등록해야 합니다.

### 3-2. 카카오톡 포스팅

1. 카카오톡 단톡방에 공고를 전송합니다.
2. 기존 kakaotalk 플러그인 스킬에 위임합니다.
3. 대상 단톡방: BCG 사내 + 주요 학회 단톡방

## Step 4: 포스팅 이력 저장

포스팅 완료 후 `data/posting_history.json`에 이력을 추가합니다:

```json
{
  "timestamp": "2026-02-17T14:30:00",
  "channel": "naver_cafe",
  "project_topic": "프로젝트 주제",
  "title": "포스팅 제목",
  "status": "success"
}
```

## 주의사항 (Phase 1)

- 포스팅 전 반드시 사용자에게 공고 내용 확인을 받을 것
- 네이버 카페 포스팅은 반자동화 (브라우저 준비까지 자동, 본문 붙여넣기는 사용자)
- 카카오톡 포스팅 시 단톡방 선택을 사용자에게 확인

---

# Phase 1 → Phase 2 전환: 배치 확인

Phase 1 완료 후, 다음 사항을 **하나의 AskUserQuestion**으로 통합하여 확인합니다:

1. **Phase 1 결과 요약**을 텍스트로 보여줍니다:
   - 프로젝트 설정 저장 여부
   - 포스팅 완료 채널 목록
2. **AskUserQuestion** (하나의 질문):
   - "Phase 2 (이력서 스크리닝)로 진행할까요?"
   - 옵션: "Phase 2로 진행" (지원 마감일 이후 권장) / "여기서 중단"
   - 중단 선택 시: 진행 상황 요약 후 종료. 나중에 `/phase2-ra-resume-screening`으로 이어서 가능함을 안내.

---

# Phase 2: 이력서 스크리닝

## 사전 조건

- `data/project_settings.json`이 존재해야 함 (Phase 0에서 생성)
- Gmail MCP 플러그인이 활성화되어 있어야 함

## Step 1: 프로젝트 정보 로드

1. `data/project_settings.json`을 읽어 프로젝트 설정을 로드합니다:
   - `project_topic`: 프로젝트 주제 (Stage 2 평가에 사용)
   - `work_start`, `work_end`: 프로젝트 기간 (Stage 1 기간 검증에 사용)
   - `application_due`: 검색 기간 설정에 활용
2. `data/posting_history.json`에서 가장 최근 포스팅 날짜를 확인합니다.

## Step 2: 이력서 수집

1. Gmail 플러그인으로 `subject:RA지원` 이메일을 검색합니다.
   - 검색 기간: 최근 포스팅 날짜 7일 전 ~ 현재
   - 예: 포스팅이 02/17이면 → `after:2026/02/10`
   - 이유: 포스팅 전에 도착한 지원 이메일 누락 방지
2. 검색된 이메일에서 PDF 첨부파일을 `data/resumes/` 디렉토리에 다운로드합니다.
3. 수집된 지원서 목록을 사용자에게 보고합니다.

## Step 3: 이메일 제목 파싱

각 이메일 제목을 파싱하여 지원자 정보를 추출합니다.

**이메일 제목 형식**: `RA지원_학교명_이름_MMDD-MMDD`

`.claude/skills/phase2-ra-resume-screening/references/subject-format.md`를 참조하여 다양한 변형을 유연하게 파싱합니다:

- `RA지원_서울대_홍길동_0330-0525` → 서울대, 홍길동, 03/30~05/25
- `RA지원_연세대학교_김철수_0227-0403` → 연세대학교, 김철수, 02/27~04/03
- 날짜가 없는 경우도 파싱 가능 (기간 미기재로 처리)

## Step 4: Stage 1 - 자격 필터

각 지원자에 대해 4가지 자격 요건을 확인합니다.

### 4-1. 대학 검증

`.claude/skills/phase2-ra-resume-screening/references/target-universities.md`를 참조하여 지원자의 대학이 타겟 대학 목록에 포함되는지 확인합니다.

- 국내: 서울대, 연세대, 고려대, KAIST, POSTECH
- 해외: 글로벌 Top 30 대학 (중국 대학 제외)

이메일 제목에서 추출한 학교명으로 판단합니다. 대학 미충족 시 탈락.

### 4-2. 학년 검증

이력서 텍스트에서 입학년도를 추출하여 3학년 이상인지 확인합니다.

- `현재연도 - 입학년도 >= 2`이면 통과
- 입학년도를 확인할 수 없는 경우 통과 처리 (benefit of the doubt)
- 학년 미충족 시 탈락.

### 4-3. 나이 검증

이력서에서 첫 번째 대학 입학년도를 추출하여 나이를 확인합니다.

- `현재연도 - 입학연도 > 7`이면 탈락 (만 26세 초과 추정)
- 입학연도를 확인할 수 없는 경우 통과 처리
- 나이 미충족 시 탈락.

### 4-4. 근무 가능 기간 검증

이메일 제목에서 파싱한 근무 가능 기간이 프로젝트 기간을 완전히 커버하는지 확인합니다.

- `지원자_시작일 <= 프로젝트_시작일` AND `지원자_종료일 >= 프로젝트_종료일`

**기간 미충족자 처리는 Step 5의 배치 확인에서 함께 처리합니다 (아래 참조).**

## Step 5: Stage 1 결과 보고 및 배치 확인

Stage 1 자격 필터를 모두 수행한 후, **하나의 보고 + AskUserQuestion**으로 통합 처리합니다:

1. **텍스트로 Stage 1 결과를 보고합니다:**
   - 전체 지원자 수
   - 대학/학년/나이 기준 통과자 수
   - 기간 미충족자 목록 (각 지원자별 부족 일수 또는 미기재 여부 표시)
   - 기간 충족 통과자 수

2. **AskUserQuestion** (multiSelect 또는 단일 질문으로 처리):
   - 기간 미충족자가 있을 경우: "기간 미충족자 N명을 어떻게 처리할까요?"
     - 옵션: "전원 포함" / "전원 제외" / "개별 선택"
     - "개별 선택" 시 추가 AskUserQuestion으로 각 지원자별 포함/제외 결정
   - 기간 미충족자가 없으면 이 질문 생략

3. 사용자 결정에 따라 Stage 1 최종 통과자 목록을 확정합니다.

## Step 6: Stage 2 - 종합 평가 (병렬 실행)

Stage 1 통과자에 대해 이력서를 읽고 종합 평가를 **Task 도구로 병렬 수행**합니다.

### 평가 기준

각 이력서 PDF를 Read 도구로 읽어서 직접 평가합니다:

**1. 리서치/분석 경험 (0-30점) — Tier 기반**

`.claude/skills/phase2-ra-resume-screening/references/ra-firms.json`을 참조하여 경험을 Tier로 분류합니다:

| Tier   | 점수    | 해당 경험                                                        |
| ------ | ------- | ---------------------------------------------------------------- |
| Tier 1 | 25-30점 | MBB (BCG, McKinsey, Bain) RA 경험                                |
| Tier 2 | 15-20점 | PE/VC 인턴, IB 인턴, 기타 전략컨설팅 RA/인턴, Big4 전략부문 인턴 |
| Tier 3 | 5-10점  | 기업 전략/기획팀 인턴, 씽크탱크/리서치기관, 학교 연구실 RA       |
| 없음   | 0점     | 리서치/분석 관련 경험 없음                                       |

- 동일 Tier 내 복수 경험 시 상위 점수 적용 (중복 합산 아님)
- 상위 Tier 경험이 있으면 하위 Tier는 무시

**2. 스타트업/주도적 경험 (0-10점)**

| 점수   | 해당 경험                                                                  |
| ------ | -------------------------------------------------------------------------- |
| 8-10점 | 직접 창업 + 의미 있는 traction (매출, 투자유치, 유명 액셀러레이터 선발 등) |
| 5-7점  | 직접 창업 경험 (초기 단계 포함)                                            |
| 3-4점  | 창업 동아리/공모전에서 실질적 사업 운영 경험                               |
| 0점    | 해당 없음                                                                  |

**3. 프로젝트 관련성 (0-5점)**

- 프로젝트 주제(`project_topic`)와 연관되는 배경(학과, 인턴 경험, 수강과목 등): 5점
- 간접적 관련성: 2-3점
- 없음: 0점

**총점 = 리서치/분석 경험(30) + 스타트업/주도적 경험(10) + 프로젝트 관련성(5) = 최대 45점**

### 병렬 평가 실행 방법

1. Stage 1 통과자를 **4~5명씩 그룹**으로 나눕니다.
2. 사전에 다음 참조 파일들을 읽어둡니다:
   - `.claude/skills/phase2-ra-resume-screening/references/ra-firms.json`의 내용
   - 위의 평가 기준 전문
3. 각 그룹을 **Task 도구** (`subagent_type: "general-purpose"`)에 위임합니다. 각 에이전트에게 전달할 프롬프트에 반드시 포함할 정보:
   - 할당된 이력서 PDF 경로 목록 (절대 경로)
   - 평가 기준 전문 (위의 Tier 표, 스타트업 점수표, 프로젝트 관련성 기준)
   - `ra-firms.json`의 전체 내용 (기업명 → Tier 매핑)
   - `project_topic` 값
   - **반환 형식 지시**: 다음 JSON 배열 형식으로 결과를 반환하라고 명시:
     ```json
     [
       {
         "pdf_path": "data/resumes/파일명.pdf",
         "total_score": 35,
         "research_experience_score": 25,
         "research_experience_tier": "tier1_mbb",
         "research_experience_reason": "BCG RA 경험",
         "startup_score": 7,
         "startup_reason": "직접 창업 경험 (초기 단계)",
         "relevance_score": 3,
         "relevance_reason": "금융 관련 인턴 경험으로 간접적 관련성"
       }
     ]
     ```
4. **가능하면 모든 그룹의 Task를 동시에 실행**합니다 (하나의 메시지에서 여러 Task 도구 호출).
5. 모든 에이전트의 결과를 수집한 후, JSON 결과를 통합합니다.

## Step 7: 결과 정리 및 배치 선발 확인

1. Stage 2 평가 결과를 총점 기준으로 내림차순 정렬합니다.
2. **텍스트로 전체 결과를 보고합니다:**
   - 전체 지원자 수
   - Stage 1 통과자 / 탈락자 (탈락 사유 포함)
   - Stage 2 점수 순위 테이블
3. **AskUserQuestion** (하나의 질문):
   - "Top N명을 면접 대상자로 선발합니다. 몇 명을 선발할까요?"
   - 옵션: 추천 인원수 (예: "5명 (추천)" / "3명" / "7명" / 직접 입력)
4. 최종 결과를 `data/screening_results.json`에 저장합니다.

### screening_results.json 스키마

```json
[
  {
    "email_id": "이메일 ID",
    "subject": "원본 제목",
    "sender": "발신자 이메일",
    "name": "지원자 이름",
    "school": "학교명",
    "availability": { "start": "YYYY-MM-DD", "end": "YYYY-MM-DD" },
    "stage1": {
      "passed": true,
      "school_match": true,
      "grade_ok": true,
      "age_ok": true,
      "period_ok": true,
      "period_user_included": false,
      "reason": "통과"
    },
    "stage2": {
      "total_score": 35,
      "research_experience_score": 25,
      "research_experience_tier": "tier1_mbb",
      "research_experience_reason": "BCG RA 경험",
      "startup_score": 7,
      "startup_reason": "직접 창업 경험 (초기 단계)",
      "relevance_score": 3,
      "relevance_reason": "금융 관련 인턴 경험으로 간접적 관련성"
    },
    "selected": true,
    "pdf_path": "data/resumes/파일명.pdf"
  }
]
```

## 주의사항 (Phase 2)

- 이력서에는 민감한 개인정보가 포함되어 있으므로 주의하여 다룰 것
- Stage 1 탈락 사유를 명확히 기록할 것
- Stage 2 평가 시 일관된 기준을 적용할 것
- 기간 미충족자는 사용자 결정 전까지 탈락 처리하지 않을 것
- 최종 선발 전 반드시 사용자 확인을 받을 것

---

# Phase 2 → Phase 3 전환: 배치 확인

Phase 2 완료 후, 다음 사항을 **하나의 AskUserQuestion**으로 통합하여 확인합니다:

1. **텍스트로 Phase 2 결과 요약**을 보여줍니다:
   - 전체 지원자 수 → Stage 1 통과 → Stage 2 선발 인원
   - 선발된 면접 대상자 목록 (이름, 학교, 점수)

2. **AskUserQuestion** (multiSelect: false, 최대 4개 질문 활용):
   - 질문 1: "면접에서 제외할 지원자가 있나요?"
     - 옵션: "없음, 전원 면접 진행" / "제외할 사람 있음"
     - "제외할 사람 있음" 선택 시 추가 AskUserQuestion으로 개별 확인
   - 질문 2: "면접 방식은?"
     - 옵션: "유선" / "온라인 (Google Meet)" / "대면"
   - 질문 3: "면접 시간은?"
     - 옵션: "30분 (기본)" / "20분" / "45분"
   - 질문 4: "Phase 3 (면접 일정 조율)로 진행할까요?"
     - 옵션: "진행" / "여기서 중단"
     - 중단 선택 시: 진행 상황 요약 후 종료. 나중에 `/phase3-ra-interview-setting`으로 이어서 가능함을 안내.

---

# Phase 3: 면접 일정 조율

## 사전 조건

- `data/screening_results.json`이 존재해야 함 (Phase 2에서 생성)
- Google Calendar 플러그인이 활성화되어 있어야 함
- Gmail MCP 플러그인이 활성화되어 있어야 함

## 플러그인 경로

| 플러그인        | 경로                                                                                                   |
| --------------- | ------------------------------------------------------------------------------------------------------ |
| Google Calendar | `~/.claude/plugins/marketplaces/team-attention-plugins/plugins/google-calendar/skills/google-calendar` |
| Gmail           | `~/.claude/plugins/marketplaces/team-attention-plugins/plugins/gmail/skills/gmail`                     |

## Step 1: 면접 대상자 확인

1. `data/screening_results.json`에서 `"selected": true`인 지원자를 로드합니다.
2. Phase 2 → Phase 3 배치 확인에서 이미 제외자, 면접 방식, 시간을 확인했으므로 해당 설정을 적용합니다.
3. 최종 면접 대상자 목록을 확정합니다.

## Step 2: Google Calendar 빈 시간 확인

1. Google Calendar 플러그인의 `accounts/` 폴더를 확인합니다.
   - 비어있으면 사용자에게 인증 설정이 필요함을 안내합니다:
     - "Google Cloud OAuth credentials가 준비되어 있나요?"
     - 준비되었다면 인증 스크립트를 실행합니다:
       ```bash
       uv run python {calendar_plugin_path}/scripts/setup_auth.py --account work
       ```
2. Google Calendar 플러그인으로 면접 가능 기간의 일정을 조회합니다:
   ```bash
   uv run python {calendar_plugin_path}/scripts/fetch_events.py \
     --account work --days 14
   ```
3. 조회된 일정에서 **비어있는 슬롯**을 추출합니다:
   - 업무 시간: 평일 09:00~18:00
   - 기존 일정과 겹치지 않는 슬롯만 추출
   - 면접 소요 시간은 Phase 2→3 전환에서 확인한 값 적용
   - 최소 5개 이상의 후보 슬롯 생성

## Step 3: 시간대 제안 및 사용자 선호도 확인

1. 추출된 빈 시간 슬롯을 사용자에게 보고합니다.
2. AskUserQuestion으로 선호 시간대를 확인합니다:
   - 가장 선호하는 슬롯 (1순위)
   - 차선 슬롯 (2~3순위)

## Step 4: 면접 일정 확인 이메일 발송

1. 이메일 본문을 작성합니다:
   - 서류 통과 축하
   - 제안된 면접 일시 (1순위 슬롯)
   - 해당 시간이 괜찮은지 확인 요청
   - 불가 시 대안 일시 제안 요청
   - 회신 기한 안내
2. **발송 전 반드시** 이메일 본문을 사용자에게 미리보기로 보여주고 확인을 받습니다.
3. 사용자 승인 후 Gmail 플러그인으로 각 면접 대상자에게 이메일을 발송합니다:
   ```bash
   uv run python {gmail_plugin_path}/scripts/send_message.py \
     --account personal \
     --to "{지원자이메일}" \
     --subject "BCG RA 면접 일정 안내" \
     --body "{이메일 본문}"
   ```

## Step 5: 일정 저장

발송 완료 후 `data/interview_schedule.json`에 `pending_confirmation` 상태로 저장합니다.

---

## Step 6: 회신 확인 및 일정 확정

> 이 단계는 회신 기한 이후에 별도로 실행합니다.

1. Gmail 플러그인으로 면접 대상자들의 회신 이메일을 검색합니다:
   ```bash
   uv run python {gmail_plugin_path}/scripts/list_messages.py \
     --account personal --query "subject:BCG RA 면접" --max-results 20
   ```
2. 각 면접 대상자별 회신 내용을 파악합니다:
   - **확인**: 제안된 시간에 면접 가능
   - **변경 요청**: 대안 일시 제안
   - **미회신**: 아직 답변 없음
3. 결과를 사용자에게 보고합니다:
   - 확인된 인원 / 변경 요청 인원 / 미회신 인원
   - 변경 요청자의 대안 일시
4. AskUserQuestion으로 사용자 결정을 요청합니다:
   - 변경 요청자: 대안 일시 수용 여부
   - 미회신자: 리마인더 발송 또는 제외
5. `data/interview_schedule.json`의 각 지원자 `status`를 업데이트합니다:
   - `"confirmed"`: 일정 확정
   - `"rescheduled"`: 변경된 일시로 확정 (`proposed_date`, `proposed_time` 업데이트)
   - `"no_response"`: 미회신

## Step 7: Google Meet 초대 발송

일정이 확정된 면접 대상자에 대해 Google Calendar 이벤트를 생성하고 Google Meet 링크를 포함한 초대를 발송합니다.

1. `data/interview_schedule.json`에서 `status`가 `"confirmed"` 또는 `"rescheduled"`인 지원자를 로드합니다.
2. 각 지원자별로 Google Calendar 이벤트를 생성합니다:

   ```bash
   uv run python {calendar_plugin_path}/scripts/manage_events.py create \
     --account work \
     --summary "RA Interview - {지원자이름}님" \
     --start "{날짜}T{시간}:00" \
     --end "{날짜}T{종료시간}:00" \
     --attendees "{지원자이메일}" \
     --meet \
     --json
   ```

   - 제목은 반드시 `"RA Interview - {지원자이름}님"` 형식으로 통일합니다.
   - `--meet` 플래그로 Google Meet 링크가 자동 생성됩니다.
   - `--attendees`에 지원자 이메일을 포함하면 Google Calendar 초대가 자동 발송됩니다.

3. 생성된 이벤트의 `meet_link`를 `data/interview_schedule.json`에 저장합니다.
4. Gmail 플러그인으로 **2종류 이메일**을 발송합니다:

   **A. 지원자에게 → 확정 안내 (첨부파일 없음)**
   - 확정된 면접 일시
   - Google Meet 링크
   - 준비 사항 안내
   - 일정 변경 시 연락 방법
   ```bash
   uv run python {gmail_plugin_path}/scripts/send_message.py \
     --account personal \
     --to "{지원자이메일}" \
     --subject "BCG RA 면접 확정 안내" \
     --body "{이메일 본문}"
   ```

   **B. 면접관(사용자)에게 → 면접 준비 통합 이메일 1건 (이력서 전원 첨부)**
   - 수신: `project_settings.json`의 사용자 본인 이메일
   - 제목: `RA 면접 준비 - 이력서 첨부`
   - 본문: 전체 면접 일정표 (이름, 학교, 일시, Meet 링크)
   - 첨부: 모든 면접 대상자의 이력서 PDF를 한 번에 첨부
   ```bash
   uv run python {gmail_plugin_path}/scripts/send_message.py \
     --account personal \
     --to "{사용자이메일}" \
     --subject "RA 면접 준비 - 이력서 첨부" \
     --body "{면접 일정표 본문}" \
     --attach "{pdf_path1},{pdf_path2},{pdf_path3},..."
   ```

5. **발송 전 반드시** 이메일 본문을 사용자에게 미리보기로 보여주고 확인을 받습니다.
6. `data/interview_schedule.json`의 `status`를 `"meet_sent"`로 업데이트합니다.

### interview_schedule.json 스키마

```json
[
  {
    "name": "지원자 이름",
    "school": "학교명",
    "email": "지원자 이메일",
    "proposed_date": "2026-02-25",
    "proposed_time": "14:00",
    "duration_minutes": 30,
    "method": "온라인",
    "status": "pending_confirmation",
    "email_sent_at": "2026-02-17T...",
    "pdf_path": "data/resumes/파일명.pdf",
    "meet_link": null,
    "calendar_event_id": null
  }
]
```

**status 값 흐름**: `pending_confirmation` → `confirmed` / `rescheduled` / `no_response` → `meet_sent`

## 주의사항 (Phase 3)

- 이메일 발송 전 반드시 사용자 확인을 받을 것
- Google Calendar 인증이 안 되어 있으면 진행 전에 먼저 설정할 것
- Google Calendar OAuth scope는 `calendar` (읽기/쓰기)여야 이벤트 생성 및 Meet 링크 생성이 가능
- Step 6~7은 회신 기한 이후 별도 실행 (사용자가 `/ra-recruiting`을 다시 호출하면 기존 `interview_schedule.json`의 상태를 확인하여 이어서 진행)

---

# Phase 3 → Phase 4 전환: 배치 확인

Phase 3 완료 후, 다음 사항을 **하나의 AskUserQuestion**으로 통합하여 확인합니다:

1. **텍스트로 Phase 3 결과 요약**을 보여줍니다:
   - 면접 완료자 목록 (`status: "meet_sent"` 인원)
   - 각 후보자의 이름, 학교, 면접 일시

2. **AskUserQuestion** (multiSelect: false):
   - "Phase 4 (최종 합격 통보)로 진행할까요?"
   - 옵션: "Phase 4로 진행" / "여기서 중단"
   - 중단 선택 시: 진행 상황 요약 후 종료. 나중에 `/phase4-ra-final-notification`으로 이어서 가능함을 안내.

---

# Phase 4: 최종 합격 통보

## 사전 조건

- `data/interview_schedule.json`이 존재해야 함 (Phase 3에서 생성)
- `data/project_settings.json`이 존재해야 함 (Phase 0에서 생성)
- Gmail 플러그인 인증이 완료되어 있어야 함

## 플러그인 경로

| 플러그인 | 경로 |
|---------|------|
| Gmail | `~/.claude/plugins/marketplaces/team-attention-plugins/plugins/gmail/skills/gmail` |

### Step 1: 데이터 로드 및 최종 합격자 선정

1. `data/interview_schedule.json`을 Read 도구로 로드합니다.
2. `status: "meet_sent"` 후보자 목록을 표시합니다.
3. AskUserQuestion (multiSelect: true)으로 최종 합격자를 선정합니다:
   - "최종 합격자를 선택해주세요."
   - 옵션: 각 후보자 이름 + 학교 (예: "유주미 (서울대)", "고예빈 (연세대)")
4. 합격자 목록을 확정합니다.

### Step 2: Resume PDF 분석 및 정보 추출

각 합격자의 `pdf_path`에서 Resume PDF를 Read 도구로 읽고 다음 정보를 추출합니다:

- **생년월일** (HR 이메일용) — 형식: YYYY.MM.DD
- **영문 주소** (HR 이메일용) — 없으면 `null`
- **대학교, 전공, 학점** (파트너 이메일용) — 학점은 X.XX/Y.YY 형식
- **핵심 경력 요약 3줄** (파트너 이메일용):
  - Line 1: 컨설팅/RA 경험 (있으면)
  - Line 2: 주요 인턴 경력
  - Line 3: 기타 관련 경험 (학회, 동아리 등)

추출 결과를 사용자에게 표 형태로 보여주고 AskUserQuestion으로 수정 여부를 확인합니다.

### Step 3: 합격자 통보 이메일 발송

1. Step 2에서 추출한 생년월일·영문주소의 누락 여부를 후보자별로 확인합니다.
2. 각 합격자에게 **합격 통보 이메일**을 발송합니다:
   - **Subject**: `BCG RA 최종 합격 안내`
   - **본문 구성**:
     - 합격 축하 인사
     - "차주 중 HR에서 자세한 입사 방법을 안내드릴 예정"
     - (생년월일 또는 영문주소 중 누락 항목이 있을 경우) 해당 정보 회신 요청
   - **누락 항목에 따른 본문 분기**:
     - **둘 다 있음** → 요청 문구 없이 합격 축하만
     - **생년월일만 없음** → "채용 절차 진행을 위해 생년월일을 회신해주시면 감사하겠습니다."
     - **영문주소만 없음** → "채용 절차 진행을 위해 영문 주소를 회신해주시면 감사하겠습니다."
     - **둘 다 없음** → "채용 절차 진행을 위해 생년월일과 영문 주소를 회신해주시면 감사하겠습니다."
3. 발송 커맨드:
   ```bash
   GMAIL_SCRIPTS=~/.claude/plugins/marketplaces/team-attention-plugins/plugins/gmail/skills/gmail/scripts

   uv run python "$GMAIL_SCRIPTS/send_message.py" \
     --account personal --to "{후보자이메일}" \
     --subject "BCG RA 최종 합격 안내" \
     --body "{합격 통보 본문}"
   ```
4. `data/final_notification.json`에 상태 기록:
   - `candidate_notified: true`
   - 누락 항목이 있으면 `missing_info_status: "requested"`, 없으면 `missing_info_status: "complete"`
   - `missing_info_items: ["birth_date", "english_address"]` (누락 항목 목록)

### Step 4: 이메일 작성

#### 4-A. HR 채용 요청 이메일 (HTML)

- **Subject**: `RA 신규 채용 요청`
- **형식**: HTML (`--html` 플래그 사용)
- **첨부**: 모든 합격자의 Resume PDF
- **Template 치환 규칙**:
  - `{}명` → 합격자 수
  - 근무 기간 → `project_settings.json`의 `work_start ~ work_end` (예: "2/27~4/3, 약 36일")
  - RA생년월일 → Resume에서 추출 (예: "최주연(2001.02.15), 도연희(2000.06.05)")
  - Client 명 → `project_settings.json`의 `client_name`
  - Case 명 → `project_settings.json`의 `case_name`
  - Case code → `project_settings.json`의 `case_code`
  - P/PL → `project_settings.json`의 `partner_pl`
  - RA영문 주소 → Resume에 있으면 "Resume 내 포함 완료", 없으면 "확인 중 (후보자 회신 대기)"

**생년월일 또는 영문주소 미확보 후보자가 있으면**: HR 이메일은 보류하고 `hr_email_status: "pending_info"` 설정. 모든 누락 정보 확보 시 daily-ra-status에서 자동 발송됩니다.

#### 4-B. 파트너 승인 이메일 (plain text)

- **Subject**: `RA 채용 승인 요청`
- **형식**: plain text (기본)
- **첨부**: 모든 합격자의 Resume PDF
- **본문 형식**:

```
안녕하세요, RA 채용 승인을 요청드립니다.

{N}명의 RA를 {근무시작일}부터 채용하고자 합니다.

[후보자 프로필]

{이름}
{대학교} {전공} ({학점 X.XX/Y.YY})
{핵심 경력 1}
{핵심 경력 2}
{핵심 경력 3}

---

{다음 후보자 반복}

검토 후 승인 부탁드립니다.
감사합니다.
```

### Step 5: 사용자 미리보기 및 발송 확인

1. HR 이메일과 파트너 이메일 각각의 미리보기를 사용자에게 표시합니다.
2. AskUserQuestion으로 수정 필요 여부를 확인합니다:
   - "이메일 내용을 확인해주세요. 수정이 필요한가요?"
   - 옵션: "수정 없이 발송" / "수정 필요"
3. 승인 후 Gmail 플러그인으로 `kim.taehyun@bcg.com`에 발송합니다:

```bash
GMAIL_SCRIPTS=~/.claude/plugins/marketplaces/team-attention-plugins/plugins/gmail/skills/gmail/scripts

# HR 이메일 (HTML + 첨부) — 영문 주소 미확보 시 보류
uv run python "$GMAIL_SCRIPTS/send_message.py" \
  --account personal \
  --to "kim.taehyun@bcg.com" \
  --subject "RA 신규 채용 요청" \
  --body "{HR 이메일 HTML}" \
  --html \
  --attach "{pdf1},{pdf2}"

# 파트너 이메일 (plain text + 첨부)
uv run python "$GMAIL_SCRIPTS/send_message.py" \
  --account personal \
  --to "kim.taehyun@bcg.com" \
  --subject "RA 채용 승인 요청" \
  --body "{파트너 이메일 본문}" \
  --attach "{pdf1},{pdf2}"
```

**누락 정보(생년월일/영문주소) 미확보 시**: 파트너 이메일만 발송하고, HR 이메일은 보류 안내.

### Step 6: 상태 저장

`data/final_notification.json`을 생성/업데이트합니다:

```json
{
  "candidates": [
    {
      "name": "이름",
      "email": "이메일",
      "school": "대학교",
      "major": "전공",
      "gpa": "학점",
      "birth_date": "YYYY.MM.DD or null",
      "english_address": "영문 주소 or null",
      "missing_info_status": "complete|requested|received",
      "missing_info_items": [],
      "candidate_notified": true,
      "profile_summary": ["경력1", "경력2", "경력3"],
      "pdf_path": "data/resumes/파일명.pdf"
    }
  ],
  "hr_email_status": "sent|pending_info",
  "partner_email_status": "sent|not_sent",
  "hr_email_sent_at": "ISO timestamp or null",
  "partner_email_sent_at": "ISO timestamp or null"
}
```

## 주의사항 (Phase 4)

- 이메일 발송 전 반드시 사용자 확인을 받을 것
- HR 이메일은 보안상 `kim.taehyun@bcg.com`으로만 발송 (사용자가 직접 HR/파트너에게 전달)
- Resume에 포함된 개인정보(생년월일, 주소 등) 처리 시 주의
- 누락 정보(생년월일/영문주소) 미확보 시 HR 이메일은 보류하고, daily-ra-status에서 자동 감지 후 발송

---

# 중단 시 처리

사용자가 중간에 중단을 선택한 경우:

1. 현재까지 완료된 Phase와 산출물을 정리하여 보고합니다.
2. 나중에 개별 스킬(`/phase1-ra-job-posting`, `/phase2-ra-resume-screening`, `/phase3-ra-interview-setting`, `/phase4-ra-final-notification`)로 이어서 진행할 수 있음을 안내합니다.
