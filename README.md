# Little Yungho

BCG RA(Research Analyst) 인턴 채용 프로세스를 Claude Code 스킬로 자동화하는 프로젝트입니다.

기존에 컨설턴트가 수동으로 수행하던 공고 작성, 이력서 스크리닝, 면접 일정 조율을 하나의 파이프라인으로 자동화합니다.

## 채용 파이프라인

| Phase | 스킬 | 역할 |
|-------|------|------|
| 1 | `/phase1-ra-job-posting` | 채용 공고 작성 및 포스팅 (네이버 카페, 카카오톡) |
| 2 | `/phase2-ra-resume-screening` | Gmail에서 이력서 수집, 자격 필터, 종합 평가 |
| 3 | `/phase3-ra-interview-setting` | Google Calendar 기반 면접 일정 조율 및 이메일 발송 |

`/ra-recruiting` 명령으로 전체 파이프라인을 순차 실행할 수 있으며, 각 Phase 사이에 진행 여부를 확인합니다.

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
   /ra-recruiting              # 전체 파이프라인
   /phase1-ra-job-posting       # Phase 1만 실행
   /phase2-ra-resume-screening  # Phase 2만 실행
   /phase3-ra-interview-setting # Phase 3만 실행
   ```

## 사전 요구사항

- [Claude Code](https://docs.anthropic.com/en/docs/claude-code) CLI
- Gmail MCP 플러그인 (이력서 수집 및 이메일 발송)
- Google Calendar MCP 플러그인 (면접 일정 조율)
- Python + Playwright (네이버 카페 포스팅)

## 프로젝트 구조

```
.claude/skills/
├── ra-recruiting/                  # 통합 파이프라인
├── phase1-ra-job-posting/          # 공고 포스팅
│   ├── assets/                     # 공고 템플릿
│   ├── references/                 # 포스팅 채널 정보
│   └── scripts/                    # 네이버 카페 자동화 스크립트
├── phase2-ra-resume-screening/     # 이력서 스크리닝
│   ├── assets/                     # 평가 기준
│   └── references/                 # 타겟 대학, 기업 목록
└── phase3-ra-interview-setting/    # 면접 일정 조율
```
