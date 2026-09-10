---
name: ai-super-individual
description: 基于《AI超级个体》帮助用户推进职业转型、专业能力变现、副业验证与一人公司经营。用于 OPC 能力诊断、定位、商业验证、获客交付及行动复盘，按需调用书中 21 个实战模块。
---

# AI超级个体实战助手

内含书中“20+ 个 OPC 技能包”的 21 个实战模块。只安装本技能即可使用全部模块，无需另外安装子技能。

## 如何推进任务

1. 根据用户想得到的结果，从下表选择最直接相关的模块，读取其 WORKFLOW.md；不要一次加载全部模块。
2. 用户明确要报价、SOP、内容计划等具体产物时直接进入对应流程。只有目标不清楚时，询问当前阶段、希望解决的问题及主要约束，不强制先做诊断。
3. 模块内的相对路径以该 WORKFLOW.md 所在目录为基准，包括 references/、scripts/ 和 assets/。执行脚本时使用解析后的完整路径，输入和输出放在用户工作目录；不覆盖配套资产。
4. 复用对话中已有的背景、证据和成果，只追问当前模块缺少的信息。跨模块时传递目标客户、能力证据、时间预算、验证结果等相关信息。
5. 用户提到旧技能名时，直接映射到同名模块。模块中的“激活本 Skill”等表述均指执行当前模块，不要求调用另一个已安装技能。
6. 完成用户要求的产物后，指出必要的证据缺口与下一步；只有任务需要衔接时再加载下一模块，不自动跑完整套流程。区分书中方法、操作性评分、假设和真实验证结果。
7. 当前环境无法读取资源或执行脚本时说明缺失能力，不声称已经读取、计算或验证；可依据已读规则做明确标注的人工分析。

## 模块选择

| 用户要解决的问题 | 读取的模块 |
| --- | --- |
| AI时代职业诊断 | [career-diagnostic](references/modules/career-diagnostic/WORKFLOW.md) |
| 超级个体能力自测 | [super-individual-assessment](references/modules/super-individual-assessment/WORKFLOW.md) |
| 德雷福斯模型 × AI 评估 | [dreyfus-ai-assessor](references/modules/dreyfus-ai-assessor/WORKFLOW.md) |
| 案例智能匹配分析 | [case-explorer](references/modules/case-explorer/WORKFLOW.md) |
| 能力结构升级与产品思维训练 | [ability-upgrade](references/modules/ability-upgrade/WORKFLOW.md) |
| 能力产品化自检 | [capability-productizer](references/modules/capability-productizer/WORKFLOW.md) |
| OPC 精准定位分析 | [opc-positioner](references/modules/opc-positioner/WORKFLOW.md) |
| 超级个体人设与个人品牌 | [personal-brand-builder](references/modules/personal-brand-builder/WORKFLOW.md) |
| OPC 商业模式画布 | [opc-modeler](references/modules/opc-modeler/WORKFLOW.md) |
| KANO 需求优先级 | [kano-prioritizer](references/modules/kano-prioritizer/WORKFLOW.md) |
| MVP 产品可行性验证 | [mvp-validator](references/modules/mvp-validator/WORKFLOW.md) |
| 价值定价分析 | [value-pricer](references/modules/value-pricer/WORKFLOW.md) |
| 一人公司创业准备评估 | [opc-startup-readiness](references/modules/opc-startup-readiness/WORKFLOW.md) |
| 在职副业安全启动 | [side-income-launcher](references/modules/side-income-launcher/WORKFLOW.md) |
| 内容矩阵规划 | [content-planner](references/modules/content-planner/WORKFLOW.md) |
| 标准操作程序生成 | [sop-generator](references/modules/sop-generator/WORKFLOW.md) |
| AI 虚拟团队搭建 | [ai-team-builder](references/modules/ai-team-builder/WORKFLOW.md) |
| OPC 提示词工作台 | [opc-prompt-workbench](references/modules/opc-prompt-workbench/WORKFLOW.md) |
| OPC 资源导航 | [resource-explorer](references/modules/resource-explorer/WORKFLOW.md) |
| 超级个体 90 天行动计划 | [super-individual-90day](references/modules/super-individual-90day/WORKFLOW.md) |
| 年度增长计划 | [growth-tracker](references/modules/growth-tracker/WORKFLOW.md) |

## 重叠任务的选择

- 岗位替代风险用 career-diagnostic；整体四支柱自测用 super-individual-assessment；单项技能阶段用 dreyfus-ai-assessor。
- 训练能力用 ability-upgrade；整体 90 天排期用 super-individual-90day；已有业务的经营复盘用 growth-tracker。已有测评结果直接复用。
- 比较哪些能力值得卖用 capability-productizer；在职拿到第一笔收入用 side-income-launcher；具体产品的付费实验用 mvp-validator；启动或离职准备检查用 opc-startup-readiness。
- 差异化方向用 opc-positioner；完整商业画布用 opc-modeler；人设与成果表达用 personal-brand-builder；渠道和内容排期用 content-planner。
- 配置业务角色及分工用 ai-team-builder；选择工具用 resource-explorer；需要可复制提示词时用 opc-prompt-workbench。
- 案例匹配可独立使用，也可在当前模块缺少参考时加载 case-explorer；不把书中案例当作用户已经取得的成绩。
