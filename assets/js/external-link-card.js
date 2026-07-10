(function () {
  var cards = document.querySelectorAll(".external-link-card[data-url]");

  if (!cards.length) {
    return;
  }

  var metadataCache = new Map();

  function normalizeText(value) {
    return value ? value.replace(/\s+/g, " ").trim() : "";
  }

  function getMeta(doc, selectors) {
    for (var i = 0; i < selectors.length; i += 1) {
      var node = doc.querySelector(selectors[i]);
      var content = node && (node.getAttribute("content") || node.textContent);
      content = normalizeText(content);

      if (content) {
        return content;
      }
    }

    return "";
  }

  function resolveUrl(baseUrl, candidate) {
    if (!candidate) {
      return "";
    }

    try {
      return new URL(candidate, baseUrl).toString();
    } catch (error) {
      return "";
    }
  }

  function fetchMetadata(url) {
    if (metadataCache.has(url)) {
      return metadataCache.get(url);
    }

    var request = fetch(
      "https://api.allorigins.win/raw?url=" + encodeURIComponent(url),
      { credentials: "omit" }
    )
      .then(function (response) {
        if (!response.ok) {
          throw new Error("metadata fetch failed");
        }

        return response.text();
      })
      .then(function (html) {
        var parser = new DOMParser();
        var doc = parser.parseFromString(html, "text/html");
        var title = getMeta(doc, [
          'meta[property="og:title"]',
          'meta[name="twitter:title"]',
          "title",
        ]);
        var description = getMeta(doc, [
          'meta[property="og:description"]',
          'meta[name="twitter:description"]',
          'meta[name="description"]',
        ]);
        var siteName = getMeta(doc, [
          'meta[property="og:site_name"]',
          'meta[name="application-name"]',
        ]);
        var image = resolveUrl(
          url,
          getMeta(doc, [
            'meta[property="og:image"]',
            'meta[name="twitter:image"]',
          ])
        );
        var favicon = resolveUrl(
          url,
          getMeta(doc, [
            'link[rel="apple-touch-icon"]',
            'link[rel="apple-touch-icon-precomposed"]',
            'link[rel="icon"]',
            'link[rel="shortcut icon"]',
          ])
        );

        return {
          title: title,
          description: description,
          siteName: siteName,
          image: image,
          favicon: favicon,
        };
      })
      .catch(function () {
        return null;
      });

    metadataCache.set(url, request);
    return request;
  }

  function applyMetadata(card, metadata) {
    if (!metadata) {
      return;
    }

    var title = card.querySelector(".external-link-card__title");
    var subtitle = card.querySelector(".external-link-card__subtitle");
    var favicon = card.querySelector(".external-link-card__favicon");
    var host = card.querySelector(".external-link-card__host");
    var thumb = card.querySelector(".external-link-card__thumb");
    var thumbInner = card.querySelector(".external-link-card__thumb-inner");
    var hostname = card.getAttribute("data-hostname") || "";

    if (metadata.title && title) {
      title.textContent = metadata.title;
    }

    if (metadata.siteName && subtitle) {
      subtitle.textContent = metadata.siteName;
    }

    if (metadata.favicon && favicon) {
      favicon.src = metadata.favicon;
    }

    if (host) {
      host.textContent = hostname;
    }

    if (metadata.image && thumb && !thumb.querySelector(".external-link-card__preview")) {
      var preview = document.createElement("img");
      preview.className = "external-link-card__preview";
      preview.src = metadata.image;
      preview.alt = metadata.title || hostname;
      preview.loading = "lazy";
      thumb.insertBefore(preview, thumb.firstChild);
      thumb.classList.add("external-link-card__thumb--has-preview");

      if (thumbInner) {
        thumbInner.classList.add("external-link-card__thumb-inner--overlay");
      }
    }
  }

  cards.forEach(function (card) {
    fetchMetadata(card.getAttribute("data-url")).then(function (metadata) {
      applyMetadata(card, metadata);
    });
  });
})();
