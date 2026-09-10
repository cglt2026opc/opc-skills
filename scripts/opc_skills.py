#!/usr/bin/env python3
"""Install or package the OPC book companion skills for supported agents."""

from __future__ import annotations

import argparse
import contextlib
import shutil
import sys
import tempfile
import zipfile
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parent.parent
SKILLS_ROOT = REPO_ROOT / "skills"
DEFAULT_SKILL = "ai-super-individual"
MODULES_ROOT = SKILLS_ROOT / DEFAULT_SKILL / "references" / "modules"

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


def discover_modules() -> dict[str, Path]:
    return {
        path.name: path for path in sorted(MODULES_ROOT.iterdir())
        if (path / "WORKFLOW.md").is_file()
    }


@contextlib.contextmanager
def selected_skills(names: list[str]):
    """Export optional standalone skills from the canonical modules."""
    available = discover_skills()
    modules = discover_modules()
    if not names:
        yield available
        return
    missing = sorted(set(names) - set(available) - set(modules))
    if missing:
        raise ValueError(f"未知 Skill：{', '.join(missing)}。运行 list --modules 查看模块。")
    with tempfile.TemporaryDirectory(prefix="opc-standalone-") as temporary:
        selected = {}
        for name in dict.fromkeys(names):
            if name in available:
                selected[name] = available[name]
            else:
                target = Path(temporary) / name
                shutil.copytree(modules[name], target, ignore=shutil.ignore_patterns("__pycache__", "*.pyc", ".DS_Store"))
                (target / "WORKFLOW.md").rename(target / "SKILL.md")
                selected[name] = target
        yield selected


def install(args: argparse.Namespace) -> int:
    if args.mode == "link" and any(name in discover_modules() for name in args.skill):
        raise ValueError("独立模块导出仅支持 --mode copy；集成版支持 --mode link。")
    with selected_skills(args.skill) as skills:
        return install_selected(args, skills)


def install_selected(args: argparse.Namespace, skills: dict[str, Path]) -> int:
    target_root = (
        Path(args.target).expanduser().resolve()
        if args.target
        else AGENT_TARGETS[args.agent]
    )

    print(f"目标智能体：{args.agent}")
    print(f"安装目录：{target_root}")
    old_names = [name for name in discover_modules() if (target_root / name).exists() or (target_root / name).is_symlink()]
    if DEFAULT_SKILL in skills and old_names:
        print(f"[迁移提示] 检测到 {len(old_names)} 个旧版独立技能；本次保留，请在确认集成版可用后自行停用或移除。")
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
            shutil.copytree(source, target, ignore=shutil.ignore_patterns("__pycache__", "*.pyc", ".DS_Store"))

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
                if (item.is_file() and item.name not in {".DS_Store", "Thumbs.db"}
                        and "__pycache__" not in item.parts and item.suffix not in {".pyc", ".pyo"}):
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
    output = Path(args.output).expanduser().resolve() / args.agent
    # A paste-only host cannot follow a local router: export the modules directly.
    names = args.skill
    missing = set(names) - set(discover_skills()) - set(discover_modules())
    if missing:
        raise ValueError(f"未知 Skill：{', '.join(sorted(missing))}。")
    if args.agent == "doubao" and (not names or DEFAULT_SKILL in names):
        names = list(discover_modules())
    with selected_skills(names) as skills:
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

    list_parser = subparsers.add_parser("list", help="列出默认安装的集成技能。")
    list_parser.add_argument("--modules", action="store_true", help="列出可选的 21 个独立模块。")

    install_parser = subparsers.add_parser(
        "install", help="安装到支持本地 SKILL.md 的智能体。"
    )
    install_parser.add_argument("--agent", choices=sorted(AGENT_TARGETS), required=True)
    install_parser.add_argument("--skill", action="append", default=[], help="默认安装一个集成技能；指定旧模块名可单独安装，可重复使用。")
    install_parser.add_argument("--mode", choices=("copy", "link"), default="copy")
    install_parser.add_argument("--target", help="覆盖默认安装目录。")
    install_parser.add_argument("--force", action="store_true", help="替换已存在的同名 Skill。")
    install_parser.add_argument("--dry-run", action="store_true", help="只显示计划，不写入文件。")

    package_parser = subparsers.add_parser(
        "package", help="生成 WorkBuddy 上传包或豆包办公提示词兼容包。"
    )
    package_parser.add_argument("--agent", choices=("workbuddy", "doubao"), required=True)
    package_parser.add_argument("--skill", action="append", default=[], help="默认导出集成版（豆包为模块提示词）；指定模块名可单独导出。")
    package_parser.add_argument("--output", default="dist", help="输出根目录，默认 dist。")

    return parser


def main() -> int:
    parser = build_parser()
    args = parser.parse_args()
    try:
        if args.command == "list":
            for name in (discover_modules() if args.modules else discover_skills()):
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
