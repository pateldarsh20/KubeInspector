import json
from pathlib import Path
from ..checks.resource_requests import ResourceRequestsCheck
from ..checks.resource_limits import ResourceLimitsCheck
from ..checks.hpa_minmax import HPAMinMaxCheck
from ..checks.hpa_cpu_mem import HPACPUMemCheck
from ..checks.hpa_behavior import HPABehaviorCheck
from ..checks.hpa_custom_rps import HPACustomRPSCheck
from ..checks.hpa_custom_latency import HPACustomLatencyCheck
from ..personality.response_builder import ResponseBuilder

class Inspector:
    """
    Master inspector that runs ALL checks against scanned resources.
    """
    
    def __init__(self, checklist_path: str = None):
        if checklist_path is None:
            import os
            checklist_path = os.path.join(os.path.dirname(__file__), '..', 'checklist.json')
        self.checklist = self._load_checklist(checklist_path)
        self.response_builder = ResponseBuilder()
        self.checks = self._initialize_checks()
    
    def _load_checklist(self, path: str) -> dict:
        with open(path, 'r') as f:
            return json.load(f)
    
    def _initialize_checks(self) -> dict:
        check_map = {
            "RESOURCE-REQ": ResourceRequestsCheck,
            "RESOURCE-LIM": ResourceLimitsCheck,
            "HPA-MINMAX": HPAMinMaxCheck,
            "HPA-CPU-MEM": HPACPUMemCheck,
            "HPA-BEHAVIOUR": HPABehaviorCheck,
            "HPA-CUSTOM-RPS": HPACustomRPSCheck,
            "HPA-CUSTOM-LATENCY": HPACustomLatencyCheck,
        }
        
        initialized = {}
        for item in self.checklist['items']:
            check_class = check_map.get(item['id'])
            if check_class:
                initialized[item['id']] = check_class(item)
        
        return initialized
    
    def inspect_resource(self, resource: dict) -> list:
        results = []
        
        kind = resource['kind']
        yaml_content = resource['content']
        name = resource['name']
        namespace = resource['namespace']
        file_path = resource.get('file_path', 'unknown')
        
        if kind in ['Deployment', 'StatefulSet', 'DaemonSet', 'ReplicaSet']:
            if 'RESOURCE-REQ' in self.checks:
                res = self.checks['RESOURCE-REQ'].execute(yaml_content, name, namespace)
                res['file_path'] = file_path
                results.append(res)
            if 'RESOURCE-LIM' in self.checks:
                res = self.checks['RESOURCE-LIM'].execute(yaml_content, name, namespace)
                res['file_path'] = file_path
                results.append(res)
        
        if kind == 'HorizontalPodAutoscaler':
            for check_id in ['HPA-MINMAX', 'HPA-CPU-MEM', 'HPA-BEHAVIOUR', 'HPA-CUSTOM-RPS', 'HPA-CUSTOM-LATENCY']:
                if check_id in self.checks:
                    res = self.checks[check_id].execute(yaml_content, name, namespace)
                    res['file_path'] = file_path
                    results.append(res)
        
        if 'linked_hpas' in resource:
            for hpa in resource['linked_hpas']:
                hpa_results = self.inspect_resource(hpa)
                results.extend(hpa_results)
        
        return results
    
    def inspect_all(self, scanned_data: dict) -> dict:
        all_results = []
        
        for workload in scanned_data['workloads']:
            results = self.inspect_resource(workload)
            all_results.extend(results)
        
        for hpa in scanned_data['hpas']:
            # Assume any HPA in this list wasn't inspected if it wasn't linked? Actually it might be inspected twice.
            # We'll just inspect all of them.
            results = self.inspect_resource(hpa)
            all_results.extend(results)
            
        # Deduplicate results based on check_id and resource_name
        seen = set()
        unique_results = []
        for r in all_results:
            key = (r['check_id'], r['resource_name'])
            if key not in seen:
                seen.add(key)
                unique_results.append(r)
        
        return self._build_report(unique_results)
    
    def filter_by_namespace(self, report: dict, namespace: str) -> dict:
        filtered = [r for r in report['all_results'] if r.get('namespace') == namespace]
        return self._build_report(filtered)
    
    def _build_report(self, all_results: list) -> dict:
        total = len(all_results)
        passed = sum(1 for r in all_results if r['status'] == 'PASSED')
        failed = sum(1 for r in all_results if r['status'] == 'FAILED')
        skipped = sum(1 for r in all_results if r['status'] == 'SKIPPED')
        
        mandatory_failed = [r for r in all_results if r['status'] == 'FAILED' and r['severity'] == 'MANDATORY']
        recommended_failed = [r for r in all_results if r['status'] == 'FAILED' and r['severity'] == 'RECOMMENDED']
        
        all_clear = len(mandatory_failed) == 0
        
        return {
            "summary": {
                "total_checks": total,
                "passed": passed,
                "failed": failed,
                "skipped": skipped,
                "all_clear": all_clear,
                "ready_to_board": all_clear
            },
            "mandatory_failures": mandatory_failed,
            "recommended_failures": recommended_failed,
            "all_results": all_results,
            "pirate_summary": self.response_builder.celebrate_all_clear() if all_clear else self.response_builder.needs_repairs_summary(mandatory_failed)
        }
