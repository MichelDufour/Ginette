#!/usr/bin/env bash
# Installe le site ginette.everestinformatique.com sur le serveur (Ubuntu + Caddy).
# À lancer une seule fois : sudo bash installer.sh
set -euo pipefail
DOSSIER=/var/www/ginette
DEPOT=https://github.com/MichelDufour/Ginette.git

command -v git >/dev/null || apt-get install -y git
if [ ! -d "$DOSSIER/.git" ]; then
  git clone --depth 1 "$DEPOT" "$DOSSIER"
else
  git -C "$DOSSIER" pull --ff-only
fi

# Mise à jour automatique toutes les 10 minutes
cat > /etc/cron.d/ginette <<CRON
*/10 * * * * root git -C $DOSSIER pull --ff-only --quiet >/dev/null 2>&1
CRON
chmod 644 /etc/cron.d/ginette

# Bloc Caddy (ajouté une seule fois)
CADDYFILE=/etc/caddy/Caddyfile
if ! grep -q "ginette.everestinformatique.com" "$CADDYFILE"; then
  cp "$CADDYFILE" "$CADDYFILE.avant-ginette"
  cat >> "$CADDYFILE" <<CADDY

ginette.everestinformatique.com {
	root * $DOSSIER
	encode zstd gzip
	@prive path /.git* /deploiement/* /outils/* /README.md
	respond @prive 404
	header /journal.json Cache-Control "no-cache"
	header /images/* Cache-Control "public, max-age=604800"
	file_server
}
CADDY
fi
caddy validate --config "$CADDYFILE" --adapter caddyfile
systemctl reload caddy
echo "Terminé : https://ginette.everestinformatique.com"
