from typing import Dict, Iterable, List

from compliance.config.models import TargetConfig


class TargetWriter:
    """负责将标准化数据写入目标库。"""

    def __init__(self, config: TargetConfig):
        self.config = config

    def write(self, records: Iterable[Dict]) -> None:
        raise NotImplementedError


class InMemoryTargetWriter(TargetWriter):
    """将数据存入内存列表，便于演示与测试。"""

    def __init__(self, config: TargetConfig):
        super().__init__(config)
        self.storage: List[Dict] = []

    def write(self, records: Iterable[Dict]) -> None:
        self.storage.extend(list(records))
