from .base_check import BaseCheck

class HPACustomRPSCheck(BaseCheck):
    """
    Checks for RPS custom metric
    """
    def execute(self, yaml_content: dict, resource_name: str, namespace: str) -> dict:
        if yaml_content.get('kind') == 'HorizontalPodAutoscaler':
            metrics = yaml_content.get('spec', {}).get('metrics', [])
            passed = any(m.get('type') in ['Object', 'Pods'] and any(kw in str(m).lower() for kw in ['rps', 'requests_per_second', 'request']) for m in metrics)
            return {
                "check_id": self.check_id, "check_name": self.name, "category": self.category, "severity": self.severity,
                "status": "PASSED" if passed else "FAILED", "resource_name": resource_name, "namespace": namespace,
                "details": "RPS metric present" if passed else "RPS custom metric missing", "issues": [] if passed else [{"issue": "MISSING"}]
            }
        return {"status": "SKIPPED", "check_id": self.check_id, "check_name": self.name, "category": self.category, "severity": self.severity, "resource_name": resource_name, "namespace": namespace}

    def get_fix(self, yaml_content: dict, issues: list) -> dict:
        import copy
        fixed_yaml = copy.deepcopy(yaml_content)
        spec = fixed_yaml.get('spec', {})
        if 'metrics' not in spec:
            spec['metrics'] = []
        spec['metrics'].append({
            "type": "Object",
            "object": {"metric": {"name": "requests_per_second"}, "target": {"type": "AverageValue", "averageValue": "100"}}
        })
        return {"can_fix": True, "fix_type": "yaml_modification", "modified_yaml": fixed_yaml, "description": "Add requests_per_second custom metric to HPA"}
