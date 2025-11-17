"""示例：运行一次数据导入与规则校验任务。"""
from pprint import pprint

from compliance.canonical.transformer import CanonicalTransformer
from compliance.config.repository import InMemoryConfigRepository
from compliance.connectors.factory import ConnectorFactory
from compliance.ingestion.pipeline import IngestionService
from compliance.rules.engine import RuleEngine


def run_demo():
    config_repo = InMemoryConfigRepository.with_demo()
    connector_factory = ConnectorFactory(config_repo)
    transformer = CanonicalTransformer()
    rule_engine = RuleEngine()

    service = IngestionService(
        config_repo=config_repo,
        connector_factory=connector_factory,
        transformer=transformer,
        rule_engine=rule_engine,
    )

    result = service.run("daily_positions")
    print("数据导入结果：")
    pprint(
        {
            "loaded": result.loaded_count,
            "rejected": result.rejected_count,
            "violations": result.violations,
            "rule_hits": result.rule_hits,
        }
    )


if __name__ == "__main__":
    run_demo()
