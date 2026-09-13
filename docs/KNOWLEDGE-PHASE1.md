# 知识资源层第一阶段交付

在原结构上增量升级：一个 ai-super-individual 入口，保留书中 21 个模块，增加 knowledge-explorer，共 22 个内部模块。版本元数据为 0.3.0，尚未发布远端版本。

## 架构

当前任务 → 原工作流交付核心成果 → 按需 knowledge-explorer → ACCESS 契约 → query_resources.py → 公共映射与本地索引 → 相关性复核后推荐。

直接找资料也可进入 knowledge-explorer。5 个显式接入模块为 opc-positioner、opc-modeler、mvp-validator、content-planner、ai-team-builder；resource-explorer 只补充分工边界。没有重写其余模块。公共映射覆盖 22 个模块，首批本地索引为 5 条真实页面元数据，不代表全站覆盖，也不代表已读全文或具备下载权限。

## 自动验证结果

- `python3 scripts/validate_repo.py`：通过，一个入口、22 个模块、frontmatter 与路由引用有效。
- skill-creator 的 quick_validate.py：通过。
- `python3 scripts/test_distribution.py`：3 项通过，覆盖默认安装、既有文件保留、force/迁移提示、符号链接、WorkBuddy ZIP、所有独立模块链接和豆包导出数量。
- `python3 scripts/test_resources.py`：8 项通过，覆盖索引一致性、PMF 查询、Excel/Word/PPT 格式区分、无关与零结果、阶段/行业/类型过滤、去重、模拟及下架记录排除、非法输入、损坏索引、导出后独立查询、所有本地 agent 目标及豆包共享文本。
- `python3 scripts/build_release.py --output /tmp/opc-skills-phase1-release`：构建并验证 26 个 ZIP（1 个集成包、22 个模块包、3 个汇总/兼容包）。
- `git diff --check`：通过。

## 对话验收用例（供宿主实机复测）

| 输入/背景 | 预期行为 |
| --- | --- |
| “有没有 PMF 自检表？” | knowledge-explorer 返回真实 PMF 条目，说明适用场景、用途、地址和快照状态，不凑 3 条 |
| “帮我选择预算 200 元的 AI 工具组合” | resource-explorer 处理选型和预算，不以知识资料替代工具方案 |
| 已给目标客户，要求定位方案 | 复用背景、先完成定位；仅下一步确需画布时补充资源 |
| “有没有量子农业白皮书？” | 本地无匹配时明确索引未覆盖，不推荐商业模式模板或首页 |
| “帮我找 GEO 模板” | 当前数据未覆盖时不把普通内容创作教程冒充 GEO 模板 |
| “不要再推荐资料，直接给行动计划” | 不附加资源推荐，完成行动计划 |
| 无 Python 的宿主查资料 | 读取 JSON 按契约人工筛选，说明本地快照，不声称执行脚本 |
| 已付费证据缺失，模型曾推测需求成立 | 推测保留为推测/假设，不记为付费事实，不重复询问已有用户事实 |

以上对话用例是验收预期，不宣称已运行各平台模型对话。

## 向后兼容与后续范围

Codex、OpenClaw、Hermes 等原目标目录及 copy/link 机制保持；WorkBuddy ZIP 仍只有一个入口。旧模块导出自动携带共享依赖并重写相对链接；豆包递归内嵌说明和 JSON。测试使用临时目录，未改动用户已安装的 Skill。没有各客户端实机验收，因此平台执行能力限制仍按原兼容指南。

[API 契约](../skills/ai-super-individual/references/resources/ACCESS.md)预留 keywords、scene、stage、type、limit 及可选 industry，定义结果 envelope、错误、缓存、回退与 provider 替换。后续已接入用户提供的 api.cgltzk.vip/mapp/search/ 关键词接口；统一接口仍为未来设计。

[OPC Context 建议](../skills/ai-super-individual/references/resources/OPC-CONTEXT.md)评估架构适配性，建议先试点定位→商业模式→MVP，使用带来源与事实状态的增量字段；项目级持久化、版本迁移与并发冲突处理留到下一阶段。

## 修改文件

