# 유니티 모바일 게임 프로젝트 초기 세팅 — 참고 문서

버전 v1.1 · 2026-09-13 · `SKILL.md`(실행 절차)의 배경 설명·상세 절차·템플릿 설명·주의점. 원본은 이 폴더이며, 각 게임 저장소에는 CLAUDE.md에 그 프로젝트가 고른 값만 남긴다.

이 문서는 필요할 때만 읽는다. 결정 항목과 실행 순서는 `SKILL.md`, 파일 템플릿은 `templates/`, 자동화는 `scripts/setup_unity_project.py`.

---

## 1. 전제

- 1인 개발, AI 에이전트(Claude Code)와 함께 기획·개발. 에이전트가 텍스트로 읽고 쓸 수 있는 형태를 우선한다.
- 저장소 루트에 `기획/` 폴더와 유니티 프로젝트 폴더를 나란히 둔다. 기획서는 단일 출처(.md).
- 유니티 프로젝트는 Unity Hub 또는 Unity CLI로 **템플릿(2D URP 등)에서 먼저 생성**한 뒤 이 가이드로 정리한다.
- Unity CLI(`unity`)가 설치되어 있고, 프로젝트에 `com.unity.pipeline` 패키지가 있으면 열린 에디터를 명령으로 조작·검증할 수 있다.

## 2. 결정 항목

질문 순서와 선택지는 `SKILL.md` 1장이 원본이다. 여기서는 배경만 적는다: 항목 3~10에서 기본값을 고르면 3장 절차를 수정 없이 실행할 수 있고, 화면 방향·기준 해상도·코드 규칙·커밋 정책은 질문 없이 기본값을 적용한다. 프로젝트가 가로 화면이면 3.5만 바꾼다.

## 3. 실행 절차

### 3.1 현황 파악

```bash
# 유니티 버전, 패키지, Assets 내용, 제품 설정, 도구 확인
cat <Unity>/ProjectSettings/ProjectVersion.txt
cat <Unity>/Packages/manifest.json
find <Unity>/Assets -type f
grep -E "productName|companyName|defaultScreenOrientation|applicationIdentifier" -A1 <Unity>/ProjectSettings/ProjectSettings.asset
git --version; which unity; tasklist | grep -i "^Unity.exe"     # 에디터가 열려 있는지
```

**에디터가 열려 있으면** 파일을 고친 뒤 반드시 에디터에 반영·검증한다(3.8). 닫혀 있으면 텍스트 편집만으로 끝나고, 다음 열 때 반영된다.

### 3.2 git 초기화 (루트)

```bash
cd <루트>
git init -b main
# 템플릿의 .gitignore / .gitattributes / .editorconfig 복사 (4장). .gitignore의 경로 접두어를 유니티 폴더 이름으로 맞춘다
git add -A && git status --short          # Library/ Temp/ Logs/ UserSettings/ *.csproj *.slnx 가 없어야 한다
git commit -m "프로젝트 기반 세팅: ..."
git ls-files | grep -c '^<Unity>/Library/'   # 0
```

GitHub 저장소를 웹에서 먼저 만들었다면(Initial commit에 .gitignore/README가 있음):

```bash
git remote add origin https://github.com/<user>/<repo>.git
git fetch origin
git rebase -X theirs origin/main     # 우리 커밋을 원격 초기 커밋 위에 올린다. 충돌(.gitignore)은 우리 것 유지
git push -u origin main
```

작업 트리에 미커밋 변경이 있으면 `git stash push -u` 후 리베이스하고 `git stash pop`. 원격의 GitHub 기본 Unity .gitignore는 유니티 폴더가 루트라고 가정하므로 우리 것으로 덮는다. 연결 뒤 CLAUDE.md에 원격 주소를 적는다.

### 3.3 폴더 구조 (기본값: Assets 바로 아래 종류별, asmdef 없음)

```
Assets/
├─ Scenes/Main.unity
├─ Scripts/{Core,Data,Game,UI,Editor}
├─ Resources/Data/            JSON 테이블
├─ Resources/Sprites/<종류>/  ID 규칙으로 로드하는 스프라이트 (파일명 = ID)
├─ Prefabs/, Prefabs/UI/
├─ Sprites/UI/, Fonts/, Audio/
└─ Tests/EditMode/
```

