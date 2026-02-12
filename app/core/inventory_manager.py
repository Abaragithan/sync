import json
import os
from typing import Dict, List, Optional, Any

from .config import INVENTORY_FILE, LABS


class InventoryManager:
    """
    Inventory supports TWO formats:

    OLD:
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
                print("[INVENTORY] Loaded from JSON.")
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

    def _save(self, data: Dict[str, Any]) -> None:
        with open(INVENTORY_FILE, "w") as f:
            json.dump(data, f, indent=2)
        print(f"[INVENTORY] Saved to {INVENTORY_FILE}")

    def _is_new_format(self) -> bool:
        return isinstance(self.data, dict) and "labs" in self.data and isinstance(self.data["labs"], dict)

    def _migrate_old_to_new_if_needed(self) -> None:
        """
        If inventory is old format, migrate it into NEW format once.
        """
        if self._is_new_format():
            return

        old = self.data
        new = {"labs": {}}

        for lab_name, pcs in old.items():
            if lab_name == "labs":
                continue
          
            new["labs"][lab_name] = {"layout": None, "pcs": pcs}

        self.data = new
        self._save(self.data)
        print("[INVENTORY] Migrated OLD format -> NEW format")



    def get_all_labs(self) -> List[str]:
        if self._is_new_format():
            labs = list(self.data["labs"].keys())
        else:
            labs = list(self.data.keys())

        print(f"[INVENTORY] All labs: {labs}")
        return labs

    def get_lab_layout(self, lab_name: str) -> Optional[dict]:
        """
        Returns layout dict if lab exists in NEW format, else None.
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

   
    def add_lab_with_layout(self, lab_name: str, layout: dict, pcs: List[Dict]) -> None:
        """
        Create/overwrite a lab in NEW format with explicit layout + pcs.
        If currently OLD format, migrate to NEW first.
        """
        self._migrate_old_to_new_if_needed()

        self.data["labs"][lab_name] = {
            "layout": layout,
            "pcs": pcs
        }
        self._save(self.data)
        print(f"[INVENTORY] Created lab '{lab_name}' with {len(pcs)} PCs")

    def delete_lab(self, lab_name: str) -> bool:
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

    def add_pc(self, lab: str, pc: Dict) -> bool:
        """
        Add a PC to a lab. Returns True if successful, False if duplicate IP.
        """
        # Check for duplicate IP first
        existing_pcs = self.get_pcs_for_lab(lab)
        for existing in existing_pcs:
            if existing.get("ip") == pc.get("ip"):
                print(f"[INVENTORY] Duplicate IP blocked: {pc.get('ip')}")
                return False
        
        if self._is_new_format():
            if lab not in self.data["labs"]:
                self.data["labs"][lab] = {"layout": None, "pcs": []}
            rec = self.data["labs"][lab]
            if "pcs" not in rec or not isinstance(rec["pcs"], list):
                rec["pcs"] = []
            rec["pcs"].append(pc)
        else:
            if lab not in self.data:
                self.data[lab] = []
            self.data[lab].append(pc)

        self._save(self.data)
        print(f"[INVENTORY] Added PC to {lab}: {pc.get('name')} ({pc.get('ip')}) at section {pc.get('section')}, row {pc.get('row')}, col {pc.get('col')}")
        return True
    
    def remove_pc(self, lab_name: str, ip: str) -> bool:
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

    def update_pc_ip(self, lab_name: str, old_ip: str, new_ip: str) -> bool:
        pcs = self.get_pcs_for_lab(lab_name)

        # prevent duplicates
        for pc in pcs:
            if pc.get("ip") == new_ip:
                print("[INVENTORY] Duplicate IP blocked:", new_ip)
                return False

      
        for pc in pcs:
            if pc.get("ip") == old_ip:
                pc["ip"] = new_ip
                self._save(self.data)
                print(f"[INVENTORY] IP updated {old_ip} → {new_ip}")
                return True

        return False
