/* ZRN Coffee — мінімальний service worker.
   Нічого не кешує зі сторінок, цін чи каталогу — завжди беремо свіже з мережі.
   Кешується лише офлайн-сторінка та іконки. Щоб скинути кеш, змініть VERSION. */
const VERSION = 'zrn-v1';
const KEEP = ['/offline.html', '/icon-192.png', '/icon-512.png', '/favicon.ico'];

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
  if (req.mode === 'navigate') {
    e.respondWith(fetch(req).catch(function () { return caches.match('/offline.html'); }));
  }
});
