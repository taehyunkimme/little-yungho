---
name: phase3-ra-interview-setting
description: BCG RA 면접 일정 조율 (Phase 3). 스크리닝 통과자와 Google Calendar 기반 면접 일정 설정 및 이메일 발송.
user_invocable: true
---

# RA 면접 일정 조율 (Phase 4)

이 스킬은 스크리닝 통과자와의 면접 일정을 Google Calendar 빈 시간 기반으로 조율하고, 면접 확인 이메일을 발송합니다.

## 사전 조건

- `data/screening_results.json`이 존재해야 함 (Phase 2에서 생성)
- Google Calendar 플러그인이 활성화되어 있어야 함
- Gmail MCP 플러그인이 활성화되어 있어야 함

## 플러그인 경로

| 플러그인 | 경로 |
|---------|------|
| Google Calendar | `~/.claude/plugins/marketplaces/team-attention-plugins/plugins/google-calendar/skills/google-calendar` |
| Gmail | `~/.claude/plugins/marketplaces/team-attention-plugins/plugins/gmail/skills/gmail` |

## 워크플로우

### Step 1: 면접 대상자 확인

1. `data/screening_results.json`에서 `"selected": true`인 지원자를 로드합니다.
2. 사용자에게 면접 대상자 목록(이름, 학교, 점수, 이메일)을 보여줍니다.
3. AskUserQuestion으로 면접 제외자를 확인합니다:
   - "면접에서 제외할 지원자가 있나요?"
   - 사용자가 제외자를 지정하면 해당 인원을 목록에서 제거
4. 최종 면접 대상자 목록을 확정하고 사용자에게 보고합니다.

### Step 2: Google Calendar 빈 시간 확인

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
3. 조회된 일정에서 **비어있는 30분 슬롯**을 추출합니다:
   - 업무 시간: 평일 09:00~18:00
   - 기존 일정과 겹치지 않는 슬롯만 추출
   - 최소 5개 이상의 후보 슬롯 생성

### Step 3: 시간대 제안 및 사용자 선호도 확인

1. 추출된 빈 시간 슬롯을 사용자에게 보고합니다.
2. AskUserQuestion으로 선호 시간대를 확인합니다:
   - 가장 선호하는 슬롯 (1순위)
   - 차선 슬롯 (2~3순위)
   - 면접 방식 (유선/온라인/대면)
   - 면접 소요 시간 (기본 30분)

### Step 4: 면접 일정 확인 이메일 발송

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

### Step 5: 일정 저장

발송 완료 후 `data/interview_schedule.json`에 `pending_confirmation` 상태로 저장합니다.

---

### Step 6: 회신 확인 및 일정 확정

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

### Step 7: Google Meet 초대 발송

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
4. Gmail 플러그인으로 각 지원자에게 확정 안내 이메일을 발송합니다:
   - 확정된 면접 일시
   - Google Meet 링크
   - 준비 사항 안내
   - 일정 변경 시 연락 방법
   - **지원자의 이력서 PDF를 첨부** (`data/interview_schedule.json`의 `pdf_path` 참조)
   ```bash
   uv run python {gmail_plugin_path}/scripts/send_message.py \
     --account personal \
     --to "{지원자이메일}" \
     --subject "BCG RA 면접 확정 안내" \
     --body "{이메일 본문}" \
     --attach "{pdf_path}"
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

## 주의사항

- 이메일 발송 전 반드시 사용자 확인을 받을 것
- Google Calendar 인증이 안 되어 있으면 진행 전에 먼저 설정할 것
- Google Calendar OAuth scope는 `calendar` (읽기/쓰기)여야 이벤트 생성 및 Meet 링크 생성이 가능
- 면접 대상자 제외는 사용자 결정에 따를 것
- Step 6~7은 회신 기한 이후 별도 실행 (사용자가 `/ra-interview`를 다시 호출하면 기존 `interview_schedule.json`의 상태를 확인하여 이어서 진행)
