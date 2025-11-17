from typing import Any, Dict, Iterable

from compliance.config.models import SourceConfig
from .base import DataConnector


class MySQLConnector(DataConnector):
    """MySQL 连接器示例。"""

    def fetch(self) -> Iterable[Dict[str, Any]]:
        # 实际实现应使用 mysqlclient / PyMySQL 等库。
        return []
