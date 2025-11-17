from typing import Any, Dict, Iterable

from compliance.config.models import SourceConfig


class DataConnector:
    """数据源连接器抽象，负责按配置读取数据。"""

    def __init__(self, config: SourceConfig):
        self.config = config

    def fetch(self) -> Iterable[Dict[str, Any]]:
        """读取数据，返回字典序列。"""
        raise NotImplementedError
