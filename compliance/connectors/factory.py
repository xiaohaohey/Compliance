from compliance.config.repository import InMemoryConfigRepository
from compliance.config.models import SourceConfig
from .base import DataConnector
from .data_access import DataAccessConnector
from .mysql import MySQLConnector
from .oracle import OracleConnector


class ConnectorFactory:
    """根据 SourceConfig 类型创建对应的连接器。"""

    def __init__(self, config_repo: InMemoryConfigRepository):
        self.config_repo = config_repo

    def create(self, config: SourceConfig) -> DataConnector:
        if config.type == "data_access":
            sample_data = getattr(self.config_repo, "sample_positions", [])
            return DataAccessConnector(config, sample_data)
        if config.type == "oracle":
            return OracleConnector(config)
        if config.type == "mysql":
            return MySQLConnector(config)
        raise ValueError(f"Unsupported source type: {config.type}")
