# Daily RA Status Check Implementation Plan

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** Automated daily Gmail check + Slack dashboard for RA recruiting status, toggled on/off via config file, running through GitHub Actions + claude-code-action.

**Architecture:** A Claude skill (`/daily-ra-status`) that uses Gmail Python scripts (via Bash) to detect new application emails and interview replies, then posts a formatted dashboard to Slack via incoming webhook. A GitHub Action runs at 8 AM KST on cron, checks a toggle in `data/automation_config.json`, and invokes the skill via `anthropics/claude-code-action@v1` only when active.

**Tech Stack:** Claude Code skill (SKILL.md), GitHub Actions (YAML), Gmail MCP Python scripts, Slack Incoming Webhook (curl), JSON config files.

---

### Task 1: Create Automation Config File

**Files:**
- Create: `data/automation_config.json`

**Step 1: Create the config file**

```json
{
  "daily_status_active": false,
  "last_checked_at": null,
  "slack_webhook_url": "",
  "slack_channel": "ra-recruiting"
}
```

- `daily_status_active`: on/off toggle. GitHub Action checks this before invoking Claude.
- `last_checked_at`: ISO 8601 timestamp of last successful check. `null` means first run (will default to 7 days ago).
- `slack_webhook_url`: Populated after Slack app setup (Task 2). Empty string locally; in CI it's overridden by `SLACK_WEBHOOK_URL` secret.
- `slack_channel`: For display/reference only.

**Step 2: Verify JSON is valid**

Run: `python3 -c "import json; json.load(open('data/automation_config.json'))"`
Expected: No output (success)

**Step 3: Commit**

```bash
git add data/automation_config.json
git commit -m "feat: add automation config for daily status check"
```

---

### Task 2: Slack Channel + Webhook Setup (User Manual Steps)

This task requires the user to perform manual steps. Present these instructions and confirm completion.

**Step 1: Create `#ra-recruiting` channel in GrabPack workspace**

1. Open Slack > GrabPack workspace
2. Click "+" next to Channels > "Create a new channel"
3. Name: `ra-recruiting`
4. Purpose: "RA 채용 프로세스 자동화 업데이트"

**Step 2: Create Slack App with Incoming Webhook**

1. Go to https://api.slack.com/apps
2. Click "Create New App" > "From scratch"
3. App Name: `Little Yungho Bot`
4. Workspace: GrabPack
5. Go to "Incoming Webhooks" > Toggle ON
6. Click "Add New Webhook to Workspace"
7. Select `#ra-recruiting` channel > Allow
8. Copy the Webhook URL (format: `https://hooks.slack.com/services/T.../B.../...`)

**Step 3: Save webhook URL to local config**

Update `data/automation_config.json` — set `slack_webhook_url` to the copied URL.

**Step 4: Test the webhook**

Run:
```bash
curl -X POST -H 'Content-type: application/json' \
  --data '{"text":"Little Yungho Bot 연결 테스트 :white_check_mark:"}' \
  "YOUR_WEBHOOK_URL_HERE"
```
Expected: `ok` response, message appears in `#ra-recruiting`

---

### Task 3: Write the Daily RA Status Skill

**Files:**
- Create: `.claude/skills/daily-ra-status/SKILL.md`

**Step 1: Create skill directory**

```bash
mkdir -p .claude/skills/daily-ra-status
```

**Step 2: Write the skill file**

Create `.claude/skills/daily-ra-status/SKILL.md`:

````markdown
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
````

**Step 3: Verify skill is recognized**

Run: `ls -la .claude/skills/daily-ra-status/SKILL.md`
Expected: File exists with content

**Step 4: Commit**

```bash
git add .claude/skills/daily-ra-status/SKILL.md
git commit -m "feat: add daily-ra-status skill for automated Gmail/Slack updates"
```

---

### Task 4: Write the GitHub Action Workflow

**Files:**
- Create: `.github/workflows/daily-ra-status.yml`

**Step 1: Create workflows directory**

```bash
mkdir -p .github/workflows
```

**Step 2: Write the workflow file**

Create `.github/workflows/daily-ra-status.yml`:

```yaml
name: Daily RA Status Check

on:
  schedule:
    # 23:00 UTC = 08:00 KST (next day)
    - cron: '0 23 * * *'
  workflow_dispatch: {}  # Manual trigger for testing

jobs:
  check-status:
    runs-on: ubuntu-latest
    steps:
      - name: Checkout repository
        uses: actions/checkout@v4

      - name: Check if automation is active
        id: check-toggle
        run: |
          if [ ! -f data/automation_config.json ]; then
            echo "Config file not found, skipping"
            echo "active=false" >> $GITHUB_OUTPUT
            exit 0
          fi
          ACTIVE=$(python3 -c "import json; print(json.load(open('data/automation_config.json'))['daily_status_active'])")
          echo "active=$ACTIVE" >> $GITHUB_OUTPUT
          echo "Automation active: $ACTIVE"

      - name: Setup Gmail credentials
        if: steps.check-toggle.outputs.active == 'True'
        run: |
          GMAIL_ACCOUNTS_DIR="$HOME/.claude/plugins/marketplaces/team-attention-plugins/plugins/gmail/skills/gmail/accounts"
          mkdir -p "$GMAIL_ACCOUNTS_DIR"
          echo '${{ secrets.GMAIL_OAUTH_TOKEN }}' > "$GMAIL_ACCOUNTS_DIR/personal.json"

          GMAIL_REFS_DIR="$HOME/.claude/plugins/marketplaces/team-attention-plugins/plugins/gmail/skills/gmail/references"
          mkdir -p "$GMAIL_REFS_DIR"
          echo '${{ secrets.GMAIL_CREDENTIALS }}' > "$GMAIL_REFS_DIR/credentials.json"

      - name: Run daily status check
        if: steps.check-toggle.outputs.active == 'True'
        uses: anthropics/claude-code-action@v1
        with:
          anthropic_api_key: ${{ secrets.ANTHROPIC_API_KEY }}
          prompt: |
            Run the /daily-ra-status skill.
            Use SLACK_WEBHOOK_URL environment variable for the Slack webhook.
            Gmail account is "personal".
            Do NOT ask any questions - just execute the skill autonomously and post the update.
        env:
          SLACK_WEBHOOK_URL: ${{ secrets.SLACK_WEBHOOK_URL }}
```

