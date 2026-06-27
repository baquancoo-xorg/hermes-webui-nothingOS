"""Tests for the batch of fixes from PRs #506-#521 (v0.50.47).

Covers:
  - /root workspace unblocking (#510/#521)
  - Attached-files split guard (#521)
  - custom_providers model visibility (#515/#519)
  - Cron skill cache invalidation (#507/#508)
  - System (auto) theme (#504/#506/#509/#514)
"""

import pathlib
import re

REPO = pathlib.Path(__file__).parent.parent


def read(rel):
    return (REPO / rel).read_text()


# ── Group A: /root workspace ──────────────────────────────────────────────────

class TestRootWorkspaceUnblocked:

    def test_root_not_in_blocked_system_roots(self):
        src = read("api/workspace.py")
        assert "Path('/root')" not in src, (
            "/root must not be in _BLOCKED_SYSTEM_ROOTS — "
            "breaks deployments where Hermes runs as root"
        )

    def test_etc_still_blocked(self):
        """Sanity: other dangerous paths remain blocked.

        After the macOS symlink fix, blocked roots are listed as bare strings
        in a tuple and ``_workspace_blocked_roots()`` materialises both the
        literal and resolved-canonical Path forms.  Assert the source still
        names ``/etc`` and ``/proc`` as blocked roots.
        """
        src = read("api/workspace.py")
        assert "'/etc'" in src or 'Path("/etc")' in src or "Path('/etc')" in src
        assert "'/proc'" in src or 'Path("/proc")' in src or "Path('/proc')" in src

    def test_split_guard_present(self):
        src = read("api/streaming.py")
        assert "'\\n\\n[Attached files:' in msg_text" in src, (
            "base_text split must guard against missing '[Attached files:' "
            "to avoid empty-string on plain messages"
        )


# ── Group B: custom_providers visibility ─────────────────────────────────────

class TestCustomProvidersVisibility:

    def test_has_custom_providers_variable_present(self):
        src = read("api/config.py")
        assert "_has_custom_providers" in src, (
            "_has_custom_providers variable must exist in get_available_models()"
        )

    def test_discard_custom_conditional_on_no_custom_providers(self):
        src = read("api/config.py")
        assert "not _has_custom_providers" in src, (
            "detected_providers.discard('custom') must be gated on "
            "'not _has_custom_providers'"
        )

    def test_custom_providers_isinstance_check(self):
        src = read("api/config.py")
        assert "isinstance(_custom_providers_cfg, list)" in src, (
            "_has_custom_providers must check isinstance(..., list)"
        )


# ── Group C: cron skill cache ─────────────────────────────────────────────────

class TestCronSkillCacheInvalidation:

    def _panels_src(self):
        return read("static/panels.js")

    def test_cache_busted_on_form_open(self):
        src = self._panels_src()
        # toggleCronForm should set cache to null unconditionally
        # openCronCreate() opens the task create form (renamed from toggleCronForm
        # in the main-view refactor). It must null the skills cache before fetching.
        m = re.search(
            r'function openCronCreate\(\)\{.*?_cronSkillsCache\s*=\s*null',
            src, re.DOTALL
        )
        assert m, (
            "openCronCreate must unconditionally null _cronSkillsCache "
            "before fetching skills"
        )

    def test_cache_not_guarded_by_if_on_open(self):
        src = self._panels_src()
        # openCronCreate must not gate the fetch behind an if(!_cronSkillsCache) guard.
        m = re.search(
            r'function openCronCreate\(\)\{.*?\}',
            src, re.DOTALL
        )
        assert m, "openCronCreate definition not found"
        assert "if(!_cronSkillsCache)" not in m.group(0), (
            "openCronCreate should not use 'if(!_cronSkillsCache)' guard — "
            "cache must always be busted on open"
        )

    def test_cache_busted_on_skill_save(self):
        src = self._panels_src()
        # saveSkillForm() is the handler invoked on skill save (renamed from
        # submitSkillSave in the main-view refactor; the old name still aliases it).
        m = re.search(
            r'async function saveSkillForm\(\).*?_skillsData\s*=\s*null.*?_cronSkillsCache\s*=\s*null',
            src, re.DOTALL
        )
        assert m, (
            "_cronSkillsCache must be set to null in saveSkillForm() "
            "right after _skillsData = null"
        )


# ── Group D: NothingOS theme contract (single skin + Light/Dark only) ─────────
# The fork removed the System (auto) theme and the 16-skin system. These tests
# assert the NEW contract: skin is locked to 'nothingos', theme is light|dark.

class TestNothingOSTheme:

    def test_apply_theme_helper_in_boot_js(self):
        src = read("static/boot.js")
        assert "function _applyTheme(" in src, (
            "_applyTheme helper function must be defined in boot.js"
        )

    def test_normalize_locks_skin_to_nothingos(self):
        src = read("static/boot.js")
        assert "skin:'nothingos'" in src, (
            "_normalizeAppearance must lock skin to 'nothingos'"
        )

    def test_theme_picker_has_light_and_dark_only(self):
        html = read("static/index.html")
        assert "_pickTheme('light')" in html, "Theme picker must have a Light button"
        assert "_pickTheme('dark')" in html, "Theme picker must have a Dark button"
        assert "_pickTheme('system')" not in html, (
            "System theme was removed — picker must not offer it"
        )

    def test_skin_picker_removed(self):
        html = read("static/index.html")
        assert "skinPickerGrid" not in html, (
            "Skin picker was removed (single locked skin)"
        )
        assert 'id="settingsSkin" value="nothingos"' in html, (
            "Locked skin hidden input must default to nothingos"
        )

    def test_prepaint_locks_nothingos(self):
        html = read("static/index.html")
        assert "localStorage.setItem('hermes-skin','nothingos')" in html, (
            "Pre-paint script must lock skin to nothingos so stale values can't persist"
        )

    def test_set_resolved_theme_toggles_light_class(self):
        src = read("static/boot.js")
        assert "classList.toggle('light'" in src, (
            "_setResolvedTheme must toggle the .light class for light mode"
        )

    def test_commands_theme_light_dark_only(self):
        src = read("static/commands.js")
        assert "val==='light'||val==='dark'" in src, (
            "/theme command must only accept light|dark"
        )
        assert "_LEGACY_THEME_MAP" not in src, (
            "Legacy theme alias map was removed"
        )

    def test_panels_reverts_via_apply_theme(self):
        src = read("static/panels.js")
        block = re.search(r"function _revertSettingsPreview\(\)\{.*?\n\}", src, re.DOTALL)
        assert block, "_revertSettingsPreview() should be present"
        assert "_applyTheme(" not in block.group(0), (
            "_revertSettingsPreview must not call _applyTheme() since Appearance autosaves"
        )
