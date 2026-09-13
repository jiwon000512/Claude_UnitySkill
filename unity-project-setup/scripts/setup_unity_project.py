#!/usr/bin/env python3
"""Unity 모바일 게임 프로젝트 기반 세팅 스크립트.

템플릿(2D URP 등)으로 생성한 Unity 프로젝트에 대해 다음을 수행한다.
  1. Assets 폴더 구조 생성 + 폴더 .meta + 잎 폴더 .gitkeep
  2. SampleScene -> Main 씬 이름 변경 (guid 유지, EditorBuildSettings 반영)
  3. manifest.json에서 불필요 패키지 제거, packages-lock.json 삭제 (에디터가 재생성)
  4. ProjectSettings 화면 방향 고정 (기본 세로)
  5. 루트에 .gitignore(.gitignore 경로 접두어 치환) / .gitattributes / .editorconfig 복사

사용 예:
  python setup_unity_project.py --root C:/project/MyGame --unity-dir MyGameUnity
  python setup_unity_project.py --root . --unity-dir Proj --landscape --keep-packages --add-newtonsoft

멱등: 이미 있는 폴더/메타/파일은 건너뛴다. 에디터가 열려 있으면 실행 후 Unity CLI로
`unity command package_resolve` 와 AssetDatabase.Refresh 를 돌려 반영해야 한다.
"""
import argparse
import json
import os
import re
import shutil
import sys
import uuid

HERE = os.path.dirname(os.path.abspath(__file__))
TEMPLATES = os.path.join(HERE, "..", "templates")

FOLDERS = [
    "Assets/Scenes",
    "Assets/Scripts", "Assets/Scripts/Core", "Assets/Scripts/Data", "Assets/Scripts/Game",
    "Assets/Scripts/UI", "Assets/Scripts/Editor",
    "Assets/Resources", "Assets/Resources/Data", "Assets/Resources/Sprites",
    "Assets/Prefabs", "Assets/Prefabs/UI",
    "Assets/Sprites", "Assets/Sprites/UI",
    "Assets/Fonts", "Assets/Audio",
    "Assets/Tests", "Assets/Tests/EditMode",
]

REMOVE_PACKAGES = [
    "com.unity.visualscripting", "com.unity.timeline", "com.unity.multiplayer.center",
    "com.unity.2d.animation", "com.unity.2d.spriteshape", "com.unity.2d.aseprite",
    "com.unity.2d.psdimporter", "com.unity.2d.tilemap.extras",
]

# 절대 지우지 않는 패키지 (CLI 연결용)
KEEP_ALWAYS = ["com.unity.pipeline"]


def log(msg):
    print(f"[setup] {msg}")


# Windows 콘솔(cp949)에서 한국어·특수문자 출력 오류 방지
for _stream in (sys.stdout, sys.stderr):
    try:
        _stream.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass


def write_text(path, text):
    with open(path, "w", encoding="utf-8", newline="\n") as f:
        f.write(text)


def folder_meta(path):
    meta = path + ".meta"
    if os.path.exists(meta):
        return False
    write_text(meta, (
        "fileFormatVersion: 2\n"
        f"guid: {uuid.uuid4().hex}\n"
        "folderAsset: yes\n"
        "DefaultImporter:\n"
        "  externalObjects: {}\n"
        "  userData: \n"
        "  assetBundleName: \n"
        "  assetBundleVariant: \n"
    ))
    return True


def step_folders(unity):
    created = 0
    for rel in FOLDERS:
        p = os.path.join(unity, rel)
        os.makedirs(p, exist_ok=True)
        if folder_meta(p):
            created += 1
    # 잎 폴더(하위 폴더 없음)이고 비어 있으면 .gitkeep
    for rel in FOLDERS:
        p = os.path.join(unity, rel)
        entries = [e for e in os.listdir(p) if not e.startswith(".")]
        has_subdir = any(os.path.isdir(os.path.join(p, e)) for e in entries)
        if not entries and not has_subdir:
            open(os.path.join(p, ".gitkeep"), "a").close()
    log(f"폴더 {len(FOLDERS)}개 확인, .meta {created}개 생성")


def step_scene(unity, scene_name):
    scenes = os.path.join(unity, "Assets", "Scenes")
    src = os.path.join(scenes, "SampleScene.unity")
    dst = os.path.join(scenes, f"{scene_name}.unity")
    if not os.path.exists(src):
        log("SampleScene.unity 없음 — 씬 이름 변경 건너뜀")
        return
    if os.path.exists(dst):
        log(f"{scene_name}.unity 이미 있음 — 건너뜀")
        return
    shutil.move(src, dst)
    if os.path.exists(src + ".meta"):
        shutil.move(src + ".meta", dst + ".meta")
    ebs = os.path.join(unity, "ProjectSettings", "EditorBuildSettings.asset")
    if os.path.exists(ebs):
        s = open(ebs, encoding="utf-8").read()
        write_text(ebs, s.replace("Assets/Scenes/SampleScene.unity", f"Assets/Scenes/{scene_name}.unity"))
    log(f"SampleScene -> {scene_name} 이름 변경 (guid 유지)")


