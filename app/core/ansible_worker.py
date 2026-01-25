import subprocess
from PySide6.QtCore import QThread, Signal

class AnsibleWorker(QThread):
    output_received = Signal(str)
    finished = Signal(bool)  # True if success

    def __init__(self, cmd: str):
        super().__init__()
        self.cmd = cmd

    def run(self):
        try:
            process = subprocess.Popen(
                self.cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True, cwd="ansible"  # Run in ansible dir
            )
            for line in iter(process.stdout.readline, ""):
                if line:
                    self.output_received.emit(line.strip())
            process.stdout.close()
            process.wait()
            self.finished.emit(process.returncode == 0)
        except Exception as e:
            self.output_received.emit(f"Error: {str(e)}")
            self.finished.emit(False)