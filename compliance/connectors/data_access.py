from typing import Any, Dict, Iterable, List

from compliance.config.models import SourceConfig
from .base import DataConnector


class DataAccessConnector(DataConnector):
    """示例 Data Access 连接器，返回预置数据集。"""

    def __init__(self, config: SourceConfig, sample_data: List[Dict[str, Any]]):
        super().__init__(config)
        self._sample_data = sample_data

    def fetch(self) -> Iterable[Dict[str, Any]]:
        # 实际实现会使用数据库连接或 API 客户端按 query + params 拉取数据
        # 这里为了演示直接返回内存数据
        return list(self._sample_data)
