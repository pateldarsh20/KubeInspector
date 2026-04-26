from .base_check import BaseCheck

class HPACustomRPSCheck(BaseCheck):
    """
    Checks for RPS custom metric
    """
    def execute(self, yaml_content: dict, resource_name: str, namespace: str) -> dict:
        if yaml_content.get('kind') == 'HorizontalPodAutoscaler':
            spec = yaml_content.get('spec') or {}
            metrics = spec.get('metrics')
            if not isinstance(metrics, list): metrics = []
            
            found_names = []
            for m in metrics:
                if not isinstance(m, dict): continue
                m_type = str(m.get('type', '')).strip().lower()
                if m_type in ['object', 'pods']:
                    metric_str = str(m).lower()
                    # Must contain rps or request, but NOT duration or latency
                    if any(kw in metric_str for kw in ['rps', 'requests_per_second', 'request']):
                        if not any(bad in metric_str for bad in ['duration', 'latency']):
                            # Try to find the actual name
                            name = "unknown"
                            if 'pods' in m: name = m['pods'].get('metric', {}).get('name', 'unknown')
                            elif 'object' in m: name = m['object'].get('metric', {}).get('name', 'unknown')
                            found_names.append(name)
            
            passed = len(found_names) > 0
            return {
                "check_id": self.check_id, "check_name": self.name, "category": self.category, "severity": self.severity,
                "status": "PASSED" if passed else "FAILED", "resource_name": resource_name, "namespace": namespace,
                "details": f"Found RPS metrics: {', '.join(found_names)}" if passed else "RPS custom metric missing", 
                "issues": [] if passed else [{"issue": "MISSING", "detail": "Add RPS-based scaling for better responsiveness"}]
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
