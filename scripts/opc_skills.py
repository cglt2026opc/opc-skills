#!/usr/bin/env python3
"""Install or package the OPC book companion skills for supported agents."""

from __future__ import annotations

import argparse
import shutil
import sys
import zipfile
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parent.parent
SKILLS_ROOT = REPO_ROOT / "skills"

AGENT_TARGETS = {
    "codex": Path("~/.agents/skills").expanduser(),
    "cursor": Path("~/.agents/skills").expanduser(),
    "gemini": Path("~/.agents/skills").expanduser(),
    "copilot": Path("~/.agents/skills").expanduser(),
    "openclaw": Path("~/.openclaw/skills").expanduser(),
    "hermes": Path("~/.hermes/skills/opc-skills").expanduser(),
    "qwenwork": Path("~/.qwenwork/skills").expanduser(),
}


def discover_skills() -> dict[str, Path]:
    skills: dict[str, Path] = {}
    for child in sorted(SKILLS_ROOT.iterdir()):
        if child.is_dir() and (child / "SKILL.md").is_file():
            skills[child.name] = child
    return skills


def selected_skills(names: list[str]) -> dict[str, Path]:
    available = discover_skills()
    if not names:
        return available

    missing = sorted(set(names) - set(available))
    if missing:
        raise ValueError(
            f"未知 Skill：{', '.join(missing)}。运行 list 查看可用名称。"
        )
    return {name: available[name] for name in names}


def install(args: argparse.Namespace) -> int:
    skills = selected_skills(args.skill)
    target_root = (
        Path(args.target).expanduser().resolve()
        if args.target
        else AGENT_TARGETS[args.agent]
    )

    print(f"目标智能体：{args.agent}")
    print(f"安装目录：{target_root}")
    if args.dry_run:
        for name in skills:
            print(f"[预览] {name} -> {target_root / name}")
        return 0

    target_root.mkdir(parents=True, exist_ok=True)
    installed = 0
    skipped = 0

    for name, source in skills.items():
        target = target_root / name
        if target.exists() or target.is_symlink():
            if not args.force:
                print(f"[跳过] {name}：目标已存在；使用 --force 才会替换。")
                skipped += 1
                continue
            if target.is_symlink() or target.is_file():
                target.unlink()
            else:
                shutil.rmtree(target)

        if args.mode == "link":
            try:
                target.symlink_to(source, target_is_directory=True)
            except OSError as exc:
                raise RuntimeError(
                    f"无法为 {name} 创建符号链接；请改用 --mode copy。原始错误：{exc}"
                ) from exc
        else:
            shutil.copytree(source, target)

        print(f"[已安装] {name}")
        installed += 1

    print(f"完成：安装 {installed} 个，跳过 {skipped} 个。")
    return 0


def strip_frontmatter(text: str) -> str:
    lines = text.splitlines()
    if not lines or lines[0].strip() != "---":
        return text.strip()
    for index in range(1, len(lines)):
        if lines[index].strip() == "---":
            return "\n".join(lines[index + 1 :]).strip()
    return text.strip()


def extract_description(text: str) -> str:
    lines = text.splitlines()
    if not lines or lines[0].strip() != "---":
        return ""
    for line in lines[1:]:
        if line.strip() == "---":
            break
        if line.startswith("description:"):
            return line.split(":", 1)[1].strip()
    return ""


def package_workbuddy(skills: dict[str, Path], output: Path) -> None:
    output.mkdir(parents=True, exist_ok=True)
    for name, source in skills.items():
        archive = output / f"{name}.zip"
        with zipfile.ZipFile(archive, "w", zipfile.ZIP_DEFLATED) as bundle:
            for item in sorted(source.rglob("*")):
                if item.is_file():
                    bundle.write(item, Path(name) / item.relative_to(source))
        print(f"[已生成] {archive}")


def package_doubao(skills: dict[str, Path], output: Path) -> None:
    output.mkdir(parents=True, exist_ok=True)
    for name, source in skills.items():
        skill_text = (source / "SKILL.md").read_text(encoding="utf-8")
        description = extract_description(skill_text)
        sections = [
            f"# {name}｜豆包办公提示词兼容版",
            "",
            "> 使用方法：将本文从“技能说明”开始复制到豆包办公的自定义技能或工作任务说明中。",
            "> 此兼容版只传递工作方法；原 Skill 中的脚本和模板需要单独上传或人工执行。",
            "",
            "## 技能说明",
            "",
            description,
            "",
            strip_frontmatter(skill_text),
        ]

        text_suffixes = {".md", ".json", ".txt", ".yaml", ".yml", ".csv"}
        reference_files = (
            sorted(
                item
                for item in (source / "references").iterdir()
                if item.is_file() and item.suffix.lower() in text_suffixes
            )
            if (source / "references").is_dir()
            else []
        )
        if reference_files:
            sections.extend(["", "## 附加参考资料"])
            for reference in reference_files:
                sections.extend(
                    [
                        "",
                        f"### {reference.name}",
                        "",
                        reference.read_text(encoding="utf-8").strip(),
                    ]
                )

        output_file = output / f"{name}.prompt.md"
        output_file.write_text("\n".join(sections).rstrip() + "\n", encoding="utf-8")
        print(f"[已生成] {output_file}")


def package(args: argparse.Namespace) -> int:
    skills = selected_skills(args.skill)
    output = Path(args.output).expanduser().resolve() / args.agent
    if args.agent == "workbuddy":
        package_workbuddy(skills, output)
    else:
        package_doubao(skills, output)
    print(f"完成：生成 {len(skills)} 个 {args.agent} 兼容包。")
    return 0


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="安装或导出《AI超级个体》OPC 配套 Skills。"
    )
    subparsers = parser.add_subparsers(dest="command", required=True)

    subparsers.add_parser("list", help="列出仓库中的全部 Skills。")

    install_parser = subparsers.add_parser(
        "install", help="安装到支持本地 SKILL.md 的智能体。"
    )
    install_parser.add_argument("--agent", choices=sorted(AGENT_TARGETS), required=True)
    install_parser.add_argument("--skill", action="append", default=[], help="只安装指定 Skill；可重复使用。")
    install_parser.add_argument("--mode", choices=("copy", "link"), default="copy")
    install_parser.add_argument("--target", help="覆盖默认安装目录。")
    install_parser.add_argument("--force", action="store_true", help="替换已存在的同名 Skill。")
    install_parser.add_argument("--dry-run", action="store_true", help="只显示计划，不写入文件。")

    package_parser = subparsers.add_parser(
        "package", help="生成 WorkBuddy 上传包或豆包办公提示词兼容包。"
    )
    package_parser.add_argument("--agent", choices=("workbuddy", "doubao"), required=True)
    package_parser.add_argument("--skill", action="append", default=[], help="只导出指定 Skill；可重复使用。")
    package_parser.add_argument("--output", default="dist", help="输出根目录，默认 dist。")

    return parser


def main() -> int:
    parser = build_parser()
    args = parser.parse_args()
    try:
        if args.command == "list":
            for name in discover_skills():
                print(name)
            return 0
        if args.command == "install":
            return install(args)
        return package(args)
    except (OSError, RuntimeError, ValueError) as exc:
        print(f"错误：{exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
