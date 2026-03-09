const CACHE_NAME = "creepchat-v1"; // Change this (e.g., v2) to force an update
const ASSETS = [
  "/",
  "/static/style.css",
  "/manifest.json"
];

self.addEventListener("install", event => {
  self.skipWaiting(); // Force the new service worker to activate immediately
  event.waitUntil(
    caches.open(CACHE_NAME).then(cache => {
      return cache.addAll(ASSETS);
    })
  );
});

self.addEventListener("activate", event => {
  event.waitUntil(clients.claim()); // Take control of all open tabs immediately
  // Clean up old caches
  event.waitUntil(
    caches.keys().then(keys => {
      return Promise.all(
        keys.filter(key => key !== CACHE_NAME).map(key => caches.delete(key))
      );
    })
  );
});

self.addEventListener("fetch", event => {
  event.respondWith(
    caches.match(event.request).then(response => {
      return response || fetch(event.request);
    })
  );
});