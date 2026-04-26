from .base_check import BaseCheck

class ResourceRequestsCheck(BaseCheck):
    """
    Checks if all containers have CPU and Memory requests set.
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
            
            if not container.get('resources'):
                container_issues['missing'].extend(['cpu_request', 'memory_request'])
                container_issues['details'] = "No resources block at all"
                issues.append(container_issues)
                passed = False
                continue
            
            resources = container.get('resources', {})
            
            if not resources.get('requests'):
                container_issues['missing'].extend(['cpu_request', 'memory_request'])
                container_issues['details'] = "No requests defined"
                issues.append(container_issues)
                passed = False
                continue
            
            requests = resources['requests']
            
            if not requests.get('cpu'):
                container_issues['missing'].append('cpu_request')
                passed = False
            else:
                container_issues['current']['cpu_request'] = requests['cpu']
            
            if not requests.get('memory'):
                container_issues['missing'].append('memory_request')
                passed = False
            else:
                container_issues['current']['memory_request'] = requests['memory']
            
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
            return "All containers have CPU and Memory requests configured"
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
            if 'requests' not in container['resources']:
                container['resources']['requests'] = {}
            requests = container['resources']['requests']
            if 'cpu' not in requests:
                requests['cpu'] = '200m'
            if 'memory' not in requests:
                requests['memory'] = '256Mi'
        
        return {
            "can_fix": True,
            "fix_type": "yaml_modification",
            "modified_yaml": fixed_yaml,
            "description": "Add CPU request=200m and Memory request=256Mi to all containers missing requests",
            "changes_made": {
                "added_requests": True,
                "default_cpu": "200m",
                "default_memory": "256Mi"
            }
        }
