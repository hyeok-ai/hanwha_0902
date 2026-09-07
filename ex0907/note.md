# 수업 내용 정리

## 1. Git 및 GitHub 기본 개념

* Git은 코드 버전을 관리하는 도구이다.
* GitHub 서버가 항상 기준이며, 서버의 코드를 최신 상태로 간주한다.
* 작업 시 기본 순서는 `pull`을 먼저 진행한 후 `push`를 해야 한다.
* 로컬 파일이 심하게 꼬였을 경우 `.git` 폴더를 삭제하여 초기화할 수 있다.

## 2. 백엔드 및 데이터 검증

* Streamlit은 데이터 시각화 및 UI 구성에 쓰이며, 데이터베이스(DB) 처리 등 백엔드 로직 구축을 위해 FastAPI를 함께 사용한다.
* Pydantic을 활용하면 복잡하고 많은 양의 데이터 입력 검증을 `if`문 없이 처리할 수 있다.

## 3. Git 실습 과정 (충돌 및 병합)

1. 로컬 레포지토리 생성 후 GitHub에 `push`
2. GitHub 웹에서 `README.md` 파일 생성
3. GitHub Desktop에서 `fetch` 및 `pull` 실행
* `fetch`: 서버의 변경 사항을 확인하는 작업
* `pull`: 서버의 변경 사항을 로컬로 가져와 합치는 작업


4. 로컬에서 `README.md` 수정 후 `push`
5. GitHub 웹에서 `README.md` 파일 수정
6. 로컬에서도 `README.md` 파일을 수정 (서버와 로컬의 파일 내용이 불일치하는 상태)
7. 로컬에서 `commit` 및 `push` 시도
8. `pull origin`을 수행하여 충돌(Merge) 발생 확인 및 내용 수정
9. `push origin`을 통해 최종 반영