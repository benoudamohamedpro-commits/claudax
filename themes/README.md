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
