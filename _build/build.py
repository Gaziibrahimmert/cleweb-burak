"""Static site generator for praxis-arkan.de.

The published site is plain HTML in /de, /tr, /en. Texts live in content_*.py;
this file only holds the layout. Run:  python _build/build.py
"""
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, HERE)

import content_de, content_tr, content_en  # noqa: E402

LANGS = [content_de.L, content_tr.L, content_en.L]
BASE = "https://praxis-arkan.de"
PAGE_KEYS = ["home", "st", "about", "contact", "imprint", "privacy"]

PRACTICE = {
    "name": "Burak Arkan",
    "street": "Albertstraße 54",
    "zip": "45894",
    "city": "Gelsenkirchen",
    # primary number (mobile) first, landline second
    "phone": "0163 670 7918",
    "phone_href": "+491636707918",
    "landline": "0209 359 765 97",
    "landline_href": "+4920935976597",
    "email": "arkanburak@gmail.com",
    "maps": "https://www.openstreetmap.org/search?query=Albertstra%C3%9Fe%2054%2C%2045894%20Gelsenkirchen",
}

ICON = {
    "phone": '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.6" aria-hidden="true"><path d="M5 3.5h3.2l1.6 4.3-2.1 1.4a11.5 11.5 0 0 0 7.1 7.1l1.4-2.1 4.3 1.6V19a1.8 1.8 0 0 1-1.9 1.8C10.6 20.3 3.7 13.4 3.2 5.4A1.8 1.8 0 0 1 5 3.5Z"/></svg>',
    "mail": '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.6" aria-hidden="true"><rect x="3" y="5" width="18" height="14" rx="1"/><path d="m3.5 6 8.5 7 8.5-7"/></svg>',
    "arrow": '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.6" aria-hidden="true"><path d="M4 12h15M13 6l6 6-6 6"/></svg>',
}


def esc_attr(s):
    return s.replace("&", "&amp;").replace('"', "&quot;").replace("<", "&lt;")


def href(L, key, frm=None):
    """Link to page `key` of language L, relative to a page in language `frm`."""
    slug = L["slugs"][key]
    if frm is None or frm["code"] == L["code"]:
        return slug
    return f"../{L['code']}/{slug}"


def url(L, key):
    slug = L["slugs"][key]
    return f"{BASE}/{L['code']}/" + ("" if slug == "index.html" else slug)


# ---------------------------------------------------------------- partials

def head(L, key):
    page = L["pages"][key]
    alts = "\n".join(
        f'  <link rel="alternate" hreflang="{o["code"]}" href="{url(o, key)}">' for o in LANGS
    )
    ld = {
        "@context": "https://schema.org",
        "@type": "MedicalBusiness",
        "name": L["ui"]["practice_name"] + " – Burak Arkan",
        "description": L["pages"]["home"]["desc"],
        "url": url(L, "home"),
        "logo": f"{BASE}/assets/img/icon-512.png",
        "telephone": PRACTICE["phone_href"],
        "email": PRACTICE["email"],
        "address": {
            "@type": "PostalAddress",
            "streetAddress": PRACTICE["street"],
            "postalCode": PRACTICE["zip"],
            "addressLocality": PRACTICE["city"],
            "addressCountry": "DE",
        },
        "areaServed": "Gelsenkirchen",
        "availableLanguage": ["de", "tr", "en"],
        "employee": {
            "@type": "Person",
            "name": "Burak Arkan",
            "jobTitle": L["ui"]["job_title"],
        },
    }
    robots = '\n  <meta name="robots" content="noindex">' if key in ("imprint", "privacy") and L["code"] != "de" else ""
    return f"""<!doctype html>
<html lang="{L['html_lang']}" class="no-js">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>{page['title']}</title>
  <meta name="description" content="{esc_attr(page['desc'])}">{robots}
  <link rel="canonical" href="{url(L, key)}">
{alts}
  <link rel="alternate" hreflang="x-default" href="{url(LANGS[0], key)}">
  <meta property="og:type" content="website">
  <meta property="og:locale" content="{L['locale']}">
  <meta property="og:title" content="{esc_attr(page['title'])}">
  <meta property="og:description" content="{esc_attr(page['desc'])}">
  <meta property="og:url" content="{url(L, key)}">
  <meta property="og:image" content="{BASE}/assets/img/icon-512.png">
  <meta name="theme-color" content="#f6f4f1">
  <link rel="icon" href="../favicon.ico" sizes="any">
  <link rel="icon" type="image/png" href="../assets/img/favicon-32.png" sizes="32x32">
  <link rel="apple-touch-icon" href="../assets/img/apple-touch-icon.png">
  <link rel="preload" href="../assets/fonts/newsreader-latin-opsz-normal.woff2" as="font" type="font/woff2" crossorigin>
  <link rel="preload" href="../assets/fonts/source-sans-3-latin-wght-normal.woff2" as="font" type="font/woff2" crossorigin>
  <link rel="stylesheet" href="../assets/css/style.css">
  <script type="application/ld+json">{json.dumps(ld, ensure_ascii=False)}</script>
</head>
<body>
<a class="skip" href="#main">{L['ui']['skip']}</a>
"""


