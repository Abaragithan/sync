import os
import subprocess
from PySide6.QtCore import QThread, Signal


class AnsibleWorker(QThread):
    """
    Runs Docker + Ansible command in a background thread.
    Emits live output lines.
    Does NOT block UI.
    """

    output_received = Signal(str)
    finished = Signal(bool)  # True if success

    def __init__(self, command_args: list):
        """
        command_args must be a LIST, not string.
        Example:
        [
            "docker", "run", "--rm",
            "-v", "...:/app",
            ...
        ]
        """
        super().__init__()
        self.command_args = command_args

    def run(self):
        try:
            process = subprocess.Popen(
                self.command_args,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                text=True
            )

            for line in iter(process.stdout.readline, ""):
                if line:
                    self.output_received.emit(line.rstrip())

            process.stdout.close()
            process.wait()

            self.finished.emit(process.returncode == 0)

        except Exception as e:
            self.output_received.emit(f"[ERROR] {str(e)}")
            self.finished.emit(False)