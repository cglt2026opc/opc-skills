# 贡献指南

感谢你帮助改进《AI超级个体》一人公司（OPC）配套 Skills。

## 开始之前

- 提交内容应服务于明确的一人公司任务，并与书中方法或已验证的实践一致。
- 不提交客户隐私、合同原文、账号密钥、未获授权的书稿或第三方版权材料。
- 修正书中方法、数据或案例时，请在 Pull Request 中说明依据和影响范围。
- 一个 Pull Request 尽量只解决一个问题，避免混入无关格式调整。

## Skill 结构

唯一可安装入口位于 `skills/ai-super-individual/SKILL.md`，只维护路由、共用约束和模块选择边界。

21 个模块位于 `skills/ai-super-individual/references/modules/<原技能名>/`，流程文件为 `WORKFLOW.md`，保留原 frontmatter，以便导出独立包。方法修改只改模块源码，不维护第二套副本。

模块的 `references/`、`scripts/`、`assets/` 和独立导出使用的 `agents/` 保持相对位置。相对路径以模块目录为基准。不要在模块目录创建 `SKILL.md`，否则宿主可能识别出额外技能。

`catalog.json` 的 `skills` 记录唯一安装入口，`modules` 记录 21 个模块；变更路径时同步更新目录与入口链接。

## 编写要求

- 目录名和 frontmatter 中的 `name` 必须一致，使用小写字母、数字和连字符。
- `description` 同时说明“能做什么”和“何时使用”，并与相邻 Skill 保持清晰边界。
- 事实、假设和待验证项应明确区分，不把模型判断包装成市场调研或专业资质结论。
- 引用 Skill 内文件时使用相对路径；不要写入作者电脑上的绝对路径。
- 入口 `SKILL.md` 与模块 `WORKFLOW.md` 保持聚焦，较长的方法、示例或数据放入 `references/`。
- 脚本优先使用标准库，说明运行时和输入格式，并对错误输入返回清晰信息。

## 本地检查

提交前在仓库根目录运行：

```bash
python3 scripts/validate_repo.py
python3 scripts/opc_skills.py list
python3 scripts/opc_skills.py list --modules
python3 scripts/test_distribution.py
python3 scripts/build_release.py
```

如果改动了脚本，还应使用最小有效输入和至少一个错误输入实际运行。修改 Word、Excel 或图片资产时，请打开生成文件完成视觉检查。

## Pull Request 说明

请写明：

1. 修改了哪个 Skill 或仓库能力。
2. 解决了什么真实使用问题。
3. 如何验证，以及验证结果。
4. 是否改变现有触发条件、输出格式、脚本行为或配套资产。