def header(L, key):
    ui = L["ui"]
    nav = "".join(
        f'<a href="{href(L, k)}"{" aria-current=\"page\"" if k == key else ""}>{L["nav"][k]}</a>'
        for k in ("st", "about", "contact")
    )
    langs = "".join(
        f'<a href="{href(o, key, L)}" hreflang="{o["code"]}" lang="{o["html_lang"]}"'
        f'{" aria-current=\"true\"" if o["code"] == L["code"] else ""} title="{o["name"]}">{o["code"].upper()}</a>'
        for o in LANGS
    )
    return f"""<header class="site-header">
  <div class="wrap">
    <a class="brand" href="{href(L, 'home')}" aria-label="{ui['practice_name']} – {ui['home']}">
      <img src="../assets/img/logo.webp" alt="" width="34" height="37">
      <span class="brand-text"><span class="brand-name">Burak Arkan</span><span class="brand-sub">{ui['practice_name']}</span></span>
    </a>
    <nav class="nav" id="nav" aria-label="{ui['nav_label']}">
      {nav}
      <div class="lang" aria-label="{ui['lang_label']}">{langs}</div>
    </nav>
    <a class="header-call" href="tel:{PRACTICE['phone_href']}">{ICON['phone']}<span class="label">{PRACTICE['phone']}</span></a>
    <button class="menu-btn" type="button" aria-controls="nav" aria-expanded="false" aria-label="{ui['menu']}"><span></span><span></span><span></span></button>
  </div>
</header>
<main id="main">
"""


def footer(L, key):
    ui = L["ui"]
    pages = "".join(f'<li><a href="{href(L, k)}">{L["nav"][k]}</a></li>' for k in ("st", "about", "contact"))
    return f"""</main>
<footer class="site-footer">
  <div class="wrap">
    <div class="foot-grid">
      <div class="foot-brand">
        <img src="../assets/img/logo.webp" alt="" width="40" height="44" loading="lazy">
        <div>
          <div class="brand-name">Burak Arkan</div>
          <p>{ui['footer_tagline']}</p>
        </div>
      </div>
      <div>
        <p class="foot-h">{ui['foot_practice']}</p>
        <ul class="foot-list">{pages}</ul>
      </div>
      <div>
        <p class="foot-h">{ui['foot_contact']}</p>
        <ul class="foot-list">
          <li><a href="tel:{PRACTICE['phone_href']}">{PRACTICE['phone']}</a></li>
          <li><a href="tel:{PRACTICE['landline_href']}">{PRACTICE['landline']}</a></li>
          <li><a href="mailto:{PRACTICE['email']}">{PRACTICE['email']}</a></li>
        </ul>
      </div>
      <div>
        <p class="foot-h">{ui['foot_address']}</p>
        <address style="font-style:normal">{PRACTICE['street']}<br>{PRACTICE['zip']} {PRACTICE['city']}</address>
        <p style="margin-top:12px"><a href="{PRACTICE['maps']}" rel="noopener" target="_blank">{ui['map_link']}</a></p>
      </div>
    </div>
    <div class="foot-bottom">
      <span>© <span data-year>2026</span> Burak Arkan · {ui['practice_name']}</span>
      <nav aria-label="{ui['legal_label']}"><a href="{href(L, 'imprint')}">{L['nav']['imprint']}</a><a href="{href(L, 'privacy')}">{L['nav']['privacy']}</a></nav>
    </div>
  </div>
</footer>
<div class="call-bar">
  <a href="tel:{PRACTICE['phone_href']}">{ICON['phone']}{ui['call_short']}</a>
  <a href="mailto:{PRACTICE['email']}">{ICON['mail']}{ui['mail_short']}</a>
</div>
<script src="../assets/js/main.js" defer></script>
</body>
</html>
"""


