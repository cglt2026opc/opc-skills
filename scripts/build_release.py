#!/usr/bin/env python3
"""Build and verify the ZIP assets attached to every GitHub Release."""

from __future__ import annotations

import argparse
import hashlib
import io
import json
import shutil
import sys
import tempfile
import zipfile
from pathlib import Path

from opc_skills import discover_skills, discover_modules, selected_skills, package_doubao


REPO_ROOT = Path(__file__).resolve().parent.parent
CATALOG_PATH = REPO_ROOT / "catalog.json"
DEFAULT_OUTPUT = REPO_ROOT / "dist" / "release"
FIXED_ZIP_TIME = (2020, 1, 1, 0, 0, 0)


def catalog_version() -> str:
    catalog = json.loads(CATALOG_PATH.read_text(encoding="utf-8"))
    version = catalog.get("version")
    if not isinstance(version, str) or not version:
        raise ValueError("catalog.json 缺少有效的 version。")
    return version


def validate_tag(tag: str | None, version: str) -> None:
    if tag is not None and tag != f"v{version}":
        raise ValueError(
            f"发布标签 {tag!r} 与 catalog.json 版本不一致；预期标签为 'v{version}'。"
        )


def archive_info(name: str, mode: int = 0o644) -> zipfile.ZipInfo:
    info = zipfile.ZipInfo(name, FIXED_ZIP_TIME)
    info.compress_type = zipfile.ZIP_DEFLATED
    info.create_system = 3
    info.external_attr = (mode & 0xFFFF) << 16
    return info


def add_file(bundle: zipfile.ZipFile, source: Path, archive_name: str) -> None:
    mode = source.stat().st_mode & 0o777
    bundle.writestr(archive_info(archive_name, mode), source.read_bytes())


def skill_files(source: Path) -> list[Path]:
    ignored_names = {".DS_Store", "Thumbs.db"}
    ignored_parts = {"__pycache__", ".pytest_cache"}
    return [
        item
        for item in sorted(source.rglob("*"))
        if item.is_file()
        and item.name not in ignored_names
        and not ignored_parts.intersection(item.relative_to(source).parts)
        and item.suffix not in {".pyc", ".pyo"}
    ]


def skill_zip_bytes(name: str, source: Path) -> bytes:
    buffer = io.BytesIO()
    with zipfile.ZipFile(buffer, "w") as bundle:
        for item in skill_files(source):
            add_file(bundle, item, str(Path(name) / item.relative_to(source)))
    return buffer.getvalue()


def write_all_skills(skills: dict[str, Path], output: Path) -> Path:
    archive = output / "opc-skills-all.zip"
    with zipfile.ZipFile(archive, "w") as bundle:
        for name, source in skills.items():
            for item in skill_files(source):
                add_file(bundle, item, str(Path(name) / item.relative_to(source)))
    return archive


def write_individual_skills(
    skills: dict[str, Path], output: Path
) -> dict[str, bytes]:
    archives: dict[str, bytes] = {}
    for name, source in skills.items():
        data = skill_zip_bytes(name, source)
        (output / f"{name}.zip").write_bytes(data)
        archives[name] = data
    return archives


def write_workbuddy_pack(archives: dict[str, bytes], output: Path) -> Path:
    archive = output / "workbuddy-pack.zip"
    with zipfile.ZipFile(archive, "w") as bundle:
        for name, data in archives.items():
            bundle.writestr(archive_info(f"{name}.zip"), data)
    return archive


def write_doubao_pack(skills: dict[str, Path], output: Path) -> Path:
    archive = output / "doubao-prompt-pack.zip"
    with tempfile.TemporaryDirectory(prefix="opc-doubao-") as temp_dir:
        prompt_dir = Path(temp_dir)
        package_doubao(skills, prompt_dir)
        with zipfile.ZipFile(archive, "w") as bundle:
            for item in sorted(prompt_dir.glob("*.prompt.md")):
                add_file(bundle, item, item.name)
    return archive


def expected_asset_names(skills: dict[str, Path]) -> set[str]:
    return {
        "opc-skills-all.zip",
        "workbuddy-pack.zip",
        "doubao-prompt-pack.zip",
        *(f"{name}.zip" for name in skills),
        *(f"{name}.zip" for name in discover_modules()),
    }


def verify_release(output: Path, skills: dict[str, Path]) -> None:
    actual = {item.name for item in output.iterdir() if item.is_file()}
    expected = expected_asset_names(skills)
    if actual != expected:
        raise RuntimeError(
            f"发布产物不完整；缺少 {sorted(expected - actual)}，多出 {sorted(actual - expected)}。"
        )

    skill_names = set(skills)
    with zipfile.ZipFile(output / "opc-skills-all.zip") as bundle:
        roots = {Path(name).parts[0] for name in bundle.namelist()}
        if roots != skill_names:
            raise RuntimeError("opc-skills-all.zip 中的 Skill 集合不正确。")

    with zipfile.ZipFile(output / "workbuddy-pack.zip") as bundle:
        if set(bundle.namelist()) != {f"{name}.zip" for name in skills}:
            raise RuntimeError("workbuddy-pack.zip 中的单独 Skill ZIP 集合不正确。")

    with zipfile.ZipFile(output / "doubao-prompt-pack.zip") as bundle:
        if set(bundle.namelist()) != {f"{name}.prompt.md" for name in discover_modules()}:
            raise RuntimeError("doubao-prompt-pack.zip 中的提示词集合不正确。")

    for name in [*skills, *discover_modules()]:
        with zipfile.ZipFile(output / f"{name}.zip") as bundle:
            if f"{name}/SKILL.md" not in bundle.namelist():
                raise RuntimeError(f"{name}.zip 缺少 {name}/SKILL.md。")


def prepare_output(output: Path) -> None:
    forbidden = {Path(output.anchor), Path.home().resolve(), REPO_ROOT.resolve()}
    if output in forbidden:
        raise ValueError(f"拒绝将受保护目录作为输出目录：{output}")
    if output.is_symlink():
        raise ValueError(f"拒绝清理符号链接输出目录：{output}")
    if output.exists():
        shutil.rmtree(output)
    output.mkdir(parents=True)


def build(output: Path, tag: str | None) -> None:
    version = catalog_version()
    validate_tag(tag, version)
    skills = discover_skills()
    if len(skills) != 1 or len(discover_modules()) != 21:
        raise RuntimeError("预期 1 个集成技能和 21 个模块。")

    prepare_output(output)

    write_all_skills(skills, output)
    individual_archives = write_individual_skills(skills, output)
    write_workbuddy_pack(individual_archives, output)
    with selected_skills(list(discover_modules())) as standalone:
        write_individual_skills(standalone, output)
        write_doubao_pack(standalone, output)
    verify_release(output, skills)

    print(f"发布版本：v{version}")
    print(f"输出目录：{output}")
    print(f"产物数量：{len(expected_asset_names(skills))}")
    for item in sorted(output.iterdir()):
        digest = hashlib.sha256(item.read_bytes()).hexdigest()[:12]
        print(f"[已验证] {item.name} ({item.stat().st_size} bytes, sha256:{digest})")


def main() -> int:
    parser = argparse.ArgumentParser(description="构建 GitHub Release 的全部 ZIP 产物。")
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument("--tag", help="校验发布标签（必须为 catalog.json 中版本的 v 前缀形式）。")
    args = parser.parse_args()
    try:
        build(args.output.expanduser().resolve(), args.tag)
        return 0
    except (OSError, RuntimeError, ValueError, zipfile.BadZipFile) as exc:
        print(f"错误：{exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
