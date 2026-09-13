# OPC Context：下一阶段设计

现有统一入口负责路由，模块已要求复用对话背景，适合在入口与模块之间增加共享状态；无需修改 21 个方法流程或引入数据库。本轮只使用会话上下文，不读写持久化用户档案。

建议先试点 opc-positioner → opc-modeler → mvp-validator：入口读取当前项目状态，模块只读取相关字段，完成任务返回字段增量和证据引用，入口合并。确认稳定后扩展报价、内容规划与 90 天计划。

建议状态结构（示意，null 为未知；不是 0 或 false）：

```yaml
schema_version: '1.0'
project_id: example-project
revision: 1
opc_profile:
  stage: null
  profession: null
  core_capabilities: []
  target_customer: null
business:
  positioning: null
  product: null
  pricing: null
  validation_status: null
  first_revenue: null
current_goal: null
evidence:
  interviews: []
  leads: []
  paid_orders: []
  revenue: []
next_actions: []
provenance: {}
```

provenance 按字段路径保存 status（user_fact / ai_inference / hypothesis）、source（对话轮次或用户文档定位）、observed_at、updated_by、evidence_ids。用户声明的事实与独立核验证据仍应区分：例如 first_revenue 被用户口述时标 user_fact，并注明尚未核对收款。AI 推测和假设不得自动升格为用户事实。

访谈、线索、订单、收入记录使用稳定 id、日期和来源；收入保留金额、币种、收款/退款状态，未知不计入已到账。next_actions 使用 id、行动、负责人、截止日期、完成证据与状态。相同证据 id 合并时去重，不能因跨模块重复统计收入。

实施顺序：

1. 定义 JSON Schema 和模块 read_fields / write_fields 的增量契约，先做会话交接。已有信息直接复用，仅询问影响当前任务的缺口。
2. 用户希望跨会话保存时，写到其项目目录下的 opc-context.json（不放 Skill 安装目录或仓库公共资源）。无文件能力的宿主输出可复制状态摘要，下次粘贴即可，不依赖任何平台专有 memory。
3. 用 revision 做乐观锁、临时文件原子替换；冲突时展示字段差异。新事实可以更新旧事实，但保留来源历史；推测不得覆盖事实，矛盾证据标记待澄清。支持 schema_version 迁移及备份恢复。
4. 资源查询只投影 scene、主题、阶段、行业和资源类型，不上传职业履历、客户名单、访谈原文或收入。按项目隔离，不从其他项目自动继承状态。

验收场景：已知目标客户不再询问；假设不能变成已付费；事实冲突可追溯；重复订单不重复计数；未知收入不显示零收入；中断写入保留旧版本；双写产生冲突提示；无文件宿主仍能交接；旧版本状态可迁移。持久化与这些测试均为下一阶段工作，不属于本轮已实现能力。
