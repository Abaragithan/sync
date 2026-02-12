# app/ui/theme.py

DARK_QSS = """
/* --- GLOBAL & BASE --- */
QWidget {
    background-color: #121212;
    color: #e2e8f0;
    font-family: 'Segoe UI', sans-serif;
    font-size: 14px;
    border: none;
}

/* =============================== */
/* ===== THEME SWITCH (DARK) ===== */
/* =============================== */
QCheckBox#ThemeSwitch {
    spacing: 10px;
    font-weight: 700;
    color: #e2e8f0;
}

QCheckBox#ThemeSwitch::indicator {
    width: 46px;
    height: 24px;
    border-radius: 12px;
    background: #334155;
    border: 1px solid #475569;
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
    color: #ffffff;
}

QLabel#SubText {
    color: #94a3b8;
    font-size: 13px;
}

QLabel#MutedText {
    color: #9aa4b2;
}

/* --- DASHBOARD CARD SPECIFIC (OLD/OTHER PAGES) --- */
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

/* ------------------------------------------------------------------ */
/* ✅ YOUR DASHBOARD LAB CARDS (LabCard)                                */
/* Realistic hover look (border glow + soft surface change)             */
/* Actual smooth animation handled in code via QGraphicsDropShadowEffect */
/* ------------------------------------------------------------------ */
QFrame#LabCard {
    background-color: rgba(255, 255, 255, 10);
    border: 1.6px solid rgba(255, 255, 255, 40);
    border-radius: 16px;
}
QFrame#LabCard:hover {
    background-color: rgba(255, 255, 255, 14);
    border: 2px solid rgba(120, 180, 255, 120);
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

/* Slight tone difference between label and value */
QLabel#LabInfoLabel { color: rgba(226, 232, 240, 170); }
QLabel#LabInfoValue { color: rgba(226, 232, 240, 235); }

/* Lab name title on card (no highlight box) */
QLabel#LabName {
    background: transparent;
    border: none;
    padding: 0px;
    margin: 0px;
    text-decoration: none;

    font-size: 16px;
    font-weight: 900;
    color: #ffffff;
}
QLabel#LabName::selected { background: transparent; color: inherit; }

/* Card buttons: compact + clean + fits card */
QFrame#LabCard QPushButton#EditButton,
QFrame#LabCard QPushButton#OpenButton,
QFrame#LabCard QPushButton#DeleteButton {
    padding: 6px 10px;
    min-height: 28px;
    max-height: 28px;
    font-size: 12px;
    font-weight: 800;
    border-radius: 10px;

    /* Important: prevent global big padding effect */
    margin: 0px;
}

/* Edit = subtle */
QFrame#LabCard QPushButton#EditButton {
    background-color: rgba(255, 255, 255, 10);
    border: 1px solid rgba(255, 255, 255, 50);
    color: rgba(226, 232, 240, 230);
}
QFrame#LabCard QPushButton#EditButton:hover {
    background-color: rgba(255, 255, 255, 16);
    border: 1px solid rgba(120, 180, 255, 130);
}

/* Open = primary */
QFrame#LabCard QPushButton#OpenButton {
    background-color: #2563eb;
    border: 1px solid rgba(37, 99, 235, 180);
    color: white;
}
QFrame#LabCard QPushButton#OpenButton:hover { background-color: #1d4ed8; }
QFrame#LabCard QPushButton#OpenButton:pressed { background-color: #1e40af; }

/* Delete = danger (but compact) */
QFrame#LabCard QPushButton#DeleteButton {
    background-color: rgba(239, 68, 68, 120);
    border: 1px solid rgba(239, 68, 68, 170);
    color: #fff;
}
QFrame#LabCard QPushButton#DeleteButton:hover {
    background-color: rgba(239, 68, 68, 160);
}
QFrame#LabCard QPushButton#DeleteButton:pressed {
    background-color: rgba(220, 38, 38, 190);
}


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
QLineEdit:focus, QComboBox:focus, QSpinBox:focus, QTextEdit:focus {
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

/* --- LIST WIDGET --- */
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

/* --- LAB PAGE --- */
QFrame#SectionCard {
    background-color: #1b1b1b;
    border: 1px solid #334155;
    border-radius: 12px;
}

QLabel#SectionTitle {
    font-weight: 700;
    color: #e2e8f0;
}

QFrame#FooterBar {
    background-color: #1b1b1b;
    border-radius: 10px;
    border: 1px solid #334155;
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
    color: #ffffff;
}

QLabel#WelcomeSub {
    color: #9aa4b2;
    font-size: 14px;
}

QLabel#WelcomeLogoFallback {
    font-size: 24px;
    font-weight: 800;
    color: #94a3b8;
}

/* --- SOFTWARE PAGE (SCOPED) --- */
QWidget#SoftwarePage QFrame#Card {
    background-color: #111827;
    border: 1px solid #334155;
    border-radius: 12px;
    padding: 10px;
}

QWidget#SoftwarePage QLabel#CardHeader {
    font-weight: 800;
    font-size: 15px;
    color: #e5e7eb;
    padding: 6px 2px;
}

QWidget#SoftwarePage QLabel#SummaryText {
    color: #e5e7eb;
}

QWidget#SoftwarePage QLabel#StatusError { color: #ff6b6b; }
QWidget#SoftwarePage QLabel#StatusSuccess { color: #4ecdc4; }

QWidget#SoftwarePage QTextEdit#Console {
    background-color: #0b1220;
    border: 1px solid #334155;
    border-radius: 10px;
    padding: 8px;
    color: #e5e7eb;
}

/* --- CREATE LAB DIALOG --- */
QDialog#CreateLabDialog QLabel#DialogTitle {
    font-size: 18px;
    font-weight: 800;
    color: #ffffff;
}
QDialog#CreateLabDialog QLabel#DialogSubText {
    color: #94a3b8;
    font-size: 12px;
}
QDialog#CreateLabDialog QFrame#DialogCard {
    background-color: #111827;
    border: 1px solid #334155;
    border-radius: 14px;
}
QDialog#CreateLabDialog QLabel#DialogSectionHeader {
    font-weight: 800;
    font-size: 13px;
    color: #e5e7eb;
    padding-top: 4px;
}
QDialog#CreateLabDialog QLabel#DialogHintText {
    color: #9aa4b2;
    font-size: 12px;
}

/* Card buttons: compact + clean + fits card */
QFrame#LabCard QPushButton#EditButton,
QFrame#LabCard QPushButton#OpenButton,
QFrame#LabCard QPushButton#DeleteButton {
    padding: 6px 10px;
    min-height: 28px;
    max-height: 28px;
    font-size: 12px;
    font-weight: 800;
    border-radius: 10px;

    /* Important: prevent global big padding effect */
    margin: 0px;
}

/* Edit = subtle */
QFrame#LabCard QPushButton#EditButton {
    background-color: rgba(255, 255, 255, 10);
    border: 1px solid rgba(255, 255, 255, 50);
    color: rgba(226, 232, 240, 230);
}
QFrame#LabCard QPushButton#EditButton:hover {
    background-color: rgba(255, 255, 255, 16);
    border: 1px solid rgba(120, 180, 255, 130);
}

/* Open = primary */
QFrame#LabCard QPushButton#OpenButton {
    background-color: #2563eb;
    border: 1px solid rgba(37, 99, 235, 180);
    color: white;
}
QFrame#LabCard QPushButton#OpenButton:hover { background-color: #1d4ed8; }
QFrame#LabCard QPushButton#OpenButton:pressed { background-color: #1e40af; }

/* Delete = danger (but compact) */
QFrame#LabCard QPushButton#DeleteButton {
    background-color: rgba(239, 68, 68, 120);
    border: 1px solid rgba(239, 68, 68, 170);
    color: #fff;
}
QFrame#LabCard QPushButton#DeleteButton:hover {
    background-color: rgba(239, 68, 68, 160);
}
QFrame#LabCard QPushButton#DeleteButton:pressed {
    background-color: rgba(220, 38, 38, 190);
}

/* ================================ */
/* ===== CONFIRM DELETE DIALOG ==== */
/* ================================ */
QDialog#ConfirmDeleteDialog { background: transparent; }

QFrame#ConfirmDeleteCard {
    background-color: rgba(20, 20, 20, 240);
    border: 1px solid rgba(255, 255, 255, 40);
    border-radius: 14px;
}

QLabel#ConfirmDeleteTitle {
    font-size: 16px;
    font-weight: 900;
    color: white;
}

QLabel#ConfirmDeleteSubtitle {
    color: rgba(226, 232, 240, 190);
    font-size: 13px;
}

QFrame#ConfirmDeleteDivider {
    background: rgba(255, 255, 255, 30);
}

QPushButton#ConfirmCancelBtn {
    background: rgba(255, 255, 255, 10);
    border: 1px solid rgba(255, 255, 255, 35);
    color: rgba(226, 232, 240, 230);
    border-radius: 10px;
    padding: 6px 14px;
    font-weight: 800;
}
QPushButton#ConfirmCancelBtn:hover {
    background: rgba(255, 255, 255, 16);
    border: 1px solid rgba(120, 180, 255, 120);
}

QPushButton#ConfirmDeleteBtn {
    background: rgba(239, 68, 68, 150);
    border: 1px solid rgba(239, 68, 68, 200);
    color: white;
    border-radius: 10px;
    padding: 6px 14px;
    font-weight: 900;
}
QPushButton#ConfirmDeleteBtn:hover { background: rgba(239, 68, 68, 190); }
QPushButton#ConfirmDeleteBtn:pressed { background: rgba(220, 38, 38, 220); }

/* =============================== */
/* ===== DASHBOARD (EXTRAS)  ===== */
/* =============================== */

QLabel#Brand {
    font-size: 20px;
    font-weight: 700;
    color: #e5e7eb;
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
    background-color: rgba(255, 255, 255, 8);
    border: 1px solid rgba(255, 255, 255, 28);
    border-radius: 18px;
}

QLabel#StatsTitle {
    font-size: 15px;
    font-weight: 800;
    color: rgba(226, 232, 240, 240);
}

QLabel#StatsSubTitle {
    font-size: 12px;
    color: rgba(226, 232, 240, 140);
}

QFrame#StatChip {
    background-color: rgba(15, 23, 42, 120);
    border: 1px solid rgba(255, 255, 255, 18);
    border-radius: 14px;
}

QLabel#StatValue {
    font-size: 16px;
    font-weight: 900;
    color: rgba(226, 232, 240, 240);
}

QLabel#StatLabel {
    font-size: 12px;
    color: rgba(226, 232, 240, 150);
}


"""


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
    border-radius: 12px;
    padding: 10px;
}

