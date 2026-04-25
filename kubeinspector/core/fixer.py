import yaml
import shutil
from pathlib import Path

class Fixer:
    """
    Applies fixes to YAML files.
    NEVER fixes without user approval.
    Creates backup before modifying.
    """
    
    def __init__(self, inspector):
        self.inspector = inspector
        self.fixes_applied = []
        self.fixes_failed = []
    
    def generate_fix_plan(self, failed_checks: list) -> dict:
        fix_plan = []
        
        for check_result in failed_checks:
            check_id = check_result['check_id']
            check_instance = self.inspector.checks.get(check_id)
            
            if check_instance:
                fix = check_instance.get_fix(
                    check_result.get('original_yaml', {}),
                    check_result.get('issues', [])
                )
                
                if fix and fix.get('can_fix'):
                    fix_plan.append({
                        "resource": check_result['resource_name'],
                        "namespace": check_result['namespace'],
                        "check": check_result['check_name'],
                        "fix_description": fix['description'],
                        "changes": fix.get('changes_made', {}),
                        "check_id": check_id
                    })
        
        return {
            "total_fixes": len(fix_plan),
            "fixes": fix_plan
        }
    
    def apply_fix(self, check_result: dict, original_yaml: dict, file_path: str) -> dict:
        check_id = check_result['check_id']
        check_instance = self.inspector.checks.get(check_id)
        
        if not check_instance:
            return {"success": False, "error": f"No fixer for {check_id}"}
        
        try:
            fix = check_instance.get_fix(original_yaml, check_result.get('issues', []))
            
            if not fix or not fix.get('can_fix'):
                return {"success": False, "error": "This issue cannot be auto-fixed"}
            
            self._create_backup(file_path)
            
            modified_yaml = fix['modified_yaml']
            with open(file_path, 'w') as f:
                yaml.dump(modified_yaml, f, default_flow_style=False, sort_keys=False)
            
            self.fixes_applied.append({
                "file": file_path,
                "resource": check_result['resource_name'],
                "fix": fix['description']
            })
            
            return {
                "success": True,
                "fix": fix['description'],
                "file": file_path
            }
            
        except Exception as e:
            self.fixes_failed.append({
                "resource": check_result['resource_name'],
                "error": str(e)
            })
            return {"success": False, "error": str(e)}
    
    def _create_backup(self, file_path: str):
        backup_path = f"{file_path}.bak"
        shutil.copy2(file_path, backup_path)
    
    def generate_new_hpa_for_workload(self, workload: dict) -> dict:
        from ..templates.hpa_templates import generate_complete_hpa
        
        hpa = generate_complete_hpa(
            target_deployment=workload['name'],
            namespace=workload['namespace']
        )
        
        return {
            "can_fix": True,
            "fix_type": "create_new_resource",
            "new_resource": hpa,
            "suggested_filename": f"{workload['name']}-hpa.yaml",
            "description": f"Create new HPA for {workload['name']} with CPU/Memory scaling, behavior policies, and sensible defaults"
        }
