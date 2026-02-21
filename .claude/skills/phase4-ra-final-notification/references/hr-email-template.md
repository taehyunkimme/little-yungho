# HR 채용 요청 이메일 템플릿

형식: HTML (`--html` 플래그 사용)

## 템플릿

```
안녕하세요,
아래 요건으로 신규 RA {한/두/세} 분 신규 채용 요청드립니다.

채용할 RA 인원 : {N}명
이미 팀에서 채용한 RA 인원 : 해당 없음
Client 명 : {<span style="color:red">작성 필요</span>}
Case 명 : {<span style="color:red">작성 필요</span>}
Case code: {<span style="color:red">작성 필요</span>}
P/PL : {<span style="color:red">작성 필요</span>}
채용 RA 역할 및 적정 인원 관련 파트너와 논의 여부 (Yes or No) : Yes
근무 기간 (예 , 3/1~3/10, 90 일 미만 근무만 가능): {근무기간, 예: 2/27~4/3, 약 36일}
채용 이유 (추천/교체/신규채용/기타 ): 신규 채용
RA 업무 내용 : 인터뷰 노트 작성, 리서치 업무 등 수행 통한 프로젝트 지원
RA 2 명 이상 신청 시 (기존 채용 포함 ) 사유 기재 (OL approval 필요) : 해당 사항 없음
RA 인솔 팀원 (SA 이상 또는 근무경력2 년 이상의 컨설턴트) : 김태현 (SA, Kim.Taehyun@bcg.com)
RA생년월일: {이름(YYYY.MM.DD), 이름(YYYY.MM.DD)}
RA영문 주소(resume에 없을 시 기재): {Resume 내 포함 완료 | 확인 중 (후보자 회신 대기)}

감사합니다.
김태현 드림
```

## 치환 규칙

- `{한/두/세} 분` → 합격자 수에 따라 한 분 / 두 분 / 세 분
- `{N}명` → 합격자 수
- Client 명 / Case 명 / Case code / P/PL → `<span style="color:red">작성 필요</span>` (빨간색)
- 근무 기간 → `project_settings.json`의 `work_start ~ work_end` (예: "2/27~4/3, 약 36일")
- RA생년월일 → Resume에서 추출, 없으면 `<span style="color:red">이름(생년월일 확인 필요 — Resume 미기재)</span>`
- RA영문 주소 → Resume에 있으면 "Resume 내 포함 완료", 없으면 "확인 중 (후보자 회신 대기)"
- HTML 발송 시 줄바꿈은 `<br>` 태그로 변환
