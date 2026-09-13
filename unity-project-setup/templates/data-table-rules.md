# 데이터 테이블 규칙

버전 v1.0 · <날짜>
게임 데이터(<테이블 목록>)를 JSON 파일로 관리하는 규칙. 사람과 AI 에이전트가 이 문서를 보고 JSON을 만들고 고친다. 기획서(`<기획서 파일>.md`)의 표가 "무엇을 넣을지"를 정하고, 이 문서는 "어떤 형태로 넣을지"를 정한다.

---

## 1. 결정 (2026-09-13)

| 항목 | 결정 |
|---|---|
| 원본 | JSON 파일이 유일한 원본. ScriptableObject는 쓰지 않는다 |
| 로드 | 게임 시작 시 `Resources.Load<TextAsset>`로 읽어 Newtonsoft.Json으로 C# 레코드에 역직렬화 |
| 파서 | Newtonsoft.Json (`com.unity.nuget.newtonsoft-json`) |
| 파일 구성 | 테이블당 파일 1개 |
| 에셋 참조 | JSON에 에셋 경로를 적지 않는다. ID로 경로를 만들어 `Resources.Load` |
| 검증 | EditMode 테스트가 모든 테이블을 로드해 규칙(7장)을 검사한다. 테스트 실패 = 데이터 오류 |

## 2. 위치와 파일

```
<Unity>/Assets/Resources/
├─ Data/
│  ├─ <table_a>.json      (기획서 n.n)
│  ├─ <table_b>.json
│  └─ game_config.json    수식 상수·시작 상태
└─ Sprites/
   └─ <종류>/{id}.png     ID 규칙으로 로드
```

- 파일 이름은 `snake_case.json`. 새 테이블을 추가하면 이 표와 8장 스키마에 함께 적는다.
- 런타임 저장 데이터(세이브 파일)는 테이블이 아니다. 여기 규칙을 따르지 않고 `Application.persistentDataPath`에 따로 둔다.

## 3. 공통 구조

행(row)이 여러 개인 테이블:

```json
{
  "table": "animals",
  "version": 1,
  "notes": ["사람/에이전트를 위한 메모. 로더는 무시한다."],
  "rows": [ { ... }, { ... } ]
}
```

상수 묶음(`game_config.json`)은 `rows` 대신 섹션 객체를 가진다 (8.4 참고).

| 필드 | 규칙 |
|---|---|
| `table` | 파일 이름(확장자 제외)과 같아야 한다. 로더가 잘못된 파일을 읽었는지 확인하는 용도 |
| `version` | 정수. **스키마(필드 구조)가 바뀔 때만** +1. 값만 바꿀 때는 올리지 않는다. 로더는 지원하지 않는 version이면 오류 |
| `notes` | 문자열 배열. 선택. 미결 항목·출처·주의점을 적는다. JSON은 주석이 없으므로 주석 대용 |
| `rows` | 행 배열. 순서는 `sortOrder`가 따로 있으면 무시되고, 없으면 파일 순서가 표시 순서 |

## 4. 표기 규칙

- **키**: `camelCase`. 영어만. 축약하지 않는다 (`baseIncomePerSecond`, `incPerSec` ✗).
- **ID**: 문자열, `^[a-z][a-z0-9_]*$`. 등급·모드 같은 열거형 값도 소문자 문자열(`"common"`, `"refundCoins"`는 예외적으로 camelCase 허용 — 코드 enum 이름과 맞추기 위함). 동물 ID는 `a` + 두 자리 번호(`a01`~`a99`). 번호는 재사용하지 않는다(삭제된 종의 번호는 비워 둔다).
- **표시 이름**: `name`에 한국어. 다국어를 도입하면 `nameKey`로 바꾸고 `name`을 지운다(version +1).
- **숫자**: 배수·비율은 소수(`0.5` = +50%), 퍼센트 정수를 쓰지 않는다. 확률은 **가중치**(정수)로 적고 로더가 합으로 나눈다. 시간은 초 단위 정수. 코인은 정수(내부 계산은 double).
- **불리언**: `true/false`. 0/1을 쓰지 않는다.
- **없음**: `null`. 필드를 생략하지 않는다 — 모든 행은 같은 필드 집합을 가진다(누락 검출을 위해).
- **색**: `"#RRGGBB"` 문자열.
- 들여쓰기 2칸, UTF-8, LF, 파일 끝 개행.

## 5. 에셋 참조 규칙 

에셋은 JSON의 **경로 칼럼**으로 가리킨다. 값은 `Resources/` 아래 상대 경로(확장자 없음)이며 코드가 `Resources.Load(path)`로 읽는다. 이름을 바꾸거나 다른 파일로 바꿀 때 JSON 값만 고치면 된다.

| 에셋 | 칼럼 | 값 예 | 없을 때 |
|---|---|---|---|
| 동물 스프라이트 | `animals.sprite` | `Sprites/Animals/<id>_<name>` | 검증 실패(테스트) |
| 등급 색 | `grades.colorHex` | `#42A5F5` (에셋 아님) | — |
| UI 프리팹 | 칼럼 없음. GameKit `UIManager`가 `UI/{뷰 타입 이름}` 규칙으로 로드 | `Resources/UI/GachaButtonView` | — |

