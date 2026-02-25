# 📝 Project Specification: AI-Powered IT Newsroom (RSS & Gemini)

## 1. 개요 (Overview)
본 프로젝트는 국내 IT 뉴스 RSS 피드를 수집하여 **Gemini 1.5 Flash** 모델로 분석하고, 날짜별로 '1장짜리 IT 보고서'를 생성하는 웹 서비스입니다. 별도의 데이터베이스 없이 **GitHub Repository를 JSON 저장소**로 활용하며, **Streamlit Cloud**를 통해 배포합니다.

## 2. 기술 스택 (Tech Stack)
- **Language:** Python 3.10+
- **Framework:** Streamlit
- **AI Model:** Google Gemini 1.5 Flash (via `google-generativeai`)
- **Data Storage:** GitHub Repository (JSON files via `PyGithub`)
- **RSS Parser:** `feedparser`
- **Deployment:** Streamlit Cloud

## 3. 환경 변수 설정 (Secrets)
Streamlit Cloud의 `Secrets` 항목에 다음 정보가 설정되어야 합니다:
- `GEMINI_API_KEY`: 구글 AI 스튜디오 API 키
- `GITHUB_TOKEN`: GitHub Personal Access Token (Repo 권한 필요)
- `REPO_NAME`: 데이터가 저장될 리포지토리명 (예: `username/my-newsroom-data`)
- `ADMIN_PASSWORD`: 관리자 페이지 접속용 비밀번호

## 4. 파일 구조 (File Structure)
```text
/
├── app.py                # 메인 진입점 및 내비게이션
├── github_storage.py     # GitHub API 연동 (JSON CRUD 로직)
├── views/
│   ├── main_page.py      # 사용자 화면 (날짜별 브리핑 출력)
│   └── admin_page.py     # 관리자 화면 (RSS 관리, AI 분석, 통계)
├── requirements.txt      # 의존성 라이브러리 목록
└── data/ (GitHub 리포지토리에 생성될 폴더)
    ├── feeds.json        # 등록된 RSS URL 목록
    ├── reports.json      # 날짜별 AI 분석 결과 데이터
    └── stats.json        # 접속자 통계 데이터
```

## 5. 상세 기능 요구사항 (Requirements)

### A. 데이터 저장 로직 (`github_storage.py`)
- `PyGithub`를 사용하여 GitHub 리포지토리 내의 JSON 파일을 직접 읽고 쓰기.
- 파일이 없을 경우 에러 처리 및 초기 빈 데이터 생성 기능.

### B. 관리자 대시보드 (`views/admin_page.py`)
1.  **RSS 피드 관리:**
    - RSS URL 추가/삭제 기능.
    - `feeds.json`에 영구 저장.
2.  **수집 및 AI 분석 (핵심):**
    - 버튼 클릭 시 등록된 모든 RSS에서 **최근 3일치** 게시물만 필터링.
    - 수집된 기사(제목, 요약, 링크)를 Gemini 1.5 Flash에 전달.
    - **Prompt 지침:** "토픽별 그룹화, 핵심 내용 요약, 기사 원문 링크 포함, A4 1장 분량의 마크다운 형식".
    - 분석 결과를 `reports.json`에 `{"YYYY-MM-DD": "Markdown Content"}` 형태로 저장.
3.  **접속 통계:**
    - `stats.json`에 기록된 일별 방문자 수를 차트로 시각화.

### C. 메인 뉴스룸 화면 (`views/main_page.py`)
- `reports.json`에서 데이터를 불러와 최신 날짜의 보고서를 첫 화면에 노출.
- 사이드바 내비게이션을 통해 과거 날짜 선택 가능.
- 마크다운 렌더링을 통해 깔끔한 뉴스레터 형식 유지.

### D. 접속자 통계 로직
- 사용자가 `app.py`에 접속할 때마다 `stats.json`의 전체 카운트 및 해당 날짜 카운트를 +1 업데이트.

## 6. Antigravity 에이전트 수행 지침 (Agent Instructions)
1.  **Step 1:** `requirements.txt`를 생성하고 필요한 라이브러리를 설치하라.
2.  **Step 2:** `github_storage.py`를 구현하여 GitHub API를 통한 JSON 지속성(Persistence)을 확보하라.
3.  **Step 3:** `admin_page.py`에서 `feedparser`와 `Gemini-1.5-Flash`를 연동하여 뉴스 분석 로직을 완성하라.
4.  **Step 4:** `app.py`에서 `streamlit`의 `option_menu` 또는 `sidebar.radio`를 사용하여 메인 화면과 관리자 화면을 분리하라.
5.  **Step 5:** 모든 UI는 다크 모드와 라이트 모드에서 가독성이 좋도록 마크다운 스타일을 지정하라.

---

### Antigravity를 위한 실행 프롬프트:
> "위 명세서를 기반으로 파이썬 코드를 작성해줘. 특히 DB 대신 GitHub 리포지토리를 JSON 저장소로 쓰는 `github_storage.py` 구현에 신경 써주고, Gemini 1.5 Flash API를 써서 RSS 뉴스들을 주제별로 멋지게 요약하는 관리자 기능을 만들어줘."