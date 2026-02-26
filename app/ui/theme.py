

LIGHT_QSS = """
/* --- GLOBAL & BASE --- */
QWidget {
    background-color: #f8fafc;
    color: #0f172a;
    font-family: 'Segoe UI', sans-serif;
    font-size: 14px;
    border: none;
}

/* ================================ */
/* ===== THEME SWITCH (LIGHT) ===== */
/* ================================ */
QCheckBox#ThemeSwitch {
    spacing: 10px;
    font-weight: 700;
    color: #0f172a;
}

QCheckBox#ThemeSwitch::indicator {
    width: 46px;
    height: 24px;
    border-radius: 12px;
    background: #cbd5e1;
    border: 1px solid #94a3b8;
}

QCheckBox#ThemeSwitch::indicator:checked {
    background: #2563eb;
    border: 1px solid #1d4ed8;
}

QCheckBox#ThemeSwitch::indicator {
    padding: 2px;
}

QCheckBox#ThemeSwitch:hover::indicator {
    border: 1px solid #64748b;
}


/* --- PAGE TITLES & TEXT --- */
QLabel#PageTitle {
    font-size: 28px;
    font-weight: 800;
    color: #0f172a;
}

QLabel#SubText {
    color: #475569;
    font-size: 13px;
}

QLabel#MutedText {
    color: #475569;
}

/* --- DASHBOARD CARD SPECIFIC (OLD/OTHER PAGES) --- */
QFrame#DashboardCard {
    background-color: #ffffff;
    border: 1px solid #e2e8f0;
    border-radius: 10px;
    padding: 0px;
}
QFrame#DashboardCard:hover {
    background-color: #f1f5f9;
    border: 1px solid #cbd5e1;
}

QLabel#CardTitle {
    font-size: 16px;
    font-weight: 700;
    color: #0f172a;
}

QLabel#CardSubtitle {
    font-size: 13px;
    color: #475569;
}

/* =============================== */
/* ===== DASHBOARD (EXTRAS)  ===== */
/* =============================== */

QLabel#Brand {
    font-size: 20px;
    font-weight: 700;
    color: #0f172a;
}

QPushButton#CreateButton {
    padding: 10px 18px;
    border-radius: 10px;
    font-weight: 800;
}

/* Lab Card Buttons (balanced size) */
QPushButton#EditButton,
QPushButton#OpenButton,
QPushButton#DeleteButton {
    padding: 9px 14px;
    border-radius: 10px;
    font-weight: 700;
}

/* Stats Panel */
QFrame#StatsPanel {
    background-color: #ffffff;
    border: 1px solid rgba(0, 0, 0, 18);
    border-radius: 18px;
}

QLabel#StatsTitle {
    font-size: 15px;
    font-weight: 800;
    color: rgba(15, 23, 42, 240);
}

QLabel#StatsSubTitle {
    font-size: 12px;
    color: rgba(15, 23, 42, 130);
}

QFrame#StatChip {
    background-color: rgba(15, 23, 42, 6);
    border: 1px solid rgba(0, 0, 0, 10);
    border-radius: 14px;
}

QLabel#StatValue {
    font-size: 16px;
    font-weight: 900;
    color: rgba(15, 23, 42, 240);
}

QLabel#StatLabel {
    font-size: 12px;
    color: rgba(15, 23, 42, 150);
}


/* ------------------------------------------------------------------ */
/* ✅ YOUR DASHBOARD LAB CARDS (LabCard)                                */
/* Realistic hover look (outline)                                       */
/* Smooth animation handled in code                                    */
/* ------------------------------------------------------------------ */
QFrame#LabCard {
    background-color: #ffffff;
    border: 1.6px solid rgba(0, 0, 0, 25);
    border-radius: 16px;
}
QFrame#LabCard:hover {
    background-color: #f8fafc;
    border: 2px solid rgba(37, 99, 235, 90);
}

/* Remove line-by-line row color */
QWidget#LabInfoRow {
    background: transparent;
}
QLabel#LabInfoLabel,
QLabel#LabInfoValue {
    background: transparent;
    border: none;
    padding: 0px;
}

QLabel#LabInfoLabel { color: rgba(15, 23, 42, 150); }
QLabel#LabInfoValue { color: rgba(15, 23, 42, 235); }

/* Lab name title on card (no highlight box) */
QLabel#LabName {
    background: transparent;
    border: none;
    padding: 0px;
    margin: 0px;
    text-decoration: none;

    font-size: 16px;
    font-weight: 900;
    color: #0f172a;
}
QLabel#LabName::selected { background: transparent; color: inherit; }

/* --- BUTTONS (GLOBAL DEFAULT) --- */
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
    background-color: #cbd5e1;
    color: #64748b;
}

/* Button Variants based on ObjectName */
QPushButton#SecondaryBtn {
    background-color: transparent;
    border: 1px solid #cbd5e1;
    color: #0f172a;
}
QPushButton#SecondaryBtn:hover {
    background-color: #e2e8f0;
    border-color: #94a3b8;
}

QPushButton#DangerBtn {
    background-color: #ef4444;
    color: #ffffff;
    padding: 8px 16px;
}
QPushButton#DangerBtn:hover { background-color: #dc2626; }

QPushButton#PrimaryBtn {
    background-color: #3b82f6;
    padding: 10px 24px;
    font-weight: 700;
}

/* --- INPUTS & COMBOBOX --- */
QLineEdit, QComboBox, QSpinBox, QTextEdit {
    background-color: #ffffff;
    border: 1px solid #cbd5e1;
    border-radius: 6px;
    padding: 8px;
    color: #0f172a;
    selection-background-color: #3b82f6;
}
QLineEdit:focus, QComboBox:focus, QSpinBox:focus, QTextEdit:focus {
    border: 1px solid #2563eb;
}

/* --- SCROLL AREA --- */
QScrollArea {
    border: none;
    background-color: transparent;
}
QScrollBar:vertical {
    background: #e2e8f0;
    width: 10px;
    border-radius: 5px;
    margin: 0px;
}
QScrollBar::handle:vertical {
    background: #94a3b8;
    border-radius: 5px;
    min-height: 20px;
}
QScrollBar::handle:vertical:hover {
    background: #64748b;
}
QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
    height: 0;
}

/* --- LIST WIDGET --- */
QListWidget {
    background-color: #ffffff;
    border: 1px solid #cbd5e1;
    border-radius: 8px;
}
QListWidget::item {
    padding: 8px;
    border-radius: 4px;
    margin-bottom: 2px;
}
QListWidget::item:selected {
    background-color: #bfdbfe;
    color: #0f172a;
}
QListWidget::item:hover {
    background-color: #f1f5f9;
}

/* --- TOOLTIP --- */
QToolTip {
    background-color: #0f172a;
    color: #ffffff;
    border: 1px solid #334155;
    padding: 6px;
    border-radius: 6px;
    font-size: 12px;
}

/* --- LAB PAGE --- */
QFrame#SectionCard {
    background-color: #ffffff;
    border: 1px solid #cbd5e1;
    border-radius: 12px;
}

QLabel#SectionTitle {
    font-weight: 700;
    color: #0f172a;
}

QFrame#FooterBar {
    background-color: #ffffff;
    border-radius: 10px;
    border: 1px solid #cbd5e1;
}

/* --- WELCOME PAGE (NO BORDER) --- */
QFrame#WelcomeCard {
    background-color: transparent;
    border: none;
    border-radius: 16px;
}

QLabel#WelcomeTitle {
    font-size: 44px;
    font-weight: 800;
    color: #0f172a;
}

QLabel#WelcomeSub {
    color: #475569;
    font-size: 14px;
}

QLabel#WelcomeLogoFallback {
    font-size: 24px;
    font-weight: 800;
    color: #64748b;
}

/* --- SOFTWARE PAGE (SCOPED) --- */
QWidget#SoftwarePage QFrame#Card {
    background-color: #ffffff;
    border: 1px solid #e2e8f0;
    border-radius: 14px;
    padding: 10px;
}

QWidget#SoftwarePage QLabel#CardHeader {
    font-weight: 900;
    font-size: 15px;
    color: #0f172a;
    padding: 6px 2px;
}

QWidget#SoftwarePage QLineEdit#SoftwareSearch {
    background-color: #ffffff;
    border: 1px solid #cbd5e1;
    border-radius: 10px;
    padding: 10px 12px;
    color: #0f172a;
}

QWidget#SoftwarePage QListWidget#SoftwareList {
    background-color: #ffffff;
    border: 1px solid #cbd5e1;
    border-radius: 10px;
}

QWidget#SoftwarePage QLabel#TargetsPill {
    background: rgba(15, 23, 42, 0.04);
    border: 1px solid rgba(15, 23, 42, 0.10);
    border-radius: 10px;
    padding: 6px 10px;
    color: rgba(15, 23, 42, 0.90);
    font-weight: 800;
}


/* Card buttons: compact + clean */
QFrame#LabCard QPushButton#EditButton,
QFrame#LabCard QPushButton#OpenButton,
QFrame#LabCard QPushButton#DeleteButton {
    padding: 6px 10px;
    min-height: 28px;
    max-height: 28px;
    font-size: 12px;
    font-weight: 800;
    border-radius: 10px;
    margin: 0px;
}

/* Edit = outlined */
QFrame#LabCard QPushButton#EditButton {
    background-color: #ffffff;
    border: 1px solid rgba(15, 23, 42, 60);
    color: rgba(15, 23, 42, 220);
}
QFrame#LabCard QPushButton#EditButton:hover {
    background-color: #f1f5f9;
    border: 1px solid rgba(37, 99, 235, 120);
}

/* Open = primary */
QFrame#LabCard QPushButton#OpenButton {
    background-color: #2563eb;
    border: 1px solid rgba(37, 99, 235, 180);
    color: white;
}
QFrame#LabCard QPushButton#OpenButton:hover { background-color: #1d4ed8; }
QFrame#LabCard QPushButton#OpenButton:pressed { background-color: #1e40af; }

/* Delete = danger */
QFrame#LabCard QPushButton#DeleteButton {
    background-color: #ef4444;
    border: 1px solid rgba(239, 68, 68, 200);
    color: white;
}
QFrame#LabCard QPushButton#DeleteButton:hover { background-color: #dc2626; }
QFrame#LabCard QPushButton#DeleteButton:pressed { background-color: #b91c1c; }


/* ================================ */
/* ===== CONFIRM DELETE DIALOG ==== */
/* ================================ */

QFrame#ConfirmDeleteCard {
    background-color: rgba(255, 255, 255, 245);
    border: 1px solid rgba(15, 23, 42, 30);
    border-radius: 14px;
}

QLabel#ConfirmDeleteTitle {
    font-size: 16px;
    font-weight: 900;
    color: #0f172a;
}

QLabel#ConfirmDeleteSubtitle {
    color: rgba(15, 23, 42, 170);
    font-size: 13px;
}

QFrame#ConfirmDeleteDivider {
    background: rgba(15, 23, 42, 20);
}

QPushButton#ConfirmCancelBtn {
    background: #ffffff;
    border: 1px solid rgba(15, 23, 42, 40);
    color: rgba(15, 23, 42, 230);
    border-radius: 10px;
    padding: 6px 14px;
    font-weight: 800;
}
QPushButton#ConfirmCancelBtn:hover {
    background: #f1f5f9;
    border: 1px solid rgba(37, 99, 235, 110);
}

QPushButton#ConfirmDeleteBtn {
    background: #ef4444;
    border: 1px solid rgba(239, 68, 68, 200);
    color: white;
    border-radius: 10px;
    padding: 6px 14px;
    font-weight: 900;
}
QPushButton#ConfirmDeleteBtn:hover { background: #dc2626; }
QPushButton#ConfirmDeleteBtn:pressed { background: #b91c1c; }

/* =============================== */
/* ===== CREATE LAB DIALOG ======= */
/* =============================== */

QDialog#CreateLabDialog QFrame#CreateLabCard {
    background-color: #ffffff;
    border: 1px solid rgba(15,23,42,0.10);
    border-radius: 16px;
}

QDialog#CreateLabDialog QLabel#CreateLabTitle {
    color: #0f172a;
    font-size: 18px;
    font-weight: 800;
}

QDialog#CreateLabDialog QLabel#CreateLabSubTitle {
    color: rgba(71,85,105,0.95);
    font-size: 12px;
}

QDialog#CreateLabDialog QFrame#CreateLabDivider {
    background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                                stop:0 rgba(59,130,246,0.05),
                                stop:0.5 rgba(59,130,246,0.30),
                                stop:1 rgba(59,130,246,0.05));
    border: none;
    border-radius: 1px;
}

QDialog#CreateLabDialog QLabel#CreateLabChip {
    background-color: rgba(15,23,42,0.04);
    border: 1px solid rgba(15,23,42,0.10);
    color: rgba(15,23,42,0.70);
    padding: 6px 10px;
    border-radius: 10px;
    font-size: 12px;
    font-weight: 700;
}

QDialog#CreateLabDialog QLabel#CreateLabLabel {
    color: rgba(15,23,42,0.70);
    font-weight: 700;
    font-size: 12px;
}

QDialog#CreateLabDialog QLineEdit#CreateLabInput {
    background-color: #ffffff;
    border: 1px solid rgba(15,23,42,0.14);
    border-radius: 10px;
    padding: 10px 12px;
    color: #0f172a;
    font-size: 13px;
}

QDialog#CreateLabDialog QLineEdit#CreateLabInput:focus {
    border: 1px solid rgba(59,130,246,0.70);
}

QDialog#CreateLabDialog QSpinBox#CreateLabSpin {
    background-color: #ffffff;
    border: 1px solid rgba(15,23,42,0.14);
    border-radius: 10px;
    padding: 6px 10px;
    color: #0f172a;
    font-size: 13px;
    min-height: 34px;
}

QDialog#CreateLabDialog QSpinBox#CreateLabSpin:focus {
    border: 1px solid rgba(59,130,246,0.70);
}

QDialog#CreateLabDialog QSpinBox::up-button,
QDialog#CreateLabDialog QSpinBox::down-button {
    width: 18px;
    border: none;
}

/* Hint box */
QDialog#CreateLabDialog QLabel#CreateLabHint {
    background-color: rgba(59, 130, 246, 0.08);
    border: 1px solid rgba(59, 130, 246, 0.18);
    color: rgba(15,23,42,0.85);
    border-radius: 12px;
    padding: 10px 12px;
    font-size: 12px;
}

QDialog#CreateLabDialog QPushButton#CreateCancelBtn {
    border: 1px solid rgba(15,23,42,0.20);
    color: rgba(15,23,42,0.80);
    border-radius: 12px;
    padding: 10px 16px;
    font-weight: 700;
}

QDialog#CreateLabDialog QPushButton#CreateCancelBtn:hover {
    background-color: rgba(15,23,42,0.04);
    border: 1px solid rgba(15,23,42,0.28);
}

QDialog#CreateLabDialog QPushButton#CreateConfirmBtn {
    background-color: rgba(59,130,246,0.95);
    border: 1px solid rgba(59,130,246,0.95);
    color: #ffffff;
    border-radius: 12px;
    padding: 10px 18px;
    font-weight: 800;
}

QDialog#CreateLabDialog QPushButton#CreateConfirmBtn:hover {
    background-color: rgba(37,99,235,1.0);
    border: 1px solid rgba(37,99,235,1.0);
}

QDialog#CreateLabDialog QPushButton#CreateConfirmBtn:pressed {
    background-color: rgba(30,64,175,1.0);
    border: 1px solid rgba(30,64,175,1.0);
}


QDialog#CreateLabDialog QLabel#CreateLabRowLabel,
QDialog#CreateLabDialog QLabel#CreateLabChipLabel,
QDialog#CreateLabDialog QLabel#CreateLabDash,
QDialog#CreateLabDialog QLabel#CreateLabTitle,
QDialog#CreateLabDialog QLabel#CreateLabSubtitle,
QDialog#CreateLabDialog QLabel#CreateLabWarningText {
    border: none;
    padding: 0px;
}

QFrame#CreateLabCard {
    background-color: rgba(255, 255, 255, 245);
    border: 1px solid rgba(15, 23, 42, 30);
    border-radius: 16px;
}

QFrame#CreateLabIconContainer {
    background: transparent;
}

QLabel#CreateLabTitle {
    font-size: 16px;
    font-weight: 900;
    color: #0f172a;
}

QLabel#CreateLabSubtitle {
    color: rgba(15, 23, 42, 170);
    font-size: 13px;
}

QFrame#CreateLabDivider {
    background: rgba(15, 23, 42, 20);
    border-radius: 1px;
}

QLabel#CreateLabRowLabel {
    color: rgba(15, 23, 42, 170);
    font-size: 12px;
    font-weight: 800;
}

QLineEdit#CreateLabInput {
    background: #ffffff;
    border: 1px solid rgba(15, 23, 42, 20);
    border-radius: 12px;
    padding: 10px 12px;
    color: rgba(15, 23, 42, 235);
    font-size: 13px;
}

QLineEdit#CreateLabInput:focus {
    border: 1px solid rgba(37, 99, 235, 140);
    background: rgba(15, 23, 42, 2);
}

QLabel#CreateLabDash {
    color: rgba(15, 23, 42, 120);
    font-weight: 900;
}

QFrame#CreateLabChip {
    background: rgba(15, 23, 42, 4);
    border: 1px solid rgba(15, 23, 42, 10);
    border-radius: 14px;
}

QLabel#CreateLabChipLabel {
    color: rgba(15, 23, 42, 180);
    font-weight: 800;
    font-size: 12px;
}

QSpinBox#CreateLabSpin {
    background: #ffffff;
    border: 1px solid rgba(15, 23, 42, 18);
    border-radius: 10px;
    padding: 6px 10px;
    color: rgba(15, 23, 42, 235);
    font-weight: 900;
    min-height: 30px;
}

QSpinBox#CreateLabSpin:focus {
    border: 1px solid rgba(37, 99, 235, 140);
}

/* warning pill */
QFrame#CreateLabWarning {
    background: rgba(15, 23, 42, 4);
    border: 1px solid rgba(15, 23, 42, 10);
    border-radius: 12px;
}

QLabel#CreateLabWarningText {
    color: rgba(15, 23, 42, 200);
    font-size: 12px;
    font-weight: 700;
}

QPushButton#CreateLabCancelBtn {
    background: #ffffff;
    border: 1px solid rgba(15, 23, 42, 40);
    color: rgba(15, 23, 42, 230);
    border-radius: 10px;
    padding: 6px 14px;
    font-weight: 800;
}
QPushButton#CreateLabCancelBtn:hover {
    background: #f1f5f9;
    border: 1px solid rgba(37, 99, 235, 110);
}

QPushButton#CreateLabCreateBtn {
    background: rgba(59, 130, 246, 1.0);
    border: 1px solid rgba(59, 130, 246, 1.0);
    color: #ffffff;
    border-radius: 10px;
    padding: 6px 14px;
    font-weight: 900;
}
QPushButton#CreateLabCreateBtn:hover {
    background: rgba(37, 99, 235, 1.0);
    border: 1px solid rgba(37, 99, 235, 1.0);
}
QPushButton#CreateLabCreateBtn:pressed {
    background: rgba(30, 64, 175, 1.0);
    border: 1px solid rgba(30, 64, 175, 1.0);
}
QPushButton#CreateLabCreateBtn:disabled {
    background: rgba(15, 23, 42, 6);
    border: 1px solid rgba(15, 23, 42, 12);
    color: rgba(15, 23, 42, 120);
}

/* =========================
   Trash (Delete) Button – Light
   ========================= */
#TrashButton {
    background: transparent;
    border: none;
}

#TrashButton:hover {
    background: rgba(0, 0, 0, 20);   /* light grey hover */
    border-radius: 6px;
}

#TrashButton:pressed {
    background: rgba(0, 0, 0, 35);
}

/* =============================== */
/* ===== EDIT IP DIALOG (LIGHT) === */
/* =============================== */
QDialog#EditPcIpDialog,


QFrame#EditPcIpCard,
QFrame#BulkIpCard {
    background-color: rgba(255, 255, 255, 248);
    border: 1px solid rgba(15, 23, 42, 22);
    border-radius: 18px;
}

QLabel#EditPcIpTitle,
QLabel#BulkIpTitle {
    color: #0f172a;
    font-size: 16px;
    font-weight: 900;
}

QLabel#EditPcIpLabel,
QLabel#BulkIpLabel {
    color: rgba(15, 23, 42, 140);
    font-size: 11px;
    font-weight: 800;
    letter-spacing: 0.6px;
}

QLabel#EditPcIpPcName {
    background: rgba(15, 23, 42, 4);
    border: 1px solid rgba(15, 23, 42, 10);
    border-radius: 12px;
    padding: 10px 12px;
    color: rgba(15, 23, 42, 235);
    font-weight: 800;
}

QLabel#EditPcIpCurrentLabel {
    color: rgba(15, 23, 42, 150);
    font-weight: 700;
}

QLabel#EditPcIpCurrentValue {
    background: rgba(15, 23, 42, 4);
    border: 1px solid rgba(15, 23, 42, 10);
    border-radius: 10px;
    padding: 6px 12px;
    color: rgba(15, 23, 42, 235);
    font-weight: 900;
    font-family: Consolas, monospace;
    min-width: 140px;
}

QFrame#EditPcIpDivider {
    background: rgba(15, 23, 42, 16);
    border-radius: 1px;
}

QLineEdit#EditPcIpInput,
QLineEdit#BulkIpInput {
    background: rgba(15, 23, 42, 4);
    border: 1px solid rgba(15, 23, 42, 12);
    border-radius: 14px;
    padding: 10px 12px;
    color: rgba(15, 23, 42, 240);
    font-size: 14px;
    font-weight: 900;
    font-family: Consolas, monospace;
}

QLineEdit#EditPcIpInput:focus,
QLineEdit#BulkIpInput:focus {
    border: 1px solid rgba(37, 99, 235, 160);
    background: rgba(15, 23, 42, 5);
}

QLabel#BulkIpHint {
    color: rgba(15, 23, 42, 170);
    background: rgba(59, 130, 246, 0.08);
    border: 1px solid rgba(59, 130, 246, 0.18);
    border-radius: 12px;
    padding: 10px 12px;
    font-size: 12px;
    font-weight: 700;
}

/* Buttons */
QPushButton#EditPcIpCancelBtn,
QPushButton#BulkIpCancelBtn {
    background: #ffffff;
    border: 1px solid rgba(15, 23, 42, 20);
    color: rgba(15, 23, 42, 220);
    border-radius: 12px;
    font-weight: 900;
}
QPushButton#EditPcIpCancelBtn:hover,
QPushButton#BulkIpCancelBtn:hover {
    background: #f1f5f9;
    border: 1px solid rgba(37, 99, 235, 110);
}

QPushButton#EditPcIpSaveBtn,
QPushButton#BulkIpApplyBtn {
    background: rgba(59, 130, 246, 0.95);
    border: 1px solid rgba(59, 130, 246, 0.95);
    color: #ffffff;
    border-radius: 12px;
    font-weight: 900;
}
QPushButton#EditPcIpSaveBtn:hover,
QPushButton#BulkIpApplyBtn:hover {
    background: rgba(37, 99, 235, 1.0);
    border: 1px solid rgba(37, 99, 235, 1.0);
}
QPushButton#EditPcIpSaveBtn:pressed,
QPushButton#BulkIpApplyBtn:pressed {
    background: rgba(30, 64, 175, 1.0);
    border: 1px solid rgba(30, 64, 175, 1.0);
}


/* Page background */
QWidget#DashboardPage {
    background: #f4f6f9;
}

/* ── Header bar ──────────────────────────────── */
QFrame#HeaderBar {
    background: #ffffff;
    border: none;
}

QFrame#HeaderDivider {
    background: #e5e8ed;
    border: none;
    min-height: 1px;
    max-height: 1px;
}

QLabel#Brand {
    font-size: 17px;
    font-weight: 700;
    color: #0f1117;
}

/* ── Scroll area ─────────────────────────────── */
QScrollArea#DashboardScroll {
    border: none;
    background: #f4f6f9;
}

QWidget#DashboardScrollWidget,
QWidget#GridContainer {
    background: #f4f6f9;
}

/* ── Section label ───────────────────────────── */
QLabel#SectionLabel {
    font-size: 11px;
    font-weight: 600;
    color: #9ba4b5;
    letter-spacing: 1px;
}

/* ── Lab card ────────────────────────────────── */
QFrame#LabCard {
    background: #ffffff;
    border: 1px solid #e8eaef;
    border-radius: 12px;
}

QLabel#CardDot {
    color: #3584e4;
    font-size: 9px;
}

QLabel#LabName {
    font-size: 15px;
    font-weight: 700;
    color: #0f1117;
}

QFrame#CardSep {
    background: #f0f2f5;
    border: none;
    min-height: 1px;
    max-height: 1px;
}

/* ── Info rows ───────────────────────────────── */
QWidget#LabInfoRow {
    background: transparent;
}

QLabel#LabInfoLabel {
    font-size: 12px;
    color: #9ba4b5;
    font-weight: 500;
}

QLabel#LabInfoValue {
    font-size: 12px;
    color: #2d3340;
    font-weight: 600;
}

/* ── Buttons ─────────────────────────────────── */
QPushButton#CreateButton {
    background: #3584e4;
    color: #ffffff;
    border: none;
    border-radius: 8px;
    padding: 0px 18px;
    font-size: 13px;
    font-weight: 600;
    min-height: 34px;
}
QPushButton#CreateButton:hover {
    background: #2870c8;
}
QPushButton#CreateButton:pressed {
    background: #2060b0;
}

QPushButton#EditButton {
    background: #f0f2f5;
    color: #2d3340;
    border: 1px solid #dde0e7;
    border-radius: 7px;
    font-size: 12px;
    font-weight: 500;
}
QPushButton#EditButton:hover {
    background: #e4e8ef;
    border-color: #c8ccd6;
}
QPushButton#EditButton:pressed {
    background: #d8dce6;
}

QPushButton#OpenButton {
    background: #3584e4;
    color: #ffffff;
    border: none;
    border-radius: 7px;
    font-size: 12px;
    font-weight: 600;
}
QPushButton#OpenButton:hover {
    background: #2870c8;
}
QPushButton#OpenButton:pressed {
    background: #2060b0;
}

QPushButton#TrashButton {
    background: transparent;
    border: none;
    border-radius: 6px;
}
QPushButton#TrashButton:hover {
    background: #fdecea;
}

/* ── Stats panel ─────────────────────────────── */
QFrame#StatsPanel {
    background: #ffffff;
    border: 1px solid #e8eaef;
    border-radius: 12px;
}

QLabel#StatsTitle {
    font-size: 13px;
    font-weight: 700;
    color: #0f1117;
}

QLabel#StatsSubTitle {
    font-size: 11px;
    color: #9ba4b5;
}

QFrame#StatChip {
    background: #f7f9fc;
    border: 1px solid #ebeef3;
    border-radius: 10px;
}

QLabel#ChipEmoji {
    font-size: 18px;
}

QLabel#StatValue {
    font-size: 22px;
    font-weight: 700;
    color: #0f1117;
}

QLabel#StatLabel {
    font-size: 11px;
    color: #9ba4b5;
    font-weight: 500;
}

/* ── Empty state ─────────────────────────────── */
QFrame#EmptyState {
    background: #ffffff;
    border: 1px dashed #d4d8e2;
    border-radius: 14px;
}

QLabel#EmptyIcon {
    font-size: 40px;
}

QLabel#EmptyTitle {
    font-size: 16px;
    font-weight: 700;
    color: #2d3340;
}

QLabel#EmptyDesc {
    font-size: 12px;
    color: #9ba4b5;
}

/* ── Scrollbar ───────────────────────────────── */
QScrollArea#DashboardScroll QScrollBar:vertical {
    background: transparent;
    width: 6px;
    margin: 0;
}
QScrollArea#DashboardScroll QScrollBar::handle:vertical {
    background: #c8cdd8;
    border-radius: 3px;
    min-height: 30px;
}
QScrollArea#DashboardScroll QScrollBar::handle:vertical:hover {
    background: #a8b0c0;
}
QScrollArea#DashboardScroll QScrollBar::add-line:vertical,
QScrollArea#DashboardScroll QScrollBar::sub-line:vertical {
    height: 0px;
}
QScrollArea#DashboardScroll QScrollBar::add-page:vertical,
QScrollArea#DashboardScroll QScrollBar::sub-page:vertical {
    background: transparent;
}


"""


def get_qss(theme_name: str) -> str:
    return LIGHT_QSS 
