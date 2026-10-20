// procrastiNOT Service Worker - Aggressive Network-First with Instant Auto-Purge
const CACHE_NAME = 'procrastinot-pwa-v13';

self.addEventListener('install', (event) => {
  // Activate immediately without waiting for existing tabs to close
  self.skipWaiting();
});

self.addEventListener('activate', (event) => {
  // Purge ALL existing caches immediately!
  event.waitUntil(
    caches.keys().then((keys) => {
      return Promise.all(keys.map((k) => caches.delete(k)));
    }).then(() => self.clients.claim())
  );
});

self.addEventListener('fetch', (event) => {
  // Only handle GET requests within same origin; bypass external APIs (Gemini, Supabase, Google Fonts)
  if (event.request.method !== 'GET' || !event.request.url.startsWith(self.location.origin)) {
    return;
  }

  // NETWORK-FIRST STRATEGY:
  // Always fetch fresh content from server so updates apply instantly.
  // Fallback to cache only when offline.
  event.respondWith(
    fetch(event.request)
      .then((networkResponse) => {
        if (networkResponse && networkResponse.status === 200) {
          const resClone = networkResponse.clone();
          caches.open(CACHE_NAME).then((cache) => cache.put(event.request, resClone));
        }
        return networkResponse;
      })
      .catch(() => caches.match(event.request))
  );
});
