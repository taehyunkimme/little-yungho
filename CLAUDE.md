# BCG RA Recruiting Process Automation: "Little Yungho"

## 프로젝트 개요

BCG RA(Research Analyst) 인턴 채용 프로세스 전체를 Claude Code 스킬 기반으로 자동화하는 프로젝트.
기존의 파편화된 Tool들을 이용해 A/C들이 수동으로 하던 RA 채용 작업 전체를 자동화하는 것을 목표로 함.

## 사용자 프로필

- BCG에서 컨설턴트로 3년차 근무 중
- 기술적 구현보다 목적 기반 문제 해결 및 의사결정 효과에 초점을 둠

## Communication Style

- Language: English
- Fully understand the question before responding
- Actively use AskUserQuestion to clarify when additional information is needed
- Do not proceed with assumptions — always confirm uncertainties
- Understand the strategic consulting context; communicate from the perspective of reducing manual work through automation
- Skill content remains in Korean

## RA 선발 파이프라인 (5 Phase) + 자동화

전체 프로세스는 5개 Phase와 자동화 스킬로 구성되며, `/스킬명` 명령으로 각 Phase를 실행.
`/ra-recruiting`으로 Phase 0~4를 순차 실행할 수 있음:

| Phase | 스킬 | 역할 |
|-------|------|------|
| 0 | `/phase0-ra-project-setup` | 프로젝트 초기 설정 (주제, 기간, 케이스 정보, 채용 인원) |
| 1 | `/phase1-ra-job-posting` | 채용 공고 작성 및 포스팅 (네이버 카페, 카카오톡) |
| 2 | `/phase2-ra-resume-screening` | 이력서 수집, 자격 필터, 종합 평가 |
| 3 | `/phase3-ra-interview-setting` | 면접 대상자 일정 조율 |
| 4 | `/phase4-ra-final-notification` | 최종 합격자 HR 채용 요청 및 파트너 승인 이메일 작성 |
| Auto | `/daily-ra-status` | 일일 Gmail 체크 + Slack 현황 대시보드 (GitHub Actions 자동화) |

## 데이터 디렉토리 스키마 (`data/`)

| 파일 | 설명 | 생성 Phase |
|------|------|-----------|
| `project_settings.json` | 프로젝트 기본 정보 (주제, 기간, 마감일, 이메일) + 케이스 정보 (Client, Case, P/PL) + 채용 인원 | Phase 0 |
| `posting_history.json` | 포스팅 이력 로그 | Phase 1 |
| `screening_results.json` | 이력서 스크리닝 결과 | Phase 2 |
| `assignment_results.json` | 과제 평가 결과 | Phase 3 |
| `interview_schedule.json` | 면접 일정 | Phase 3 |
| `final_notification.json` | 최종 합격 통보 상태 및 후보자 정보 | Phase 4 |
| `automation_config.json` | 일일 자동 체크 설정 (on/off 토글, 마지막 체크 시간) | Auto |
| `naver_cookies.json` | 네이버 로그인 세션 쿠키 (gitignored) | Phase 1 |
| `resumes/` | 다운로드된 이력서 PDF (gitignored) | Phase 2 |

### `project_settings.json` 스키마

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

## 외부 의존성

| 기능 | 처리 방식 |
|------|----------|
| Gmail 검색/발송 | gmail MCP 플러그인 스킬 활용 |
| KakaoTalk 발송 | kakaotalk MCP 플러그인 스킬 활용 |
| 네이버 카페 포스팅 | Playwright 스크립트 (`scripts/naver_cafe_writer.py`) |
| 이력서 평가 | Claude가 직접 수행 (외부 API 불필요) |
| PDF 읽기 | Claude Code Read 도구 활용 |
| Slack 대시보드 | Incoming Webhook (`#ra-recruiting` 채널) |
| 데이터 저장 | JSON 파일 (Read/Write 도구) |

## 작업 규칙

- 사용자(컨설턴트)의 최종 확인이 필요한 의사결정 포인트를 명시할 것
- 과도한 엔지니어링을 피하고, 현재 필요한 기능에 집중할 것
- 보안: 개인정보(이력서, 이메일) 처리 시 민감 데이터 관리에 주의
- Phase 간 데이터는 `data/` 디렉토리의 JSON 파일로 연계