- 새 폴더마다 **`.meta`를 함께 만든다** (`folderAsset: yes`, guid는 임의 32자리 hex). 에디터가 열려 있을 때 폴더만 만들면 에디터가 자기 guid로 만들고, 닫혀 있을 때도 다음 실행 때 만들어 주지만, 직접 만들면 커밋 시점에 이미 존재해 이력이 깔끔하다.
- 빈 폴더는 `.gitkeep`으로 유지한다. Unity는 점(.)으로 시작하는 파일을 무시하므로 `.meta`가 생기지 않는다. 하위 폴더가 있는 폴더에는 넣지 않는다.
- `Core/`는 UnityEngine을 참조하지 않는다(에디터 없이 테스트하기 위한 규칙). asmdef 없이 규칙으로만 지킨다.
- 템플릿 씬(`SampleScene`)은 `Main`으로 이름 변경. `.unity`와 `.meta`를 함께 옮겨 guid를 유지하고 `ProjectSettings/EditorBuildSettings.asset`의 경로를 고친다.

이 폴더의 `scripts/setup_unity_project.py`가 3.3~3.5를 한 번에 수행한다.

### 3.4 패키지 정리 (기본값: 제거)

`Packages/manifest.json`에서 지우고 `packages-lock.json`을 삭제한다(에디터가 재생성 → 재생성된 파일을 커밋).

| 제거 | 이유 |
|---|---|
| `com.unity.visualscripting`, `com.unity.timeline`, `com.unity.multiplayer.center` | 사용 안 함 |
| `com.unity.2d.animation`, `com.unity.2d.spriteshape`, `com.unity.2d.aseprite`, `com.unity.2d.psdimporter`, `com.unity.2d.tilemap.extras` | 스프라이트 시트 애니메이션만 쓰면 불필요 |

| 유지 | 이유 |
|---|---|
| `com.unity.pipeline` | Unity CLI가 에디터에 연결하는 패키지. **지우지 않는다** |
| `com.unity.2d.sprite`, `com.unity.2d.tilemap`, `com.unity.2d.tooling`, `com.unity.ugui`, `com.unity.inputsystem`, `com.unity.render-pipelines.universal`, `com.unity.test-framework`, IDE 패키지 | 사용 |
| `com.unity.modules.*` | 빌드 시 자동 스트리핑되고 URP가 일부(terrain 등)에 의존하므로 손대지 않음 |

추가: 데이터 방식이 JSON+Newtonsoft이면 `"com.unity.nuget.newtonsoft-json"`을 명시적으로 넣는다(버전은 `Library/PackageCache`에 이미 있는 것과 맞춘다). 간접 의존으로 이미 깔려 있어도 직접 의존으로 선언해야 나중에 사라지지 않는다.

### 3.5 ProjectSettings

`ProjectSettings/ProjectSettings.asset`을 텍스트로 고친다.

| 필드 | 세로 고정 값 | 의미 |
|---|---|---|
| `defaultScreenOrientation` | `0` | 0 Portrait, 1 PortraitUpsideDown, 2 LandscapeRight, 3 LandscapeLeft, 4 AutoRotation |
| `allowedAutorotateToPortrait` | `1` | |
| `allowedAutorotateToPortraitUpsideDown` / `…LandscapeRight` / `…LandscapeLeft` | `0` | |
| `useOSAutorotation` | `0` | |

Android는 템플릿 기본이 IL2CPP(`scriptingBackend: Android: 1`)·ARM64(`AndroidTargetArchitectures: 2`)인지 확인만 한다. 제품명·회사명·패키지 ID는 결정 5를 따른다. 활성 빌드 타깃 전환(Standalone → Android)은 전체 리임포트가 걸리므로 첫 기기 빌드 직전에 한다.

### 3.6 루트 파일

4장의 템플릿으로 `.gitignore`, `.gitattributes`, `.editorconfig`, `CLAUDE.md`를 만든다. CLAUDE.md에는 폴더 트리, 기술 결정 표, 코드 규칙, 작업 방식(기획 변경은 객관식으로 하나씩 질문, 커밋은 요청 시에만)을 적는다.

