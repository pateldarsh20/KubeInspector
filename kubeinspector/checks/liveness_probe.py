from .base_check import BaseCheck

class LivenessProbeCheck(BaseCheck):
    """
    Checks if all containers have a livenessProbe set.
    """
    
    def execute(self, yaml_content: dict, resource_name: str, namespace: str) -> dict:
        containers = self._get_containers(yaml_content)
        issues = []
        passed = True
        
        for container in containers:
            container_name = container.get('name', 'unnamed')
            if not container.get('livenessProbe'):
                issues.append({
                    'container': container_name,
                    'missing': ['livenessProbe']
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
            "containers_checked": len(containers),
            "containers_with_issues": len(issues),
            "issues": issues,
            "details": self._build_details(issues, passed)
        }
    
    def _build_details(self, issues: list, passed: bool) -> str:
        if passed:
            return "All containers have livenessProbe configured"
        details_parts = []
        for issue in issues:
            details_parts.append(f"Container '{issue['container']}' missing: livenessProbe")
        return "; ".join(details_parts)
    
    def get_fix(self, yaml_content: dict, issues: list) -> dict:
        import copy
        fixed_yaml = copy.deepcopy(yaml_content)
        containers = fixed_yaml['spec']['template']['spec']['containers']
        for container in containers:
            if 'livenessProbe' not in container:
                container['livenessProbe'] = {
                    'httpGet': {
                        'path': '/health',
                        'port': 3000
                    },
                    'initialDelaySeconds': 30,
                    'periodSeconds': 30,
                    'timeoutSeconds': 2,
                    'failureThreshold': 3
                }
        
        return {
            "can_fix": True,
            "fix_type": "yaml_modification",
            "modified_yaml": fixed_yaml,
            "description": "Add livenessProbe to all containers missing it",
            "changes_made": {
                "added_livenessProbe": True
            }
        }
