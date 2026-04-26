from .base_check import BaseCheck

class HPACPUMemCheck(BaseCheck):
    """
    Checks if HPA has CPU and/or Memory utilization metrics configured.
    """
    
    def execute(self, yaml_content: dict, resource_name: str, namespace: str) -> dict:
        if yaml_content.get('kind') == 'HorizontalPodAutoscaler':
            return self._check_hpa_directly(yaml_content, resource_name, namespace)
        
        return {
            "check_id": self.check_id,
            "check_name": self.name,
            "category": self.category,
            "severity": self.severity,
            "status": "SKIPPED",
            "resource_name": resource_name,
            "namespace": namespace,
            "details": "Not an HPA resource",
            "issues": []
        }
    
    def _check_hpa_directly(self, hpa_yaml: dict, resource_name: str, namespace: str) -> dict:
        spec = hpa_yaml.get('spec') or {}
        metrics = spec.get('metrics')
        if not isinstance(metrics, list): metrics = []
        
        found_metrics = []
        has_cpu = False
        has_mem = False
        
        for metric in metrics:
            if not isinstance(metric, dict): continue
            m_type = str(metric.get('type', '')).strip().lower()
            if m_type == 'resource':
                res = metric.get('resource') or {}
                res_name = str(res.get('name', '')).strip().lower()
                if res_name == 'cpu':
                    has_cpu = True
                    found_metrics.append("CPU")
                elif res_name == 'memory':
                    has_mem = True
                    found_metrics.append("Memory")
        
        passed = has_cpu and has_mem
        issues = []
        if not has_cpu:
            issues.append({"field": "metrics", "issue": "MISSING", "detail": "CPU utilization metric missing from HPA spec"})
        if not has_mem:
            issues.append({"field": "metrics", "issue": "MISSING", "detail": "Memory utilization metric missing from HPA spec"})
            
        details = f"Found metrics: {', '.join(found_metrics)}" if passed else f"Missing: {'CPU' if not has_cpu else ''}{' and ' if not has_cpu and not has_mem else ''}{'Memory' if not has_mem else ''} scaling metric(s)"
            
        return {
            "check_id": self.check_id,
            "check_name": self.name,
            "category": self.category,
            "severity": self.severity,
            "status": "PASSED" if passed else "FAILED",
            "resource_name": resource_name,
            "namespace": namespace,
            "issues": issues,
            "details": details
        }
        
    def get_fix(self, yaml_content: dict, issues: list) -> dict:
        import copy
        fixed_yaml = copy.deepcopy(yaml_content)
        spec = fixed_yaml.get('spec', {})
        
        if not spec.get('metrics'):
            spec['metrics'] = []
            
        spec['metrics'].append({
            "type": "Resource",
            "resource": {
                "name": "cpu",
                "target": {
                    "type": "Utilization",
                    "averageUtilization": 70
                }
            }
        })
        
        return {
            "can_fix": True,
            "fix_type": "yaml_modification",
            "modified_yaml": fixed_yaml,
            "description": "Add CPU utilization metric (target 70%) to HPA"
        }
