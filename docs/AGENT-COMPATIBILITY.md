# 智能体兼容与安装指南

本仓库以开放的 `SKILL.md` 目录结构维护同一套 Skills，并按各平台当前公开能力提供原生安装或兼容导出。

默认安装一个 `ai-super-individual` 技能，内含书中 21 个 OPC 实战模块。单独技能包为可选导出；豆包提示词兼容版保留按模块选择。

## 支持级别

| 平台 | 支持级别 | 安装位置或方式 | 调用方式 |
| --- | --- | --- | --- |
| Codex | 原生 | `~/.agents/skills/` | `$skill-name` 或自然语言触发 |
| Cursor | 原生 | `~/.agents/skills/` | `/skill-name` 或自然语言触发 |
| Gemini CLI | 原生 | `~/.agents/skills/` | `/skills` 管理或自然语言触发 |
| GitHub Copilot | 原生 | `~/.agents/skills/` | `/skill-name` 或自然语言触发 |
| OpenClaw | 原生 | `~/.openclaw/skills/` | Skill 名称或自然语言触发 |
| Hermes Agent | 原生 | `~/.hermes/skills/opc-skills/` | `/skill-name` 或自然语言触发 |
| WorkBuddy | 原生导入 | 在技能页面上传 ZIP 包 | 在对话中选择或自动触发 |
| 千问办公 / QwenWork | 原生 | `~/.qwenwork/skills/` 或界面上传 | `/skill-name`、指定调用或自动触发 |
| 豆包办公 | 提示词兼容 | 导入生成的 `.prompt.md` 内容 | 在自定义技能或工作任务中使用 |

“原生”表示平台公开支持以 `SKILL.md` 为入口的技能目录。“提示词兼容”表示保留核心方法和工作流，但脚本、模板、自动触发与工具调用能力取决于平台，不能视为完整的 Agent Skills 运行时。

## 使用跨平台工具

查看默认集成技能（使用 `list --modules` 查看 21 个模块）：

```bash
python3 scripts/opc_skills.py list
```

安装集成技能（只安装一个入口）：

```bash
python3 scripts/opc_skills.py install --agent openclaw
python3 scripts/opc_skills.py install --agent hermes
python3 scripts/opc_skills.py install --agent qwenwork
```

可选：只安装某个独立模块：

```bash
python3 scripts/opc_skills.py install \
  --agent openclaw \
  --skill mvp-validator
```

默认使用复制模式，不会覆盖同名 Skill。开发时可以使用符号链接，让源文件更新立即生效：

```bash
python3 scripts/opc_skills.py install --agent hermes --mode link
```

先预览安装计划：

```bash
python3 scripts/opc_skills.py install --agent qwenwork --dry-run
```

## OpenClaw

OpenClaw 支持工作区 `skills/`、工作区 `.agents/skills/`、个人 `~/.agents/skills/` 和共享的 `~/.openclaw/skills/`。本工具默认安装到 `~/.openclaw/skills/`，供本机 OpenClaw 智能体使用。

```bash
python3 scripts/opc_skills.py install --agent openclaw
```

也可以使用 OpenClaw 自带命令安装集成目录：

```bash
openclaw skills install ./skills/ai-super-individual
```

## Hermes Agent

Hermes 的技能根目录是 `~/.hermes/skills/`，并允许按类别建立子目录。本工具将这套书籍 Skills 放在 `opc-skills/` 分类下：

```bash
python3 scripts/opc_skills.py install --agent hermes
hermes skills list
```

本仓库已作为公开的自定义 Hermes Tap 提供，也可以通过 Skills Hub 直接安装：

```bash
hermes skills tap add cglt2026opc/opc-skills
hermes skills search ai-super-individual --source github
hermes skills install cglt2026opc/opc-skills/skills/ai-super-individual
```

安装后在对话中使用 `/ai-super-individual`。只安装单个技能时，可以省略 `tap add`，直接执行完整路径的安装命令。Hub 安装会执行安全扫描并记录来源，安装位置由 Hermes 管理；上面的本地安装器则使用 `opc-skills/` 分类目录，两种方式选择一种即可。

