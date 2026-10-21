/* ZRN Coffee — аналітика, згода на cookie і джерело замовлення.
   1) Джерело візиту (UTM/реферер) запамʼятовується в браузері і додається до замовлення — без cookie, без сторонніх сервісів.
   2) GA4 працює в Google Consent Mode v2: без згоди — без cookie (анонімні пінги), зі згодою — повна статистика.
   3) Meta Pixel і Clarity вмикаються ТІЛЬКИ після згоди.
   ID — у блоці IDS. Порожній ID = лічильник пропускається. */
(function () {
  'use strict';
  var IDS = { ga: 'G-48K7D4T5YX', meta: '2014029492638771', clarity: 'z03t1a5xtl' };
  var KEY = 'zrn_consent', AKEY = 'zrn_attr', TTL = 30 * 864e5;

  function store(v) { try { if (v === null) localStorage.removeItem(KEY); else localStorage.setItem(KEY, v); } catch (e) {} }
  function consent() { try { return localStorage.getItem(KEY); } catch (e) { return null; } }
  function lang() {
    try { var l = localStorage.getItem('zrn_language'); if (l === 'ru' || l === 'uk') return l; } catch (e) {}
    return /^\/ru(\/|$)/.test(location.pathname) ? 'ru' : 'uk';
  }

  /* ---------- 1. Джерело візиту (first-party, для замовлення) ---------- */
  var REF = [[/(^|\.)google\./, 'google'], [/bing\.com$/, 'bing'], [/duckduckgo\.com$/, 'duckduckgo'], [/yahoo\./, 'yahoo'],
    [/instagram\.com$/, 'instagram'], [/(facebook|fb)\.com$|fb\.me$/, 'facebook'], [/(^|\.)t\.me$|telegram\.(org|me)$/, 'telegram'],
    [/viber\.com$/, 'viber'], [/youtube\.com$|youtu\.be$/, 'youtube'], [/tiktok\.com$/, 'tiktok']];
  function clip(s, n) { return String(s || '').replace(/[\r\n\t]+/g, ' ').trim().slice(0, n); }
  function detect() {
    var q = new URLSearchParams(location.search), us = clip(q.get('utm_source'), 40), s = '', strong = false;
    if (us) { s = us; var m = clip(q.get('utm_medium'), 30), c = clip(q.get('utm_campaign'), 40); if (m) s += ' / ' + m; if (c) s += ' / ' + c; strong = true; }
    else if (q.get('gclid')) { s = 'google ads'; strong = true; }
    else if (q.get('fbclid')) { s = 'facebook/instagram (реклама)'; strong = true; }
    else if (document.referrer) {
      var h = '';
      try { h = new URL(document.referrer).hostname.replace(/^www\./, ''); } catch (e) {}
      if (h && h !== location.hostname.replace(/^www\./, '')) {
        s = h; for (var i = 0; i < REF.length; i++) if (REF[i][0].test(h)) { s = REF[i][1]; break; }
        if (s === 'google' || s === 'bing' || s === 'duckduckgo' || s === 'yahoo') s += ' (пошук)';
        strong = true;
      }
    }
    return { s: s || 'прямий захід', l: clip(location.pathname, 80), t: Date.now(), strong: strong };
  }
  var mem = null;
  function readA() { try { return JSON.parse(localStorage.getItem(AKEY)); } catch (e) { return mem; } }
  function writeA(a) { mem = a; try { localStorage.setItem(AKEY, JSON.stringify(a)); } catch (e) {} }
  (function capture() {
    var cur = detect(), old = readA(), fresh = old && old.t && (Date.now() - old.t) < TTL;
    if (!fresh || cur.strong) writeA({ s: cur.s, l: cur.l, t: Date.now() });
  })();
  window.zrnAttribution = function () {
    var a = readA() || mem;
    return a && a.s ? { source: a.s, landing: a.l || '' } : { source: 'прямий захід', landing: clip(location.pathname, 80) };
  };

  /* ---------- 2. GA4 (Consent Mode v2) ---------- */
  window.dataLayer = window.dataLayer || [];
  window.gtag = function () { window.dataLayer.push(arguments); };
  var DENY = { ad_storage: 'denied', ad_user_data: 'denied', ad_personalization: 'denied', analytics_storage: 'denied' };
  var GRANT = { ad_storage: 'granted', ad_user_data: 'granted', ad_personalization: 'granted', analytics_storage: 'granted' };
  if (IDS.ga) {
    gtag('consent', 'default', Object.assign({ wait_for_update: 500 }, DENY));
    gtag('set', 'ads_data_redaction', true);
    if (consent() === 'granted') gtag('consent', 'update', GRANT);
    gtag('js', new Date());
    gtag('config', IDS.ga);
  }

  /* ---------- 3. Meta Pixel + Clarity: лише після згоди ---------- */
  var stubbed = false, injected = false;
  function stubs() {                       // заглушки: події не втрачаються до завантаження скриптів
    if (stubbed) return; stubbed = true;
    if (IDS.meta && !window.fbq) {
      var n = window.fbq = function () { n.callMethod ? n.callMethod.apply(n, arguments) : n.queue.push(arguments); };
      if (!window._fbq) window._fbq = n; n.push = n; n.loaded = true; n.version = '2.0'; n.queue = [];
      n('init', IDS.meta); n('track', 'PageView');
    }
    if (IDS.clarity && !window.clarity) {
      window.clarity = function () { (window.clarity.q = window.clarity.q || []).push(arguments); };
    }
  }
  function inject(src) { var s = document.createElement('script'); s.async = true; s.src = src; document.head.appendChild(s); }
  function injectAll() {
    if (injected) return; injected = true;
    if (IDS.ga) inject('https://www.googletagmanager.com/gtag/js?id=' + IDS.ga);
    if (consent() === 'granted') {
      if (IDS.meta) inject('https://connect.facebook.net/en_US/fbevents.js');
      if (IDS.clarity) inject('https://www.clarity.ms/tag/' + IDS.clarity);
    }
  }
  function later(fn) {
    var go = function () { window.requestIdleCallback ? requestIdleCallback(fn, { timeout: 3000 }) : setTimeout(fn, 1500); };
    if (document.readyState === 'complete') go(); else window.addEventListener('load', go, { once: true });
  }
  function onGrant() {
    if (IDS.ga) gtag('consent', 'update', GRANT);
    stubs();
    if (injected) { if (IDS.meta) inject('https://connect.facebook.net/en_US/fbevents.js'); if (IDS.clarity) inject('https://www.clarity.ms/tag/' + IDS.clarity); }
    else injectAll();
  }
  if (consent() === 'granted') stubs();
  later(injectAll);

  /* ---------- події: zrnTrack(імʼя GA4, параметри GA4) ---------- */
  var META = { view_item: 'ViewContent', add_to_cart: 'AddToCart', begin_checkout: 'InitiateCheckout', purchase: 'Purchase', generate_lead: 'Lead' };
  function metaParams(p) {
    var o = { currency: p.currency || 'UAH' };
    if (p.value != null) o.value = p.value;
    if (p.items && p.items.length) {
      o.content_type = 'product';
      o.content_ids = p.items.map(function (i) { return i.item_id; });
      o.contents = p.items.map(function (i) { return { id: i.item_id, quantity: i.quantity || 1, item_price: i.price }; });
      o.num_items = p.items.reduce(function (s, i) { return s + (i.quantity || 1); }, 0);
      if (p.items.length === 1) o.content_name = p.items[0].item_name;
    }
    return o;
  }
  window.zrnTrack = function (name, params) {
    params = params || {};
    if (IDS.ga) gtag('event', name, params);                       // без згоди — анонімно (Consent Mode)
    if (consent() === 'granted' && window.fbq) {
      var mp = metaParams(params);
      if (META[name]) {
        if (params.transaction_id) window.fbq('track', META[name], mp, { eventID: params.transaction_id });
        else window.fbq('track', META[name], mp);
      } else window.fbq('trackCustom', name.replace(/(^|_)(\w)/g, function (m, a, c) { return c.toUpperCase(); }), mp);
    }
  };
  window.zrnPurchase = function (orderId, value, items) {          // один раз на замовлення
    var done = [];
    try { done = JSON.parse(localStorage.getItem('zrn_purchased') || '[]'); } catch (e) {}
    if (done.indexOf(orderId) >= 0) return;
    done.push(orderId);
    try { localStorage.setItem('zrn_purchased', JSON.stringify(done.slice(-30))); } catch (e) {}
    window.zrnTrack('purchase', { transaction_id: orderId, currency: 'UAH', value: value, items: items });
  };

  /* ---------- плашка ---------- */
  var TX = {
    uk: { t: 'Cookie допомагають нам покращувати сайт. ', more: 'Детальніше', ok: 'Прийняти', no: 'Лише необхідні', aria: 'Налаштування cookie' },
    ru: { t: 'Cookie помогают нам улучшать сайт. ', more: 'Подробнее', ok: 'Принять', no: 'Только необходимые', aria: 'Настройки cookie' }
  };
  var bar;
  function css() {
    if (document.getElementById('zrnCkCss')) return;
    var s = document.createElement('style'); s.id = 'zrnCkCss';
    s.textContent = '.zrn-ck{position:fixed;left:10px;right:10px;bottom:10px;z-index:46;max-width:560px;margin:0 auto;display:flex;align-items:center;gap:6px 12px;flex-wrap:wrap;padding:8px 10px 8px 14px;background:#1f1912;color:#f3ead9;border-radius:12px;box-shadow:0 6px 22px rgba(0,0,0,.25);font:400 .78rem/1.35 Inter,system-ui,sans-serif}'
      + '.zrn-ck p{margin:0;flex:1 1 200px}.zrn-ck a{color:#e6c98a;text-decoration:underline}'
      + '.zrn-ck-b{display:flex;align-items:center;gap:12px;margin-left:auto}'
      + '.zrn-ck button{font:inherit;cursor:pointer;min-height:36px}'
      + '.zrn-ck .y{font-weight:600;padding:7px 16px;border-radius:9px;border:0;background:#c9a24d;color:#1f1912}'
      + '.zrn-ck .n{padding:7px 2px;border:0;background:none;color:#b9ab93;text-decoration:underline;text-underline-offset:2px}'
      + '.zrn-ck button:focus-visible{outline:2px solid #e6c98a;outline-offset:2px}';
    document.head.appendChild(s);
  }
  function hide() { if (bar && bar.parentNode) bar.parentNode.removeChild(bar); bar = null; }
  function show() {
    hide(); css();
    var x = TX[lang()], pre = lang() === 'ru' ? '/ru' : '';
    bar = document.createElement('div'); bar.className = 'zrn-ck'; bar.setAttribute('role', 'region'); bar.setAttribute('aria-label', x.aria);
    bar.innerHTML = '<p>' + x.t + '<a href="' + pre + '/privacy/">' + x.more + '</a></p><div class="zrn-ck-b"><button type="button" class="n">' + x.no + '</button><button type="button" class="y">' + x.ok + '</button></div>';
    bar.querySelector('.y').onclick = function () { var was = consent(); store('granted'); hide(); if (was !== 'granted') onGrant(); };
    bar.querySelector('.n').onclick = function () {
      var was = consent() === 'granted'; store('denied'); hide();
      if (IDS.ga) gtag('consent', 'update', DENY);
      if (was) {
        ['_ga', '_gid', '_fbp', '_clck', '_clsk'].forEach(function (n) {
          document.cookie = n + '=; Max-Age=0; path=/'; document.cookie = n + '=; Max-Age=0; path=/; domain=.' + location.hostname.replace(/^www\./, '');
        });
        location.reload();
      }
    };
    document.body.appendChild(bar);
  }
  window.zrnCookieSettings = show;
  document.addEventListener('click', function (e) {
    var a = e.target.closest && e.target.closest('[data-cookie-settings]');
    if (a) { e.preventDefault(); show(); }
  });
  function init() { if (consent() === null) show(); }
  if (document.body) init(); else document.addEventListener('DOMContentLoaded', init);
})();
