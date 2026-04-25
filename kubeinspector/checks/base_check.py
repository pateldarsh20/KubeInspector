from abc import ABC, abstractmethod

class BaseCheck(ABC):
    """
    Abstract base class for all checks.
    Every new checklist item extends this.
    """
    
    def __init__(self, check_config: dict):
        self.check_id = check_config["id"]
        self.category = check_config["category"]
        self.name = check_config["name"]
        self.description = check_config["description"]
        self.severity = check_config["severity"]
        self.pirate_phrases = check_config.get("pirate_phrases", {})
    
    @abstractmethod
    def execute(self, yaml_content: dict, resource_name: str, namespace: str) -> dict:
        pass
    
    @abstractmethod
    def get_fix(self, yaml_content: dict, issues: list) -> dict:
        pass
    
    def _get_containers(self, yaml_content: dict) -> list:
        try:
            return yaml_content['spec']['template']['spec']['containers']
        except KeyError:
            return []
    
    def _has_hpa(self, yaml_content: dict) -> bool:
        return yaml_content.get('kind') == 'HorizontalPodAutoscaler'