def motif(cls="hero-motif"):
    return f'<img class="{cls}" src="../assets/img/motif.webp" alt="" width="900" height="980" aria-hidden="true">'


def btn_call(L, ghost=False):
    return (f'<a class="btn {"btn-ghost" if ghost else "btn-primary"}" href="tel:{PRACTICE["phone_href"]}">'
            f'{ICON["phone"]}{L["ui"]["call"]}</a>')


def btn_mail(L):
    return f'<a class="btn btn-ghost" href="mailto:{PRACTICE["email"]}">{ICON["mail"]}{L["ui"]["write"]}</a>'


def link_arrow(text, to):
    return f'<a class="link-arrow" href="{to}">{text}{ICON["arrow"]}</a>'


def page_hero(p):
    return f"""<section class="page-hero">
  {motif()}
  <div class="wrap">
    <p class="eyebrow">{p['eyebrow']}</p>
    <h1>{p['h1']}</h1>
    <p class="lead">{p['lead']}</p>
  </div>
</section>
"""


def lines(items, single=False):
    lis = "".join(f"<li><b>{b}</b><span>{s}</span></li>" for b, s in items)
    return f'<ul class="list-lines{" single" if single else ""}">{lis}</ul>'


def bullets(items, cols=False):
    return f'<ul class="bullets{" cols-2" if cols else ""}">' + "".join(f"<li>{i}</li>" for i in items) + "</ul>"


def paras(items):
    return "".join(f"<p>{p}</p>" for p in items)


def faq(items):
    return '<div class="faq">' + "".join(
        f'<details><summary>{q}</summary><div class="answer">{paras(a if isinstance(a, list) else [a])}</div></details>'
        for q, a in items) + "</div>"


def split(h2, body, eyebrow=None, ident=None, cls="section"):
    eb = f'<p class="eyebrow">{eyebrow}</p>' if eyebrow else ""
    idattr = f' id="{ident}"' if ident else ""
    return f"""<section class="{cls}"{idattr}>
  <div class="wrap split">
    <div class="reveal">{eb}<h2>{h2}</h2></div>
    <div class="reveal">{body}</div>
  </div>
</section>
"""


def cta_end(L):
    c = L["cta"]
    return f"""<section class="cta-end">
  <div class="wrap">
    <div class="reveal"><p class="eyebrow">{c['eyebrow']}</p><h2>{c['h2']}</h2></div>
    <div class="reveal">
      <a class="phone-big" href="tel:{PRACTICE['phone_href']}">{PRACTICE['phone']}</a>
      <p class="muted">{c['text']}</p>
      <div class="btn-row" style="margin-top:24px">{btn_mail(L)}</div>
    </div>
  </div>
</section>
"""


# ---------------------------------------------------------------- pages

