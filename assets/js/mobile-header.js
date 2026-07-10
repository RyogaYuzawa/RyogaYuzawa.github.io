(function () {
  var header = document.querySelector(".site-header");
  var toggle = document.querySelector(".site-nav-toggle");
  var nav = document.querySelector(".site-nav");

  if (!header) {
    return;
  }

  var lastScrollY = window.scrollY;

  function isMenuOpen() {
    return header.classList.contains("site-nav-open");
  }

  function setMenuState(open) {
    if (!toggle || !nav) {
      return;
    }

    header.classList.toggle("site-nav-open", open);
    toggle.setAttribute("aria-expanded", open ? "true" : "false");
  }

  function updateHeader(forceVisible) {
    var currentScrollY = window.scrollY;
    var revealThreshold = 12;
    var hideThreshold = 96;

    if (isMenuOpen() || currentScrollY <= revealThreshold) {
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

  if (toggle && nav) {
    toggle.addEventListener("click", function () {
      setMenuState(!isMenuOpen());
      updateHeader(true);
    });

    nav.addEventListener("click", function (event) {
      if (event.target.closest(".page-link")) {
        setMenuState(false);
      }
    });

    window.addEventListener("resize", function () {
      if (window.innerWidth > 600) {
        setMenuState(false);
      }
    });
  }

  updateHeader(true);
})();
