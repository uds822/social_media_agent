const CACHE_NAME = 'buniyaad-admin-v3';
const STATIC_ASSETS = [
  './',
  './index.html',
  './style.css',
  './app.js',
  './manifest.json',
];

// On install: cache static assets and activate immediately
self.addEventListener('install', (event) => {
  self.skipWaiting();
  event.waitUntil(
    caches.open(CACHE_NAME).then((cache) => cache.addAll(STATIC_ASSETS))
  );
});

// On activate: delete ALL old caches so stale JS/CSS is never served
self.addEventListener('activate', (event) => {
  event.waitUntil(
    caches.keys().then((keys) =>
      Promise.all(keys.filter((k) => k !== CACHE_NAME).map((k) => caches.delete(k)))
    ).then(() => self.clients.claim())
  );
});

// Network-first for app files (always get fresh code), cache-first for fonts
self.addEventListener('fetch', (event) => {
  // Only handle GET requests
  if (event.request.method !== 'GET') return;

  const url = new URL(event.request.url);

  // For Google Fonts: cache-first (they don't change)
  if (url.hostname.includes('fonts.g')) {
    event.respondWith(
      caches.match(event.request).then((cached) => cached || fetch(event.request))
    );
    return;
  }

  // Bypass cross-origin requests entirely (API calls, Cloudinary images)
  // This is critical for WebViews and APK wrappers where caching opaque responses can fail
  if (url.origin !== self.location.origin) {
    return;
  }

  // For everything else (app JS, CSS, HTML): network-first
  event.respondWith(
    fetch(event.request)
      .then((response) => {
        // Only cache valid OK responses
        if (response.status === 200) {
          const clone = response.clone();
          caches.open(CACHE_NAME).then((cache) => cache.put(event.request, clone));
        }
        return response;
      })
      .catch(() => caches.match(event.request)) // fallback to cache if offline
  );
});
