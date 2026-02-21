# Little Yungho

BCG RA(Research Analyst) 인턴 채용 프로세스를 Claude Code 스킬로 자동화하는 프로젝트입니다.

기존에 컨설턴트가 수동으로 수행하던 프로젝트 설정, 공고 작성, 이력서 스크리닝, 면접 일정 조율, 최종 합격 통보를 하나의 파이프라인으로 자동화합니다.

## 채용 파이프라인

| Phase | 스킬 | 역할 |
|-------|------|------|
| 0 | `/phase0-ra-project-setup` | 프로젝트 초기 설정 (주제, 기간, 케이스 정보, 채용 인원) |
| 1 | `/phase1-ra-job-posting` | 채용 공고 작성 및 포스팅 (네이버 카페, 카카오톡) |
| 2 | `/phase2-ra-resume-screening` | Gmail에서 이력서 수집, 자격 필터, 종합 평가 |
| 3 | `/phase3-ra-interview-setting` | Google Calendar 기반 면접 일정 조율 및 이메일 발송 |
| 4 | `/phase4-ra-final-notification` | 최종 합격자 HR 채용 요청 및 파트너 승인 이메일 작성 |
| Auto | `/daily-ra-status` | 일일 Gmail 체크 + Slack 현황 대시보드 (GitHub Actions 자동화) |

`/ra-recruiting` 명령으로 Phase 0~4 전체 파이프라인을 순차 실행할 수 있으며, 각 Phase 사이에 진행 여부를 확인합니다.

## 사용 방법

1. 리포지토리를 클론합니다:
   ```bash
   git clone https://github.com/taehyunkimme/little-yungho.git
   ```

2. 해당 디렉토리에서 Claude Code를 실행합니다:
   ```bash
   cd little-yungho
   claude
   ```

3. 전체 프로세스 실행 또는 개별 Phase 실행:
   ```
   /ra-recruiting                # 전체 파이프라인 (Phase 0~4)
   /phase0-ra-project-setup      # Phase 0: 프로젝트 초기 설정
   /phase1-ra-job-posting        # Phase 1: 채용 공고 포스팅
   /phase2-ra-resume-screening   # Phase 2: 이력서 스크리닝
   /phase3-ra-interview-setting  # Phase 3: 면접 일정 조율
   /phase4-ra-final-notification # Phase 4: 최종 합격 통보
   /daily-ra-status              # 일일 현황 체크 (수동 실행)
   ```

## 일일 자동화

GitHub Actions가 매일 오전 8시(KST)에 `/daily-ra-status`를 자동 실행하여:
- Gmail에서 신규 지원 이메일 및 면접 회신을 확인
- 합격자 누락 정보(생년월일, 영문주소) 회신 여부를 체크
- Slack `#ra-recruiting` 채널에 현황 대시보드를 전송

`data/automation_config.json`의 `daily_status_active`로 on/off 제어.

## 사전 요구사항

- [Claude Code](https://docs.anthropic.com/en/docs/claude-code) CLI
- Gmail MCP 플러그인 (이력서 수집 및 이메일 발송)
- Google Calendar MCP 플러그인 (면접 일정 조율)
- Python + Playwright (네이버 카페 포스팅)
- Slack Incoming Webhook (일일 현황 대시보드)
- GitHub Actions Secrets: `ANTHROPIC_API_KEY`, `SLACK_WEBHOOK_URL`, `GMAIL_OAUTH_TOKEN`, `GMAIL_CREDENTIALS`

## 프로젝트 구조

```
.claude/skills/
├── ra-recruiting/                     # 통합 파이프라인 (Phase 0~4 순차 실행)
├── phase0-ra-project-setup/           # 프로젝트 초기 설정
├── phase1-ra-job-posting/             # 공고 포스팅
│   ├── assets/                        # 공고 템플릿
│   ├── references/                    # 포스팅 채널 정보
│   └── scripts/                       # 네이버 카페 자동화 스크립트
├── phase2-ra-resume-screening/        # 이력서 스크리닝
│   ├── assets/                        # 평가 기준
│   └── references/                    # 타겟 대학, 기업 목록
├── phase3-ra-interview-setting/       # 면접 일정 조율
├── phase4-ra-final-notification/      # 최종 합격 통보
│   └── references/                    # HR/파트너 이메일 템플릿
└── daily-ra-status/                   # 일일 자동 현황 체크

.github/workflows/
└── daily-ra-status.yml                # 매일 08:00 KST 자동 실행

data/
├── project_settings.json              # 프로젝트/케이스 설정 (Phase 0)
├── posting_history.json               # 포스팅 이력 (Phase 1)
├── screening_results.json             # 스크리닝 결과 (Phase 2)
├── interview_schedule.json            # 면접 일정 (Phase 3)
├── final_notification.json            # 합격 통보 상태 (Phase 4)
├── automation_config.json             # 자동화 설정 (on/off)
├── naver_cookies.json                 # 네이버 세션 (gitignored)
└── resumes/                           # 이력서 PDF (gitignored)
```
