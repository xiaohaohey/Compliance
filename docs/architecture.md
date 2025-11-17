# 基金合规平台架构设计

本设计概述了一套用于多数据源整合、数据标准化以及规则校验的基金合规平台。目标是通过可配置的数据采集、统一的记录格式和灵活的规则引擎，支持基金合规的持续监控与审核。

## 核心需求
- **数据采集**：按照配置从 Data Access、Oracle、MySQL 等异构数据源读取数据。
- **目标落库**：将数据转换为统一的记录格式后导入配置指定的数据库（可为 Oracle、MySQL 或专用合规库）。
- **规则编写与校验**：基于统一数据模型与本地法规，编写和运行合规规则。
- **配置管理与可视化**：集中维护数据源、映射、调度、规则的配置，并可浏览源数据与落库后的标准化数据。

## 模块划分
1. **配置中心（Config Service）**
   - 存储数据源、目标库、表映射、调度、规则等配置。
   - 提供版本化、草稿/发布、差异对比与回滚能力。
   - 暴露 API/UI 供数据导入、规则引擎、运维门户读取配置。

2. **连接器层（Connectors）**
   - 针对 Data Access、Oracle、MySQL 等实现适配器，统一暴露读取接口（分页/游标）。
   - 支持参数化查询与行级过滤，敏感字段可在连接器侧脱敏。

3. **数据管道（Ingestion Pipeline）**
   - 由调度器触发，按配置选择连接器读取数据。
   - **预处理**：字段映射、类型转换、枚举规范化、时区/货币换算。
   - **校验**：必填校验、主键/外键存在性、数据质量规则。
   - **加载**：写入目标库的标准化表（可选分区/分片策略）。
   - **可观测性**：任务日志、指标（行数、耗时、失败原因）、告警（重试/死信队列）。

4. **统一数据模型（Canonical Model）**
   - 统一定义基金、账户、交易、估值等核心实体及字段。
   - 配置层维护“源字段 → 目标字段”的映射，支持表达式/函数（例如汇率换算）。
   - 版本化模型，确保规则与数据模型兼容。

5. **规则引擎（Rules Engine）**
   - 提供规则 DSL（或 SQL/JavaScript 表达式）与运行器。
   - 规则可以基于单表或多表关联执行，支持时间窗口、批处理与实时流式模式。
   - 支持严重性分级、阈值、白名单、豁免期限，产生审计日志与工单。

6. **规则工作台（Rules Authoring UI/API）**
   - 规则模板库（示例：持仓集中度、投资范围、异常交易频率）。
   - 规则调试：样例数据预览、即时运行、命中记录预览。
   - 版本与发布管理：草稿、审批、发布、回滚。

7. **配置与数据浏览（Data Explorer）**
   - 配置文件可视化编辑器：数据源、映射、调度、规则依赖。
   - 数据预览：查看源表（分页/字段过滤）与落库后的标准化表。
   - 任务运行历史与指标展示。

8. **安全与合规**
   - RBAC/ABAC 控制不同角色（运营、合规官、开发、审计）权限。
   - 敏感字段加密存储，传输使用 TLS，密钥/凭据托管在密钥管理服务。
   - 审计日志覆盖配置变更、规则变更、数据访问与校验结果。

## 端到端流程
1. **配置阶段**
   - 在配置中心创建数据源（连接信息、凭据）、目标库、表映射与调度计划。
   - 为新数据模型版本配置字段映射与校验规则。
   - 在规则工作台编写/复用规则模板，绑定数据模型版本。

2. **数据导入阶段**
   - 调度器按 Cron/事件触发数据管道。
   - 连接器读取源数据 → 预处理/映射 → 质量校验 → 写入目标库。
   - 记录运行日志与指标，异常进入告警与补偿流程。

3. **规则校验阶段**
   - 规则引擎读取最新发布的规则与标准化数据。
   - 执行批处理或流式校验，输出命中明细与汇总报告。
   - 结果推送至告警/工单/邮件渠道，并存档审计。

4. **运维与监控**
   - 仪表盘监控数据导入成功率、延迟、规则命中率。
   - 配置变更与规则发布均需审批与审计。

## 配置示例
```yaml
version: 1.2.0
sources:
  - id: data_access
    type: sqlserver
    conn: ${VAULT:DATA_ACCESS_URL}
    credential: ${VAULT:DATA_ACCESS_SECRET}
    query: select * from positions where biz_date = :biz_date
  - id: legacy_oracle
    type: oracle
    dsn: ${VAULT:ORACLE_DSN}
    user: ${VAULT:ORACLE_USER}
    password: ${VAULT:ORACLE_PASS}
  - id: custody_mysql
    type: mysql
    host: ${VAULT:CUSTODY_HOST}
    port: 3306
    user: ingest
    password: ${VAULT:CUSTODY_PASS}
    database: custody

target:
  type: postgres
  host: ${VAULT:CANONICAL_HOST}
  database: compliance
  table: canonical_positions

mapping:
  primary_key: [fund_code, account_no, position_date, security_code]
  fields:
    fund_code: src.fund_id
    account_no: src.account
    position_date: to_date(src.biz_date, 'YYYY-MM-DD')
    security_code: src.sec_code
    quantity: cast(src.qty as decimal(30,6))
    market_value_cny: fx_convert(src.mv, src.ccy, 'CNY')
    updated_at: now()

schedules:
  - id: daily_positions
    source: data_access
    frequency: "0 2 * * *"
    params:
      biz_date: today()
    retries: 3
    timeout: 30m

quality_rules:
  - name: required_fields
    type: required
    fields: [fund_code, account_no, security_code, quantity]
  - name: non_negative_qty
    type: expression
    expr: quantity >= 0

rule_packs:
  - id: concentration_limit
    version: 1.0
    severity: high
    rules:
      - expr: market_value_cny / fund_nav_cny <= 0.10
        message: "单一证券市值占比超 10%"
```

## 数据模型与规则对齐
- 统一数据模型需要与规则 DSL 共演进；规则中引用的字段必须存在于模型并有明确的数据类型与语义。
- 在配置发布时，进行“模型-规则兼容性”检查，避免因字段变更导致规则运行失败。
- 规则应支持元数据（责任人、合规依据条款、到期时间）以便审计。

## 交付形态
- **后端**：微服务/模块化（配置、连接器、数据管道、规则引擎、审计日志）。
- **前端**：统一控制台，提供配置管理、数据预览、规则工作台、监控面板。
- **部署**：容器化 + 编排（Kubernetes），结合 CI/CD 与配置/规则的灰度发布。

## 后续迭代建议
- 增加实时流式摄取与实时规则校验。
- 引入数据血缘与影响分析，用于评估配置/规则变更的影响面。
- 与工单系统、告警平台集成，形成闭环处理流程。
- 建立合规知识库，沉淀法规条款与规则模板的映射关系。
