#!/usr/bin/env python3
"""Met à jour le site public à partir du journal privé.

Usage : python3 outils/publier.py <journal.json privé> <dossier où sont les images du journal>
Copie seulement les caricatures publiées (sans « statut »: « propose ») et leurs images,
et écrit journal.json à la racine du site. Le carnet privé n'est jamais copié.
"""
import json, shutil, sys, pathlib, unicodedata, re, html

racine = pathlib.Path(__file__).resolve().parent.parent
source_json = pathlib.Path(sys.argv[1])
source_images = pathlib.Path(sys.argv[2])

donnees = json.loads(source_json.read_text(encoding="utf-8"))
champs = ["date", "titre", "image", "genre", "resume", "description", "post", "reponse", "source"]
publiees = []
for e in donnees.get("entrees", []):
    if e.get("statut") == "propose":
        continue
    publiees.append({k: e[k] for k in champs if e.get(k)})

(racine / "images").mkdir(exist_ok=True)
manquantes = []
for e in publiees:
    nom = pathlib.Path(e["image"]).name
    src = source_images / nom
    dst = racine / "images" / nom
    if src.exists():
        if not dst.exists() or dst.stat().st_size != src.stat().st_size:
            shutil.copy2(src, dst)
    elif not dst.exists():
        manquantes.append(nom)

dates = {e["date"] for e in publiees}
jours = {k: v for k, v in (donnees.get("jours") or {}).items() if k in dates}
sortie = {"mis_a_jour": donnees.get("mis_a_jour"), "jours": jours, "entrees": publiees}
(racine / "journal.json").write_text(json.dumps(sortie, ensure_ascii=False, indent=1), encoding="utf-8")
print(f"{len(publiees)} caricatures publiées écrites dans journal.json")
if manquantes:
    print("Images manquantes :", ", ".join(manquantes))

# Une petite page par caricature, pour que Facebook et X montrent l'image et le titre
SITE = "https://ginette.everestinformatique.com/"
def slug(t):
    t = "".join(c for c in unicodedata.normalize("NFD", t) if not ("\u0300" <= c <= "\u036f")).lower()
    return re.sub(r"[^a-z0-9]+", "-", t).strip("-")[:60]
GABARIT = """<!doctype html>
<html lang="fr-CA"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>{titre} · Ginette Pantoufle (parodie)</title>
<meta name="description" content="{desc}">
<link rel="canonical" href="{url}">
<meta property="og:type" content="article">
<meta property="og:locale" content="fr_CA">
<meta property="og:site_name" content="Ginette Pantoufle (parodie)">
<meta property="og:title" content="{titre}">
<meta property="og:description" content="{desc}">
<meta property="og:url" content="{url}">
<meta property="og:image" content="{image}">
<meta property="og:image:alt" content="{titre}, caricature de Ginette Pantoufle">
<meta name="twitter:card" content="summary_large_image">
<meta name="twitter:site" content="@GinettePantouf">
<meta name="twitter:title" content="{titre}">
<meta name="twitter:description" content="{desc}">
<meta name="twitter:image" content="{image}">
<style>body{{margin:0;font-family:system-ui,sans-serif;background:#fff5f8;color:#3a2340;text-align:center;padding:24px 16px}}img{{max-width:100%;height:auto;border-radius:12px}}a{{color:#d23c7c;font-weight:700}}</style>
<script>location.replace({cible});</script>
</head><body>
<h1>{titre}</h1>
<p><img src="{image}" alt="{titre}"></p>
<p>{desc}</p>
<p><a href="{cible_html}">Voir la caricature sur le site de Ginette</a></p>
</body></html>
"""
dossier = racine / "c"
dossier.mkdir(exist_ok=True)
gardes = set()
for e in publiees:
    i = slug(e["date"] + "-" + e["titre"])
    nom = i + ".html"
    gardes.add(nom)
    cible = SITE + "#" + i
    desc = e.get("resume") or e.get("post") or "Caricature du compte parodique @GinettePantouf"
    (dossier / nom).write_text(GABARIT.format(
        titre=html.escape(e["titre"]), desc=html.escape(desc), url=SITE + "c/" + nom,
        image=SITE + "images/" + pathlib.Path(e["image"]).name,
        cible=json.dumps(cible), cible_html=html.escape(cible)), encoding="utf-8")
for f in dossier.glob("*.html"):
    if f.name not in gardes:
        f.unlink()
print(f"{len(gardes)} pages de partage dans c/")
