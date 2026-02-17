# BCG RA Recruiting Process Automation: "Little Yungho"

## 프로젝트 개요

BCG RA(Research Analyst) 인턴 채용 프로세스 전체를 Claude Code 스킬 기반으로 자동화하는 프로젝트.
기존의 파편화된 Tool들을 이용해 A/C들이 수동으로 하던 RA 채용 작업 전체를 자동화하는 것을 목표로 함.

## 사용자 프로필

- BCG에서 컨설턴트로 3년차 근무 중
- 기술적 구현보다 목적 기반 문제 해결 및 의사결정 효과에 초점을 둠

## 소통 방식

- 언어: 한국어로 소통
- 질문을 최대한 온전하게 이해한 후 응답할 것
- 추가 정보가 필요하면 적극적으로 AskUserQuestion을 활용하여 명확히 할 것
- 추측으로 진행하지 말고, 불확실한 부분은 반드시 확인 후 진행
- 전략 컨설팅의 맥락을 이해하고, 자동화를 통한 업무 시간 감소의 관점에서 소통할 것

## RA 선발 파이프라인 (3 Phase)

전체 프로세스는 3개 Claude Skill로 구성되며, `/스킬명` 명령으로 각 Phase를 실행:

| Phase | 스킬 | 역할 |
|-------|------|------|
| 1 | `/phase1-ra-job-posting` | 채용 공고 작성 및 포스팅 (네이버 카페, 카카오톡) |
| 2 | `/phase2-ra-resume-screening` | 이력서 수집, 자격 필터, 종합 평가 |
| 3 | `/phase3-ra-interview-setting` | 면접 대상자 일정 조율 |

## 데이터 디렉토리 스키마 (`data/`)

| 파일 | 설명 | 생성 Phase |
|------|------|-----------|
| `project_settings.json` | 프로젝트 기본 정보 (주제, 기간, 마감일, 이메일) | Phase 1 |
| `posting_history.json` | 포스팅 이력 로그 | Phase 1 |
| `screening_results.json` | 이력서 스크리닝 결과 | Phase 2 |
| `assignment_results.json` | 과제 평가 결과 | Phase 3 |
| `interview_schedule.json` | 면접 일정 | Phase 4 |
| `naver_cookies.json` | 네이버 로그인 세션 쿠키 (gitignored) | Phase 1 |
| `resumes/` | 다운로드된 이력서 PDF (gitignored) | Phase 2 |

### `project_settings.json` 스키마

```json
{
  "project_topic": "프로젝트 주제",
  "application_due": "YYYY-MM-DD",
  "work_start": "YYYY-MM-DD",
  "work_end": "YYYY-MM-DD",
  "email_addresses": "[이메일1], [이메일2]"
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
| 데이터 저장 | JSON 파일 (Read/Write 도구) |

## 작업 규칙

- 사용자(컨설턴트)의 최종 확인이 필요한 의사결정 포인트를 명시할 것
- 과도한 엔지니어링을 피하고, 현재 필요한 기능에 집중할 것
- 보안: 개인정보(이력서, 이메일) 처리 시 민감 데이터 관리에 주의
- Phase 간 데이터는 `data/` 디렉토리의 JSON 파일로 연계
