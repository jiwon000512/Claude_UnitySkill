---
name: unity-project-setup
description: 유니티 모바일 게임 프로젝트의 초기 세팅을 정해진 순서로 진행한다. 템플릿으로 생성한 Unity 프로젝트를 정리할 때(git 초기화, Assets 폴더 구조와 .meta, 불필요 패키지 제거, 세로 고정, CLAUDE.md/.gitignore/.editorconfig, JSON 데이터 테이블 규칙) 사용. "새 유니티 프로젝트 세팅", "프로젝트 기반 세팅", "초기 세팅", "데이터 테이블 규칙 정하자" 같은 요청에 호출한다. 동물원 타이쿤(2026-09)에서 정한 방식을 기본값으로 쓴다.
---

# Unity 프로젝트 초기 세팅

동물원 타이쿤(2026-09, jiwon000512/IdleTycoon)에서 정한 방식을 다음 프로젝트에 그대로 적용하는 절차. **이 폴더가 원본**이다. 배경 설명·상세 절차·주의점은 `reference.md`(필요할 때만 읽음), 파일 템플릿은 `templates/`, 자동화는 `scripts/`.

세팅 방식이 바뀌면 이 폴더를 고치고 커밋한다. 게임 저장소에는 그 프로젝트가 고른 값만 CLAUDE.md에 남기고, 가이드를 복제하지 않는다.

## 진행 원칙

- 결정이 필요한 항목은 **AskUserQuestion으로 하나씩** 묻는다. 한 번에 여러 질문을 묶지 않는다. 첫 선택지는 항상 기본값(Recommended).
- 결정이 끝난 항목부터 바로 실행한다. 질문과 무관한 작업(현황 파악 등)은 먼저 한다.
- 식별자는 영어, 문서·주석·커밋 메시지는 한국어.
- 커밋은 사용자가 git 초기화를 선택했을 때 초기 커밋 1회만. 이후 커밋은 요청 시에만.
- 긴 한국어 문서는 bash 히어독 대신 Write 도구나 Python으로 쓴다(따옴표 처리 실패 방지).

## 0. 현황 파악 (질문 전에 먼저)

```bash
cat <Unity>/ProjectSettings/ProjectVersion.txt
cat <Unity>/Packages/manifest.json
find <Unity>/Assets -type f
grep -E "productName|companyName|defaultScreenOrientation|applicationIdentifier" -A1 <Unity>/ProjectSettings/ProjectSettings.asset
git --version; which unity; tasklist | grep -i "^Unity.exe"
```

기획 폴더의 기획서를 읽고 장르·화면 방향·데이터 규모를 파악한다. 에디터가 열려 있는지 기록해 둔다(5장에서 반영 방법이 달라짐).

## 1. 질문 순서

각 질문은 아래 표의 선택지로 낸다. 사용자가 이미 말한 항목은 건너뛴다.

