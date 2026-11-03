# 멜찌 카드뉴스 자동 제작 — 실행 절차

이 저장소는 멜찌(MELZZI, 일반식품 젤리) 인스타그램 카드뉴스를 만드는 도구다.
예약 작업은 아래 1단계(20:00) 또는 2단계(20:30) 중 지시받은 단계만 수행한다.
스프레드시트 ID와 탭 이름은 예약 작업 지시문에 있다. 이 저장소는 공개 저장소이므로 시트 ID 같은 비공개 정보를 커밋하지 않는다.

## 절대 규칙

- 인스타그램에 직접 게시하지 않는다. `마케터_승인` 열은 절대 TRUE로 바꾸지 않는다. 게시는 사람이 승인한 뒤 Make가 한다.
- 대본은 `prompts/script_prompt.md`를 그대로 따른다(일반식품 광고 규칙, 존댓말, 정보형은 제품·패키지 없음).
- 렌더러 규칙 검사(`--check-only`)를 통과하지 못한 대본은 고쳐서 다시 검사한다. 세 번 실패하면 `제작_상태`를 `오류`로 하고 `검수_메모`에 이유를 쓴다.
- 기존 행의 사람이 쓴 내용(캡션 수정, 메모)은 덮어쓰지 않는다. 자기 행만 고친다.

## 시트 열 (카드뉴스 탭, 1행은 머리글)

| 열 | 이름 | 누가 |
| --- | --- | --- |
| A | 콘텐츠_ID (`YYYY-MM-DD_영문-슬러그`) | 1단계 |
| B | 제작일 (`YYYY-MM-DD`) | 1단계 |
| C | 라인 (CLEAR/GLOW/CALM/BALANCE) | 1단계 |
| D | 주제 | 1단계 |
| E | 사진_프롬프트 | 1단계 |
| F | 표지사진_URL | Make |
| G | 제작_상태: 사진 대기 → 사진 완료 → 검수 대기 / 다시 만들기 / 오류 | 1단계·Make·2단계 |
| H | 이미지_URL (7개, 쉼표로 구분) | 2단계 |
| I | 인스타_피드_캡션 | 2단계 |
| J | 검수_메모 | 2단계 |
| K | 마케터_승인 (체크박스) | 사람만 |
| L | 발행_상태 | 2단계가 `대기`로 시작, 이후 Make |

## 1단계 (월·수·금 20:00) — 주제와 대본

1. `git pull`. 시트 A:D 전체와 `content/` 파일 목록을 읽어 지난 주제를 파악한다.
2. 라인은 마지막 행의 다음 순서로 돌린다: CLEAR → GLOW → CALM → BALANCE → CLEAR. 행이 없으면 CLEAR.
3. 주제를 고른다. 오늘 날짜의 계절에 맞는 뷰티·건강 생활 습관 주제, 해당 라인 멤버의 담당 주제(지침의 표) 안에서, 최근 12개 주제와 겹치지 않게. 질병 자체가 주제인 것은 피한다.
4. `prompts/script_prompt.md`와 `assets/characters/manifest.json`, `assets/props/_list.txt`를 읽고 대본 JSON을 `content/<콘텐츠_ID>.json`으로 쓴다. 표지 슬라이드에 `scene`과 `photo_prompt`를 모두 넣는다.
5. `python3 src/render.py content/<ID>.json --check-only` 통과를 확인한다.
6. 커밋하고 푸시한다: `git add content && git -c user.name="MELZZI bot" -c user.email=noreply@anthropic.com commit -m "카드뉴스 <ID> 대본" && git pull --rebase && git push`.
7. A열을 읽어 첫 빈 행 번호를 찾고, 그 행에 `update_values`로 쓴다(`append`는 서식 때문에 500행 뒤에 붙으므로 쓰지 않는다): A=ID, B=오늘, C=라인, D=주제, E=photo_prompt, F 빈칸, G=`사진 대기`, H~J 빈칸, K=FALSE, L 빈칸.

## 2단계 (월·수·금 20:30) — 렌더링과 업로드

1. `git pull`. 시트에서 G가 `사진 완료`, `사진 대기`, `다시 만들기`인 행을 찾는다. 없으면 끝낸다.
2. 각 행마다:
   - 표지 사진: `covers/<ID>.png` 또는 `covers/<ID>.jpg`가 있으면 `--cover`로 쓴다. 없으면 소품 표지로 만들고 J에 `표지 사진 없음 — 소품 표지로 제작`을 남긴다.
   - `python3 src/render.py content/<ID>.json [--cover covers/<ID>.png]`
   - `python3 src/preview.py out/<ID>`로 만든 미리보기를 직접 열어 보고, 글자 넘침·겹침·잘림이 있으면 대본을 고쳐 다시 렌더링한다.
   - `python3 src/publish.py <ID>` → 출력 JSON의 `urls`와 `caption`을 쓴다.
   - 시트 그 행: H=urls를 쉼표로 연결, I=caption, J=메모(없으면 `소품: ...` 등 짧게), G=`검수 대기`, L=`대기`.
3. 끝나면 처리한 ID 목록과 각 첫 장 URL을 짧게 보고한다.

## 도구

- `src/render.py <대본> [--cover 파일] [--check-only]` — 규칙 검사 + 1080×1350 JPEG 7장 + caption.txt (`out/<ID>/`)
- `src/preview.py out/<ID>` — 7장 한눈에 보기
- `src/publish.py <ID>` — `posts/<ID>/`로 복사, 커밋·푸시, 공개 이미지 URL 출력
- 렌더링에는 Playwright(Chromium), Jinja2, Pillow가 필요하다(클라우드 환경에 기본 설치).