这是可订阅的社区 Tap，不代表进入 Hermes 官方默认技能源。维护者将更新推送至本仓库默认分支后，用户即可从同一路径获取新版。Tap 目录规范见 [Hermes 官方发布说明](https://hermes-agent.nousresearch.com/docs/user-guide/features/skills#publishing-a-custom-skill-tap)。

## WorkBuddy

WorkBuddy 支持从界面上传本地技能包，并兼容 OpenClaw 生态 Skill。默认生成一个集成 ZIP：

```bash
python3 scripts/opc_skills.py package --agent workbuddy
```

文件生成到 `dist/workbuddy/ai-super-individual.zip`，内含一个技能入口与 21 个模块。在 WorkBuddy 中打开“专家·技能·连接器”→“技能”→“添加技能”→“上传技能”，选择该集成 ZIP。使用 `--skill mvp-validator` 可另外导出独立包。Release 的 `workbuddy-pack.zip` 需先解压，再上传里面的 `ai-super-individual.zip`。

发布到 WorkBuddy 技能市场时，还需根据开放平台要求补充 `description_zh`、`description_en`、`version`、`author` 等上架元数据，并完成平台审核；本地上传包与市场发行包不能混为一谈。

## 千问办公 / QwenWork

千问办公将 Skill 保存于 `~/.qwenwork/skills/`，支持从 GitHub 获取、文件系统安装或在界面上传：

```bash
python3 scripts/opc_skills.py install --agent qwenwork
```

也可以把单个 Skill 目录或其中的 `SKILL.md` 与辅助文件，通过“扩展”→“技能”→“安装技能”上传。

## 豆包办公

豆包工作任务模式公开支持自定义技能与办公工作流，但当前没有在公开产品文档中确认一个与开放 Agent Skills 完全一致、长期稳定的本地目录规范。因此本仓库提供提示词兼容导出：

```bash
python3 scripts/opc_skills.py package --agent doubao
```

生成文件位于 `dist/doubao/`。默认导出 21 份模块提示词，不是一个可按需读取本地文件的集成技能。每个 `.prompt.md` 会包含 Skill 主流程和 Markdown 参考资料，可粘贴到豆包的自定义技能或工作任务说明中。

该方式不会自动携带 Python 脚本、Word/Excel 模板或宿主工具权限。使用包含这些资源的 Skill 时，应把模板作为附件另外上传，并在豆包界面中检查实际可用工具。

## 旧版迁移

新安装默认只有一个技能。此前的 21 个独立技能不会自动删除；确认集成版可用后，在平台中停用或移除它们。旧版源目录已迁移，之前安装的旧符号链接需要移除并重新安装。独立模块导出只支持复制模式，集成版支持符号链接。

## 安全与维护

- 第三方智能体拥有的文件、终端、网络和账号权限各不相同；安装前检查 `SKILL.md` 与脚本。
- 默认安装模式不会覆盖现有同名目录。只有明确需要替换时才使用 `--force`。
- 不把客户隐私、合同原文、账号密码或 API Key 写入 Skill、模板和提示词包。
- 平台升级可能改变安装目录或导入字段。发行新版本前，应依据各平台官方文档重新验证。

## 官方参考

- [Agent Skills 开放规范](https://agentskills.io/specification)
- [OpenClaw Skills](https://docs.openclaw.ai/skills)
- [Hermes Agent Skills System](https://hermes-agent.nousresearch.com/docs/user-guide/features/skills)
- [WorkBuddy 技能](https://www.workbuddy.cn/docs/workbuddy/From-Beginner-to-Expert-Guide/Function-Description/Skills-Market)
- [WorkBuddy 开放平台技能结构](https://open.workbuddy.cn/docs/skill)
- [千问办公 Skills](https://docs.qwenwork.ai/zh/desktop/skills)
