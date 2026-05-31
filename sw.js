var CACHE_NAME = "gg-tank-v15";
var STATIC_ASSETS = [
  "/",
  "/dashboard.html",
  "/config.json",
  "/manifest.json",
  "/lib/maplibre-gl.js",
  "/lib/maplibre-gl.css"
];

self.addEventListener("install", function (event) {
  event.waitUntil(
    caches.open(CACHE_NAME).then(function (cache) {
      return cache.addAll(STATIC_ASSETS);
    })
  );
  self.skipWaiting();
});

self.addEventListener("activate", function (event) {
  event.waitUntil(
    caches.keys().then(function (names) {
      return Promise.all(
        names
          .filter(function (name) { return name !== CACHE_NAME; })
          .map(function (name) { return caches.delete(name); })
      );
    })
  );
  self.clients.claim();
});

self.addEventListener("fetch", function (event) {
  var url = new URL(event.request.url);

  // Network-first for status.json (always try fresh data)
  if (url.pathname.endsWith("/status.json")) {
    event.respondWith(
      fetch(event.request)
        .then(function (response) {
          var clone = response.clone();
          caches.open(CACHE_NAME).then(function (cache) {
            cache.put(event.request, clone);
          });
          return response;
        })
        .catch(function () {
          return caches.match(event.request);
        })
    );
    return;
  }

  // Cache-first for static assets
  if (event.request.method === "GET" && url.origin === self.location.origin) {
    event.respondWith(
      caches.match(event.request).then(function (cached) {
        if (cached) { return cached; }
        return fetch(event.request).then(function (response) {
          if (response.ok) {
            var clone = response.clone();
            caches.open(CACHE_NAME).then(function (cache) {
              cache.put(event.request, clone);
            });
          }
          return response;
        });
      })
    );
    return;
  }

  // Cross-origin requests (OpenFreeMap map style/tiles/glyphs/sprites, NOAA wind,
  // fonts): do NOT intercept. Falling through without event.respondWith() lets the
  // browser fetch them natively. Wrapping them in respondWith(fetch(event.request))
  // made the service worker the failure point: Firefox rejects the re-dispatched
  // cross-origin fetch ("CORS request did not succeed" / NetworkError), so the map
  // style + glyph tiles never loaded and the map blanked on reload — but only on
  // reload, because the SW does not control the page until after the first load.
});
