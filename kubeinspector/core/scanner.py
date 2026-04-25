import os
import yaml
from pathlib import Path

class Scanner:
    """
    Scans directories for Kubernetes YAML files.
    Handles multi-document YAML files.
    Zero AI - pure file I/O and YAML parsing.
    """
    
    WORKLOAD_KINDS = ['Deployment', 'StatefulSet', 'DaemonSet', 'ReplicaSet']
    HPA_KIND = 'HorizontalPodAutoscaler'
    
    def __init__(self, path: str = "."):
        self.path = Path(path)
        self.resources = []
        self.hpas = []
        self.other_resources = []
    
    def scan(self) -> dict:
        yaml_files = list(self.path.rglob("*.yaml")) + list(self.path.rglob("*.yml"))
        
        for yaml_file in yaml_files:
            try:
                docs = self._parse_multi_document_yaml(yaml_file)
                for doc in docs:
                    if not doc or not isinstance(doc, dict):
                        continue
                    
                    kind = doc.get('kind', '')
                    resource_name = doc.get('metadata', {}).get('name', 'unnamed')
                    
                    resource_info = {
                        "file_path": str(yaml_file),
                        "name": resource_name,
                        "namespace": doc.get('metadata', {}).get('namespace', 'default'),
                        "kind": kind,
                        "content": doc
                    }
                    
                    if kind in self.WORKLOAD_KINDS:
                        self.resources.append(resource_info)
                    elif kind == self.HPA_KIND:
                        self.hpas.append(resource_info)
                    else:
                        self.other_resources.append(resource_info)
                        
            except yaml.YAMLError as e:
                print(f"⚠️  Failed to parse {yaml_file}: {e}")
                continue
        
        self._link_hpas_to_workloads()
        
        return {
            "workloads": self.resources,
            "hpas": self.hpas,
            "other_resources": self.other_resources,
            "total_files_scanned": len(yaml_files),
            "total_resources_found": len(self.resources) + len(self.hpas)
        }
    
    def _parse_multi_document_yaml(self, file_path: str) -> list:
        with open(file_path, 'r') as f:
            content = f.read()
        
        docs = []
        for doc in yaml.safe_load_all(content):
            if doc:
                docs.append(doc)
        
        return docs if docs else [yaml.safe_load(content)]
    
    def _link_hpas_to_workloads(self):
        for hpa in self.hpas:
            target_name = hpa['content']['spec']['scaleTargetRef']['name']
            
            for workload in self.resources:
                if workload['name'] == target_name:
                    if 'linked_hpas' not in workload:
                        workload['linked_hpas'] = []
                    workload['linked_hpas'].append(hpa)
                    break
    
    def get_workloads_without_hpa(self) -> list:
        return [
            w for w in self.resources 
            if 'linked_hpas' not in w or len(w['linked_hpas']) == 0
        ]
