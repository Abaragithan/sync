from dataclasses import dataclass, field
from typing import List, Optional

@dataclass
class AppState:
    current_lab: str = ""
    selected_targets: List[str] = field(default_factory=list)

    # Dual-boot: OS choice is global for all selected PCs
    target_os: str = "windows"  # "windows" or "linux"

    action: str = "install"
    selected_software: Optional[str] = None

    def clear_targets(self):
        self.selected_targets.clear()
