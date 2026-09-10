#!/usr/bin/env python3
"""Validate the repository's Agent Skills structure without third-party packages."""

from __future__ import annotations

import json
import re
import sys
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parent.parent
SKILLS_ROOT = REPO_ROOT / "skills"
NAME_PATTERN = re.compile(r"^[a-z0-9]+(?:-[a-z0-9]+)*$")
MARKDOWN_LINK_PATTERN = re.compile(r"\]\(([^)]+)\)")


def parse_frontmatter(path: Path) -> tuple[dict[str, str], list[str]]:
    errors: list[str] = []
    lines = path.read_text(encoding="utf-8").splitlines()
    if not lines or lines[0] != "---":
        return {}, ["frontmatter 必须从文件第一行开始"]

    try:
        end = lines.index("---", 1)
    except ValueError:
        return {}, ["frontmatter 缺少结束分隔符"]

    metadata: dict[str, str] = {}
    for line in lines[1:end]:
        if not line.strip() or line.startswith((" ", "\t")):
            continue
        if ":" not in line:
            errors.append(f"无法解析 frontmatter 行：{line}")
            continue
        key, value = line.split(":", 1)
        metadata[key.strip()] = value.strip().strip('"\'')
    return metadata, errors


def validate_skill(skill_dir: Path, filename: str = "SKILL.md") -> list[str]:
    errors: list[str] = []
    skill_file = skill_dir / filename
    metadata, parse_errors = parse_frontmatter(skill_file)
    errors.extend(parse_errors)

    name = metadata.get("name", "")
    description = metadata.get("description", "")
    if name != skill_dir.name:
        errors.append(f"name '{name}' 与目录名 '{skill_dir.name}' 不一致")
    if not NAME_PATTERN.fullmatch(name):
        errors.append("name 必须使用小写字母、数字和单连字符")
    if not description:
        errors.append("缺少 description")
    elif len(description) > 1024:
        errors.append("description 超过 1024 个字符")

    text = skill_file.read_text(encoding="utf-8")
    if len(text.splitlines()) > 500:
        errors.append("SKILL.md 超过建议的 500 行")
    if str(REPO_ROOT) in text or re.search(r"/Users/[^/]+/", text):
        errors.append("包含本机绝对路径")

    for target in MARKDOWN_LINK_PATTERN.findall(text):
        if "://" in target or target.startswith("#"):
            continue
        clean_target = target.split("#", 1)[0]
        if clean_target and not (skill_dir / clean_target).exists():
            errors.append(f"引用文件不存在：{target}")

    return errors


def main() -> int:
    if not SKILLS_ROOT.is_dir():
        print("错误：缺少 skills/ 目录", file=sys.stderr)
        return 1

    skill_dirs = sorted(
        path for path in SKILLS_ROOT.iterdir() if (path / "SKILL.md").is_file()
    )
    if not skill_dirs:
        print("错误：skills/ 中没有发现 SKILL.md", file=sys.stderr)
        return 1

    catalog_path = REPO_ROOT / "catalog.json"
    try:
        catalog = json.loads(catalog_path.read_text(encoding="utf-8"))
        catalog_names = {item["name"] for item in catalog["skills"]}
    except (FileNotFoundError, KeyError, TypeError, ValueError) as exc:
        print(f"错误：catalog.json 无法读取：{exc}", file=sys.stderr)
        return 1

    directory_names = {path.name for path in skill_dirs}
    if catalog_names != directory_names:
        missing = sorted(directory_names - catalog_names)
        extra = sorted(catalog_names - directory_names)
        print(
            f"错误：catalog.json 与 skills/ 不一致；缺少 {missing}，多出 {extra}",
            file=sys.stderr,
        )
        return 1

    from opc_skills import discover_modules, DEFAULT_SKILL
    modules = discover_modules()
    if catalog.get("default_skill") != DEFAULT_SKILL or len(skill_dirs) != 1:
        print("错误：必须只有一个默认集成技能。", file=sys.stderr)
        return 1
    if len(modules) != 21 or {item["name"] for item in catalog.get("modules", [])} != set(modules):
        print("错误：catalog 模块与 21 个内部模块不一致。", file=sys.stderr)
        return 1
    for item in [*catalog["skills"], *catalog["modules"]]:
        expected = SKILLS_ROOT / item["name"] if item["name"] == DEFAULT_SKILL else modules[item["name"]]
        if REPO_ROOT / item["path"] != expected:
            print(f"错误：catalog 路径不正确：{item['name']}", file=sys.stderr)
            return 1
    nested = list(SKILLS_ROOT.rglob("SKILL.md"))
    if len(nested) != 1:
        print("错误：集成包内不应出现嵌套 SKILL.md。", file=sys.stderr)
        return 1
    failures = 0
    for module in modules.values():
        for error in validate_skill(module, "WORKFLOW.md"):
            failures += 1
            print(f"[失败] {module.name}: {error}")

    for skill_dir in skill_dirs:
        errors = validate_skill(skill_dir)
        if errors:
            failures += len(errors)
            for error in errors:
                print(f"[失败] {skill_dir.name}: {error}")
        else:
            print(f"[通过] {skill_dir.name}")

    if failures:
        print(f"校验失败：{failures} 个问题。", file=sys.stderr)
        return 1
    print(f"校验通过：{len(skill_dirs)} 个集成 Skill，21 个模块。")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
