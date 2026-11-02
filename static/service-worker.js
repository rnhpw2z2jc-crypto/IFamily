// Service worker de iFamily.
// Estrategia red-primero para navegacion y estaticos: evita que el navegador
// muestre una version antigua de la app despues de un redespliegue.
const CACHE_NAME = 'ifamily-v3';

self.addEventListener('install', event => {
  self.skipWaiting();
});

self.addEventListener('activate', event => {
  event.waitUntil(
    caches.keys().then(keys =>
      Promise.all(keys.filter(k => k !== CACHE_NAME).map(k => caches.delete(k)))
    ).then(() => self.clients.claim())
  );
});

self.addEventListener('fetch', event => {
  if (event.request.method !== 'GET') return;

  // Navegacion y websocket de Streamlit siempre a la red.
  event.respondWith(
    fetch(event.request).catch(() => caches.match(event.request))
  );
});
