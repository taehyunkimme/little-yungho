---
name: daily-ra-status
description: RA 채용 현황 일일 체크. Gmail에서 신규 지원/면접 회신 확인 후 Slack 대시보드 업데이트.
user_invocable: true
---

# RA 채용 현황 일일 체크

이 스킬은 Gmail에서 새로운 RA 지원 이메일과 면접 회신을 확인하고, Slack `#ra-recruiting` 채널에 현황 대시보드를 포스팅합니다.

## 사전 조건

- `data/automation_config.json`이 존재해야 함
- `data/project_settings.json`이 존재해야 함
- Gmail 플러그인 인증이 완료되어 있어야 함 (accounts/personal.json)
- Slack Webhook URL이 설정되어 있어야 함 (config 또는 환경변수)

## 플러그인 경로

| 플러그인 | 경로 |
|---------|------|
| Gmail | `~/.claude/plugins/marketplaces/team-attention-plugins/plugins/gmail/skills/gmail` |

## 워크플로우

### Step 1: 설정 로드

1. `data/automation_config.json`을 Read 도구로 로드합니다.
2. `daily_status_active`가 `false`이면 "일일 체크가 비활성화 상태입니다. `data/automation_config.json`에서 `daily_status_active`를 `true`로 변경해주세요." 메시지를 출력하고 종료합니다.
3. `last_checked_at` 값을 확인합니다:
   - `null`이면 7일 전 날짜를 기본값으로 사용합니다.
   - 값이 있으면 해당 타임스탬프를 사용합니다.
4. Slack Webhook URL을 확인합니다:
   - 환경변수 `SLACK_WEBHOOK_URL`이 있으면 사용
   - 없으면 `automation_config.json`의 `slack_webhook_url` 사용
   - 둘 다 없으면 에러 메시지 출력 후 종료

### Step 2: Gmail에서 신규 지원 이메일 검색

Gmail 플러그인 스크립트를 사용하여 새로운 RA 지원 이메일을 검색합니다.

```bash
GMAIL_SCRIPTS=~/.claude/plugins/marketplaces/team-attention-plugins/plugins/gmail/skills/gmail/scripts

uv run python "$GMAIL_SCRIPTS/list_messages.py" \
  --account personal \
  --query "subject:RA지원 after:{last_checked_date_YYYY/MM/DD}" \
  --full --json
```

- `{last_checked_date_YYYY/MM/DD}`: `last_checked_at`을 `YYYY/MM/DD` 형식으로 변환
- JSON 출력에서 각 이메일의 `subject`, `from`, `date`를 추출
- `data/screening_results.json`의 기존 지원자 이메일과 비교하여 신규 지원자만 필터링

### Step 3: Gmail에서 면접 회신 이메일 검색

면접 일정 관련 회신 이메일을 검색합니다.

```bash
uv run python "$GMAIL_SCRIPTS/list_messages.py" \
  --account personal \
  --query "subject:BCG RA 면접 after:{last_checked_date_YYYY/MM/DD}" \
  --full --json
```

- 검색 결과에서 `data/interview_schedule.json`의 지원자 이메일과 매칭
- 각 회신의 내용을 분석하여 분류:
  - **확인**: "가능합니다", "확인했습니다" 등 긍정 표현
  - **변경 요청**: 다른 시간/날짜 제안
  - **거절**: "불가", "어렵습니다" 등
- 필요시 개별 이메일 내용을 읽어 상세 확인:

```bash
uv run python "$GMAIL_SCRIPTS/read_message.py" \
  --account personal \
  --id {message_id} --json
```

### Step 4: 현황 집계

`data/` 디렉토리의 JSON 파일들을 Read 도구로 로드하여 전체 현황을 집계합니다.

1. `data/screening_results.json`:
   - 총 지원자 수
   - Stage 1 통과자 수
   - Stage 2 평가 완료자 수
   - `selected: true` 인원 수

2. `data/interview_schedule.json`:
   - 각 status별 인원 수: `pending_confirmation`, `confirmed`, `rescheduled`, `no_response`, `meet_sent`

3. 신규 변동 사항:
   - Step 2에서 발견된 신규 지원자 수 및 목록
   - Step 3에서 발견된 면접 회신 내역

### Step 5: Slack 대시보드 포스팅

Webhook URL로 포맷된 메시지를 전송합니다.

메시지 포맷:
```
📋 RA 채용 현황 업데이트 ({오늘날짜} {시간} KST)

📬 신규 지원 ({N}건)
{신규 지원자가 있으면}
• {이메일 제목} (from: {발신자})
...
{없으면}
• 신규 지원 없음

📩 면접 회신 ({N}건)
{회신이 있으면}
• {이름} ({학교}) — {회신 요약}
...
{없으면}
• 신규 회신 없음

📊 전체 현황
• 총 지원자: {N}명 {신규가 있으면 "(신규 +N)"}
• 스크리닝 통과: {N}명
• 면접 확정(meet_sent): {N}명 | 대기(pending): {N}명

⚡ 필요 조치
{조치 항목이 있으면 나열}
• 신규 이력서 {N}건 스크리닝 필요
• {이름} 면접 확정 처리 필요
• {이름} 일정 변경 요청 확인 필요
{없으면}
• 현재 필요한 조치 없음
```

Slack 전송:
```bash
curl -X POST -H 'Content-type: application/json' \
  --data '{"text":"{위 메시지}"}' \
  "{SLACK_WEBHOOK_URL}"
```

**주의**: JSON 문자열에서 줄바꿈은 `\n`, 큰따옴표는 `\"`, 이모지는 그대로 사용합니다.

### Step 6: 상태 업데이트

1. `data/automation_config.json`의 `last_checked_at`을 현재 시간(ISO 8601, KST)으로 업데이트합니다.
2. Write 도구로 저장합니다.

## CI 환경에서의 실행

GitHub Actions에서 실행될 때:
- Gmail OAuth 토큰: `GMAIL_OAUTH_TOKEN` 시크릿에서 `accounts/personal.json`으로 복원
- Slack Webhook URL: `SLACK_WEBHOOK_URL` 환경변수로 전달
- `data/` 디렉토리: 레포지토리에 커밋된 JSON 파일 사용

## 주의사항

- 이 스킬은 **보고 전용**입니다. 자동으로 스크리닝이나 면접 설정을 수행하지 않습니다.
- 신규 지원자 처리는 사용자가 `/phase2-ra-resume-screening`을 직접 실행해야 합니다.
- 면접 회신 처리는 사용자가 `/phase3-ra-interview-setting`을 직접 실행해야 합니다.
