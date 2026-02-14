/*  Hypernet Unity Website - Service Worker
    Enables offline functionality and performance improvements
    Progressive Web App support
*/

const CACHE_NAME = "hypernet-v1";
const ASSETS_TO_CACHE = [
    "/",
    "/index.html",
    "/style.css",
    "/script.js",
    "/robots.txt",
    "/sitemap.xml",
];

// Install event - cache assets
self.addEventListener("install", (event) => {
    event.waitUntil(
    caches
    .open(CACHE_NAME)
    .then((cache) => {
        return cache.addAll(ASSETS_TO_CACHE);
    })
    .catch((error) => {
        console.log("Service Worker install error:", error);
    }),
    );
    self.skipWaiting();
});

// Activate event - clean old caches
self.addEventListener("activate", (event) => {
    event.waitUntil(
    caches.keys().then((cacheNames) => {
    return Promise.all(
        cacheNames.map((cacheName) => {
        if (cacheName !== CACHE_NAME) {
            return caches.delete(cacheName);
        }
        }),
    );
    }),
    );
    self.clients.claim();
});

// Fetch event - serve from cache, fallback to network
self.addEventListener("fetch", (event) => {
  // Only cache GET requests
    if (event.request.method !== "GET") {
    return;
}

    event.respondWith(
    caches.match(event.request).then((response) => {
    if (response) {
        return response;
    }

    return fetch(event.request)
        .then((response) => {
          // Don't cache non-successful responses
        if (
            !response ||
            response.status !== 200 ||
            response.type !== "basic"
        ) {
            return response;
        }

          // Clone the response
        const responseToCache = response.clone();

          // Cache successful responses
        caches.open(CACHE_NAME).then((cache) => {
            cache.put(event.request, responseToCache);
        });

        return response;
        })
        .catch(() => {
          // Return offline page if available
        return new Response(
            "<h1>Offline</h1><p>Please check your internet connection.</p>",
            {
            headers: { "Content-Type": "text/html" },
            status: 503,
            statusText: "Service Unavailable",
            },
        );
        });
    }),
);
});

// Background sync for form submissions (queue when offline)
self.addEventListener("sync", (event) => {
    if (event.tag === "sync-form-submissions") {
    event.waitUntil(syncFormSubmissions());
    }
});

async function syncFormSubmissions() {
    try {
    const submissions = JSON.parse(
    localStorage.getItem("hypernetSubmissions") || "[]",
    );

    for (const submission of submissions) {
    await fetch("/api/submissions", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(submission),
    });
    }

    localStorage.removeItem("hypernetSubmissions");
    } catch (error) {
    console.log("Sync error:", error);
}
}

// Push notifications (for future newsletter/updates)
self.addEventListener("push", (event) => {
    const data = event.data?.json() || {};
    const options = {
    body: data.body,
    icon: "/assets/icon.png",
    badge: "/assets/badge.png",
    tag: "hypernet-notification",
    requireInteraction: false,
};

    event.waitUntil(
    self.registration.showNotification(
    data.title || "Hypernet Update",
    options,
    ),
);
});

// Handle notification clicks
self.addEventListener("notificationclick", (event) => {
    event.notification.close();
    event.waitUntil(
    clients.matchAll({ type: "window" }).then((clientList) => {
    for (let i = 0; i < clientList.length; i++) {
        if (clientList[i].url === "/" && "focus" in clientList[i]) {
        return clientList[i].focus();
        }
    }
    if (clients.openWindow) {
        return clients.openWindow("/");
    }
    }),
);
});
