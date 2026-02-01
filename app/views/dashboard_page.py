from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, 
    QFrame, QScrollArea, QMessageBox, QDialog, QSizePolicy, QGridLayout
)
from PySide6.QtCore import Signal, Qt

# Make sure you have access to these classes from your project structure
from .create_lab_dialog import CreateLabDialog 
from core.inventory_manager import InventoryManager

class DashboardPage(QWidget):
    """
    Page inserted between Welcome and Lab.
    Lists labs in a 2-column Grid. Each card is a single large container.
    """
    lab_selected = Signal(str)      # Emits lab name when "Open" is clicked
    edit_lab_requested = Signal(str) # NEW: Emits lab name when "Edit" is clicked
    back_requested = Signal()       # Emits when "Back" is clicked

    def __init__(self, inventory_manager):
        super().__init__()
        self.inventory_manager = inventory_manager
        self._build_ui()
        self.refresh_labs()

    def _build_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(30, 30, 30, 30)
        layout.setSpacing(20)

        # --- Header ---
        header_layout = QHBoxLayout()
        
        # Back Button (if you want it here, though you removed it in previous prompt. 
        # I will leave it out based on your latest request unless you asked to keep it. 
        # But the previous code had it removed. I'll keep it clean as per your paste.)
        
        self.title = QLabel("Lab Management")
        self.title.setObjectName("PageTitle")
        header_layout.addWidget(self.title)
        
        header_layout.addStretch()
        
        self.create_btn = QPushButton("Create New Lab")
        self.create_btn.setObjectName("PrimaryBtn")
        self.create_btn.setCursor(Qt.PointingHandCursor)
        self.create_btn.clicked.connect(self._open_create_dialog)
        header_layout.addWidget(self.create_btn)
        
        layout.addLayout(header_layout)

        # --- Scroll Area for Lab Grid ---
        self.scroll = QScrollArea()
        self.scroll.setWidgetResizable(True)
        self.scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        
        self.scroll_widget = QWidget()
        
        # CHANGED: Using QGridLayout instead of QVBoxLayout
        # This creates the "half display size" effect (2 columns)
        self.scroll_layout = QGridLayout(self.scroll_widget)
        self.scroll_layout.setSpacing(16) # Space between cards
        self.scroll_layout.setAlignment(Qt.AlignTop | Qt.AlignLeft)
        
        self.scroll.setWidget(self.scroll_widget)
        layout.addWidget(self.scroll)

        # --- Status Label (Footer) ---
        self.status_lbl = QLabel("Select a lab to manage or create a new one.")
        self.status_lbl.setObjectName("SubText")
        self.status_lbl.setAlignment(Qt.AlignCenter)
        layout.addWidget(self.status_lbl)

    def refresh_labs(self):
        """Clears current view and reloads labs in a grid."""
        # 1. Clear existing widgets
        while self.scroll_layout.count():
            item = self.scroll_layout.takeAt(0)
            widget = item.widget()
            if widget:
                widget.deleteLater()

        # 2. Fetch data
        labs = self.inventory_manager.get_all_labs()
        
        if not labs:
            self.status_lbl.setText("No labs found. Create one to get started.")
            return

        self.status_lbl.setText(f"Found {len(labs)} lab(s).")

        # 3. Build UI in Grid (2 Columns)
        # row = index // 2, col = index % 2
        for i, lab_name in enumerate(labs):
            card = self._create_lab_card(lab_name)
            self.scroll_layout.addWidget(card, i // 2, i % 2)

    def _create_lab_card(self, lab_name: str) -> QFrame:
        """
        Creates ONE single container for a lab.
        All details are stacked vertically inside this one box.
        """
        card = QFrame()
        card.setObjectName("DashboardCard")
        
        # Size Policies: Expands horizontally, Fixed vertically (enough height)
        card.setMinimumWidth(300) 
        card.setMinimumHeight(200) 
        card.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        
        # Main Vertical Layout for the Container
        main_layout = QVBoxLayout(card)
        main_layout.setContentsMargins(20, 16, 20, 16)
        main_layout.setSpacing(10)

        # --- 1. Title ---
        name_lbl = QLabel(lab_name)
        name_lbl.setObjectName("CardTitle")
        main_layout.addWidget(name_lbl)

        # --- 2. Separator Line (Visual separation) ---
        line = QFrame()
        line.setFrameShape(QFrame.HLine)
        line.setFrameShadow(QFrame.Sunken)
        line.setStyleSheet("background-color: #334155; max-height: 1px; margin-top: 5px;")
        main_layout.addWidget(line)

        # --- 3. Details (Stacked vertically) ---
        pcs = self.inventory_manager.get_pcs_for_lab(lab_name)
        layout_data = self.inventory_manager.get_lab_layout(lab_name)
        
        # Calculate IP Range
        ip_range = "N/A"
        if pcs:
            ip_list = sorted([pc['ip'] for pc in pcs])
            ip_range = f"{ip_list[0]} - {ip_list[-1]}"

        # Layout string
        layout_str = "N/A"
        if layout_data:
            layout_str = f"{layout_data.get('sections', 0)} Sections, {layout_data.get('rows', 0)} Rows, {layout_data.get('cols', 0)} Cols"

        # Detail Labels
        lbl_pcs = QLabel(f"Total PCs: {len(pcs)}")
        lbl_pcs.setObjectName("CardSubtitle")
        
        lbl_layout = QLabel(f"Structure: {layout_str}")
        lbl_layout.setObjectName("CardSubtitle")
        
        lbl_ip = QLabel(f"IP Range: {ip_range}")
        lbl_ip.setObjectName("CardSubtitle")

        main_layout.addWidget(lbl_pcs)
        main_layout.addWidget(lbl_layout)
        main_layout.addWidget(lbl_ip)

        # --- 4. Spacer to push buttons down ---
        main_layout.addStretch()

        # --- 5. Buttons (Bottom of container) ---
        btn_layout = QHBoxLayout()
        btn_layout.setSpacing(10)
        
        # 1. Delete Button
        del_btn = QPushButton("Delete")
        del_btn.setObjectName("DangerBtn")
        del_btn.setFixedWidth(90)
        del_btn.setFixedHeight(32)
        del_btn.clicked.connect(lambda checked, name=lab_name: self._confirm_delete(name))
        
        # 2. Edit Button (NEW)
        edit_btn = QPushButton("Edit")
        edit_btn.setObjectName("SecondaryBtn")
        edit_btn.setFixedWidth(90)
        edit_btn.setFixedHeight(32)
        edit_btn.clicked.connect(lambda: self.edit_lab_requested.emit(lab_name))
        
        # 3. Open Button
        open_btn = QPushButton("Open Lab")
        open_btn.setObjectName("SecondaryBtn")
        # Make button fill remaining width
        open_btn.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        open_btn.setFixedHeight(32)
        open_btn.clicked.connect(lambda: self.lab_selected.emit(lab_name))

        # Add in order: Delete -> Edit -> (Stretch) -> Open
        btn_layout.addWidget(del_btn)
        btn_layout.addWidget(edit_btn)
        btn_layout.addWidget(open_btn)

        main_layout.addLayout(btn_layout)

        return card

    def _open_create_dialog(self):
        """Opens the dialog to create a new lab."""
        try:
            dlg = CreateLabDialog(self)
            if dlg.exec() != QDialog.Accepted:
                return

            data = dlg.get_data()
            layout = data["layout"]
            ips = data["ips"]

            # Reconstruct PC list
            pcs = []
            idx = 0
            for sec in range(1, layout["sections"] + 1):
                for r in range(1, layout["rows"] + 1):
                    for c in range(1, layout["cols"] + 1):
                        pcs.append({
                            "name": f"PC-{idx+1:03d}",
                            "ip": ips[idx],
                            "section": sec,
                            "row": r,
                            "col": c
                        })
                        idx += 1

            self.inventory_manager.add_lab_with_layout(data["lab_name"], layout, pcs)
            self.refresh_labs()
            
            QMessageBox.information(self, "Success", f"Lab '{data['lab_name']}' created.")

        except NameError:
            QMessageBox.critical(self, "Error", "CreateLabDialog not found in imports.")
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to create lab: {str(e)}")

    def _confirm_delete(self, lab_name: str):
        reply = QMessageBox.question(
            self, 
            "Delete Lab", 
            f"Are you sure you want to delete '{lab_name}'?", 
            QMessageBox.Yes | QMessageBox.No
        )
        if reply == QMessageBox.Yes:
            if self.inventory_manager.delete_lab(lab_name):
                self.refresh_labs()
            else:
                QMessageBox.warning(self, "Error", "Could not delete lab.")