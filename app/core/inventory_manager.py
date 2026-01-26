import json
import os
from typing import Dict, List, Optional, Any

from .config import INVENTORY_FILE, LABS


class InventoryManager:
    """
    Inventory supports TWO formats:

    OLD (your current):
      {
        "Lab1": [ {ip, os, name}, ... ],
        "Lab2": [ ... ]
      }

    NEW (for custom layouts):
      {
        "labs": {
          "CSL 1&2": {
            "layout": {"sections":3,"rows":7,"cols":5},
            "pcs": [ {name, ip, section, row, col}, ... ]
          }
        }
      }
    """

    def __init__(self):
        self.data: Dict[str, Any] = self._load()
        print(f"[INVENTORY] Loaded {len(self.get_all_labs())} labs: {self.get_all_labs()}")

   

    def _load(self) -> Dict[str, Any]:
        data_dir = os.path.dirname(INVENTORY_FILE)
        os.makedirs(data_dir, exist_ok=True)
        print(f"[INVENTORY] Data dir: {data_dir}, File: {INVENTORY_FILE}")

        if os.path.exists(INVENTORY_FILE):
            try:
                with open(INVENTORY_FILE, "r") as f:
                    loaded = json.load(f)
                print(f"[INVENTORY] Loaded from JSON.")
                return loaded
            except (json.JSONDecodeError, IOError) as e:
                print(f"[INVENTORY] JSON load error: {e}. Re-seeding...")

       
        print("[INVENTORY] Seeding default inventory...")
        default: Dict[str, List[Dict]] = {}
        base_ip = 101
        for lab in LABS:
            default[lab] = [
                {
                    "ip": f"192.168.132.{base_ip + i}",
                    "os": "windows" if i % 2 == 0 else "linux",
                    "name": f"PC-{base_ip + i:03d}",
                }
                for i in range(100)
            ]
            base_ip += 100

        self._save(default)
        print(f"[INVENTORY] Seeded {len(default)} labs with 100 PCs each.")
        return default

    def _save(self, data: Dict[str, Any]):
        try:
            with open(INVENTORY_FILE, "w") as f:
                json.dump(data, f, indent=2)
            print(f"[INVENTORY] Saved to {INVENTORY_FILE}")
        except IOError as e:
            print(f"[INVENTORY] Save error: {e}")
            raise

    def _is_new_format(self) -> bool:
        return isinstance(self.data, dict) and "labs" in self.data and isinstance(self.data["labs"], dict)

    

    def get_all_labs(self) -> List[str]:
        if self._is_new_format():
            labs = list(self.data["labs"].keys())
        else:
            labs = list(self.data.keys())

        print(f"[INVENTORY] All labs: {labs}")
        return labs

    def get_lab_layout(self, lab_name: str) -> Optional[dict]:
        """
        Returns layout dict if lab exists in NEW format. Otherwise None.
        """
        if self._is_new_format():
            rec = self.data["labs"].get(lab_name)
            if isinstance(rec, dict) and isinstance(rec.get("layout"), dict):
                return rec["layout"]
        return None

    def get_pcs_for_lab(self, lab: str, os_filter: Optional[str] = None) -> List[Dict]:
        """
        OLD format: supports os_filter ("windows"/"linux"/"All")
        NEW format: returns pcs list; os_filter ignored because dual-boot selection is global.
        """
        pcs: List[Dict] = []

        if self._is_new_format():
            rec = self.data["labs"].get(lab, {})
            pcs = rec.get("pcs", []) if isinstance(rec, dict) else []
           
        else:
            pcs = self.data.get(lab, [])
            if os_filter and os_filter != "All":
                pcs = [pc for pc in pcs if pc.get("os") == os_filter]

        print(f"[INVENTORY] {len(pcs)} PCs for {lab} (filter: {os_filter})")
        return pcs

    def add_pc(self, lab: str, pc: Dict):
        """
        Add PC to OLD format labs (simple list).
        If you're using NEW format labs, prefer add_lab_with_layout / editing pcs directly.
        """
        if self._is_new_format():
            if lab not in self.data["labs"]:
                self.data["labs"][lab] = {"layout": {"sections": 1, "rows": 1, "cols": 1}, "pcs": []}
            rec = self.data["labs"][lab]
            if "pcs" not in rec or not isinstance(rec["pcs"], list):
                rec["pcs"] = []
            rec["pcs"].append(pc)
        else:
            if lab not in self.data:
                self.data[lab] = []
            self.data[lab].append(pc)

        self._save(self.data)
        print(f"[INVENTORY] Added PC to {lab}: {pc.get('name')} ({pc.get('ip')})")

    def add_lab_with_layout(self, lab_name: str, layout: dict, pcs: List[Dict]) -> None:
        """
        Creates/overwrites a lab using NEW format and persists to JSON.

        If current inventory is OLD format, it will be migrated into NEW format automatically.
        """
        if not self._is_new_format():
           
            old = self.data
            self.data = {"labs": {}}
            for old_lab, old_pcs in old.items():
                if old_lab == "labs":
                    continue
                self.data["labs"][old_lab] = {"layout": None, "pcs": old_pcs}

        self.data["labs"][lab_name] = {"layout": layout, "pcs": pcs}
        self._save(self.data)
        print(f"[INVENTORY] Created lab '{lab_name}' with layout {layout} and {len(pcs)} PCs")

    def remove_pc(self, lab_name: str, ip: str) -> bool:
        """
        Remove a PC by IP from a lab and persist.
        Works for both formats.
        """
        removed = False

        if self._is_new_format():
            rec = self.data["labs"].get(lab_name)
            if isinstance(rec, dict) and isinstance(rec.get("pcs"), list):
                before = len(rec["pcs"])
                rec["pcs"] = [pc for pc in rec["pcs"] if pc.get("ip") != ip]
                removed = len(rec["pcs"]) != before
        else:
            if lab_name in self.data and isinstance(self.data[lab_name], list):
                before = len(self.data[lab_name])
                self.data[lab_name] = [pc for pc in self.data[lab_name] if pc.get("ip") != ip]
                removed = len(self.data[lab_name]) != before

        if removed:
            self._save(self.data)
            print(f"[INVENTORY] Removed {ip} from {lab_name}")
        else:
            print(f"[INVENTORY] Remove failed (not found): {ip} in {lab_name}")

        return removed

    
    def delete_lab(self, lab_name: str) -> bool:
        """
        Delete an entire lab (OLD or NEW format).
        Returns True if deleted.
        """
        deleted = False

        if self._is_new_format():
            if lab_name in self.data["labs"]:
                del self.data["labs"][lab_name]
                deleted = True
        else:
            if lab_name in self.data:
                del self.data[lab_name]
                deleted = True

        if deleted:
            self._save(self.data)
            print(f"[INVENTORY] Deleted lab '{lab_name}'")
        else:
            print(f"[INVENTORY] Delete failed (lab not found): {lab_name}")

        return deleted
