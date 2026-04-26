from .base_check import BaseCheck

class HPAMinMaxCheck(BaseCheck):
    """
    Checks if HPA has minReplicas and maxReplicas defined.
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
            "details": "Not an HPA resource - check will run on HPA files",
            "issues": []
        }
    
    def _check_hpa_directly(self, hpa_yaml: dict, resource_name: str, namespace: str) -> dict:
        spec = hpa_yaml.get('spec') or {}
        issues = []
        passed = True
        
        min_val = spec.get('minReplicas')
        max_val = spec.get('maxReplicas')
        
        # Check existence
        if min_val is None:
            issues.append({'field': 'minReplicas', 'issue': 'MISSING', 'detail': 'Minimum replicas not defined'})
            passed = False
        
        if max_val is None:
            issues.append({'field': 'maxReplicas', 'issue': 'MISSING', 'detail': 'Maximum replicas not defined'})
            passed = False
        
        # Only do value checks if both are valid integers
        if isinstance(min_val, int):
            if min_val < 2:
                issues.append({
                    'field': 'minReplicas',
                    'issue': 'LOW_REPLICAS',
                    'detail': f"minReplicas ({min_val}) should be at least 2 for High Availability",
                    'current_min': min_val
                })
                passed = False
        
        if isinstance(min_val, int) and isinstance(max_val, int):
            if min_val >= max_val:
                issues.append({
                    'field': 'minReplicas/maxReplicas',
                    'issue': 'INVALID',
                    'detail': f"minReplicas ({min_val}) must be less than maxReplicas ({max_val})",
                    'current_min': min_val,
                    'current_max': max_val
                })
                passed = False
        
        return {
            "check_id": self.check_id,
            "check_name": self.name,
            "category": self.category,
            "severity": self.severity,
            "status": "PASSED" if passed else "FAILED",
            "resource_name": resource_name,
            "namespace": namespace,
            "issues": issues,
            "current_min": min_val if min_val is not None else 'NOT SET',
            "current_max": max_val if max_val is not None else 'NOT SET',
            "details": f"minReplicas={min_val if min_val is not None else 'MISSING'}, maxReplicas={max_val if max_val is not None else 'MISSING'}"
        }
    
    def get_fix(self, yaml_content: dict, issues: list) -> dict:
        import copy
        fixed_yaml = copy.deepcopy(yaml_content)
        spec = fixed_yaml['spec']
        
        for issue in issues:
            if issue['field'] == 'minReplicas' and (issue['issue'] == 'MISSING' or issue['issue'] == 'LOW_REPLICAS'):
                spec['minReplicas'] = 2
            elif issue['field'] == 'maxReplicas' and issue['issue'] == 'MISSING':
                spec['maxReplicas'] = 10
            elif issue['issue'] == 'INVALID':
                spec['minReplicas'] = 2
                spec['maxReplicas'] = 10
        
        return {
            "can_fix": True,
            "fix_type": "yaml_modification",
            "modified_yaml": fixed_yaml,
            "description": "Set minReplicas=2, maxReplicas=10 for HPA",
            "changes_made": {
                "min_replicas": spec.get('minReplicas'),
                "max_replicas": spec.get('maxReplicas')
            }
        }