- 개발 중에는 에이전트가 경로 자리에 **더미 리소스**(단색 스프라이트 등)를 만들어 둔다. 사용자가 같은 경로·이름의 실제 리소스로 덮어써 교체한다. 교체 시 JSON·코드 수정 없음.
- 검증기는 경로 칼럼이 비어 있지 않은지만 검사한다. 파일 존재는 EditMode 테스트가 `Assets/Resources/<path>.*` 로 확인한다.
- v1.0의 "ID 규칙 경로" 방식은 폐기. 이유: 실제 리소스 교체 시 이름을 ID에 맞추는 부담을 없애고, 한 종이 여러 에셋(스프라이트·아이콘·사운드)을 갖게 될 때 칼럼만 늘리면 되게 하기 위함.

## 6. 변경 절차

1. 기획서의 해당 표/문단을 먼저 고친다(값의 출처는 항상 기획서).
2. JSON 값을 고친다. 구조가 바뀌면 `version` +1, 8장 스키마 표와 C# 레코드를 함께 고친다.
3. EditMode 테스트(테이블 검증)를 돌려 통과를 확인한다.
4. 미결이거나 가정한 값은 `notes`에 "기획서 n장 미결"로 남긴다.

에이전트 작업 규칙:
- JSON은 항상 파일 전체를 유효한 JSON으로 다시 쓴다(부분 문자열 치환으로 쉼표를 깨뜨리지 않는다).
- 행을 추가할 때 기존 ID·`sortOrder`를 바꾸지 않는다. 삭제는 행 제거가 아니라 `notes`에 사유를 적고 제거한다(세이브 호환은 코드가 "없는 ID 무시"로 처리).
- 값을 바꾸면 커밋 메시지나 보고에 "기획서 x.y 표 → 필드명 이전값→새값"을 적는다.

## 7. 검증 규칙 (테스트가 검사하는 것)

공통 규칙은 그대로 쓰고, 테이블별 규칙은 아래 예시(동물원 타이쿤)를 참고해 게임에 맞게 다시 쓴다.

공통
- 파일이 유효한 JSON이고 `table`이 파일 이름과 같다. `version`이 코드가 지원하는 값이다.
- 모든 행이 스키마의 필드를 전부 가진다(추가 필드가 있으면 경고).
- `id`는 테이블 안에서 유일하고 4장 패턴을 만족한다. `sortOrder`는 유일하다.

animals
- `grade`가 `grades.rows[].id` 중 하나다.
- `baseIncomePerSecond > 0`, `gachaWeight >= 1`(정수).
- 등급별로 최소 1종이 있다.
- `Resources/Sprites/Animals/{id}` 스프라이트가 존재한다(첫 아트가 들어오기 전에는 경고).

grades
- `gachaWeight >= 0`(정수), 합 > 0.
- 계산된 확률(가중치/합)을 기획서 6.1 표와 비교해 `notes`에 기록.

zoo_levels
- `level`이 1부터 연속 정수. `requiredTotalCoins`와 `cageCount`가 레벨 순으로 단조 증가(같은 값 허용 안 함). 첫 레벨은 `requiredTotalCoins == 0`.
- `unlocksPromotion == true`인 레벨이 정확히 1개.
- 마지막 레벨의 `cageCount <= cageGrid.columns × cageGrid.rows`.

game_config
- `gacha.costGrowth > 1`, `promotion.costGrowth > 1`, `baseCost > 0`.
- `animalLevel.maxLevel >= 1`, `incomeBonusPerLevel >= 0`.
- `offline.maxSeconds > 0`. `start.coins >= gacha.baseCost`(첫 뽑기가 가능해야 함).
- 열거형 문자열이 허용 값 안에 있다(8.4 표).

## 8. 테이블 스키마

게임별로 채운다. 테이블마다 아래 표 하나씩. 기획서의 표 번호를 제목에 적는다.

### 8.1 <table>.json — 기획서 <n.n>

| 필드 | 타입 | 의미 |
|---|---|---|
| `id` | string | |
| `name` | string | 표시 이름(한국어) |
| `sortOrder` | int | 표시 순서 |

### 8.x game_config.json — 수식 상수·시작 상태

`rows` 없이 섹션 객체. 미결 항목은 enum 값과 "미결(기획서 n장)" 표시를 남긴다.

| 경로 | 타입 | 의미 | 기획서 |
|---|---|---|---|
| `start.<field>` | | 시작 상태 | |

## 9. 이후 확장 시 규칙

- 종 추가(8 → 16): `animals.json`에 행 추가, `cageGrid` 확대, `zoo_levels`에 우리 해금 레벨 추가. version은 올리지 않는다(값 변경).
- 색깔 변형: `variants.json` 신설(`id`, `name`, `hueShift`, `gachaWeight`). `animals.variantId`는 그대로 두고 변형 개체는 세이브 쪽에서 표현.
- 고유 효과: `animals`에 `effectId`(null 허용) 필드 추가 → version 2. `effects.json` 신설.
- 원격 설정: 같은 JSON을 서버에서 내려받아 로컬 파일보다 우선 적용. 형식은 바꾸지 않는다.

## 변경 이력

- v1.0 (<날짜>) 최초 작성. unity-project-setup 스킬 템플릿에서 생성
