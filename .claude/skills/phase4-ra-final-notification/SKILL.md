---
name: phase4-ra-final-notification
description: BCG RA 최종 합격자 HR 채용 요청 및 파트너 승인 이메일 작성. 사용자 업무 메일로 발송.
user_invocable: true
---

# RA 최종 합격 통보 (Phase 4)

이 스킬은 면접 완료 후 최종 합격자에 대해 HR 채용 요청 이메일과 파트너 승인 이메일을 작성하여 사용자의 업무 메일(`kim.taehyun@bcg.com`)로 발송합니다.

## 사전 조건

- `data/interview_schedule.json`이 존재해야 함 (Phase 3에서 생성)
- `data/project_settings.json`이 존재해야 함 (Phase 0에서 생성)
- Gmail 플러그인 인증이 완료되어 있어야 함

## 플러그인 경로

| 플러그인 | 경로 |
|---------|------|
| Gmail | `~/.claude/plugins/marketplaces/team-attention-plugins/plugins/gmail/skills/gmail` |

## 워크플로우

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
   - "수정 필요" 선택 시 수정 사항을 반영하고 다시 미리보기를 보여줍니다.
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

**누락 정보(생년월일/영문주소) 미확보 시**: 파트너 이메일만 발송하고, HR 이메일은 보류 안내를 사용자에게 전달합니다.

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

## 주의사항

- 이메일 발송 전 반드시 사용자 확인을 받을 것
- HR 이메일은 보안상 `kim.taehyun@bcg.com`으로만 발송 (사용자가 직접 HR/파트너에게 전달)
- Resume에 포함된 개인정보(생년월일, 주소 등) 처리 시 주의
- 누락 정보(생년월일/영문주소) 미확보 시 HR 이메일은 보류하고, daily-ra-status에서 자동 감지 후 발송
