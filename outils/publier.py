#!/usr/bin/env python3
"""Met à jour le site public à partir du journal privé.

Usage : python3 outils/publier.py <journal.json privé> <dossier où sont les images du journal>
Copie seulement les caricatures publiées (sans « statut »: « propose ») et leurs images,
et écrit journal.json à la racine du site. Le carnet privé n'est jamais copié.
"""
import json, shutil, sys, pathlib

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
