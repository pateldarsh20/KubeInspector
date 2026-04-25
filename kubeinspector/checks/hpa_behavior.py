from .base_check import BaseCheck

class HPABehaviorCheck(BaseCheck):
    """
    Checks if HPA has scaleUp and scaleDown behavior policies defined.
    """
    def execute(self, yaml_content: dict, resource_name: str, namespace: str) -> dict:
        if yaml_content.get('kind') == 'HorizontalPodAutoscaler':
            spec = yaml_content.get('spec', {})
            behavior = spec.get('behavior', {})
            
            passed = 'scaleUp' in behavior and 'scaleDown' in behavior
            issues = []
            if not passed:
                issues.append({"field": "behavior", "issue": "MISSING", "detail": "Missing scaleUp/scaleDown policies"})
                
            return {
                "check_id": self.check_id,
                "check_name": self.name,
                "category": self.category,
                "severity": self.severity,
                "status": "PASSED" if passed else "FAILED",
                "resource_name": resource_name,
                "namespace": namespace,
                "issues": issues,
                "details": "Behavior defined" if passed else "Missing behavior configuration"
            }
        return {"status": "SKIPPED", "check_id": self.check_id, "check_name": self.name, "category": self.category, "severity": self.severity, "resource_name": resource_name, "namespace": namespace}

    def get_fix(self, yaml_content: dict, issues: list) -> dict:
        import copy
        fixed_yaml = copy.deepcopy(yaml_content)
        spec = fixed_yaml.get('spec', {})
        if 'behavior' not in spec:
            spec['behavior'] = {}
        if 'scaleDown' not in spec['behavior']:
            spec['behavior']['scaleDown'] = {"stabilizationWindowSeconds": 300, "policies": [{"type": "Percent", "value": 50, "periodSeconds": 60}]}
        if 'scaleUp' not in spec['behavior']:
            spec['behavior']['scaleUp'] = {"stabilizationWindowSeconds": 0, "policies": [{"type": "Percent", "value": 100, "periodSeconds": 15}]}
        
        return {
            "can_fix": True,
            "fix_type": "yaml_modification",
            "modified_yaml": fixed_yaml,
            "description": "Add default scaleUp/scaleDown behavior policies to HPA"
        }