QWidget#SoftwarePage QLabel#CardHeader {
    font-weight: 800;
    font-size: 15px;
    color: #0f172a;
    padding: 6px 2px;
}

QWidget#SoftwarePage QLabel#SummaryText {
    color: #0f172a;
}

QWidget#SoftwarePage QLabel#StatusError { color: #dc2626; }
QWidget#SoftwarePage QLabel#StatusSuccess { color: #0f766e; }

QWidget#SoftwarePage QTextEdit#Console {
    background-color: #ffffff;
    border: 1px solid #cbd5e1;
    border-radius: 10px;
    padding: 8px;
    color: #0f172a;
}

/* --- CREATE LAB DIALOG --- */
QDialog#CreateLabDialog QLabel#DialogTitle {
    font-size: 18px;
    font-weight: 800;
    color: #0f172a;
}
QDialog#CreateLabDialog QLabel#DialogSubText {
    color: #475569;
    font-size: 12px;
}
QDialog#CreateLabDialog QFrame#DialogCard {
    background-color: #ffffff;
    border: 1px solid #cbd5e1;
    border-radius: 14px;
}
QDialog#CreateLabDialog QLabel#DialogSectionHeader {
    font-weight: 800;
    font-size: 13px;
    color: #0f172a;
    padding-top: 4px;
}
QDialog#CreateLabDialog QLabel#DialogHintText {
    color: #475569;
    font-size: 12px;
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
QDialog#ConfirmDeleteDialog { background: transparent; }

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
    background: transparent;
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
    background-color: transparent;
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

"""


def get_qss(theme_name: str) -> str:
    return LIGHT_QSS if (theme_name or "").lower() == "light" else DARK_QSS
