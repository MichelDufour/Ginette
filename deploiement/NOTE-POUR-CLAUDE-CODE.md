## Site Ginette Pantoufle sur ce serveur (à ne pas briser)

Ce serveur héberge aussi le site public **https://ginette.everestinformatique.com** (compte parodique @GinettePantouf). Il n'a rien à voir avec EverestIA, mais il partage le même Caddy.

- **Fichiers** : `/var/www/ginette` (clone du dépôt GitHub `MichelDufour/Ginette`). Site statique : `index.html`, `journal.json`, `images/`.
- **Caddy** : un bloc `ginette.everestinformatique.com { … }` à la fin de `/etc/caddy/Caddyfile`. Copie de la configuration d'avant : `/etc/caddy/Caddyfile.avant-ginette`.
- **Mise à jour** : `/etc/cron.d/ginette` fait `git pull --ff-only` toutes les 10 minutes. Le contenu est poussé dans le dépôt par Claude (claude.ai) quand Michel confirme qu'il a publié un post.
- **DNS** : enregistrement A `ginette` → IP de ce serveur.

Règles pour le projet EverestIA :
- Ne pas supprimer ni modifier le bloc Caddy de ginette, le dossier `/var/www/ginette` ou le cron `/etc/cron.d/ginette`.
- Ne jamais modifier les fichiers de `/var/www/ginette` à la main : ils seraient écrasés par le prochain `git pull`.
- Si tu modifies le Caddyfile pour EverestIA, garde le bloc ginette, puis lance `caddy validate --config /etc/caddy/Caddyfile --adapter caddyfile` avant `systemctl reload caddy`.