- [.github/workflows/validate.yml](../.github/workflows/validate.yml)
- [CONTRIBUTING.md](../CONTRIBUTING.md)
- [README.md](../README.md)
- [catalog.json](../catalog.json)
- [docs/AGENT-COMPATIBILITY.md](../docs/AGENT-COMPATIBILITY.md)
- [scripts/build_release.py](../scripts/build_release.py)
- [scripts/opc_skills.py](../scripts/opc_skills.py)
- [scripts/test_distribution.py](../scripts/test_distribution.py)
- [scripts/validate_repo.py](../scripts/validate_repo.py)
- [skills/ai-super-individual/SKILL.md](../skills/ai-super-individual/SKILL.md)
- [skills/ai-super-individual/agents/openai.yaml](../skills/ai-super-individual/agents/openai.yaml)
- [skills/ai-super-individual/references/modules/ai-team-builder/WORKFLOW.md](../skills/ai-super-individual/references/modules/ai-team-builder/WORKFLOW.md)
- [skills/ai-super-individual/references/modules/content-planner/WORKFLOW.md](../skills/ai-super-individual/references/modules/content-planner/WORKFLOW.md)
- [skills/ai-super-individual/references/modules/mvp-validator/WORKFLOW.md](../skills/ai-super-individual/references/modules/mvp-validator/WORKFLOW.md)
- [skills/ai-super-individual/references/modules/opc-modeler/WORKFLOW.md](../skills/ai-super-individual/references/modules/opc-modeler/WORKFLOW.md)
- [skills/ai-super-individual/references/modules/opc-positioner/WORKFLOW.md](../skills/ai-super-individual/references/modules/opc-positioner/WORKFLOW.md)
- [skills/ai-super-individual/references/modules/resource-explorer/WORKFLOW.md](../skills/ai-super-individual/references/modules/resource-explorer/WORKFLOW.md)
- [scripts/test_resources.py](../scripts/test_resources.py)
- [skills/ai-super-individual/references/modules/knowledge-explorer/WORKFLOW.md](../skills/ai-super-individual/references/modules/knowledge-explorer/WORKFLOW.md)
- [skills/ai-super-individual/references/resources/ACCESS.md](../skills/ai-super-individual/references/resources/ACCESS.md)
- [skills/ai-super-individual/references/resources/OPC-CONTEXT.md](../skills/ai-super-individual/references/resources/OPC-CONTEXT.md)
- [skills/ai-super-individual/references/resources/cgltzk-resources.json](../skills/ai-super-individual/references/resources/cgltzk-resources.json)
- [skills/ai-super-individual/references/resources/query_resources.py](../skills/ai-super-individual/references/resources/query_resources.py)
- [skills/ai-super-individual/references/resources/resource-map.json](../skills/ai-super-individual/references/resources/resource-map.json)
- [docs/KNOWLEDGE-PHASE1.md](../docs/KNOWLEDGE-PHASE1.md)

保留用户原有未跟踪文件 `副业启动方案_初版.md`，未修改或加入发布包。

## 现有搜索 API 接入补充（2026-09-13）

新增 `references/resources/http_resources.py` 与 `scripts/test_http_resources.py`；查询入口增加 --provider http，默认仍 local。在线仅收集文档导航必要字段，清理标题高亮，按 id 生成已确认模式的详情地址；类型标为推断，阶段/行业留给工作流复核。错误不隐藏、不自动重试或回退。

7 项 HTTP 离线契约测试覆盖中文编码、字段映射、过滤去重、数量限制、空结果、未知类型、模块词映射、不支持的标签、错误结构、超时及 HTTP 错误。实测“智慧养老”接口返回上游 count=15，报告类型筛选得到 3 条；详情页 /doc/30343/ 标题与 API 一致。快照和下载权限边界保持不变。

## 回答后的专题引导

新增共享规则 `references/resources/FOLLOW-UP.md`，由统一入口及 knowledge-explorer 按需读取；完整交付后可追问一个行动问题，系统学习或书籍配套场景优先引导 https://www.cgltzk.vip/book/opc.html。未批量重写原有模块。

对话复测：定位完成且希望了解完整路径时可带专题链接并追问商业画布；只需访谈提纲时先完成产物，不强制引导；用户拒绝推荐或刚提供过链接时不重复；资源搜索无结果时不以专题页冒充命中资源。

## OPC 研究模式融合

基于用户提供的 opc-research-guide 功能介绍，采用 knowledge-explorer 内部研究模式，不新增顶层 Skill 或第 23 个模块。新增共享 RESEARCH.md，更新统一入口、knowledge-explorer 路由与 README；未读取或复制外部 Skill 源码，未独立核验其安装量。

行为验收用例（供模型实测，非自动执行结果）：

| 输入 | 应有行为 |
| --- | --- |
| 找 3 份 OPC 报告 | 资源导航，不强制写全景报告 |
| 分析 OPC 市场前景 | 研究模式，区分 OPC 与邻近市场数据，关键结论有来源 |
| 拆解指定人物产品收入案例 | 先核实人物产品与收入来源，自述和独立事实分开；不虚构七步细节 |
| OPC 有哪些补贴，未给地区 | 可先查全国层面并询问省市，不猜当地政策 |
| 给我三档报价 | 进入 value-pricer，不先走研究报告 |
| 无浏览能力要求最新政策 | 说明能力缺口，提供有限范围分析或待核实清单，不伪造现行政策 |
| 研究报告需要 8 个关键证据 | 允许超过 5 个引用，推荐清单上限不限制证据数量 |

新增共享引用沿用独立包依赖复制和豆包递归内嵌机制；默认安装及模块数量保持不变。

## 在线自测引导补充

统一入口与共享 FOLLOW-UP.md 增加在线自测可选引导；5 个自测/诊断模块增加轻量引用，不改变原有评分。独立导出支持直接引用公共资源的模块，自动复制依赖和重写相对路径。

行为验收：询问“在哪在线测”时给 assessments.html 及对应测评名；对话测评进行中不中断；已提交网页结果时复用，不声称自动同步；评分口径不明时不混算；拒绝推荐时不加链接；不同时堆叠专题和自测入口。
