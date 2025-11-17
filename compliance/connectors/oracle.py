from typing import Any, Dict, Iterable

from compliance.config.models import SourceConfig
from .base import DataConnector


class OracleConnector(DataConnector):
    """Oracle 连接器示例，展示查询接口。"""

    def fetch(self) -> Iterable[Dict[str, Any]]:
        # 实际实现应使用 cx_Oracle/SQLAlchemy 查询。
        # 这里返回空集合以保持示例轻量化。
        return []
