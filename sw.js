/* ZRN Coffee — мінімальний service worker.
   Сторінки, ціни й каталог не кешуються наперед: завжди беремо свіже з мережі.
   Наперед кешуються лише офлайн-сторінка й іконки.
   Калькулятор кави (/calculator/, /ru/calculator/, calc.js, pages.css) кешується після першого візиту
   за схемою «спочатку мережа, а якщо мережі нема, то збережена копія», тож свіжа версія завжди в пріоритеті.
   Щоб скинути кеш, змініть VERSION. */
const VERSION = 'zrn-v2';
const KEEP = ['/offline.html', '/icon-192.png', '/icon-512.png', '/favicon.ico'];
const CALC = ['/calculator/', '/ru/calculator/', '/calc.js', '/pages.css'];

self.addEventListener('install', function (e) {
  e.waitUntil(caches.open(VERSION).then(function (c) { return c.addAll(KEEP); }).then(function () { return self.skipWaiting(); }));
});
self.addEventListener('activate', function (e) {
  e.waitUntil(caches.keys().then(function (keys) {
    return Promise.all(keys.filter(function (k) { return k !== VERSION; }).map(function (k) { return caches.delete(k); }));
  }).then(function () { return self.clients.claim(); }));
});
self.addEventListener('fetch', function (e) {
  const req = e.request;
  if (req.method !== 'GET') return;
  const url = new URL(req.url);
  if (url.origin === self.location.origin && CALC.indexOf(url.pathname) !== -1) {
    e.respondWith(fetch(req).then(function (res) {
      if (res && res.ok) { const copy = res.clone(); caches.open(VERSION).then(function (c) { c.put(url.pathname, copy); }); }
      return res;
    }).catch(function () {
      return caches.match(url.pathname).then(function (hit) { return hit || (req.mode === 'navigate' ? caches.match('/offline.html') : Response.error()); });
    }));
    return;
  }
  if (req.mode === 'navigate') {
    e.respondWith(fetch(req).catch(function () { return caches.match('/offline.html'); }));
  }
});
