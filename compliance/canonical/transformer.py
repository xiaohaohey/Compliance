from typing import Any, Dict


class CanonicalTransformer:
    """根据映射规则将原始记录转换为标准化字段。"""

    def transform(self, record: Dict[str, Any], mappings) -> Dict[str, Any]:
        transformed = {}
        for target_field, fn in mappings.items():
            transformed[target_field] = fn(record)
        return transformed