### 3.7 데이터 테이블 (기본값: JSON 단일 원본)

1. `기획/데이터-테이블-규칙.md`를 5장 템플릿으로 만들고 게임의 테이블 스키마(8장)를 채운다.
2. `Assets/Resources/Data/<table>.json` 을 테이블당 하나 만든다. 공통 구조 `{ "table", "version", "notes", "rows" }`. 상수 묶음은 `rows` 대신 섹션 객체.
3. 스프라이트는 `Resources/Sprites/<종류>/{id}.png`. JSON에는 경로를 적지 않는다.
4. 기획서의 구현 메모를 JSON 기준으로 고치고 버전을 올린다.
5. (범위에 포함되면) Core에 레코드·로더·검증기, `Tests/EditMode`에 테이블 검증 테스트.

### 3.8 에디터 반영과 검증 (Unity CLI)

```bash
P="--no-banner --format json --project-path <Unity 절대경로>"
unity pipeline list --no-banner --format json     # 실행 중인 에디터와 Pipeline 서버(포트) 확인. unity status 는 인스턴스를 못 찾는 경우가 있어 이걸 쓴다
unity command $P                                   # 명령 목록
unity command package_resolve $P                   # manifest 변경 반영(패키지 제거·추가). 완료 후 requiresRecompile 확인
unity command console_status $P                    # error/warn 카운트가 0인지
unity command package_list $P                      # 설치 목록에서 제거 확인
unity command list_open_scenes $P                  # 씬 이름 변경이 반영됐는지 (Main, isDirty=false)
unity command get_build_settings $P                # 빌드 씬 목록
unity command eval $P --code 'UnityEditor.AssetDatabase.Refresh(UnityEditor.ImportAssetOptions.ForceSynchronousImport); return UnityEngine.Resources.Load<UnityEngine.TextAsset>("Data/animals") != null;'
unity command eval $P --code 'return UnityEditor.PlayerSettings.defaultInterfaceOrientation.ToString();'   # 메모리상 설정 확인
```

에디터가 닫혀 있으면 `unity run <Unity> --timeout 540 -- -logFile <log>`로 배치 모드 1회 실행 후 로그에서 `error`를 검색한다. 프로젝트가 이미 열려 있으면 이 명령은 실패한다(PID를 알려 줌).

## 4. 템플릿 — 루트 파일

완성본은 이 폴더의 `templates/`에 있다. 동물원 타이쿤 저장소(jiwon000512/IdleTycoon)의 실제 파일도 같은 내용이다.

### 4.1 .gitignore

유니티 폴더가 저장소 루트의 하위 폴더이므로 모든 유니티 패턴에 `<Unity>/` 접두어를 붙인다. 제외 대상: `Library/ Temp/ Obj/ Build/ Builds/ Logs/ UserSettings/ MemoryCaptures/ Recordings/`, IDE 폴더(`.vs .idea .vscode`), 생성 파일(`*.csproj *.sln *.slnx *.suo *.user *.pdb *.mdb …`), 빌드 산출물(`*.apk *.aab *.unitypackage`), OS 파일, `.claude/settings.local.json`.

### 4.2 .gitattributes

`* text=auto`. Unity YAML(`.unity .prefab .asset .meta .mat .anim .controller .overrideController .physicsMaterial2D`)은 `text merge=unityyamlmerge eol=lf`. `.inputactions .asmdef .json`은 `text eol=lf`. `.cs`는 `text diff=csharp`. 이미지·폰트·오디오·모델·dll은 `binary`.

### 4.3 .editorconfig

UTF-8, LF, 마지막 줄 개행, 공백 4칸(json/asmdef/yml은 2칸). C#: 여는 중괄호 새 줄, private 필드 `_camelCase` 네이밍 규칙.

### 4.4 CLAUDE.md 골격

