#!/usr/bin/env python3
"""PRO iURE – úvodná stránka podľa vizuálu klienta (úvodná stránka final 3, mail 19. 10. 2026).

Zdroj obsahu je tu (služby, texty), výstup index.html. Cache busting ?v=<hash> sa dopĺňa sám.
  python3 build.py
"""
import hashlib, re
from pathlib import Path

D = Path(__file__).parent
MAIL = "peter.lacko@proiure.sk"
TEL = "+421948884242"
TEL_TXT = "+421 948 884 242"

def v(p):
    return hashlib.md5((D / p).read_bytes()).hexdigest()[:8]

# ikony (čiarové, 24×24) – ako vo vizuáli
I = {
 "zmluvy": '<path d="M13 3H5v18h8"/><path d="M13 3l5 5v3"/><path d="M13 3v5h5"/><path d="M8 9h3M8 13h6M8 17h3"/><path d="M14.5 21l.8-2.8 5.2-5.2 2 2-5.2 5.2z"/>',
 "analyza": '<circle cx="10" cy="10" r="6.2"/><path d="M14.6 14.6L21 21"/>',
 "konzultacie": '<circle cx="8" cy="7.5" r="2.8"/><circle cx="16.5" cy="7.5" r="2.8"/><path d="M2.5 19.5c0-3.2 2.5-5.5 5.5-5.5s5.5 2.3 5.5 5.5"/><path d="M13.6 14.5c.9-.4 1.9-.5 2.9-.5 3 0 5.5 2.3 5.5 5.5"/>',
 "pohladavky": '<ellipse cx="12" cy="5.8" rx="7" ry="2.6"/><path d="M5 5.8v4.1c0 1.4 3.1 2.6 7 2.6s7-1.2 7-2.6V5.8"/><path d="M5 9.9v4.1c0 1.4 3.1 2.6 7 2.6s7-1.2 7-2.6V9.9"/><path d="M5 14v4.1c0 1.4 3.1 2.6 7 2.6s7-1.2 7-2.6V14"/>',
 "spolocnosti": '<circle cx="12" cy="7" r="2.7"/><circle cx="5.3" cy="9" r="2.1"/><circle cx="18.7" cy="9" r="2.1"/><path d="M7 20.5v-1.8a5 5 0 0 1 10 0v1.8"/><path d="M2 19.5v-.8a3.5 3.5 0 0 1 4.6-3.3"/><path d="M22 19.5v-.8a3.5 3.5 0 0 0-4.6-3.3"/>',
 "zivnostnici": '<circle cx="12" cy="8" r="4"/><path d="M4 21a8 8 0 0 1 16 0z"/>',
 "praca": '<rect x="3" y="7" width="18" height="13" rx="1.6"/><path d="M9 7V5.2C9 4.5 9.5 4 10.2 4h3.6c.7 0 1.2.5 1.2 1.2V7"/><path d="M3 12.5h18"/><path d="M10.5 11.5h3v2.4h-3z"/>',
 "nehnutelnosti": '<path d="M3 11.2L12 4l9 7.2"/><path d="M5.5 9.4V20h13V9.4"/><path d="M10 20v-6h4v6"/>',
 "rodina": '<circle cx="8" cy="7.8" r="3.1"/><circle cx="16.8" cy="9.2" r="2.5"/><path d="M2.5 20.5a5.5 5.5 0 0 1 11 0z"/><path d="M14.3 15.6a4.6 4.6 0 0 1 7.2 3.8v1.1h-6"/>',
 "sud": '<path d="M12 3.5v16.5M8 20.5h8M5 7h14M12 4.5l-7 2.5M12 4.5l7 2.5"/><path d="M5 7l-2.8 6.5h5.6z"/><path d="M19 7l-2.8 6.5h5.6z"/><path d="M2.2 13.5a2.8 2.8 0 0 0 5.6 0M16.2 13.5a2.8 2.8 0 0 0 5.6 0"/>',
 "urady": '<path d="M3 9l9-5 9 5z"/><path d="M5.5 9.5v8M9.8 9.5v8M14.2 9.5v8M18.5 9.5v8"/><path d="M4 18h16M3 20.5h18"/>',
 "ine": '<path d="M4.5 4.5h15a1.5 1.5 0 0 1 1.5 1.5v9a1.5 1.5 0 0 1-1.5 1.5H10l-4.8 3.6V16.5H4.5A1.5 1.5 0 0 1 3 15V6a1.5 1.5 0 0 1 1.5-1.5z"/><circle cx="8.3" cy="10.5" r=".9" class="f"/><circle cx="12" cy="10.5" r=".9" class="f"/><circle cx="15.7" cy="10.5" r=".9" class="f"/>',
}

