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
