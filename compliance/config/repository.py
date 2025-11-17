"""提供从数据库或其他存储读取配置的接口与内存实现。"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, Iterable, List

from .models import PipelineConfig, RuleConfig, SourceConfig, TargetConfig, QualityRule


class ConfigRepository:
    """配置仓库抽象，可由数据库实现。"""

    def get_pipeline(self, pipeline_id: str) -> PipelineConfig:
        raise NotImplementedError

    def list_rules(self, pipeline_id: str) -> Iterable[RuleConfig]:
        raise NotImplementedError


@dataclass
class _DemoData:
    pipelines: Dict[str, PipelineConfig]
    rules: Dict[str, List[RuleConfig]]


class InMemoryConfigRepository(ConfigRepository):
    """使用内存数据来模拟配置中心，便于演示与测试。"""

    def __init__(self, data: _DemoData):
        self._data = data

    @classmethod
    def with_demo(cls) -> "InMemoryConfigRepository":
        from datetime import datetime

        # 样例源数据：模拟 Data Access 返回的持仓记录
        sample_positions = [
            {
                "fund_id": "F001",
                "account": "A-01",
                "biz_date": "2024-05-01",
                "sec_code": "600000",
                "qty": 1_000_000,
                "mv": 1_050_000.0,
                "ccy": "CNY",
                "fund_nav": 10_500_000.0,
            },
            {
                "fund_id": "F001",
                "account": "A-01",
                "biz_date": "2024-05-01",
                "sec_code": "600111",
                "qty": -5,  # 非法数量，质量规则会拦截
                "mv": 30_000.0,
                "ccy": "CNY",
                "fund_nav": 10_500_000.0,
            },
        ]

        source = SourceConfig(
            id="data_access_positions",
            type="data_access",
            connection={"url": "jdbc:data-access"},
            query="select * from positions",
            params={"as_of": "2024-05-01"},
        )
        target = TargetConfig(
            type="compliance_db",
            table="canonical_positions",
            connection={"dsn": "compliance.db"},
        )

        def _map_date(src):
            return datetime.fromisoformat(src["biz_date"]).date()

        pipeline = PipelineConfig(
            id="daily_positions",
            source=source,
            target=target,
            field_mappings={
                "fund_code": lambda src: src["fund_id"],
                "account_no": lambda src: src["account"],
                "position_date": _map_date,
                "security_code": lambda src: src["sec_code"],
                "quantity": lambda src: float(src["qty"]),
                "market_value_cny": lambda src: float(src["mv"]),
                "fund_nav_cny": lambda src: float(src.get("fund_nav", 0.0)),
            },
            required_fields=["fund_code", "account_no", "security_code", "quantity"],
            quality_rules=[
                QualityRule(
                    name="non_negative_quantity",
                    check=lambda record: record.get("quantity", 0) >= 0,
                    message="数量不能为负数",
                ),
                QualityRule(
                    name="has_market_value",
                    check=lambda record: record.get("market_value_cny", 0) > 0,
                    message="市值必须大于 0",
                ),
            ],
        )

        rules = [
            RuleConfig(
                name="concentration_limit",
                description="单一证券市值占比不得超过 10%",
                severity="high",
                apply=lambda rec: None
                if rec["fund_nav_cny"] == 0 or rec["market_value_cny"] / rec["fund_nav_cny"] <= 0.10
                else "单一证券市值占比超 10%",
            ),
            RuleConfig(
                name="non_negative_quantity",
                description="持仓数量应大于等于 0",
                severity="medium",
                apply=lambda rec: None if rec.get("quantity", 0) >= 0 else "数量为负数",
            ),
        ]

        demo = _DemoData(
            pipelines={pipeline.id: pipeline},
            rules={pipeline.id: rules},
        )

        repo = cls(demo)
        # 将样例数据放在实例属性上，连接器会读取
        repo.sample_positions = sample_positions
        return repo

    def get_pipeline(self, pipeline_id: str) -> PipelineConfig:
        if pipeline_id not in self._data.pipelines:
            raise KeyError(f"Pipeline '{pipeline_id}' not found")
        return self._data.pipelines[pipeline_id]

    def list_rules(self, pipeline_id: str):
        return self._data.rules.get(pipeline_id, [])
