(function () {
  var mediaQuery = window.matchMedia("(max-width: 768px)");
  var header = document.querySelector(".site-header");

  if (!header) {
    return;
  }

  var lastScrollY = window.scrollY;

  function updateHeader(forceVisible) {
    if (!mediaQuery.matches) {
      header.classList.remove("site-header-hidden");
      lastScrollY = window.scrollY;
      return;
    }

    var currentScrollY = window.scrollY;

    if (forceVisible || currentScrollY <= 8 || currentScrollY < lastScrollY) {
      header.classList.remove("site-header-hidden");
    } else if (currentScrollY > lastScrollY && currentScrollY > 80) {
      header.classList.add("site-header-hidden");
    }

    lastScrollY = currentScrollY;
  }

  window.addEventListener(
    "scroll",
    function () {
      updateHeader(false);
    },
    { passive: true }
  );

  if (typeof mediaQuery.addEventListener === "function") {
    mediaQuery.addEventListener("change", function () {
      updateHeader(true);
    });
  } else if (typeof mediaQuery.addListener === "function") {
    mediaQuery.addListener(function () {
      updateHeader(true);
    });
  }

  updateHeader(true);
})();
