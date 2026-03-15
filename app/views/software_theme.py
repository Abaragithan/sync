# views/software_theme.py

_STEPS = [
    ("select_pcs", "Select PCs"),
    ("configure",  "Configure"),
    ("executing",  "Executing"),
    ("done",       "Done"),
]
_STEP_INDEX = {key: i for i, (key, _) in enumerate(_STEPS)}
_ACTIONS = [("install", "Install"), ("remove", "Remove"), ("update", "Update")]

LIGHT = {
    "chrome_bg": "#ffffff", "chrome_bdr": "#e2e8f0",
    "pill_done": "#1d4ed8", "pill_active": "#2563eb",
    "pill_fail": "#dc2626", "pill_idle": "#cbd5e1",
    "pill_text": "#ffffff", "pill_muted": "#94a3b8",
    "line_done": "#2563eb", "line_idle": "#e2e8f0",
    "log_bg": "#f8fafc", "log_header": "#f1f5f9", "log_border": "#e2e8f0",
    "log_text": "#1e293b", "log_error": "#b91c1c", "log_dim": "#94a3b8",
    "scrollbar": "#e2e8f0", "scroll_hdl": "#94a3b8",
    "btn_idle_bg": "#ffffff", "btn_idle_bdr": "#e2e8f0", "btn_idle_fg": "#64748b",
    "radio_bg": "#ffffff", "radio_bdr": "#cbd5e1", "radio_fg": "#64748b",
    "radio_chk_bg": "#2563eb", "radio_chk_fg": "#ffffff",
    "radio_hov_bdr": "#2563eb", "radio_hov_fg": "#0f172a",
    "act_idle_bg": "#ffffff", "act_idle_bdr": "#cbd5e1", "act_idle_fg": "#64748b",
    "act_active_bg": "#2563eb", "act_active_bdr": "#1d4ed8", "act_active_fg": "#ffffff",
    "div_color": "#e2e8f0",
    "badge_ok_fg": "#14532d", "badge_ok_bg": "#dcfce7", "badge_ok_bdr": "#15803d",
    "badge_fail_fg": "#991b1b", "badge_fail_bg": "#fee2e2", "badge_fail_bdr": "#dc2626",
    "abar_bg": "#f1f5f9", "abar_bdr": "#e2e8f0",
    "abar_btn_bg": "#ffffff", "abar_btn_bdr": "#e2e8f0", "abar_btn_fg": "#334155",
    "back_bg": "#ffffff", "back_bdr": "#e2e8f0", "back_fg": "#64748b",
    "lbl_muted": "#64748b", "lbl_title": "#0f172a", "lbl_sub": "#64748b",
    "vline": "#e2e8f0",
}

def _t() -> dict:
    return LIGHT