# služby presne v poradí vizuálu (4 × 3), názvy 2 služieb opravené podľa mailu 19. 10.
S = [
 ("zmluvy", "Zmluvy", "Príprava, kontrola a pripomienkovanie zmlúv",
  "Vypracovanie a posudzovanie obchodnoprávnych a občianskoprávnych zmlúv. Zmluvu pred podpisom skontrolujeme a upozorníme Vás na riziká."),
 ("analyza", "Právna analýza", "Posúdenie právnych otázok a rizík",
  "Posúdime Vašu právnu otázku alebo plánovaný krok a povieme Vám, aké riziká z neho plynú a ako ich obmedziť."),
 ("konzultacie", "Konzultácie", "Telefonicky, online alebo osobne",
  "Konzultáciu si môžete dohodnúť telefonicky, online alebo osobne v kancelárii v Bratislave. Najrýchlejšie nám napíšte, čo potrebujete."),
 ("pohladavky", "Vymáhanie pohľadávok", "Mimosúdne a súdne vymáhanie",
  "Mimosúdne aj súdne vymáhanie pohľadávok, zastupovanie veriteľov vrátane konkurzného konania."),
 ("spolocnosti", "Obchodné spoločnosti", "Založenie, zmeny, zrušenie a likvidácia",
  "Zakladanie obchodných spoločností, zmeny v obchodnom registri, valné zhromaždenia, zbierka listín, splynutie, zlúčenie a rozdelenie, zrušenie a likvidácia."),
 ("zivnostnici", "Živnostníci a SZČO", "Založenie, zmena a zrušenie živností, živnostenský register, transformácia na obchodnú spoločnosť",
  "Založenie, zmena a zrušenie živnosti, zápisy v živnostenskom registri a transformácia podnikania živnostníka na obchodnú spoločnosť."),
 ("praca", "Pracovné právo", "Pracovné zmluvy, spory a poradenstvo",
  "Pracovné zmluvy, skončenie pracovného pomeru a zastupovanie na súdoch v pracovnoprávnych sporoch."),
 ("nehnutelnosti", "Nehnuteľnosti a iný majetok", "Kúpa, predaj, nájom, zmluvy, kataster a ďalšie majetkové záležitosti",
  "Nadobúdanie a prevod nehnuteľností, nájomné a kúpne zmluvy, návrhy na vklad do katastra a ďalšie majetkové záležitosti."),
 ("rodina", "Rodinné právo a dedenie", "Rozvody, vyporiadanie BSM a dedenie",
  "Rozvody, vyporiadanie bezpodielového spoluvlastníctva manželov a dedičské konanie."),
 ("sud", "Zastupovanie na súde", "Príprava žalôb a návrhov, procesná obrana",
  "Príprava žalôb, návrhov a opravných prostriedkov a zastupovanie pred súdmi vo všetkých stupňoch konania."),
 ("urady", "Zastupovanie pred úradmi", "Komunikácia s orgánmi verejnej správy",
  "Zastupovanie v správnom konaní, vypracovanie podaní a návrhov, opravné prostriedky a súdne preskúmanie rozhodnutí."),
 ("ine", "Iný právny problém", "Napíšte nám, radi Vám pomôžeme",
  "Nenašli ste svoju oblasť? Napíšte nám, o čo ide, a povieme Vám, či Vám vieme pomôcť a ako ďalej."),
]

def mailto(subj):
    from urllib.parse import quote
    return f"mailto:{MAIL}?subject={quote(subj)}"

ARROW = '<svg class="ar" viewBox="0 0 24 24" aria-hidden="true"><path d="M4 12h15M13.5 6.5L19 12l-5.5 5.5"/></svg>'
tiles = "\n".join(
    f'<a class="tile" href="#s-{k}" data-open="{k}" aria-controls="s-{k}" aria-expanded="false">'
    f'<svg class="ti" viewBox="0 0 24 24" aria-hidden="true">{I[k]}</svg>'
    f'<span><b>{t}</b><small>{p}</small></span>{ARROW}</a>' for k, t, p, _ in S)
