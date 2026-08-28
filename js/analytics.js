/*
 * analytics.js — lightweight first-party visitor tracker for jyogi.in.
 *
 * No cookies, no third party, no raw IP ever leaves the visitor's browser
 * (the backend hashes IP+UA server-side and discards the IP immediately).
 * Fires a page_view beacon on load and exposes window.jyogiTrack(event) for
 * click-level events (WhatsApp, Apply, Book Now, etc).
 */
(function () {
  var API_BASE = (window.SITE_CONFIG && window.SITE_CONFIG.apiBase) || 'https://jyogi-api.onrender.com';
  var ENDPOINT = API_BASE + '/api/analytics/event';

  // ── Session id: one per browser tab session, not a persistent identifier ──
  function getSessionId() {
    try {
      var sid = sessionStorage.getItem('jyogi_sid');
      if (!sid) {
        sid = 'sid_' + Date.now().toString(36) + '_' + Math.random().toString(36).slice(2, 10);
        sessionStorage.setItem('jyogi_sid', sid);
      }
      return sid;
    } catch (e) { return ''; }
  }

  // ── Cheap UA sniff — good enough for device/browser/OS buckets ──
  function parseUA() {
    var ua = navigator.userAgent || '';
    var device = 'desktop';
    if (/Tablet|iPad/.test(ua)) device = 'tablet';
    else if (/Mobi|Android/.test(ua)) device = 'mobile';

    var browser = 'Other';
    if (/Edg\//.test(ua)) browser = 'Edge';
    else if (/OPR\//.test(ua)) browser = 'Opera';
    else if (/Chrome\//.test(ua) && !/Chromium/.test(ua)) browser = 'Chrome';
    else if (/Firefox\//.test(ua)) browser = 'Firefox';
    else if (/Safari\//.test(ua) && !/Chrome/.test(ua)) browser = 'Safari';

    var os = 'Other';
    if (/Windows/.test(ua)) os = 'Windows';
    else if (/Mac OS X/.test(ua) && !/Mobi/.test(ua)) os = 'macOS';
    else if (/Android/.test(ua)) os = 'Android';
    else if (/iPhone|iPad|iPod/.test(ua)) os = 'iOS';
    else if (/Linux/.test(ua)) os = 'Linux';

    return { device: device, browser: browser, os: os };
  }

  function utmParam(name) {
    try {
      return new URLSearchParams(location.search).get(name) || '';
    } catch (e) { return ''; }
  }

  function send(payload) {
    var body = JSON.stringify(payload);
    try {
      if (navigator.sendBeacon) {
        var blob = new Blob([body], { type: 'application/json' });
        navigator.sendBeacon(ENDPOINT, blob);
        return;
      }
    } catch (e) { /* fall through to fetch */ }
    try {
      fetch(ENDPOINT, { method: 'POST', body: body, headers: { 'Content-Type': 'application/json' }, keepalive: true });
    } catch (e) { /* tracking must never break the page */ }
  }

  function basePayload(eventName) {
    var ua = parseUA();
    return {
      event: eventName,
      path: location.pathname,
      title: document.title || '',
      referrer: document.referrer || '',
      utm_source: utmParam('utm_source'),
      utm_medium: utmParam('utm_medium'),
      utm_campaign: utmParam('utm_campaign'),
      session_id: getSessionId(),
      device_type: ua.device,
      browser: ua.browser,
      os: ua.os,
      screen_w: window.screen ? window.screen.width : 0,
      lang: (navigator.language || '').slice(0, 10)
    };
  }

  // Public API for click-level events, e.g.:
  //   <button onclick="jyogiTrack('whatsapp_click')">
  window.jyogiTrack = function (eventName) {
    if (!eventName) return;
    send(basePayload(eventName));
  };

  // Fire the page_view beacon once the page has something to report.
  if (document.readyState === 'complete') {
    send(basePayload('page_view'));
  } else {
    window.addEventListener('load', function () { send(basePayload('page_view')); });
  }
})();
