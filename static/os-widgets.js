/* NothingOS shell widgets — ambient status and route-shell compatibility.
 *
 * V2 keeps this file FEED-ONLY: it reads state that the existing app already
 * computes/renders (S.busy, approval card, composer chip labels, gitBadge) and
 * mirrors it into ambient/glance surfaces. It creates NO new API calls and
 * changes NO stream logic — it wraps a few global functions to observe state
 * transitions, then delegates to them.
 *
 * Surfaces it owns:
 *   #osAmbient  — AmbientStatusStrip (idle/thinking/tool_running/waiting_approval/error/complete)
 *   #osQuick    — inert compatibility mount; V2 route controls live inside route surfaces
 *   .os-glance  — GlanceWidgets, injected into the workspace rightpanel
 */
(function () {
  'use strict';

  var $ = function (id) { return document.getElementById(id); };

  // ── AmbientStatusStrip ────────────────────────────────────────────────────
  var AMBIENT_LABELS = {
    idle: 'IDLE',
    thinking: 'THINKING',
    tool_running: 'TOOL RUNNING',
    waiting_approval: 'WAITING / APPROVAL',
    error: 'ERROR',
    complete: 'COMPLETE',
  };
  var _completeTimer = null;

  function setAmbient(state) {
    var el = $('osAmbient');
    if (!el) return;
    if (!AMBIENT_LABELS[state]) state = 'idle';
    el.dataset.state = state;
    var label = $('osAmbientState');
    if (label) label.textContent = AMBIENT_LABELS[state];
    // "complete" is a one-shot sweep that settles back to idle.
    if (_completeTimer) { clearTimeout(_completeTimer); _completeTimer = null; }
    if (state === 'complete') {
      _completeTimer = setTimeout(function () { setAmbient('idle'); }, 900);
    }
  }
  window.osAmbientState = setAmbient;

  // ── GlanceWidgets ─────────────────────────────────────────────────────────
  // Rendered into the workspace rightpanel header so the file browser stays.
  function ensureGlance() {
    var host = document.querySelector('.rightpanel');
    if (!host || $('osGlance')) return $('osGlance');
    var g = document.createElement('div');
    g.className = 'os-glance';
    g.id = 'osGlance';
    g.innerHTML =
      '<div class="os-glance-widget"><h4>Current run</h4>' +
        '<div class="os-glance-metric" id="osGlanceTurns">00</div>' +
        '<div class="os-glance-sub" id="osGlanceRunSub">idle</div></div>' +
      '<div class="os-glance-widget"><h4>Memory mode</h4>' +
        '<div class="os-glance-metric" id="osGlanceModel" style="font-size:18px">—</div>' +
        '<div class="os-glance-sub" id="osGlanceBranch">no branch</div></div>';
    // Insert after the panel header so resize handle + actions keep working.
    var header = host.querySelector('.panel-header');
    if (header && header.nextSibling) host.insertBefore(g, header.nextSibling);
    else host.appendChild(g);
    return g;
  }

  function _chipText(id, fallback) {
    var el = $(id);
    var v = el && (el.textContent || '').trim();
    return v || fallback;
  }

  function renderGlance() {
    ensureGlance();
    var turnsEl = $('osGlanceTurns');
    if (turnsEl) {
      var count = 0;
      try {
        if (window.S && Array.isArray(S.messages)) count = S.messages.length;
      } catch (e) {}
      turnsEl.textContent = String(count).padStart(2, '0');
    }
    var runSub = $('osGlanceRunSub');
    if (runSub) {
      var busy = false;
      try { busy = !!(window.S && S.busy); } catch (e) {}
      runSub.textContent = busy ? 'streaming' : 'idle';
    }
    var modelEl = $('osGlanceModel');
    if (modelEl) modelEl.textContent = _chipText('composerModelLabel', '—');
    var branchEl = $('osGlanceBranch');
    if (branchEl) {
      var badge = $('gitBadge');
      var txt = badge && badge.style.display !== 'none' ? (badge.textContent || '').trim() : '';
      branchEl.textContent = txt || 'no branch';
    }
  }
  window.osRenderGlance = renderGlance;

  // ── RouteCommandDock compatibility mount ───────────────────────────────────
  // V2 removes the persistent global QuickCommandTray. Keep #osQuick as an inert
  // mount for old tests/extensions, but do not build global MODEL/WORKSPACE tiles.
  function buildTray() {
    var tray = $('osQuick');
    if (!tray) return;
    tray.hidden = true;
    tray.setAttribute('aria-hidden', 'true');
    tray.innerHTML = '';
  }

  function refreshTray() {
    var tray = $('osQuick');
    if (tray) tray.hidden = true;
  }
  window.osRefreshTray = refreshTray;

  // ── Hook existing globals (observe-then-delegate) ─────────────────────────
  function wrap(name, before) {
    var orig = window[name];
    if (typeof orig !== 'function' || orig.__osWrapped) return;
    var wrapped = function () {
      try { before.apply(this, arguments); } catch (e) {}
      return orig.apply(this, arguments);
    };
    wrapped.__osWrapped = true;
    window[name] = wrapped;
  }

  function install() {
    buildTray();
    renderGlance();

    // setBusy(true) → thinking; setBusy(false) → complete then settle to idle.
    wrap('setBusy', function (v) {
      // Don't override an active approval/error wait when going busy.
      var cur = $('osAmbient') && $('osAmbient').dataset.state;
      if (v) { setAmbient('thinking'); }
      else if (cur !== 'waiting_approval' && cur !== 'error') { setAmbient('complete'); }
      renderGlance();
    });

    // Approval card shown/hidden → waiting_approval / back to busy-or-idle.
    wrap('showApprovalCard', function () { setAmbient('waiting_approval'); });
    wrap('hideApprovalCard', function () {
      var busy = false;
      try { busy = !!(window.S && S.busy); } catch (e) {}
      setAmbient(busy ? 'thinking' : 'idle');
    });

    // Keep glance/tray fresh when sessions or chips change. Cheap + idempotent.
    wrap('loadSession', function () { setTimeout(function () { renderGlance(); refreshTray(); }, 50); });
    wrap('renderMessages', function () { renderGlance(); });

    // Lightweight periodic sync for chip-driven tiles (model/tools labels update
    // asynchronously after dropdown picks). 2s cadence, DOM-read only.
    setInterval(function () { refreshTray(); renderGlance(); }, 2000);
  }

  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', install);
  } else {
    install();
  }
})();
