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

## Variante « structure » noir / blanc / rouge (boutique cd70bx-gg)

`horizon-nbr.zip` est généré depuis `horizon-svf/` par `build-nbr.py` (`python3 build-nbr.py horizon-svf horizon-nbr.zip`).
Importé sur cd70bx-gg le 2026-10-12 sous le nom « Horizon - Structure Noir Blanc Rouge » (non publié).

Structure seule : code, disposition des sections et blocs de chaque page, réglages de style. Retiré :
- les templates des produits et collections de Sacoche Vélo France (`product.*`, `collection.*`) et des apps (`page.app-*`)
- textes, images, vidéos, liens, produits et collections choisis, menus autres que `main-menu` / `footer`
- avis (section désactivée), sections Liquid personnalisé, blocs d'apps, logo, favicon, logos de marques vélo
Les réglages retirés reprennent leur valeur par défaut d'Horizon.

Ajout : section « Bande damier » (`nbr/sections/damier.liquid`, damier noir et blanc en CSS, sans image),
à la place de la section « Ils se sont équipés » sur l'accueil et la fiche produit. Réglable dans l'éditeur :
couleurs, taille des cases (66 px ordinateur, 40 px mobile par défaut), nombre de rangées (2).

Ajout : en bas de l'accueil, section « Entretenez et réparez en toute autonomie. » (image à gauche,
texte à droite, fond `#ebebeb`, largeur 1400 px), suivie de la section FAQ, décrite dans `nbr/append/templates/index.json`. Image : fichier
Shopify `magasin-modelisme-voitures-rc-v2.webp` (1024×644, bandes blanches retirées, luminosité −15 %) envoyé sur cd70bx-gg.

Couleurs :
- jaune `#fcdc00` / `#fbcb05` → rouge `#e10600` ; texte posé sur ce rouge → blanc (contraste 4,97:1, WCAG AA)
- texte et bordures rouges sur fond noir (bandeau d'annonce) → `#ff2d20` (5,65:1 ; `#e10600` n'y fait que 4,23:1)
- gris clairs `#f6f6f6` / `#f8f8f8` → blanc ; gris foncé `#252525` → noir
- badge promo : fond rouge, texte blanc ; badge épuisé : fond noir, texte blanc ; boutons principaux noirs

DA sombre (`nbr/assets/nbr-da.css`, chargée avec les polices Google Anton et Archivo 800 depuis
`snippets/stylesheets.liquid`) : fond `#0a0a0a` à carreaux de 48 px, lueur rouge en haut à droite.
Appliquée au footer (titres condensés italiques, liens en gras, newsletter sombre, bouton rouge) et à
la section FAQ de l'accueil (classe `nbr-dark` : étiquette « FAQ », titre souligné, 8 questions numérotées).
Les réponses de la FAQ sont à rédiger.

Bannière du haut de l'accueil (`image_banner_VXNP89`, réglages modifiés via la clé `update` de
`nbr/append/templates/index.json`) : image `banniere-voitures-drift.webp` (1935×812) à la place de la vidéo, option « Image entière » activée (aucun rognage).
Mobile (moins de 750 px) : image verticale `banniere-voitures-drift-mobile.webp` (825×1024), affichée entière ;
`build-nbr.py` ajoute `--svf-hero-ratio-mobile` dans `sections/hero.liquid` pour que la hauteur suive son format.
FAQ intégrée au footer (première section du groupe footer, visible sur toutes les pages) : un seul bloc (quadrillage calé sur la fenêtre, une seule lueur en haut de la FAQ). Footer modifié
via `nbr/append/sections/footer-group.json` : bloc logo « My Store » géant retiré, logos de paiement 44 px.
