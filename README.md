# Sauvegardes VPS

Site public minimal présentant une application personnelle de sauvegarde et de restauration de fichiers de VPS vers Google Drive avec rclone et Restic.

## Prérequis

- Python 3 (uniquement pour la prévisualisation locale et les tests)

## Prévisualisation locale

```bash
python3 -m http.server 8000 --bind 127.0.0.1
```

Ouvrir ensuite `http://127.0.0.1:8000/`.

## Tests

```bash
python3 tests.py
```

Le script vérifie la structure HTML, les liens locaux, l’absence de scripts et recherche des motifs de secrets ou d’identifiants sensibles, sans dépendance externe.

## Déploiement

Candidat local préparé pour GitHub Pages. La publication doit être effectuée uniquement après audit indépendant, dans le dépôt public dédié `grums67/sauvegardes-vps-site`.
