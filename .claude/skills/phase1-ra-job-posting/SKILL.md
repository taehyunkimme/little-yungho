---
name: phase1-ra-job-posting
description: BCG RA 채용 공고 작성 및 포스팅 (Phase 1). 프로젝트 정보 수집, 공고 생성, 네이버 카페/카카오톡 포스팅.
user_invocable: true
---

# RA 채용 공고 포스팅 (Phase 1)

이 스킬은 BCG RA 채용 공고를 작성하고 여러 채널에 포스팅하는 전체 워크플로우를 수행합니다.

## 워크플로우

### Step 1: 프로젝트 정보 수집

1. `data/project_settings.json` 파일이 존재하면 읽어서 기존 설정을 로드합니다.
2. 사용자에게 프로젝트 정보를 확인합니다:
   - **프로젝트 주제** (예: "국내 금융 지주사 성장 전략")
   - **근무 기간** (시작일 ~ 종료일)
   - **Application Due** (지원 마감일)
   - **지원 이메일 주소** (To, CC는 항상 Seoul.RAApplication@bcg.com)
3. 확인된 정보를 `data/project_settings.json`에 저장합니다.

### Step 2: 채용 공고 생성

1. 이 스킬의 `assets/job-posting-template.md` 파일을 읽습니다.
2. 템플릿의 placeholder를 치환합니다:
   - `{{project_topic}}` → 프로젝트 주제
   - `{{work_period}}` → 근무 기간 (예: "2026.02.27 ~ 2026.04.03")
   - `{{application_due}}` → 지원 마감일 (예: "2026.02.18")
   - `{{email_addresses}}` → 이메일 주소
3. 완성된 공고를 사용자에게 미리보기로 보여주고 확인을 받습니다.

### Step 3: 채널별 포스팅

포스팅 채널 정보는 `references/posting-channels.md`를 참조합니다.

#### 3-1. 네이버 카페 포스팅

1. `data/naver_cookies.json` 존재 여부 확인
   - 없으면: `scripts/naver_login.py`를 실행하여 네이버 로그인 세션을 저장
2. 포스팅 제목 생성: `[BCG] Research Analyst 채용 (~{마감일})`
3. `scripts/naver_cafe_writer.py`를 실행:
   ```bash
   python .claude/skills/ra-job-posting/scripts/naver_cafe_writer.py \
     --title "포스팅 제목" \
     --content "채용 공고 본문" \
     --cookie-path data/naver_cookies.json \
     --prefix "긴급"
   ```
4. 스크립트가 브라우저를 열고 글쓰기 페이지를 준비합니다. 사용자가 본문을 Cmd+V로 붙여넣고 등록해야 합니다.

#### 3-2. 카카오톡 포스팅

1. 카카오톡 단톡방에 공고를 전송합니다.
2. 기존 kakaotalk 플러그인 스킬에 위임합니다.
3. 대상 단톡방: BCG 사내 + 주요 학회 단톡방

### Step 4: 포스팅 이력 저장

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

## 주의사항

- 포스팅 전 반드시 사용자에게 공고 내용 확인을 받을 것
- 네이버 카페 포스팅은 반자동화 (브라우저 준비까지 자동, 본문 붙여넣기는 사용자)
- 카카오톡 포스팅 시 단톡방 선택을 사용자에게 확인
