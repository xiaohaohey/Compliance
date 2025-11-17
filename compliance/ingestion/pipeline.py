from dataclasses import dataclass
from typing import Dict, Iterable, List

from compliance.canonical.transformer import CanonicalTransformer
from compliance.config.models import PipelineConfig
from compliance.config.repository import ConfigRepository
from compliance.connectors.factory import ConnectorFactory
from compliance.rules.engine import RuleEngine
from .target import InMemoryTargetWriter


@dataclass
class IngestionResult:
    loaded_count: int
    rejected_count: int
    violations: List[str]
    rule_hits: Dict[str, List[str]]


class IngestionService:
    """调度数据导入、质量校验与规则执行。"""

    def __init__(
        self,
        config_repo: ConfigRepository,
        connector_factory: ConnectorFactory,
        transformer: CanonicalTransformer,
        rule_engine: RuleEngine,
    ) -> None:
        self.config_repo = config_repo
        self.connector_factory = connector_factory
        self.transformer = transformer
        self.rule_engine = rule_engine

    def run(self, pipeline_id: str) -> IngestionResult:
        pipeline = self.config_repo.get_pipeline(pipeline_id)
        connector = self.connector_factory.create(pipeline.source)
        raw_records = list(connector.fetch())

        transformed: List[Dict] = []
        violations: List[str] = []

        for raw in raw_records:
            canonical = self.transformer.transform(raw, pipeline.field_mappings)
            missing = [field for field in pipeline.required_fields if not canonical.get(field)]
            if missing:
                violations.append(f"缺少必填字段: {','.join(missing)}")
                continue

            failed_rules = [
                rule.message for rule in pipeline.quality_rules if not rule.check(canonical)
            ]
            if failed_rules:
                violations.extend(failed_rules)
                continue

            transformed.append(canonical)

        writer = InMemoryTargetWriter(pipeline.target)
        writer.write(transformed)

        # 运行合规规则
        rule_hits = self.rule_engine.run_rules(
            records=writer.storage,
            rules=self.config_repo.list_rules(pipeline_id),
        )

        return IngestionResult(
            loaded_count=len(writer.storage),
            rejected_count=len(raw_records) - len(writer.storage),
            violations=violations,
            rule_hits=rule_hits,
        )
