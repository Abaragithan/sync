APP_QSS = """
/* --- GLOBAL & BASE --- */
QWidget {
    background-color: #121212;
    color: #e2e8f0;
    font-family: 'Segoe UI', sans-serif;
    font-size: 14px;
    border: none;
}

/* --- PAGE TITLES & TEXT --- */
QLabel#PageTitle {
    font-size: 28px;
    font-weight: 800;
    color: #ffffff;
}

QLabel#SubText {
    color: #94a3b8;
    font-size: 13px;
}

/* --- DASHBOARD CARD SPECIFIC --- */
QFrame#DashboardCard {
    background-color: #1e293b;
    border: 1px solid #334155;
    border-radius: 10px;
    padding: 0px;
}
QFrame#DashboardCard:hover {
    background-color: #263346;
    border: 1px solid #475569;
}

QLabel#CardTitle {
    font-size: 16px;
    font-weight: 700;
    color: #ffffff;
}

QLabel#CardSubtitle {
    font-size: 13px;
    color: #94a3b8;
}

/* --- BUTTONS --- */
QPushButton {
    background-color: #2563eb;
    color: #ffffff;
    border: none;
    border-radius: 8px;
    padding: 10px 20px;
    font-weight: 600;
    font-size: 14px;
}
QPushButton:hover { background-color: #1d4ed8; }
QPushButton:pressed { background-color: #1e40af; }
QPushButton:disabled {
    background-color: #334155;
    color: #64748b;
}

/* Button Variants based on ObjectName */
QPushButton#SecondaryBtn {
    background-color: transparent;
    border: 1px solid #475569;
    color: #cbd5e1;
}
QPushButton#SecondaryBtn:hover {
    background-color: #334155;
    border-color: #64748b;
    color: #fff;
}

QPushButton#DangerBtn {
    background-color: #7f1d1d;
    color: #fecaca;
    padding: 8px 16px;
}
QPushButton#DangerBtn:hover { background-color: #991b1b; }

QPushButton#PrimaryBtn {
    background-color: #3b82f6;
    padding: 10px 24px;
    font-weight: 700;
}

/* --- INPUTS & COMBOBOX --- */
QLineEdit, QComboBox, QSpinBox, QTextEdit {
    background-color: #0f172a;
    border: 1px solid #334155;
    border-radius: 6px;
    padding: 8px;
    color: white;
    selection-background-color: #3b82f6;
}
QLineEdit:focus, QComboBox:focus, QSpinBox:focus {
    border: 1px solid #3b82f6;
}

/* --- SCROLL AREA --- */
QScrollArea {
    border: none;
    background-color: transparent;
}
QScrollBar:vertical {
    background: #1e293b;
    width: 10px;
    border-radius: 5px;
    margin: 0px;
}
QScrollBar::handle:vertical {
    background: #475569;
    border-radius: 5px;
    min-height: 20px;
}
QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
    height: 0;
}

/* --- LIST WIDGET (For Edit Page) --- */
QListWidget {
    background-color: #0f172a;
    border: 1px solid #334155;
    border-radius: 8px;
}
QListWidget::item {
    padding: 8px;
    border-radius: 4px;
    margin-bottom: 2px;
}
QListWidget::item:selected {
    background-color: #1e3a8a;
    color: white;
}
QListWidget::item:hover {
    background-color: #1e293b;
}

/* --- TOOLTIP --- */
QToolTip {
    background-color: #020617;
    color: #ffffff;
    border: 1px solid #334155;
    padding: 6px;
    border-radius: 6px;
    font-size: 12px;
}
"""