def page_home(L):
    t = L["home"]
    facts = "".join(
        f'<li><span class="n">{i + 1:02d}</span><div><b>{b}</b><span>{s}</span></div></li>'
        for i, (b, s) in enumerate(t["facts"]))
    return f"""<section class="hero">
  {motif()}
  <div class="wrap hero-grid">
    <div class="reveal">
      <p class="eyebrow">{t['eyebrow']}</p>
      <h1>{t['h1']}</h1>
      <p class="lead">{t['lead']}</p>
      <div class="btn-row">{btn_call(L)}{link_arrow(t['more'], href(L, 'st')).replace('class="link-arrow"', 'class="btn btn-ghost"')}</div>
    </div>
    <aside class="hero-aside reveal" aria-label="{t['facts_label']}">
      <ul class="facts">{facts}</ul>
    </aside>
  </div>
</section>

<section class="section">
  <div class="wrap statement-wrap">
    <p class="eyebrow reveal">{t['intro_eyebrow']}</p>
    <div class="reveal">
      <p class="statement">{t['statement']}</p>
      <div style="margin-top:36px; max-width:60ch" class="muted">{paras(t['intro'])}</div>
      <p style="margin-top:28px">{link_arrow(t['intro_link'], href(L, 'st'))}</p>
    </div>
  </div>
</section>

<section class="section tint">
  <div class="wrap split-even">
    <figure class="figure reveal">
      <img src="../assets/img/portrait.webp" alt="{t['portrait_alt']}" width="800" height="1000" loading="lazy">
    </figure>
    <div class="reveal">
      <p class="eyebrow">{t['about_eyebrow']}</p>
      <h2>{t['about_h2']}</h2>
      <div class="muted">{paras(t['about'])}</div>
      <p style="margin-top:28px">{link_arrow(t['about_link'], href(L, 'about'))}</p>
    </div>
  </div>
</section>
{cta_end(L)}"""


def section_body(s):
    """Body of one content section: intro paragraphs, optional lead-in, list, closing note."""
    html = paras(s.get("text", []))
    if s.get("list_intro"):
        html += f'<p style="margin-top:28px"><strong>{s["list_intro"]}</strong></p>'
    if s.get("list"):
        html += bullets(s["list"], cols=s.get("cols", False))
    if s.get("after"):
        html += f'<div style="margin-top:28px">{paras(s["after"])}</div>'
    if s.get("note"):
        html += f'<p class="note" style="margin-top:28px">{s["note"]}</p>'
    return html


def page_st(L):
    t = L["st"]
    out = page_hero(t)
    for s in t["sections"]:
        out += split(s["h2"], section_body(s), s.get("eyebrow"), ident=s.get("id"),
                     cls="section tint" if s.get("tint") else "section")
    return out + split(t["faq_h2"], faq(t["faq"]), t["faq_eyebrow"], ident="fragen") + cta_end(L)


def page_about(L):
    t = L["about"]
    services = "".join(f"<li><b>{b}</b><span>{s}</span></li>" for b, s in t["services"])
    return (f"""<section class="page-hero">
  {motif()}
  <div class="wrap split-even" style="align-items:start">
    <figure class="figure reveal">
      <img src="../assets/img/portrait.webp" alt="{t['portrait_alt']}" width="800" height="1000">
    </figure>
    <div class="reveal">
      <p class="eyebrow">{t['eyebrow']}</p>
      <h1>Burak Arkan</h1>
      <p class="small" style="letter-spacing:.04em;margin-bottom:32px">{t['titles']}</p>
      <div class="muted">{paras(t['intro'])}</div>
    </div>
  </div>
</section>
"""
            + split(t["work_h2"], paras(t["work"]), t["work_eyebrow"])
            + split(t["services_h2"], f'<ul class="list-lines">{services}</ul>', t["services_eyebrow"], cls="section tint")
            + cta_end(L))


