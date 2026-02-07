from dataclasses import dataclass, field
from typing import List, Optional
import os
import json

def _state_file_path() -> str:
   
    return os.path.join(os.path.expanduser("~"), ".sync_state.json")

@dataclass
class AppState:
    current_lab: str = ""
    selected_targets: List[str] = field(default_factory=list)

    target_os: str = "windows"  
    action: str = "install"
    selected_software: Optional[str] = None

    theme: str = "dark"  

    def clear_targets(self):
        self.selected_targets.clear()

    def load(self):
        try:
            path = _state_file_path()
            if not os.path.exists(path):
                return
            with open(path, "r", encoding="utf-8") as f:
                data = json.load(f)

            self.theme = (data.get("theme", self.theme) or self.theme).lower()

        except Exception:
            
            pass

    def save(self):
        try:
            data = {
                "theme": (self.theme or "dark").lower(),
            }
            with open(_state_file_path(), "w", encoding="utf-8") as f:
                json.dump(data, f)
        except Exception:
            pass
