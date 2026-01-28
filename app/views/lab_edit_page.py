from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QLabel, QListWidget,
    QPushButton, QHBoxLayout, QMessageBox, QDialog,
    QListWidgetItem, QLineEdit, QFormLayout, QDialogButtonBox
)
from PySide6.QtCore import Qt

from .dialogs.edit_pc_ip_dialog import EditPcIpDialog


class AddPcDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Add PC")
        self.setMinimumSize(420, 200)

        layout = QVBoxLayout(self)
        form = QFormLayout()
        form.setLabelAlignment(Qt.AlignLeft)

        self.name_in = QLineEdit()
        self.name_in.setPlaceholderText("e.g., PC-106")
        self.ip_in = QLineEdit()
        self.ip_in.setPlaceholderText("e.g., 192.168.132.250")

        form.addRow("PC Name:", self.name_in)
        form.addRow("IP Address:", self.ip_in)
        layout.addLayout(form)

        buttons = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)
        layout.addWidget(buttons)

    def values(self):
        return self.name_in.text().strip(), self.ip_in.text().strip()


class BulkIpDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Bulk IP Assign")
        self.setMinimumSize(420, 170)

        layout = QVBoxLayout(self)
        form = QFormLayout()

        self.start_ip = QLineEdit()
        self.start_ip.setPlaceholderText("e.g., 192.168.132.101")
        form.addRow("Starting IP:", self.start_ip)
        layout.addLayout(form)

        hint = QLabel("This will assign IPs sequentially to all PCs in this lab.")
        hint.setStyleSheet("color:#9aa4b2;")
        layout.addWidget(hint)

        buttons = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)
        layout.addWidget(buttons)

    def value(self):
        return self.start_ip.text().strip()


class LabEditPage(QWidget):
    def __init__(self, inventory_manager):
        super().__init__()
        self.inventory_manager = inventory_manager
        self.current_lab = None

        self._build_ui()

    def _build_ui(self):
        lay = QVBoxLayout(self)

        self.title = QLabel("Edit Lab")
        self.title.setStyleSheet("font-size:22px; font-weight:700;")
        lay.addWidget(self.title)

        self.pc_list = QListWidget()
        self.pc_list.setEditTriggers(QListWidget.DoubleClicked)
        self.pc_list.itemChanged.connect(self._inline_edit_ip)
        lay.addWidget(self.pc_list, 1)

        btns = QHBoxLayout()

        self.back_btn = QPushButton("← Back")
        self.add_btn = QPushButton("➕ Add PC")
        self.remove_btn = QPushButton("🗑 Remove PC")
        self.bulk_btn = QPushButton("🔁 Bulk IP Assign")
        self.edit_ip_btn = QPushButton("✏ Edit IP")

        self.add_btn.clicked.connect(self._add_pc)
        self.remove_btn.clicked.connect(self._remove_pc)
        self.bulk_btn.clicked.connect(self._bulk_ip_assign)
        self.edit_ip_btn.clicked.connect(self._edit_ip)

        btns.addWidget(self.back_btn)
        btns.addWidget(self.add_btn)
        btns.addWidget(self.remove_btn)
        btns.addWidget(self.bulk_btn)
        btns.addStretch()
        btns.addWidget(self.edit_ip_btn)

        lay.addLayout(btns)

    def load_lab(self, lab_name: str):
        self.current_lab = lab_name
        self.title.setText(f"Edit Lab – {lab_name}")
        self.pc_list.clear()

        pcs = self.inventory_manager.get_pcs_for_lab(lab_name)
        for pc in pcs:
            item = QListWidgetItem(f"{pc.get('name','PC')}  |  {pc.get('ip','')}")
            item.setData(Qt.UserRole, pc.copy())
            item.setFlags(item.flags() | Qt.ItemIsEditable)
            self.pc_list.addItem(item)

    # -------- Add PC --------

    def _add_pc(self):
        if not self.current_lab:
            QMessageBox.warning(self, "No Lab", "Load a lab first.")
            return

        dlg = AddPcDialog(self)
        if dlg.exec() != QDialog.Accepted:
            return

        name, ip = dlg.values()
        ok = self.inventory_manager.add_pc_to_lab(self.current_lab, name, ip)
        if not ok:
            QMessageBox.warning(self, "Add PC Failed", "Invalid IP or duplicate IP.")
            return

        self.load_lab(self.current_lab)

    # -------- Remove PC --------

    def _remove_pc(self):
        item = self.pc_list.currentItem()
        if not item:
            QMessageBox.warning(self, "Remove PC", "Select a PC first.")
            return

        try:
            _, ip = [x.strip() for x in item.text().split("|")]
        except ValueError:
            QMessageBox.warning(self, "Remove PC", "Invalid row format.")
            return

        if QMessageBox.question(self, "Remove PC", f"Remove PC with IP {ip}?") != QMessageBox.Yes:
            return

        self.inventory_manager.remove_pc(self.current_lab, ip)
        self.load_lab(self.current_lab)

 

    def _bulk_ip_assign(self):
        if not self.current_lab:
            QMessageBox.warning(self, "No Lab", "Load a lab first.")
            return

        dlg = BulkIpDialog(self)
        if dlg.exec() != QDialog.Accepted:
            return

        start_ip = dlg.value()
        ok = self.inventory_manager.bulk_assign_ips(self.current_lab, start_ip)
        if not ok:
            QMessageBox.warning(self, "Bulk Assign Failed", "Invalid IP or conflict.")
            return

        self.load_lab(self.current_lab)

  

    def _edit_ip(self):
        item = self.pc_list.currentItem()
        if not item:
            QMessageBox.warning(self, "Select PC", "Select a PC first")
            return

        text = item.text()
        name, ip = [x.strip() for x in text.split("|")]

        dlg = EditPcIpDialog(name, ip, self)
        if dlg.exec() != QDialog.Accepted:
            return

        if self.inventory_manager.update_pc_ip(self.current_lab, ip, dlg.new_ip):
            self.load_lab(self.current_lab)
        else:
            QMessageBox.warning(self, "IP Error", "Invalid or duplicate IP")

 

    def _inline_edit_ip(self, item: QListWidgetItem):
        old_pc = item.data(Qt.UserRole)
        if not old_pc:
            return

        try:
            name, new_ip = [x.strip() for x in item.text().split("|")]
        except ValueError:
            item.setText(f"{old_pc.get('name','PC')}  |  {old_pc.get('ip','')}")
            return

        old_ip = old_pc.get("ip")
        if new_ip == old_ip:
            return

        if self.inventory_manager.update_pc_ip(self.current_lab, old_ip, new_ip):
            old_pc["ip"] = new_ip
            old_pc["name"] = name or old_pc.get("name", "PC")
            item.setData(Qt.UserRole, old_pc)
        else:
            QMessageBox.warning(self, "IP Error", "Invalid or duplicate IP")
            item.setText(f"{old_pc.get('name','PC')}  |  {old_pc.get('ip','')}")
