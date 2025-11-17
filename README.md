# Compliance

基金合规平台的目标是将异构数据源（Data Access、Oracle、MySQL 等）采集到统一的数据模型中，并基于统一数据进行规则编写与校验。

- 架构概览与设计要点参见 [docs/architecture.md](docs/architecture.md)。
- 侧重能力：可配置的数据导入、标准化落库、规则工作台、规则执行与审计。

## Python 示例
仓库包含一个基于 Python 的轻量级演示，覆盖配置读取、连接器、标准化映射、数据质量校验与规则执行：

```bash
python -m compliance.main
```

输出会显示加载/拒绝的数据行数、质量检查失败原因以及规则命中情况，便于快速验证端到端流程。

## 如何检查是否已经实现功能
1. **查看示例配置**：打开 `compliance/config/repository.py` 中的 `IN_MEMORY_CONFIG`，确认数据源、目标库以及字段映射均已定义。
2. **运行端到端流程**：执行 `python -m compliance.main`，终端输出会展示连接器读取的数据、标准化后的字段、数据质量校验（如缺失必填字段）、以及规则引擎判定的合规/不合规条目。
3. **验证规则执行**：在输出中查找 `rule_results` 部分，确认每条规则的命中与否；同时可在 `compliance/rules/engine.py` 的 `RuleDefinition` 列表中查看规则内容。
4. **调整配置并重跑**：修改 `IN_MEMORY_CONFIG` 的规则或字段映射（例如新增必填字段或阈值），再次运行 `python -m compliance.main`，通过对比输出验证配置变更是否生效。

如需进一步扩展，可按照 `docs/architecture.md` 中的架构说明接入真实数据库连接器或配置存储。