```
# <게임 이름>
한 줄 소개. 기획서 경로(버전). 데이터 규칙 문서 경로.
## 폴더            (3.3 트리 + 각 폴더의 역할)
## 기술 결정       (엔진 버전 / UI / 입력 / 화면 / 숫자 표기 / 저장 / 데이터 / 빌드 / 제외·유지 패키지 표)
## 코드 규칙       (식별자 영어·주석 한국어, 4칸, 중괄호 새 줄, _camelCase, 네임스페이스, MonoBehaviour 얇게, 숫자는 JSON에)
## 작업 방식       (개발 순서, 기획 변경은 객관식으로 하나씩 질문 → 기획서 반영, Unity CLI 사용법, .meta 함께 생성, 커밋은 요청 시에만)
## 유용한 명령
```

## 5. 템플릿 — 데이터 테이블 규칙 문서

`templates/data-table-rules.md`(동물원 타이쿤 `기획/데이터-테이블-규칙.md`에서 일반화)의 1~7장·9장은 게임과 무관하게 재사용하고, 8장(테이블 스키마)만 게임별로 채운다. 재사용 부분의 핵심:

- 공통 구조 `table`(파일명과 일치) / `version`(스키마 변경 시만 +1) / `notes`(주석 대용, 로더 무시) / `rows`.
- 표기: 키 camelCase 영어, ID `^[a-z][a-z0-9_]*$`, 배수는 소수, 확률은 정수 가중치, 시간은 초, 불리언 true/false, 없음은 null(필드 생략 금지), 색 `#RRGGBB`, 2칸 들여쓰기 LF.
- 에셋은 ID 규칙 경로로 로드. 규칙 표를 문서에 둔다.
- 변경 절차: 기획서 → JSON → (구조 변경 시 version·스키마 표·레코드) → 검증 테스트 → 미결은 notes.
- 에이전트 규칙: 파일 전체를 유효한 JSON으로 다시 쓴다. 기존 ID·sortOrder 변경 금지.
- 검증 규칙: table 일치, version 지원, 필드 집합 일치, ID·sortOrder 유일, 외래 ID 존재, 수치 범위, 레벨 연속·단조 증가, 에셋 존재.

완성본(8장은 빈 표)은 스킬 `templates/data-table-rules.md`.

## 6. 이번 프로젝트에서 배운 주의점

- **에디터가 열린 채로 파일을 고쳤다면** 반드시 `package_resolve`, `AssetDatabase.Refresh`로 반영하고 `console_status`로 오류를 확인한다. 에디터는 포커스를 받기 전까지 변경을 모른다. ProjectSettings 변경도 에디터가 정상적으로 읽어 들였다(덮어쓰지 않음).
- `unity status`가 "인스턴스 없음"을 돌려주더라도 `unity pipeline list`·`unity command`는 연결될 수 있다. 연결 확인은 `pipeline list`로 한다.
- `unity run`은 프로젝트가 이미 열려 있으면 실패한다. 배치 검증은 에디터를 닫은 뒤에만.
- `com.unity.pipeline`은 "Unity Pipeline"이라는 이름 때문에 렌더 파이프라인처럼 보이지만 CLI 연결용이다.
- 템플릿 `.gitignore`는 유니티 폴더가 저장소 루트라고 가정한다. 하위 폴더에 있으면 경로 접두어를 붙여야 한다.
- Windows에서 `core.autocrlf=true`면 커밋 시 CRLF 경고가 뜬다. `.gitattributes`로 저장소 쪽은 LF로 통일되므로 무시해도 되고, 소음이 싫으면 저장소 로컬로 `git config core.autocrlf false`.
- `Resources.Load`로 ID 기반 로드를 하려면 스프라이트가 `Assets/Resources/` 아래에 있어야 한다. 폴더 구조를 잡을 때 처음부터 `Resources/Sprites/...`로 둔다.
- bash 히어독으로 긴 한국어 마크다운을 쓰면 따옴표 처리로 실패할 수 있다. 긴 문서는 Write 도구나 Python으로 쓴다.

## 변경 이력

- v1.0 (2026-09-13) 동물원 타이쿤 기반 세팅·데이터 테이블 결정을 일반화해 최초 작성 (Tycoon 저장소 `기획/유니티-프로젝트-초기-세팅-가이드.md`로 시작)
- v1.1 (2026-09-13) 원본을 스킬 폴더로 이동. GitHub 원격 연결 절차 추가. 질문 표는 SKILL.md로 분리
