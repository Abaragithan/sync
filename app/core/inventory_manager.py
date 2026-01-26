import json
import os
from typing import Dict, List, Optional

from .config import INVENTORY_FILE, LABS

class InventoryManager:
    def __init__(self):
        self.data: Dict[str, List[Dict]] = self._load()
        print(f"[INVENTORY] Loaded {len(self.data)} labs: {list(self.data.keys())}")  # Diagnostic

    def _load(self) -> Dict[str, List[Dict]]:
        # Force-create data dir
        data_dir = os.path.dirname(INVENTORY_FILE)
        os.makedirs(data_dir, exist_ok=True)
        print(f"[INVENTORY] Data dir: {data_dir}, File: {INVENTORY_FILE}")  # Diagnostic

        if os.path.exists(INVENTORY_FILE):
            try:
                with open(INVENTORY_FILE, 'r') as f:
                    loaded = json.load(f)
                print(f"[INVENTORY] Loaded from JSON: {len(loaded)} labs")  # Diagnostic
                return loaded
            except (json.JSONDecodeError, IOError) as e:
                print(f"[INVENTORY] JSON load error: {e}. Re-seeding...")  # Diagnostic
                # Fall through to seed

        # Seed default: 3 labs, 100 PCs each (mixed OS, sequential IPs)
        print("[INVENTORY] Seeding default inventory...")  # Diagnostic
        default = {}
        base_ip = 101
        for lab in LABS:
            default[lab] = [
                {
                    "ip": f"192.168.132.{base_ip + i}",
                    "os": "windows" if i % 2 == 0 else "linux",
                    "name": f"PC-{base_ip + i:03d}"
                }
                for i in range(100)
            ]
            base_ip += 100  # Next lab starts at next 100 IPs
        self._save(default)
        print(f"[INVENTORY] Seeded {len(default)} labs with 100 PCs each.")  # Diagnostic
        return default

    def _save(self, data: Dict):
        try:
            with open(INVENTORY_FILE, 'w') as f:
                json.dump(data, f, indent=2)
            print(f"[INVENTORY] Saved to {INVENTORY_FILE}")  # Diagnostic
        except IOError as e:
            print(f"[INVENTORY] Save error: {e}")  # Diagnostic
            raise

    def get_pcs_for_lab(self, lab: str, os_filter: Optional[str] = None) -> List[Dict]:
        pcs = self.data.get(lab, [])
        if os_filter and os_filter != "All":
            pcs = [pc for pc in pcs if pc["os"] == os_filter]
        print(f"[INVENTORY] {len(pcs)} PCs for {lab} (filter: {os_filter})")  # Diagnostic
        return pcs

    def add_pc(self, lab: str, pc: Dict):
        if lab not in self.data:
            self.data[lab] = []
        self.data[lab].append(pc)
        self._save(self.data)
        print(f"[INVENTORY] Added PC to {lab}: {pc['name']} ({pc['ip']})")  # Diagnostic

    def get_all_labs(self) -> List[str]:
        labs = list(self.data.keys())
        print(f"[INVENTORY] All labs: {labs}")  # Diagnostic
        return labs

    def _save_inventory_json(self):
        """Save current inventory data back to inventory.json"""
        with open(self.inventory_file, "w") as f:
            json.dump(self.inventory, f, indent=2)

    def remove_pc(self, lab_name: str, ip: str) -> bool:
        """
        Remove a PC by IP from a lab and persist to JSON.
        Returns True if removed, False if not found.
        """
        removed = False

        # ✅ Case 1: inventory stored like {"labs": {"Lab1": [pcs], ...}}
        if isinstance(self.inventory, dict) and "labs" in self.inventory and isinstance(self.inventory["labs"], dict):
            if lab_name in self.inventory["labs"] and isinstance(self.inventory["labs"][lab_name], list):
                before = len(self.inventory["labs"][lab_name])
                self.inventory["labs"][lab_name] = [pc for pc in self.inventory["labs"][lab_name] if pc.get("ip") != ip]
                removed = len(self.inventory["labs"][lab_name]) != before

        # ✅ Case 2: inventory stored like {"labs": [{"name":"Lab1","pcs":[...]}, ...]}
        elif isinstance(self.inventory, dict) and "labs" in self.inventory and isinstance(self.inventory["labs"], list):
            for lab in self.inventory["labs"]:
                if isinstance(lab, dict) and lab.get("name") == lab_name:
                    pcs = lab.get("pcs", [])
                    if isinstance(pcs, list):
                        before = len(pcs)
                        lab["pcs"] = [pc for pc in pcs if pc.get("ip") != ip]
                        removed = len(lab["pcs"]) != before
                    break

        # ✅ Case 3: inventory stored directly as {"Lab1":[pcs], "Lab2":[pcs]}
        elif isinstance(self.inventory, dict) and lab_name in self.inventory and isinstance(self.inventory[lab_name], list):
            before = len(self.inventory[lab_name])
            self.inventory[lab_name] = [pc for pc in self.inventory[lab_name] if pc.get("ip") != ip]
            removed = len(self.inventory[lab_name]) != before

        if removed:
            self._save_inventory_json()

        return removed