| # | 질문 | 선택지 (① = 기본값) |
|---|---|---|
| 1 | 이번 세션에서 가장 먼저 만들 것은? | ① 프로젝트 기반 세팅 ② 코어 로직 + 임시 UI 수직 슬라이스 ③ 코어 로직만 ④ 기획 미결 항목 마무리 |
| 2 | git 저장소는? | ① 루트에 하나(기획 + 유니티) ② 유니티 폴더에만 ③ 루트 + GitHub 원격 바로 생성 ④ 이번엔 안 함 |
| 3 | Assets 폴더 구조와 코드 계층은? | ① Assets 바로 아래 종류별 + asmdef 6개로 계층 강제(Core/Data/Game/UI/Editor/Tests) ② 종류별 + asmdef 2개(순수 C#/Unity) ③ 종류별, asmdef 없음 |
| 4 | UI 시스템은? | ① uGUI + TextMeshPro ② UI Toolkit |
| 5 | 제품명·회사명·패키지 ID는? | ① 템플릿 기본값 유지 ② 임시값 지정 ③ 직접 입력 |
| 6 | 불필요 패키지는? | ① 제거 ② 그대로 둠 ③ 제거 + TMP Essentials 임포트 |
| 7 | 데이터 테이블 원본·로드는? | ① JSON 단일 원본, 런타임 직접 로드 ② JSON + 에디터에서 SO 변환 ③ ScriptableObject만 |
| 8 | JSON 파서는? | ① Newtonsoft.Json ② JsonUtility ③ System.Text.Json(비권장) |
| 9 | JSON 파일 구성은? | ① 테이블당 1개 ② 전체 1파일 ③ 항목당 1파일 |
| 10 | JSON에서 에셋 참조는? | ① ID 기반 경로 + Resources.Load ② JSON에 경로 필드 ③ Addressables |
| 11 | 데이터 작업 범위는? | ① 규칙 문서 + JSON ② + Core 모델·로더·검증·테스트 ③ 규칙 문서만 |
| 12 | UI 패턴은? | ① MVP(View MonoBehaviour + Presenter 순수 C#) ② MVVM + R3 ③ View가 모델 직접 구독 |
| 13 | 의존성 주입은? | ① 수동 컴포지션 루트 + 생성자 주입 ② VContainer ③ SO 서비스 로케이터 |
| 14 | 이벤트·비동기는? | ① 순수 C# event + 동기 틱 ② C# event + UniTask ③ R3 |
| 15 | 공통 기반(GameKit) 접근 방식은? | ① MonoSingleton<T> Manager(lazy 자기 초기화, Game·UI 계층만 접근) ② 컴포지션 루트 주입만 ③ 제한된 서비스 로케이터 |
| 16 | 오류 전달은? | ① 예상된 실패는 Result/TryXxx, 버그는 예외 ② 예외 중심 ③ bool + 로그 |
| 17 | private 필드 접두어는? | ① m_ (static s_, const k_; Unity 6판 예시 권장) ② _ ③ 없음 |
| 18 | 중괄호는? | ① Allman(새 줄) ② K&R(같은 줄, Unity 예시) |
| 19 | 이벤트 핸들러 이름은? | ① Subject_EventName(Unity 예시) ② HandleEventName ③ OnEventName |

질문하지 않고 기본 적용: 세로 고정(기획서가 가로면 가로), 기준 해상도 1080×1920, 스타일(`_camelCase`, 중괄호 새 줄, 4칸), 커밋 정책. 7~11은 데이터 테이블 작업에 들어갈 때, 12~19는 코드 규칙·프로그래밍 규약을 정할 때(첫 코드 작성 전) 묻는다. 프로그래밍 규약의 기준은 Unity 6판 C# 스타일 가이드(unity.com/kr/resources/c-sharp-style-guide-unity-6, 예시 저장소 thomasjacobsen-unity/Unity-Code-Style-Guide)이며, 가이드가 팀 선택으로 남긴 것만 묻는다.

## 2. 기반 세팅 실행 (질문 1~6 뒤)

`scripts/setup_unity_project.py`가 폴더·.meta·씬 이름·패키지·세로 고정을 한 번에 처리한다.

```bash
python ~/.claude/skills/unity-project-setup/scripts/setup_unity_project.py \
  --root <저장소 루트> --unity-dir <유니티 폴더 이름> \
  [--landscape] [--keep-packages] [--scene-name Main] [--add-newtonsoft]
```

스크립트가 하는 일: `Assets/{Scenes,Scripts/{Core,Data,Game,UI,Editor},Resources/{Data,Sprites},Prefabs/UI,Sprites/UI,Fonts,Audio,Tests/EditMode}` 생성 + 폴더 .meta + 잎 폴더 .gitkeep, `--asmdef <Namespace>`로 asmdef 6개(Core·Data는 noEngineReferences, Data는 Newtonsoft.Json.dll 참조, Game/UI는 UnityEngine.UI·Unity.InputSystem·Unity.TextMeshPro 참조, Tests는 TestRunner) 생성, `SampleScene`→`Main` 이름 변경(guid 유지, EditorBuildSettings 반영), manifest에서 제거 목록 삭제 + `packages-lock.json` 삭제, ProjectSettings 화면 방향, 루트에 `.gitignore`(접두어 치환)·`.gitattributes`·`.editorconfig` 복사.

수동으로 할 것:
1. `templates/CLAUDE.md.template`을 채워 루트 `CLAUDE.md` 작성. `{{GAME_NAME}}`, `{{UNITY_DIR}}`, `{{UNITY_VERSION}}`, `{{PLAN_DOC}}` 치환, 기술 결정 표를 답변대로 고침.
2. git 선택 시 `git init -b main && git add -A && git status --short`로 Library/Temp/Logs/UserSettings/*.csproj/*.slnx가 빠졌는지 확인 후 초기 커밋. `git ls-files | grep -c '^<Unity>/Library/'`가 0.
3. 질문 5에서 값을 정했으면 `ProjectSettings.asset`의 `productName`, `companyName`, `applicationIdentifier`를 고친다.
4. GitHub 저장소를 사용자가 웹에서 먼저 만들었으면: `git remote add origin <url>` → `git fetch origin` → `git rebase -X theirs origin/main`(원격 Initial commit의 .gitignore 대신 우리 것 유지; 미커밋 변경은 stash) → `git push -u origin main`. CLAUDE.md에 원격 주소를 한 줄 적는다.

### 제거 패키지 목록(기본)

`com.unity.visualscripting`, `com.unity.timeline`, `com.unity.multiplayer.center`, `com.unity.2d.animation`, `com.unity.2d.spriteshape`, `com.unity.2d.aseprite`, `com.unity.2d.psdimporter`, `com.unity.2d.tilemap.extras`.
**유지**: `com.unity.pipeline`(Unity CLI 연결용, 렌더 파이프라인 아님), `com.unity.modules.*`(URP 의존, 빌드 시 스트리핑).

## 3. 데이터 테이블 (질문 7~11 뒤, 기본값 기준)

1. `templates/data-table-rules.md`를 `기획/데이터-테이블-규칙.md`로 복사하고 `<...>` 자리와 8장 스키마 표를 게임 테이블로 채운다.
2. `Assets/Resources/Data/<table>.json`을 테이블당 하나 만든다. 구조는 `{"table": "<파일명>", "version": 1, "notes": [...], "rows": [...]}`. 상수 묶음(`game_config.json`)은 `rows` 대신 섹션 객체. 기획서의 미결 항목은 가정값을 넣고 `notes`에 "기획서 n장 미결"로 표시.
3. 기획서 구현 메모의 데이터 문구를 JSON 기준으로 고치고 기획서 버전 +0.1, 변경 이력 추가. CLAUDE.md의 데이터 행·폴더 트리도 맞춘다.
4. ID 기반 로드용 스프라이트 폴더는 `Assets/Resources/Sprites/<종류>/` (Resources 밖이면 `Resources.Load` 불가).
5. Newtonsoft 선택 시 manifest에 `com.unity.nuget.newtonsoft-json`을 직접 의존으로 추가(버전은 `Library/PackageCache` 것과 맞춤). 스크립트의 `--add-newtonsoft`.
6. 범위 ②면 Core에 레코드·로더·검증기, `Tests/EditMode`에 규칙 문서 7장의 검증 테스트.

## 3-1. 코드 규칙 (질문 12~14 뒤, 첫 코드 작성 전)

1. `templates/code-rules.md`를 `기획/코드-규칙.md`로 복사하고 `{{NAMESPACE}}`와 8장 클래스 지도를 채운다. 계층 강제(asmdef)·MVP·수동 DI·C# event가 기본값이며, 답이 다르면 1장 결정 표와 해당 절만 고친다.
2. asmdef가 아직 없으면 `scripts/setup_unity_project.py --asmdef <Namespace>`로 생성(에디터가 열려 있으면 `unity command write_text_file`로 써도 된다). Newtonsoft는 `unity command package_add --identifier com.unity.nuget.newtonsoft-json@<ver> --confirm true --wait true`.
3. `templates/programming-conventions.md`를 `기획/프로그래밍-규약.md`로 복사하고 1장 결정 표를 답변(15~19)대로 고친다. `.editorconfig`는 `templates/editorconfig`(m_/s_/k_·Allman 기준)를 쓰고, 답이 다르면 접두어·중괄호 항목만 바꾼다.
4. CLAUDE.md 「코드 규칙」절은 핵심 금지·필수 항목 5~6줄과 두 문서 링크만 둔다. 문서 전문을 복제하지 않는다.
5. 공통 기반은 GameKit UPM 패키지(jiwon000512/UnityGameKit)를 manifest에 git URL로 추가한다. 게임 코드에서 새로 만들지 않는다.
6. 기능 구현은 코드-규칙 6장 절차대로: 설계 목록(계층/클래스/책임/의존) → 사용자 확인 → Core·Data → Game → UI → CLI 검증(컴파일 0·콘솔 0·테스트).

## 4. 기획서 반영

결정이 기획서 내용을 바꾸면(예: SO → JSON) 기획서의 해당 문단을 고치고 버전·변경 이력을 올린다. 기획서는 단일 출처이므로 CLAUDE.md와 어긋나지 않게 한다.

## 5. 에디터 반영과 검증

**에디터가 열려 있으면** (`unity pipeline list`로 확인; `unity status`는 인스턴스를 못 찾을 수 있음):

```bash
P="--no-banner --format json --project-path <Unity 절대경로>"
unity command package_resolve $P        # manifest 변경 반영
unity command console_status $P         # error/warn 0 확인
unity command package_list $P           # 제거 확인
unity command list_open_scenes $P       # Main 열림, isDirty false
unity command get_build_settings $P     # 빌드 씬 경로
unity command eval $P --code 'UnityEditor.AssetDatabase.Refresh(UnityEditor.ImportAssetOptions.ForceSynchronousImport); return UnityEditor.PlayerSettings.defaultInterfaceOrientation.ToString();'
```

JSON을 만든 뒤에는 Refresh로 `.meta`를 생성시키고 `Resources.Load<TextAsset>("Data/<table>")`이 null이 아닌지 eval로 확인한다. 재생성된 `packages-lock.json`은 커밋한다(git 선택 시).

**에디터가 닫혀 있으면** `unity run <Unity> --timeout 540 -- -logFile <scratch>/open.log` 1회 실행 후 로그에서 error 검색. 프로젝트가 열려 있으면 이 명령은 실패한다.

## 6. 마무리 보고

결정 표(항목·선택), 만든 파일 목록(링크), 검증 결과(콘솔 오류 수, 패키지 목록), 남은 결정(기획서 미결 항목)을 한국어로 요약한다. 다음 단계는 기획서의 개발 순서를 따른다.

## 주의점 (동물원 타이쿤에서 배운 것)

- 에디터가 열린 채로 파일을 고치면 포커스를 받기 전까지 반영되지 않는다. 반드시 5장 명령으로 반영·검증한다. ProjectSettings 텍스트 편집은 에디터가 정상적으로 읽어 들인다.
- 빈 폴더 유지용 `.gitkeep`은 Unity가 무시하므로 `.meta`가 생기지 않는다. 하위 폴더가 있는 폴더에는 넣지 않는다.
- 폴더 `.meta`는 직접 만들어도 된다(`folderAsset: yes`, 임의 guid). 씬 이름 변경은 `.unity`와 `.meta`를 함께 옮겨 guid를 유지한다.
- Windows `core.autocrlf=true`의 CRLF 경고는 무시 가능(.gitattributes로 저장소 쪽 LF 통일).
- 활성 빌드 타깃 전환(→ Android)은 전체 리임포트라 첫 기기 빌드 직전에 한다.
- Unity CLI로 개발할 때: `eval`은 `using` 문을 받지 않으므로 여러 줄 C#은 `run_script --file <cs> --entry Type.Method`로 실행한다. Git Bash에서는 `/Canvas/Button` 같은 계층 경로가 윈도 경로로 바뀌므로 `export MSYS_NO_PATHCONV=1`을 먼저 둔다. Screen Space Overlay UI 캡처는 플레이 모드에서 `capture_game_view --source screen`으로만 된다(저장 경로는 Assets 기준). TMP Essential Resources는 `AssetDatabase.ImportPackage(<ugui 패키지>/Package Resources/TMP Essential Resources.unitypackage, false)`로 비대화식 임포트가 된다. `run_tests`는 동기 호출이 CLI 타임아웃(180s)에 걸릴 수 있어 `--async_tests true` 후 `test_status`로 폴링한다. EditMode 테스트는 asmdef가 있어야 게임 코드를 참조할 수 있다.
