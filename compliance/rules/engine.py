from typing import Dict, Iterable, List

from compliance.config.models import RuleConfig


class RuleEngine:
    """在标准化数据上执行合规规则。"""

    def run_rules(self, records: Iterable[Dict], rules: Iterable[RuleConfig]):
        rule_list = list(rules)
        results: Dict[str, List[str]] = {rule.name: [] for rule in rule_list}
        for record in records:
            for rule in rule_list:
                message = rule.apply(record)
                if message:
                    results[rule.name].append(message)
        return results
