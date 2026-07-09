(function () {
  var header = document.querySelector(".site-header");

  if (!header) {
    return;
  }

  var lastScrollY = window.scrollY;

  function updateHeader(forceVisible) {
    var currentScrollY = window.scrollY;
    var revealThreshold = 12;
    var hideThreshold = 96;

    if (currentScrollY <= revealThreshold) {
      header.classList.remove("site-header-hidden");
    }
    else if (forceVisible || currentScrollY < lastScrollY) {
      header.classList.remove("site-header-hidden");
    } else if (currentScrollY > lastScrollY && currentScrollY > hideThreshold) {
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

  updateHeader(true);
})();