def page_contact(L):
    t = L["contact"]
    ui = L["ui"]
    P = PRACTICE
    return (page_hero(t)
            + f"""<section class="section">
  <div class="wrap contact-grid">
    <div class="reveal">
      <ul class="contact-list">
        <li><span class="k">{ui['mobile_label']}</span><span class="v"><a href="tel:{P['phone_href']}">{P['phone']}</a><small>{t['phone_hint']}</small></span></li>
        <li><span class="k">{ui['phone_label']}</span><span class="v"><a href="tel:{P['landline_href']}">{P['landline']}</a></span></li>
        <li><span class="k">{ui['email_label']}</span><span class="v"><a href="mailto:{P['email']}">{P['email']}</a></span></li>
        <li><span class="k">{ui['address_label']}</span><span class="v">{P['street']}<br>{P['zip']} {P['city']}<small><a href="{P['maps']}" target="_blank" rel="noopener">{ui['map_link']} ↗</a></small></span></li>
        <li><span class="k">{ui['hours_label']}</span><span class="v">{t['hours']}</span></li>
      </ul>
    </div>
    <div class="reveal">
      <figure class="figure wide" style="margin:0">
        <img src="../assets/img/praxis.webp" alt="{t['room_alt']}" width="1200" height="800" loading="lazy">
      </figure>
    </div>
  </div>
</section>
""")


def page_legal(L, key):
    t = L[key]
    return f"""<section class="page-hero">
  <div class="wrap">
    <p class="eyebrow">{t['eyebrow']}</p>
    <h1>{t['h1']}</h1>
  </div>
</section>
<section class="section" style="padding-top:0">
  <div class="wrap"><div class="prose">{t['html']}</div></div>
</section>
"""


RENDER = {
    "home": page_home, "st": page_st, "about": page_about,
    "contact": page_contact,
    "imprint": lambda L: page_legal(L, "imprint"),
    "privacy": lambda L: page_legal(L, "privacy"),
}


def root_index():
    return f"""<!doctype html>
<html lang="de">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>Praxis für Soziotherapie – Burak Arkan, Gelsenkirchen</title>
  <meta name="description" content="{esc_attr(LANGS[0]['pages']['home']['desc'])}">
  <link rel="canonical" href="{BASE}/de/">
  <link rel="icon" href="favicon.ico" sizes="any">
  <meta http-equiv="refresh" content="2; url=de/">
  <script>
    (function () {{
      var l = null;
      try {{ l = localStorage.getItem("lang"); }} catch (e) {{}}
      if (!l) {{
        var n = (navigator.languages && navigator.languages[0]) || navigator.language || "de";
        n = n.toLowerCase();
        l = n.indexOf("tr") === 0 ? "tr" : n.indexOf("de") === 0 ? "de" : n.indexOf("en") === 0 ? "en" : "de";
      }}
      if (["de", "tr", "en"].indexOf(l) < 0) l = "de";
      location.replace(l + "/");
    }})();
  </script>
  <style>body{{font:16px/1.6 Georgia,serif;background:#f6f4f1;color:#2b2733;display:grid;place-items:center;min-height:100vh;margin:0}}a{{color:#574d68;margin:0 .6em}}</style>
</head>
<body>
  <p><a href="de/">Deutsch</a> · <a href="tr/">Türkçe</a> · <a href="en/">English</a></p>
</body>
</html>
"""


def main():
    count = 0
    for L in LANGS:
        out_dir = os.path.join(ROOT, L["code"])
        os.makedirs(out_dir, exist_ok=True)
        for key in PAGE_KEYS:
            html = head(L, key) + header(L, key) + RENDER[key](L) + footer(L, key)
            with open(os.path.join(out_dir, L["slugs"][key]), "w", encoding="utf-8", newline="\n") as f:
                f.write(html)
            count += 1
    with open(os.path.join(ROOT, "index.html"), "w", encoding="utf-8", newline="\n") as f:
        f.write(root_index())
    urls = "".join(
        f"  <url><loc>{url(L, k)}</loc></url>\n" for L in LANGS for k in PAGE_KEYS if k not in ("imprint", "privacy") or L["code"] == "de")
    with open(os.path.join(ROOT, "sitemap.xml"), "w", encoding="utf-8", newline="\n") as f:
        f.write(f'<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n{urls}</urlset>\n')
    with open(os.path.join(ROOT, "robots.txt"), "w", encoding="utf-8", newline="\n") as f:
        f.write(f"User-agent: *\nAllow: /\nDisallow: /_build/\n\nSitemap: {BASE}/sitemap.xml\n")
    print(f"built {count} pages")


if __name__ == "__main__":
    main()
