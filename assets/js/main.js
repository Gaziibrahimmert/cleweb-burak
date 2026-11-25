(function () {
  var root = document.documentElement;
  root.classList.remove("no-js");

  // mobile menu
  var btn = document.querySelector(".menu-btn");
  if (btn) {
    btn.addEventListener("click", function () {
      var open = document.body.classList.toggle("menu-open");
      btn.setAttribute("aria-expanded", open ? "true" : "false");
    });
    document.addEventListener("keydown", function (e) {
      if (e.key === "Escape" && document.body.classList.contains("menu-open")) {
        document.body.classList.remove("menu-open");
        btn.setAttribute("aria-expanded", "false");
        btn.focus();
      }
    });
  }

  // header hairline once scrolled
  var header = document.querySelector(".site-header");
  if (header) {
    var onScroll = function () { header.classList.toggle("is-scrolled", window.scrollY > 8); };
    window.addEventListener("scroll", onScroll, { passive: true });
    onScroll();
  }

  // gentle reveal
  var items = document.querySelectorAll(".reveal");
  if ("IntersectionObserver" in window && items.length) {
    var io = new IntersectionObserver(function (entries) {
      entries.forEach(function (en) {
        if (en.isIntersecting) { en.target.classList.add("is-in"); io.unobserve(en.target); }
      });
    }, { rootMargin: "0px 0px -8% 0px", threshold: 0.08 });
    items.forEach(function (el) { io.observe(el); });
  } else {
    items.forEach(function (el) { el.classList.add("is-in"); });
  }

  // remember an explicit language choice for the root redirect
  document.querySelectorAll(".lang a").forEach(function (a) {
    a.addEventListener("click", function () {
      try { localStorage.setItem("lang", a.getAttribute("hreflang")); } catch (e) {}
    });
  });

  // contact form: send via fetch, fall back to a normal post without JS
  var form = document.querySelector(".contact-form");
  if (form) {
    var msg = JSON.parse(form.getAttribute("data-msg") || "{}");
    var status = form.querySelector(".form-status");
    var button = form.querySelector("button[type=submit]");
    var show = function (text, cls) { status.textContent = text; status.className = "form-status " + (cls || ""); };

    // result of a no-JS post comes back in the query string
    var q = location.search;
    if (/[?&]gesendet=1/.test(q)) show(msg.ok, "ok");
    else { var m = q.match(/[?&]fehler=(\w+)/); if (m) show(msg[m[1]] || msg.send, "err"); }

    form.addEventListener("submit", function (e) {
      e.preventDefault();
      var fields = {
        name: form.elements.name, email: form.elements.email,
        message: form.elements.message, consent: form.elements.consent
      };
      var bad = [];
      if (fields.name.value.trim().length < 2) bad.push("name");
      if (!/^\S+@\S+\.\S{2,}$/.test(fields.email.value.trim())) bad.push("email");
      if (fields.message.value.trim().length < 5) bad.push("message");
      if (!fields.consent.checked) bad.push("consent");
      Object.keys(fields).forEach(function (k) {
        var el = k === "consent" ? fields[k].closest(".consent") : fields[k];
        el.classList.toggle("is-invalid", bad.indexOf(k) >= 0);
        if (k !== "consent") fields[k].setAttribute("aria-invalid", bad.indexOf(k) >= 0 ? "true" : "false");
      });
      if (bad.length) { show(msg.invalid, "err"); (bad[0] === "consent" ? fields.consent : fields[bad[0]]).focus(); return; }

      var data = {};
      new FormData(form).forEach(function (v, k) { data[k] = v; });
      data.consent = true;
      button.disabled = true;
      show(msg.sending);
      fetch(form.action, { method: "POST", headers: { "Content-Type": "application/json" }, body: JSON.stringify(data) })
        .then(function (r) { return r.json().catch(function () { return { ok: false, error: "send" }; }); })
        .then(function (res) {
          if (res.ok) { form.reset(); show(msg.ok, "ok"); }
          else show(msg[res.error] || msg.send, "err");
        })
        .catch(function () { show(msg.send, "err"); })
        .then(function () { button.disabled = false; });
    });
  }

  var y = document.querySelector("[data-year]");
  if (y) y.textContent = new Date().getFullYear();
})();
