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
        spec = hpa_yaml.get('spec', {})
        metrics = spec.get('metrics', [])
        
        has_cpu = False
        has_mem = False
        
        for metric in metrics:
            if metric.get('type') == 'Resource':
                res_name = metric.get('resource', {}).get('name')
                if res_name == 'cpu': has_cpu = True
                if res_name == 'memory': has_mem = True
        
        passed = has_cpu or has_mem
        
        issues = []
        if not passed:
            issues.append({"field": "metrics", "issue": "MISSING", "detail": "No CPU or Memory metric found"})
            
        return {
            "check_id": self.check_id,
            "check_name": self.name,
            "category": self.category,
            "severity": self.severity,
            "status": "PASSED" if passed else "FAILED",
            "resource_name": resource_name,
            "namespace": namespace,
            "issues": issues,
            "details": "CPU/Memory metrics found" if passed else "Missing CPU/Memory metrics"
        }
        
    def get_fix(self, yaml_content: dict, issues: list) -> dict:
        import copy
        fixed_yaml = copy.deepcopy(yaml_content)
        spec = fixed_yaml.get('spec', {})
        
        if 'metrics' not in spec:
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
