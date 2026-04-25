import random
from .pirate_phrases import PIRATE_PHRASES

class ResponseBuilder:
    """
    Builds pirate-themed responses based on context.
    Zero AI - pure template filling with randomization.
    """
    
    def __init__(self):
        self.phrases = PIRATE_PHRASES
    
    def greeting(self) -> str:
        """Random pirate greeting"""
        return random.choice(self.phrases["greeting"])
    
    def report_issue(self, check_result: dict) -> str:
        """
        Takes a check result and builds a contextual pirate response.
        """
        severity = check_result.get("severity", "MANDATORY")
        category_name = self.phrases["categories"].get(severity, severity)
        
        if severity == "MANDATORY":
            templates = self.phrases["critical_finding"]
        elif severity == "RECOMMENDED":
            templates = self.phrases["recommended_finding"]
        else:
            templates = self.phrases["optional_finding"]
        
        template = random.choice(templates)
        
        return template.format(
            check_name=check_result.get("check_name", ""),
            container=check_result.get("resource_name", "unknown"),
            namespace=check_result.get("namespace", "default"),
            severity=category_name,
            details=check_result.get("details", "")
        )
    
    def celebrate_all_clear(self) -> str:
        """Called when ALL checks pass"""
        clear = random.choice(self.phrases["all_clear"])
        ready = random.choice(self.phrases["ready_to_board"])
        
        return f"""
🏴☠️  {clear}

⚓  {ready}

        ⠀⠀⠀⠀⠀⠀⠀⠀⠀⢀⣤⣤⣤⣤⣤⣤⣤⣤⣤⣤⣀⠀⠀⠀⠀⠀⠀⠀⠀⠀
        ⠀⠀⠀⠀⠀⠀⠀⠀⣾⠁⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠈⢻⡄⠀⠀⠀⠀⠀⠀⠀⠀
        ⠀⠀⠀⠀⠀⠀⠀⢰⡇⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⢸⡇⠀⠀⠀⠀⠀⠀⠀⠀
        ⠀⠀⠀⠀⠀⠀⠀⢸⡇⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⢸⡇⠀⠀⠀⠀⠀⠀⠀⠀
        ⠀⠀⠀⠀⠀⠀⠀⢸⡇⠀⠀⠀⠀⢀⣀⣀⣀⡀⠀⠀⠀⢸⡇⠀
        ⠀⠀⠀⠀⠀⠀⠀⢸⡇⠀⠀⠀⣾⠛⠉⠉⠛⢷⡀⠀⠀⢸⡇⠀⠀⠀⠀⠀⠀⠀⠀
        ⠀⠀⠀⠀⠀⠀⠀⢸⡇⠀⠀⢰⣧⡀⠀⠀⠀⣸⡇⠀⠀⢸⡇⠀⠀⠀⠀⠀⠀⠀⠀
        ⠀⠀⠀⠀⠀⠀⠀⠘⣧⡀⠀⠈⠙⠻⠿⠿⠟⠋⠁⠀⢀⣼⠃⠀⠀⠀⠀⠀⠀⠀⠀
        ⠀⠀⠀⠀⠀⠀⠀⠀⠈⠻⣦⣀⡀⠀⠀⠀⠀⠀⣀⣴⠟⠁⠀⠀⠀⠀⠀⠀⠀⠀⠀
        ⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠈⠙⠛⠿⠿⠿⠿⠛⠋⠁⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀

                    🌊 THE SEA AWAITS, CAPTAIN! 🌊
"""

    def needs_repairs_summary(self, mandatory_failed: list) -> str:
        """Called when checks fail"""
        repair = random.choice(self.phrases["needs_repairs"])
        return f"☠️  {repair}"
    
    def fix_summary(self, fixes_applied: list, fixes_skipped: list) -> str:
        """Summarize what was fixed"""
        return "Fixes applied! Ship is tighter than a drum!"
    
    def get_explanation(self, check_id: str) -> str:
        """Get pirate explanation for a check"""
        return self.phrases["explanations"].get(
            check_id, 
            "Captain, this be important for the ship's safety!"
        )
    
    def suggest_fix(self, check_id: str, context: dict) -> str:
        """Get fix suggestion with pirate flavor"""
        suggestion = self.phrases["fix_suggestions"].get(check_id, "")
        return suggestion.format(**context) if suggestion else ""
