from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
INDEX = (ROOT / "static" / "index.html").read_text(encoding="utf-8")
PANELS = (ROOT / "static" / "panels.js").read_text(encoding="utf-8")
STYLE = (ROOT / "static" / "style.css").read_text(encoding="utf-8")
I18N = (ROOT / "static" / "i18n.js").read_text(encoding="utf-8")
OS_WIDGETS = (ROOT / "static" / "os-widgets.js").read_text(encoding="utf-8")


def test_nothingos_jobs_list_uses_led_status_without_robot_emoji():
    assert "🤖" not in PANELS
    assert "cron-agent-badge" not in PANELS
    assert "cron-job-index" in PANELS
    assert "cron-status os-led" in PANELS
    assert ".cron-status.os-led" in STYLE


def test_nothingos_jobs_cards_show_real_schedule_metadata():
    assert "schedule_display" in PANELS
    assert "next_run_at" in PANELS
    assert "last_run_at" in PANELS
    assert "cron-card-meta" in PANELS
    assert ".cron-card-meta" in STYLE


def test_nothingos_jobs_new_job_is_labeled_primary_action():
    marker = 'cron-new-job-btn'
    marker_pos = INDEX.find(marker)
    assert marker_pos != -1
    button_start = INDEX.rfind("<button", 0, marker_pos)
    button_html = INDEX[button_start: INDEX.find("</button>", marker_pos)]
    assert "New job" in button_html
    assert "panel-head-btn--label" in button_html


def test_nothingos_appearance_copy_does_not_advertise_missing_accent_control():
    assert "Theme, accent colors, and visual style." not in INDEX
    assert "Theme, accent colors, and visual style." not in I18N
    assert "Theme and readable visual scale." in I18N


def test_nothingos_global_quick_tray_is_inert_compat_mount():
    os_quick_pos = INDEX.find('id="osQuick"')
    assert os_quick_pos != -1
    os_quick_tag_start = INDEX.rfind("<section", 0, os_quick_pos)
    os_quick_tag = INDEX[os_quick_tag_start: INDEX.find(">", os_quick_pos)]
    assert "hidden" in os_quick_tag
    assert "tray.hidden = true" in OS_WIDGETS
    assert "tray.setAttribute('aria-hidden', 'true')" in OS_WIDGETS
    assert "tray.innerHTML = ''" in OS_WIDGETS