dets = "\n".join(
    f'<article id="s-{k}" class="det" tabindex="-1"><h3>{t}</h3><p>{d}</p>'
    f'<a class="btn" href="{mailto(t)}">Napíšte nám →</a></article>' for k, t, _, d in S)

logo_path = (D / "logo_wordmark.svgpath").read_text().strip()
LOGO = (f'<svg class="lw" viewBox="-2 -4 654 108" aria-hidden="true">{logo_path}</svg>'
        '<span class="ld" aria-hidden="true"></span><span class="lt">Advokátska<br>kancelária</span>')

NAV = [("domov", "Domov"), ("o-mne", "O mne"), ("sluzby", "Právne služby"), ("poradna", "Poradňa"),
       ("aktuality", "Aktuality"), ("kontakt", "Kontakt")]
nav = "".join(f'<a href="#{a}"{" class=\"on\"" if a == "domov" else ""}>{t}</a>' for a, t in NAV)
fnav = '<span aria-hidden="true">|</span>'.join(f'<a href="#{a}">{t}</a>' for a, t in NAV)

MAILI = '<svg viewBox="0 0 24 24" aria-hidden="true"><rect x="2.5" y="5" width="19" height="14" rx="1.2"/><path d="M3 6l9 7 9-7"/></svg>'
TELI = '<svg viewBox="0 0 24 24" aria-hidden="true"><path d="M6.6 3.5l2.6.6 1.2 4.2-2 1.6a12 12 0 0 0 5.7 5.7l1.6-2 4.2 1.2.6 2.6c.2.8-.3 1.6-1.1 1.8C11.5 21 3 12.5 4.8 4.6c.2-.8 1-1.3 1.8-1.1z"/></svg>'

