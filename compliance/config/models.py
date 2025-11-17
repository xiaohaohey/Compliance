from dataclasses import dataclass, field
from typing import Any, Callable, Dict, List, Optional


@dataclass
class SourceConfig:
    """配置一个源数据库或数据 API."""

    id: str
    type: str
    connection: Dict[str, Any]
    query: Optional[str] = None
    params: Dict[str, Any] = field(default_factory=dict)


@dataclass
class TargetConfig:
    """落库目标配置，可以指向任何兼容的数据库。"""

    type: str
    table: str
    connection: Dict[str, Any]


@dataclass
class QualityRule:
    """数据质量检查规则（在落库前执行）。"""

    name: str
    check: Callable[[Dict[str, Any]], bool]
    message: str


@dataclass
class PipelineConfig:
    """单个数据导入任务的配置。"""

    id: str
    source: SourceConfig
    target: TargetConfig
    # target field -> mapping function that receives the source record
    field_mappings: Dict[str, Callable[[Dict[str, Any]], Any]]
    required_fields: List[str] = field(default_factory=list)
    quality_rules: List[QualityRule] = field(default_factory=list)


@dataclass
class RuleConfig:
    """合规规则配置，运行在标准化数据之上。"""

    name: str
    description: str
    severity: str
    apply: Callable[[Dict[str, Any]], Optional[str]]
