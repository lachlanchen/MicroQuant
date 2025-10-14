// Very small service worker: cache shell assets; network-first for API
const CACHE_NAME = 'microquant-v1';
const SHELL = [
  '/',
  '/app',
  '/static/manifest.webmanifest',
  '/static/logo.png',
  '/static/favicon.ico'
];

self.addEventListener('install', (event) => {
  event.waitUntil(caches.open(CACHE_NAME).then(c => c.addAll(SHELL)));
  self.skipWaiting();
});

self.addEventListener('activate', (event) => {
  event.waitUntil(
    caches.keys().then(keys => Promise.all(keys.map(k => k !== CACHE_NAME ? caches.delete(k) : Promise.resolve())))
  );
  self.clients.claim();
});

self.addEventListener('fetch', (event) => {
  const url = new URL(event.request.url);
  if (url.pathname.startsWith('/api/')) {
    // Network-first for dynamic data
    event.respondWith(
      fetch(event.request).catch(() => caches.match(event.request))
    );
    return;
  }
  // Cache-first for shell/static
  event.respondWith(
    caches.match(event.request).then((resp) => resp || fetch(event.request))
  );
});