html = f'''<!DOCTYPE html>
<html lang="sk"><head>
<meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<meta name="robots" content="noindex,nofollow">
<title>PRO iURE – advokátska kancelária, Bratislava</title>
<meta name="description" content="Advokátska kancelária PRO iURE, JUDr. Peter Lacko, Bratislava. Zmluvy, spoločnosti, nehnuteľnosti, pracovné právo, pohľadávky a zastupovanie, slovensky aj nemecky.">
<meta property="og:title" content="PRO iURE – advokátska kancelária, Bratislava">
<meta property="og:description" content="Priamou cestou k ochrane Vašich práv a záujmov.">
<meta property="og:image" content="https://webhunter-navrhy.github.io/sk-proiure/img/og.jpg">
<script type="application/ld+json">{{"@context":"https://schema.org","@type":"LegalService","name":"PRO iURE – advokátska kancelária, s.r.o.","founder":{{"@type":"Person","name":"JUDr. Peter Lacko"}},"email":"{MAIL}","telephone":"{TEL}","knowsLanguage":["sk","de"],"address":{{"@type":"PostalAddress","streetAddress":"Zámocká 32","postalCode":"811 01","addressLocality":"Bratislava","addressCountry":"SK"}}}}</script>
<link rel="preconnect" href="https://fonts.googleapis.com"><link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Red+Hat+Display:wght@400;500;600;700&display=swap" rel="stylesheet">
<link rel="preload" as="image" href="img/hero-lab.webp?v={v("img/hero-lab.webp")}" media="(min-width:821px)">
<link rel="stylesheet" href="style.css?v={v("style.css")}">
</head><body>
<header class="top">
<a class="logo" href="#domov" aria-label="PRO iURE – advokátska kancelária">{LOGO}</a>
<button class="burger" type="button" aria-label="Menu" aria-expanded="false" aria-controls="menu"><span></span></button>
<nav aria-label="Hlavné menu" id="menu">{nav}</nav>
</header>
<main id="domov">
<section class="hero">
<picture class="hero-i"><source media="(max-width:820px)" srcset="img/hero-lab-m.webp?v={v("img/hero-lab-m.webp")}"><img src="img/hero-lab.webp?v={v("img/hero-lab.webp")}" width="1600" height="924" alt="Advokát s aktovkou kráča priamou cestou cez labyrint paragrafov k jemnej siluete justície s váhami"></picture>
<div class="hero-t">
<h1>Priamou cestou k ochrane <span>Vašich práv a záujmov.</span></h1>
<p class="lead">Napíšte nám, čo potrebujete, a my Vám poradíme, ako to dosiahnuť, pri minimalizácii právnych rizík.</p>
<p class="cta"><a class="btn" href="#kontakt">Dohodnite si konzultáciu <span aria-hidden="true">→</span></a><a class="ic" href="mailto:{MAIL}" aria-label="Napísať e-mail" title="{MAIL}">{MAILI}</a><a class="ic" href="tel:{TEL}" aria-label="Zavolať" title="{TEL_TXT}">{TELI}</a></p>
</div>
</section>

<section id="sluzby" class="sec">
<h2>Akú právnu službu potrebujete?</h2>
<p class="sub">Vyberte si oblasť, ktorá najlepšie vystihuje Váš právny problém. Alebo nám rovno napíšte alebo zavolajte.</p>
<div class="tiles">
{tiles}
</div>
<div class="dets" id="detaily">
{dets}
</div>
</section>

<section id="o-mne" class="sec omne">
<div class="o-grid">
<figure class="o-foto"><div class="o-ph"><span>Miesto pre fotografiu</span></div></figure>
<div class="o-t">
<h2>O mne</h2>
<p class="o-name">JUDr. Peter Lacko</p><p class="o-role">advokát</p>
<p>Mám bohaté skúsenosti v oblastiach obchodného a občianskeho práva, najmä v zmluvnom práve a v práve nehnuteľností.</p>
<p>Študoval som na Právnickej fakulte UPJŠ v Košiciach a na Právnickej fakulte Univerzity v Regensburgu. Pred založením advokátskej kancelárie PRO iURE som bol advokátskym koncipientom v advokátskej kancelárii Blaha, Erben a partneri. Právne služby poskytujem v slovenskom a nemeckom jazyku.</p>
<ul class="hod">
<li><b>Individuálny prístup</b>Každý právny prípad je vo svojej podstate jedinečný a každý klient si zaslúži zodpovedajúci individuálny prístup.</li>
<li><b>Profesionalita</b>Klient môže byť spokojný iba s profesionálnym prístupom a s nadštandardnou úrovňou znalostí.</li>
<li><b>Dôvera</b>Dôveryhodnosť je prienikom charakteru a odbornosti, preto budujeme oboje.</li>
</ul>
</div>
</div>
</section>

<section id="poradna" class="sec pk">
<div class="pk-grid">
<div><h2>Poradňa</h2><p>Máte právnu otázku a neviete, či je to vec pre advokáta? Napíšte nám ju vlastnými slovami. Odpovieme Vám e-mailom a povieme, aký je najvhodnejší ďalší krok.</p><p><a class="btn" href="{mailto("Otázka do poradne")}">Položiť otázku →</a></p></div>
<div id="aktuality"><h2>Aktuality</h2><p>Novinky z legislatívy a praktické rady tu pribudnú postupne.</p></div>
</div>
</section>

<section id="kontakt" class="sec pk">
<div class="pk-grid">
<div><h2>Kontakt</h2><address><strong>PRO iURE – advokátska kancelária, s.r.o.</strong><br>Zámocká 32<br>811 01 Bratislava</address></div>
<div><dl class="kd"><div><dt>E-mail</dt><dd><a href="mailto:{MAIL}">{MAIL}</a></dd></div><div><dt>Telefón</dt><dd><a href="tel:{TEL}">{TEL_TXT}</a></dd></div><div><dt>Jazyky</dt><dd>slovenčina, nemčina</dd></div></dl>
<p><a class="btn" href="{mailto("Konzultácia")}">Dohodnite si konzultáciu →</a></p></div>
</div>
</section>
</main>
<footer>
<div class="f-in">
<a class="logo flogo" href="#domov" aria-label="PRO iURE – advokátska kancelária">{LOGO}</a>
<nav class="fnav" aria-label="Pätička">{fnav}</nav>
<p class="fmesto">Bratislava<br>Slovensko</p>
</div>
<p class="wh">© PRO iURE – advokátska kancelária, s.r.o. · Náhľad pripravil WebHunter s.r.o. · <button type="button" id="logo-farba">Logo: prepnúť na červené</button></p>
</footer>
<script src="app.js?v={v("app.js")}"></script>
</body></html>
'''
(D / "index.html").write_text(html)
print("index.html", len(html))
