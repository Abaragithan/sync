# views/software_controller.py
from __future__ import annotations

import os
import sys

from core.ansible_worker import AnsibleWorker


def _get_project_root() -> str:
    if getattr(sys, "frozen", False):
        exe_dir = os.path.dirname(sys.executable)
        project_root = os.path.abspath(os.path.join(exe_dir, ".."))
    else:
        here = os.path.dirname(os.path.abspath(__file__))
        project_root = os.path.abspath(os.path.join(here, "..", ".."))

    ansible_dir = os.path.join(project_root, "ansible")
    if not os.path.exists(ansible_dir):
        print(f"[WARNING] ansible/ folder not found at: {project_root}")

    return project_root


class SoftwareController:
    def __init__(self, log_panel, progress_bar, execute_btn, state):
        self.log_panel    = log_panel
        self.progress_bar = progress_bar
        self.execute_btn  = execute_btn
        self.state        = state
        self._worker: AnsibleWorker | None = None
        self._last_payload: dict | None = None

    # =========================================================================
    # Public API called by SoftwarePage
    # =========================================================================
    def run(self, payload: dict):
        self._last_payload = payload
        self.log_panel.clear()
        self._run_ansible(payload)

    def retry(self):
        if self._last_payload is None:
            return
        self.progress_bar.set_step("executing")
        self.execute_btn.setEnabled(False)
        self.execute_btn.setText("Executing...")
        self.log_panel.clear()
        self._run_ansible(self._last_payload)

    # =========================================================================
    # Internal logic
    # =========================================================================
    def _run_ansible(self, payload: dict):
        os_name = payload.get("os", self.state.target_os)
        action  = payload.get("action", self.state.action)
        targets = payload.get("targets", self.state.selected_targets)

        project_root = _get_project_root()
        ssh_dir      = os.path.expanduser("~/.ssh")
        vault_pass   = os.path.expanduser("~/.ansible_vault_pass")
        sw_repo      = os.path.join(project_root, "software_repo")

        app_state_map = {"install": "present", "remove": "absent", "update": "latest"}
        app_state = app_state_map.get(action, "present")

        target_host = "windows_clients" if os_name == "windows" else "linux_clients"
        extra: dict[str, str] = {
            "app_state":   app_state,
            "target_host": target_host,
        }

        # ── Windows Install ───────────────────────────────────────────────────
        if action == "install" and os_name == "windows":
            choco_pkg = payload.get("choco_package", "").strip()
            file_path = payload.get("file", "").strip()

            if not choco_pkg and not file_path:
                self.log_panel.append_line(
                    "✗ Enter a Chocolatey package name or select a local installer file.", "error"
                )
                self._on_execution_finished(ok=False)
                return

            if choco_pkg:
                extra["choco_package"] = choco_pkg
            else:
                file_name = os.path.basename(file_path)
                extra["file_name"] = file_name
                self._ensure_in_repo(file_path, sw_repo)
                if payload.get("args", "").strip():
                    extra["custom_install_args"] = payload["args"].strip()

        # ── Windows Remove ────────────────────────────────────────────────────
        elif action == "remove" and os_name == "windows":
            choco_pkg = payload.get("choco_package", "").strip()
            app_name  = payload.get("app_name", "").strip()

            if not choco_pkg and not app_name:
                self.log_panel.append_line(
                    "✗ Enter a Chocolatey package name or an application display name.", "error"
                )
                self._on_execution_finished(ok=False)
                return

            if choco_pkg:
                extra["choco_package"] = choco_pkg
            else:
                extra["app_name"] = app_name

        # ── Windows Update ────────────────────────────────────────────────────
        elif action == "update" and os_name == "windows":
            choco_pkg = payload.get("choco_package", "").strip()
            if not choco_pkg:
                self.log_panel.append_line(
                    "✗ Enter a Chocolatey package name or tick 'Upgrade ALL'.", "error"
                )
                self._on_execution_finished(ok=False)
                return
            extra["choco_package"] = choco_pkg

        # ── Linux Install ─────────────────────────────────────────────────────
        elif action == "install" and os_name == "linux":
            pkgs = payload.get("packages", "").strip()
            if not pkgs:
                self.log_panel.append_line("✗ No packages specified.", "error")
                self._on_execution_finished(ok=False)
                return
            extra["package_name"] = pkgs

        # ── Linux Remove ──────────────────────────────────────────────────────
        elif action == "remove" and os_name == "linux":
            pkgs = payload.get("packages", "").strip()
            if not pkgs:
                self.log_panel.append_line("✗ No packages specified.", "error")
                self._on_execution_finished(ok=False)
                return
            extra["package_name"] = pkgs
            extra["purge"]        = "true" if payload.get("purge", False) else "false"
            extra["autoremove"]   = "true" if payload.get("autoremove", True) else "false"

        # ── Linux Update ──────────────────────────────────────────────────────
        elif action == "update" and os_name == "linux":
            dist_upgrade = payload.get("dist_upgrade", False)
            pkgs         = payload.get("packages", "").strip()
            extra["dist_upgrade"] = "true" if dist_upgrade else "false"
            if pkgs and not dist_upgrade:
                extra["package_name"] = pkgs

        # ── Write temp inventory ──────────────────────────────────────────────
        tmp_inv = self._write_temp_inventory(
            project_root, targets, os_name, target_host
        )
        if tmp_inv is None:
            self.log_panel.append_line("✗ Could not write temporary inventory.", "error")
            self._on_execution_finished(ok=False)
            return

        inv_container_path = "/app/ansible/inventory/_sync_tmp_inventory.ini"

        ev_str = " ".join(f"{k}={v}" for k, v in extra.items())

        self.log_panel.append_line(
            f"▶ ansible-playbook  [{action.upper()} / {os_name.upper()}]"
            f"  →  {len(targets)} host(s)", "dim"
        )
        self.log_panel.append_line(f"  Hosts : {', '.join(targets)}", "dim")
        self.log_panel.append_line(f"  Vars  : {ev_str}", "dim")
        self.log_panel.append_line("", "dim")

        cmd = [
            "docker", "run", "--rm",
            "-v", f"{project_root}:/app",
            "-v", f"{ssh_dir}:/root/.ssh:ro",
        ]

        if action == "install" and os_name == "windows" and extra.get("file_name"):
            cmd += ["-v", f"{sw_repo}:/app/software_repo"]

        if os_name == "linux" and os.path.exists(vault_pass):
            cmd += ["-v", f"{vault_pass}:/vault_pass:ro"]

        cmd += [
            "-w", "/app/ansible",
            "sync-ansible:latest",
            "ansible-playbook",
            "-i", inv_container_path,
            "playbooks/master_deploy_v2.yml",
            "-e", ev_str,
        ]

        if os_name == "linux" and os.path.exists(vault_pass):
            cmd += ["--vault-password-file=/vault_pass"]

        if self._worker and self._worker.isRunning():
            self.log_panel.append_line(
                "⚠ A task is already running. Wait for it to finish.", "error"
            )
            return

        self._worker = AnsibleWorker(cmd)
        self._worker.output_received.connect(self._on_ansible_line)
        self._worker.finished.connect(
            lambda ok: self._on_execution_finished(ok, tmp_inv)
        )
        self._worker.start()

    @staticmethod
    def _write_temp_inventory(
        project_root: str,
        targets: list[str],
        os_name: str,
        group: str,
    ) -> str | None:

        ansible_dir = os.path.join(project_root, "ansible")
        real_inv    = os.path.join(ansible_dir, "inventory", "hosts.ini")
        inv_dir     = os.path.join(ansible_dir, "inventory")
        os.makedirs(inv_dir, exist_ok=True)
        tmp_path    = os.path.join(inv_dir, "_sync_tmp_inventory.ini")

        group_vars_lines: list[str] = []
        if os.path.exists(real_inv):
            with open(real_inv, "r") as f:
                in_vars = False
                for line in f:
                    stripped = line.strip()
                    if stripped == f"[{group}:vars]":
                        in_vars = True
                        group_vars_lines.append(line)
                        continue
                    if in_vars:
                        if stripped.startswith("["):
                            in_vars = False
                        else:
                            group_vars_lines.append(line)
        else:
            print(f"[SoftwarePage] WARNING: hosts.ini not found at {real_inv}")

        try:
            with open(tmp_path, "w") as f:
                f.write(f"[{group}]\n")
                for ip in targets:
                    f.write(f"{ip}\n")
                f.write("\n")
                for line in group_vars_lines:
                    f.write(line)
            return tmp_path
        except OSError as e:
            print(f"[SoftwarePage] Failed to write temp inventory: {e}")
            return None

    @staticmethod
    def _ensure_in_repo(src_path: str, repo_dir: str):
        import shutil
        os.makedirs(repo_dir, exist_ok=True)
        dst = os.path.join(repo_dir, os.path.basename(src_path))
        if not os.path.exists(dst):
            try:
                shutil.copy2(src_path, dst)
            except OSError as e:
                print(f"[SoftwarePage] Could not copy installer to repo: {e}")

    def _on_ansible_line(self, line: str):
        low = line.lower()
        if any(kw in low for kw in ("fatal:", "error", "failed!", "unreachable")):
            self.log_panel.append_line(line, "error")
        elif line.strip() == "" or line.strip().startswith("*"):
            self.log_panel.append_line(line, "dim")
        else:
            self.log_panel.append_line(line, "normal")

    def _on_execution_finished(self, ok: bool, tmp_inv: str | None = None):
        if tmp_inv and os.path.exists(tmp_inv):
            try:
                os.remove(tmp_inv)
            except OSError:
                pass
        self.progress_bar.set_step("done", failed=not ok)
        self.log_panel.set_status(ok)
        self.execute_btn.setEnabled(True)
        self.execute_btn.setText("Execute →")
        self._worker = None