/* ZRN Coffee — аналітика з согласием на cookie.
   Лічильники (GA4, Meta Pixel, Clarity) НЕ завантажуються, доки відвідувач не натисне «Прийняти».
   ID лічильників — у блоці IDS нижче. Порожній ID = лічильник пропускається. */
(function () {
  'use strict';
  var IDS = { ga: 'G-48K7D4T5YX', meta: '2014029492638771', clarity: 'z03t1a5xtl' };
  var KEY = 'zrn_consent';
  var loaded = false;

  function store(v) { try { if (v === null) localStorage.removeItem(KEY); else localStorage.setItem(KEY, v); } catch (e) {} }
  function consent() { try { return localStorage.getItem(KEY); } catch (e) { return null; } }
  function lang() {
    try { var l = localStorage.getItem('zrn_language'); if (l === 'ru' || l === 'uk') return l; } catch (e) {}
    return /^\/ru(\/|$)/.test(location.pathname) ? 'ru' : 'uk';
  }
  var TX = {
    uk: { t: 'Використовуємо cookie для статистики та реклами. ', more: 'Детальніше', ok: 'Прийняти', no: 'Відхилити', aria: 'Налаштування cookie' },
    ru: { t: 'Используем cookie для статистики и рекламы. ', more: 'Подробнее', ok: 'Принять', no: 'Отклонить', aria: 'Настройки cookie' }
  };

  /* ---------- завантаження лічильників (після згоди, поза критичним шляхом) ---------- */
  function load() {
    if (loaded) return; loaded = true;
    if (IDS.ga) {
      window.dataLayer = window.dataLayer || [];
      window.gtag = function () { window.dataLayer.push(arguments); };
      window.gtag('js', new Date());
      window.gtag('config', IDS.ga);
      var s = document.createElement('script'); s.async = true;
      s.src = 'https://www.googletagmanager.com/gtag/js?id=' + IDS.ga;
      document.head.appendChild(s);
    }
    if (IDS.meta) {
      (function (f, b, e, v, n, t, s) {
        if (f.fbq) return; n = f.fbq = function () { n.callMethod ? n.callMethod.apply(n, arguments) : n.queue.push(arguments); };
        if (!f._fbq) f._fbq = n; n.push = n; n.loaded = !0; n.version = '2.0'; n.queue = [];
        t = b.createElement(e); t.async = !0; t.src = v; s = b.getElementsByTagName(e)[0]; s.parentNode.insertBefore(t, s);
      })(window, document, 'script', 'https://connect.facebook.net/en_US/fbevents.js');
      window.fbq('init', IDS.meta);
      window.fbq('track', 'PageView');
    }
    if (IDS.clarity) {
      (function (c, l, a, r, i, t, y) {
        c[a] = c[a] || function () { (c[a].q = c[a].q || []).push(arguments); };
        t = l.createElement(r); t.async = 1; t.src = 'https://www.clarity.ms/tag/' + i;
        y = l.getElementsByTagName(r)[0]; y.parentNode.insertBefore(t, y);
      })(window, document, 'clarity', 'script', IDS.clarity);
    }
  }
  function loadLater() {
    var go = function () { (window.requestIdleCallback ? requestIdleCallback(load, { timeout: 3000 }) : setTimeout(load, 1500)); };
    if (document.readyState === 'complete') go(); else window.addEventListener('load', go, { once: true });
  }

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
  var q = [];                       // події, що трапилися до завантаження лічильників (лише після згоди)
  function send(name, p) {
    if (window.gtag) window.gtag('event', name, p);
    if (window.fbq) {
      var mp = metaParams(p);
      if (META[name]) {
        var opts = p.transaction_id ? { eventID: p.transaction_id } : undefined;
        opts ? window.fbq('track', META[name], mp, opts) : window.fbq('track', META[name], mp);
      } else window.fbq('trackCustom', name.replace(/(^|_)(\w)/g, function (m, a, c) { return c.toUpperCase(); }), mp);
    }
  }
  window.zrnTrack = function (name, params) {
    if (consent() !== 'granted') return;           // без згоди нічого не відправляємо і не накопичуємо
    params = params || {};
    if (!loaded) { q.push([name, params]); return; }
    if (!window.gtag && !window.fbq) { q.push([name, params]); return; }
    send(name, params);
  };
  // події, відкладені до моменту ініціалізації, відправляються, щойно gtag/fbq з'явилися
  setInterval(function () { if (q.length && loaded && (window.gtag || window.fbq)) { var a = q.splice(0); a.forEach(function (e) { send(e[0], e[1]); }); } }, 400);

  /* purchase — один раз на замовлення (захист від повторів навіть після перезавантаження) */
  window.zrnPurchase = function (orderId, value, items) {
    if (consent() !== 'granted') return;
    var done = [];
    try { done = JSON.parse(localStorage.getItem('zrn_purchased') || '[]'); } catch (e) {}
    if (done.indexOf(orderId) >= 0) return;
    done.push(orderId);
    try { localStorage.setItem('zrn_purchased', JSON.stringify(done.slice(-30))); } catch (e) {}
    window.zrnTrack('purchase', { transaction_id: orderId, currency: 'UAH', value: value, items: items });
  };

  /* ---------- плашка згоди ---------- */
  var bar;
  function css() {
    if (document.getElementById('zrnCkCss')) return;
    var s = document.createElement('style'); s.id = 'zrnCkCss';
    s.textContent = '.zrn-ck{position:fixed;left:12px;right:12px;bottom:12px;z-index:2147483000;max-width:640px;margin:0 auto;display:flex;flex-wrap:wrap;align-items:center;gap:10px 14px;padding:12px 14px;background:#1f1912;color:#f3ead9;border-radius:14px;box-shadow:0 8px 28px rgba(0,0,0,.28);font:400 .86rem/1.4 Inter,system-ui,sans-serif}'
      + '.zrn-ck p{margin:0;flex:1 1 240px}.zrn-ck a{color:#e6c98a;text-decoration:underline}'
      + '.zrn-ck-b{display:flex;gap:8px;flex:0 0 auto}.zrn-ck button{font:600 .84rem Inter,system-ui,sans-serif;padding:9px 16px;border-radius:10px;border:1px solid #6b5a3e;background:transparent;color:#f3ead9;cursor:pointer;min-height:40px}'
      + '.zrn-ck button.y{background:#c9a24d;border-color:#c9a24d;color:#1f1912}.zrn-ck button:focus-visible{outline:2px solid #e6c98a;outline-offset:2px}'
      + '@media(max-width:480px){.zrn-ck-b{width:100%}.zrn-ck-b button{flex:1}}';
    document.head.appendChild(s);
  }
  function hide() { if (bar && bar.parentNode) bar.parentNode.removeChild(bar); bar = null; }
  function show() {
    hide(); css();
    var x = TX[lang()], pre = lang() === 'ru' ? '/ru' : '';
    bar = document.createElement('div'); bar.className = 'zrn-ck'; bar.setAttribute('role', 'region'); bar.setAttribute('aria-label', x.aria);
    bar.innerHTML = '<p>' + x.t + '<a href="' + pre + '/privacy/">' + x.more + '</a></p><div class="zrn-ck-b"><button type="button" class="n">' + x.no + '</button><button type="button" class="y">' + x.ok + '</button></div>';
    bar.querySelector('.y').onclick = function () { store('granted'); hide(); load(); };
    bar.querySelector('.n').onclick = function () {
      var was = consent() === 'granted'; store('denied'); hide();
      if (was) { // згоду відкликано: прибираємо cookie лічильників і перезавантажуємо без них
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

  function init() {
    var c = consent();
    if (c === 'granted') loadLater();
    else if (c !== 'denied') show();
  }
  if (document.body) init(); else document.addEventListener('DOMContentLoaded', init);
})();
