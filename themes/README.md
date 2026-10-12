# Thème Horizon — Sacoche Vélo France

Copie exacte du thème en ligne de **Sacoche Vélo France** (`Zoom mobile 100% - 2026-10-10`,
Horizon 4.2.0, 596 fichiers), extraite le 2026-10-12 via l'Admin API. Les images de la
médiathèque (`shopify://shop_images/...`) ne sont **pas** incluses : seule la structure du thème.

- `horizon-svf/` : fichiers du thème (assets, blocks, config, layout, locales, sections, snippets, templates)
- `horizon-svf.zip` : même contenu, prêt à importer

## Importer sur une autre boutique

- Admin Shopify → Boutique en ligne → Thèmes → Ajouter un thème → Importer un fichier zip → `horizon-svf.zip`
- Ou via l'API : `stagedUploadsCreate` (resource `FILE`, mimeType `application/zip`), upload du ZIP,
  puis `themeCreate(source: resourceUrl, name: "Horizon - Sacoche Vélo France")`.

La publication du thème se fait à la main dans l'admin.

## Variante noir / blanc / rouge (boutique cd70bx-gg)

`horizon-nbr.zip` est généré depuis `horizon-svf/` par `recolor-nbr.py` (`python3 recolor-nbr.py horizon-svf horizon-nbr.zip`).
Importé sur cd70bx-gg le 2026-10-12 sous le nom « Horizon - Noir Blanc Rouge » (non publié).

- jaune `#fcdc00` / `#fbcb05` → rouge `#e10600` ; texte posé sur ce rouge → blanc (contraste 4,97:1, WCAG AA)
- texte et bordures rouges sur fond noir (bandeau d'annonce, section UGC) → `#ff2d20` (5,65:1 ; `#e10600` n'y fait que 4,23:1)
- gris clairs `#f6f6f6` / `#f8f8f8` → blanc ; gris foncé `#252525` → noir
- badge promo : fond rouge, texte blanc ; badge épuisé : fond noir, texte blanc
- conservé : boutons principaux noirs, fonds gris des vignettes d'avis sans photo (`snippets/svf-review.liquid`)
