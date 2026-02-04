// ============================================================================
// HYPERNET UNITY WEBSITE - JAVASCRIPT
// Progressive enhancement for mobile navigation and form handling
// ============================================================================

document.addEventListener("DOMContentLoaded", function () {
  initializeMobileNavigation();
  initializeFormHandling();
  initializeSmoothScroll();
  initializeAnalytics();
});

// ============================================================================
// MOBILE NAVIGATION
// ============================================================================
function initializeMobileNavigation() {
  const mobileToggle = document.querySelector(".mobile-toggle");
  const navMenu = document.querySelector(".nav-menu");

  if (!mobileToggle || !navMenu) return;

  mobileToggle.addEventListener("click", function () {
    navMenu.classList.toggle("active");
    mobileToggle.classList.toggle("active");
  });

  // Close mobile menu when a link is clicked
  const navLinks = navMenu.querySelectorAll("a");
  navLinks.forEach((link) => {
    link.addEventListener("click", function () {
      navMenu.classList.remove("active");
      mobileToggle.classList.remove("active");
    });
  });

  // Close menu when clicking outside
  document.addEventListener("click", function (event) {
    const isClickInsideNav = navMenu.contains(event.target);
    const isClickOnToggle = mobileToggle.contains(event.target);

    if (
      !isClickInsideNav &&
      !isClickOnToggle &&
      navMenu.classList.contains("active")
    ) {
      navMenu.classList.remove("active");
      mobileToggle.classList.remove("active");
    }
  });
}

// ============================================================================
// FORM HANDLING
// ============================================================================
function initializeFormHandling() {
  const contactForm = document.getElementById("contactForm");

  if (!contactForm) return;

  contactForm.addEventListener("submit", function (e) {
    e.preventDefault();

    const formData = {
      name: document.getElementById("name").value.trim(),
      email: document.getElementById("email").value.trim(),
      interest: document.getElementById("interest").value,
      message: document.getElementById("message").value.trim(),
      newsletter: document.getElementById("newsletter").checked,
      timestamp: new Date().toISOString(),
      source: "website-contact-form",
    };

    // Validation
    if (
      !formData.name ||
      !formData.email ||
      !formData.interest ||
      !formData.message
    ) {
      showFormMessage("Please fill in all required fields.", "error");
      return;
    }

    if (!isValidEmail(formData.email)) {
      showFormMessage("Please enter a valid email address.", "error");
      return;
    }

    // Submit form (using formspree or custom backend)
    submitFormData(contactForm, formData);
  });
}

function isValidEmail(email) {
  const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
  return emailRegex.test(email);
}

function submitFormData(form, data) {
  const submitButton = form.querySelector('button[type="submit"]');
  const originalText = submitButton.textContent;

  submitButton.textContent = "Sending...";
  submitButton.disabled = true;

  // Use Formspree or similar service
  fetch(form.getAttribute("action"), {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
      Accept: "application/json",
    },
    body: JSON.stringify(data),
  })
    .then((response) => {
      if (response.ok) {
        showFormMessage("Thank you! We'll be in touch soon.", "success");
        form.reset();

        // Store submission in localStorage for analytics
        storeSubmission(data);
      } else {
        throw new Error("Form submission failed");
      }
    })
    .catch((error) => {
      console.error("Error:", error);
      showFormMessage(
        "Unable to send message. Please try again or contact hello@hypernet.unity",
        "error",
      );
    })
    .finally(() => {
      submitButton.textContent = originalText;
      submitButton.disabled = false;
    });
}

function showFormMessage(message, type) {
  const form = document.getElementById("contactForm");
  let messageDiv = form.querySelector(".form-message");

  if (!messageDiv) {
    messageDiv = document.createElement("div");
    messageDiv.className = "form-message";
    form.insertBefore(messageDiv, form.firstChild);
  }

  messageDiv.textContent = message;
  messageDiv.className = `form-message form-message-${type}`;
  messageDiv.style.display = "block";

  setTimeout(() => {
    messageDiv.style.display = "none";
  }, 5000);
}

function storeSubmission(data) {
  try {
    const submissions =
      JSON.parse(localStorage.getItem("hypernetSubmissions")) || [];
    submissions.push(data);
    localStorage.setItem("hypernetSubmissions", JSON.stringify(submissions));
  } catch (e) {
    console.log("Local storage not available");
  }
}

// ============================================================================
// SMOOTH SCROLL (for browsers that don't support natively)
// ============================================================================
function initializeSmoothScroll() {
  const links = document.querySelectorAll('a[href^="#"]');

  links.forEach((link) => {
    link.addEventListener("click", function (e) {
      const href = this.getAttribute("href");
      if (href === "#") return;

      const target = document.querySelector(href);
      if (target) {
        e.preventDefault();
        const offsetTop = target.offsetTop - 80; // Account for fixed navbar
        window.scrollTo({
          top: offsetTop,
          behavior: "smooth",
        });
      }
    });
  });
}

