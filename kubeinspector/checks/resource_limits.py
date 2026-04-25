from .base_check import BaseCheck

class ResourceLimitsCheck(BaseCheck):
    """
    Checks if all containers have CPU and Memory limits set.
    """
    
    def execute(self, yaml_content: dict, resource_name: str, namespace: str) -> dict:
        containers = self._get_containers(yaml_content)
        issues = []
        passed = True
        
        for container in containers:
            container_name = container.get('name', 'unnamed')
            container_issues = {
                'container': container_name,
                'missing': [],
                'current': {}
            }
            
            if 'resources' not in container:
                container_issues['missing'].extend(['cpu_limit', 'memory_limit'])
                container_issues['details'] = "No resources block at all"
                issues.append(container_issues)
                passed = False
                continue
            
            resources = container.get('resources', {})
            
            if 'limits' not in resources:
                container_issues['missing'].extend(['cpu_limit', 'memory_limit'])
                container_issues['details'] = "No limits defined"
                issues.append(container_issues)
                passed = False
                continue
            
            limits = resources['limits']
            
            if 'cpu' not in limits:
                container_issues['missing'].append('cpu_limit')
                passed = False
            else:
                container_issues['current']['cpu_limit'] = limits['cpu']
            
            if 'memory' not in limits:
                container_issues['missing'].append('memory_limit')
                passed = False
            else:
                container_issues['current']['memory_limit'] = limits['memory']
            
            if container_issues['missing']:
                issues.append(container_issues)
        
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
            return "All containers have CPU and Memory limits configured"
        details_parts = []
        for issue in issues:
            container = issue['container']
            missing = ', '.join(issue['missing'])
            details_parts.append(f"Container '{container}' missing: {missing}")
        return "; ".join(details_parts)
    
    def get_fix(self, yaml_content: dict, issues: list) -> dict:
        import copy
        fixed_yaml = copy.deepcopy(yaml_content)
        containers = fixed_yaml['spec']['template']['spec']['containers']
        for i, container in enumerate(containers):
            if 'resources' not in container:
                container['resources'] = {}
            if 'limits' not in container['resources']:
                container['resources']['limits'] = {}
            limits = container['resources']['limits']
            if 'cpu' not in limits:
                limits['cpu'] = '500m'
            if 'memory' not in limits:
                limits['memory'] = '512Mi'
        
        return {
            "can_fix": True,
            "fix_type": "yaml_modification",
            "modified_yaml": fixed_yaml,
            "description": "Add CPU limit=500m and Memory limit=512Mi to all containers missing limits",
            "changes_made": {
                "added_limits": True,
                "default_cpu": "500m",
                "default_memory": "512Mi"
            }
        }