def find_cached_version(unity, pkg):
    cache = os.path.join(unity, "Library", "PackageCache")
    if not os.path.isdir(cache):
        return None
    for d in os.listdir(cache):
        if d.startswith(pkg + "@"):
            try:
                j = json.load(open(os.path.join(cache, d, "package.json"), encoding="utf-8"))
                return j.get("version")
            except Exception:
                pass
    return None


def step_packages(unity, keep, add_newtonsoft):
    mp = os.path.join(unity, "Packages", "manifest.json")
    m = json.load(open(mp, encoding="utf-8"))
    deps = m["dependencies"]
    changed = False
    if not keep:
        removed = [p for p in REMOVE_PACKAGES if p in deps and p not in KEEP_ALWAYS]
        for p in removed:
            deps.pop(p)
        if removed:
            changed = True
        log(f"패키지 제거: {removed or '없음'}")
    if add_newtonsoft and "com.unity.nuget.newtonsoft-json" not in deps:
        ver = find_cached_version(unity, "com.unity.nuget.newtonsoft-json") or "3.2.1"
        deps["com.unity.nuget.newtonsoft-json"] = ver
        changed = True
        log(f"Newtonsoft.Json {ver} 직접 의존으로 추가")
    if changed:
        m["dependencies"] = dict(sorted(deps.items(), key=lambda kv: (kv[0].startswith("com.unity.modules."), kv[0])))
        write_text(mp, json.dumps(m, indent=2, ensure_ascii=False) + "\n")
        lock = os.path.join(unity, "Packages", "packages-lock.json")
        if os.path.exists(lock):
            os.remove(lock)
            log("packages-lock.json 삭제 (에디터가 재생성 — 재생성본을 커밋)")


def step_orientation(unity, landscape):
    p = os.path.join(unity, "ProjectSettings", "ProjectSettings.asset")
    s = open(p, encoding="utf-8").read()
    if landscape:
        s = re.sub(r"defaultScreenOrientation: \d+", "defaultScreenOrientation: 3", s)
        flags = {"allowedAutorotateToPortrait": 0, "allowedAutorotateToPortraitUpsideDown": 0,
                 "allowedAutorotateToLandscapeRight": 1, "allowedAutorotateToLandscapeLeft": 1}
    else:
        s = re.sub(r"defaultScreenOrientation: \d+", "defaultScreenOrientation: 0", s)
        flags = {"allowedAutorotateToPortrait": 1, "allowedAutorotateToPortraitUpsideDown": 0,
                 "allowedAutorotateToLandscapeRight": 0, "allowedAutorotateToLandscapeLeft": 0}
    for k, v in flags.items():
        s = re.sub(rf"{k}: \d", f"{k}: {v}", s)
    s = re.sub(r"useOSAutorotation: \d", "useOSAutorotation: 0", s)
    write_text(p, s)
    log(f"화면 방향: {'가로' if landscape else '세로'} 고정")


def step_root_files(root, unity_dir):
    pairs = [("gitignore", ".gitignore"), ("gitattributes", ".gitattributes"), ("editorconfig", ".editorconfig")]
    for src, dst in pairs:
        d = os.path.join(root, dst)
        if os.path.exists(d):
            log(f"{dst} 이미 있음 — 건너뜀")
            continue
        s = open(os.path.join(TEMPLATES, src), encoding="utf-8").read()
        s = s.replace("{{UNITY_DIR}}", unity_dir)
        write_text(d, s)
        log(f"{dst} 생성")


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--root", required=True, help="저장소 루트 (기획/ 과 유니티 폴더의 부모)")
    ap.add_argument("--unity-dir", required=True, help="루트 아래 유니티 프로젝트 폴더 이름")
    ap.add_argument("--scene-name", default="Main")
    ap.add_argument("--landscape", action="store_true", help="가로 고정 (기본 세로)")
    ap.add_argument("--keep-packages", action="store_true", help="불필요 패키지를 제거하지 않음")
    ap.add_argument("--add-newtonsoft", action="store_true", help="com.unity.nuget.newtonsoft-json 직접 의존 추가")
    ap.add_argument("--skip-root-files", action="store_true")
    a = ap.parse_args()

    root = os.path.abspath(a.root)
    unity = os.path.join(root, a.unity_dir)
    if not os.path.isdir(os.path.join(unity, "ProjectSettings")):
        sys.exit(f"유니티 프로젝트가 아님: {unity}")

    step_folders(unity)
    step_scene(unity, a.scene_name)
    step_packages(unity, a.keep_packages, a.add_newtonsoft)
    step_orientation(unity, a.landscape)
    if not a.skip_root_files:
        step_root_files(root, a.unity_dir)
    log("완료. 다음: CLAUDE.md 작성, git init, 에디터 열려 있으면 unity command package_resolve")


if __name__ == "__main__":
    main()