// ============================================================================
// ANALYTICS
// ============================================================================
function initializeAnalytics() {
  // Track page view
  trackEvent("pageview", {
    page: window.location.pathname,
    title: document.title,
  });

  // Track section views
  observeSections();

  // Track external links
  trackExternalLinks();
}

function trackEvent(eventName, eventData) {
  // Send to Google Analytics, Mixpanel, or custom backend
  if (window.gtag) {
    gtag("event", eventName, eventData);
  }

  // Fallback: console log in development
  if (location.hostname === "localhost" || location.hostname === "127.0.0.1") {
    console.log("Event:", eventName, eventData);
  }

  // Store in localStorage
  try {
    const events = JSON.parse(localStorage.getItem("hypernetEvents")) || [];
    events.push({
      event: eventName,
      data: eventData,
      timestamp: new Date().toISOString(),
    });
    localStorage.setItem("hypernetEvents", JSON.stringify(events.slice(-100)));
  } catch (e) {
    console.log("Local storage not available");
  }
}

function observeSections() {
  const sections = document.querySelectorAll("section[id]");

  const observer = new IntersectionObserver(
    (entries) => {
      entries.forEach((entry) => {
        if (entry.isIntersecting) {
          trackEvent("section_view", {
            section: entry.target.id,
          });
        }
      });
    },
    { threshold: 0.25 },
  );

  sections.forEach((section) => observer.observe(section));
}

function trackExternalLinks() {
  const links = document.querySelectorAll(
    'a[target="_blank"][rel*="noopener"]',
  );

  links.forEach((link) => {
    link.addEventListener("click", function () {
      trackEvent("external_link_click", {
        url: this.href,
        text: this.textContent,
      });
    });
  });
}

// ============================================================================
// PERFORMANCE MONITORING
// ============================================================================
function reportWebVitals() {
  if ("web-vital" in window) {
    // Using Web Vitals library
    webVitals.getCLS((metric) => trackEvent("CLS", metric));
    webVitals.getFID((metric) => trackEvent("FID", metric));
    webVitals.getFCP((metric) => trackEvent("FCP", metric));
    webVitals.getLCP((metric) => trackEvent("LCP", metric));
    webVitals.getTTFB((metric) => trackEvent("TTFB", metric));
  }

  // Performance API fallback
  if (window.performance && window.performance.timing) {
    window.addEventListener("load", function () {
      const perfData = window.performance.timing;
      const pageLoadTime = perfData.loadEventEnd - perfData.navigationStart;

      trackEvent("page_load_time", {
        duration: pageLoadTime,
        dns: perfData.domainLookupEnd - perfData.domainLookupStart,
        tcp: perfData.connectEnd - perfData.connectStart,
        ttfb: perfData.responseStart - perfData.navigationStart,
        dom: perfData.domInteractive - perfData.navigationStart,
        resources: perfData.loadEventEnd - perfData.domInteractive,
      });
    });
  }
}

// Call after analytics initialization
if (document.readyState === "loading") {
  document.addEventListener("DOMContentLoaded", reportWebVitals);
} else {
  reportWebVitals();
}

// ============================================================================
// SERVICE WORKER REGISTRATION (Progressive Web App)
// ============================================================================
if ("serviceWorker" in navigator) {
  navigator.serviceWorker.register("/sw.js").catch((error) => {
    if (location.hostname !== "localhost") {
      console.log("Service Worker registration failed:", error);
    }
  });
}

// ============================================================================
// PERFORMANCE OPTIMIZATION: Lazy Loading
// ============================================================================
if ("IntersectionObserver" in window) {
  const imageObserver = new IntersectionObserver((entries, observer) => {
    entries.forEach((entry) => {
      if (entry.isIntersecting) {
        const img = entry.target;
        img.src = img.dataset.src;
        img.classList.remove("lazy");
        imageObserver.unobserve(img);
      }
    });
  });

  document.querySelectorAll("img[data-src]").forEach((img) => {
    imageObserver.observe(img);
  });
}

// ============================================================================
// UTILITY: Debounce function
// ============================================================================
function debounce(func, wait) {
  let timeout;
  return function executedFunction(...args) {
    const later = () => {
      clearTimeout(timeout);
      func(...args);
    };
    clearTimeout(timeout);
    timeout = setTimeout(later, wait);
  };
}

// ============================================================================
// EXPORT for module systems
// ============================================================================
if (typeof module !== "undefined" && module.exports) {
  module.exports = {
    trackEvent,
    isValidEmail,
    debounce,
  };
}