**Step 3: Verify YAML syntax**

Run: `python3 -c "import yaml; yaml.safe_load(open('.github/workflows/daily-ra-status.yml'))"`
Expected: No output (success). If `yaml` not available, run: `python3 -c "import json; print('YAML file created')"` and manually verify structure.

**Step 4: Commit**

```bash
git add .github/workflows/daily-ra-status.yml
git commit -m "feat: add GitHub Action for daily RA status check (8AM KST cron)"
```

---

### Task 5: Update CLAUDE.md

**Files:**
- Modify: `CLAUDE.md`

**Step 1: Add daily-ra-status to the pipeline table**

Add a new row to the RA 선발 파이프라인 table in CLAUDE.md:

```markdown
## RA 선발 파이프라인 (3 Phase) + 자동화

전체 프로세스는 3개 Claude Skill로 구성되며, `/스킬명` 명령으로 각 Phase를 실행:

| Phase | 스킬 | 역할 |
|-------|------|------|
| 1 | `/phase1-ra-job-posting` | 채용 공고 작성 및 포스팅 (네이버 카페, 카카오톡) |
| 2 | `/phase2-ra-resume-screening` | 이력서 수집, 자격 필터, 종합 평가 |
| 3 | `/phase3-ra-interview-setting` | 면접 대상자 일정 조율 |
| Auto | `/daily-ra-status` | 일일 Gmail 체크 + Slack 현황 대시보드 (GitHub Actions 자동화) |
```

**Step 2: Add automation_config.json to data directory schema**

Add to the 데이터 디렉토리 스키마 table:

```markdown
| `automation_config.json` | 일일 자동 체크 설정 (on/off 토글, 마지막 체크 시간) | Auto |
```

**Step 3: Add Slack webhook to 외부 의존성 table**

```markdown
| Slack 대시보드 | Incoming Webhook (`#ra-recruiting` 채널) |
```

**Step 4: Commit**

```bash
git add CLAUDE.md
git commit -m "docs: add daily-ra-status skill to CLAUDE.md pipeline docs"
```

---

### Task 6: Setup GitHub Secrets (User Manual Steps)

Present these instructions to the user and confirm completion.

**Required GitHub Secrets:**

| Secret Name | Value | How to Get |
|-------------|-------|------------|
| `ANTHROPIC_API_KEY` | Anthropic API key | https://console.anthropic.com/settings/keys |
| `SLACK_WEBHOOK_URL` | Slack Incoming Webhook URL | From Task 2 Step 2 |
| `GMAIL_OAUTH_TOKEN` | Contents of Gmail `accounts/personal.json` | `cat ~/.claude/plugins/marketplaces/team-attention-plugins/plugins/gmail/skills/gmail/accounts/personal.json` |
| `GMAIL_CREDENTIALS` | Contents of Gmail `references/credentials.json` | `cat ~/.claude/plugins/marketplaces/team-attention-plugins/plugins/gmail/skills/gmail/references/credentials.json` |

**Steps:**
1. Go to GitHub repo > Settings > Secrets and variables > Actions
2. Click "New repository secret" for each secret
3. Paste the exact file contents as the value

---

### Task 7: Local Test Run

**Step 1: Enable automation**

Edit `data/automation_config.json`: set `daily_status_active` to `true`.

**Step 2: Run the skill locally**

Invoke `/daily-ra-status` in Claude Code.

**Step 3: Verify results**

- Check `#ra-recruiting` channel in Slack for the dashboard message
- Check `data/automation_config.json` — `last_checked_at` should be updated
- Verify message format matches the design spec

**Step 4: Disable automation (optional)**

Set `daily_status_active` back to `false` if not ready for daily runs.

**Step 5: Commit updated config**

```bash
git add data/automation_config.json
git commit -m "chore: update automation config after test run"
```

---

### Task 8: Final Commit and Push

**Step 1: Review all changes**

```bash
git log --oneline -5
git status
```

**Step 2: Push to remote**

```bash
git push origin master
```

After pushing, the GitHub Action will be registered. It will run daily at 8 AM KST, but only invoke Claude when `daily_status_active` is `true`.
