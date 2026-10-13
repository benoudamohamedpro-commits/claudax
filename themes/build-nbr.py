"""Construit la variante « structure » noir / blanc / rouge du thème Horizon de Sacoche Vélo France.

1. Couleurs :
- jaune (#fcdc00, #fbcb05) -> rouge #e10600 ; texte posé sur ce rouge -> blanc (contraste 4,97:1)
- texte rouge sur fond noir (bandeau d'annonce, section UGC) -> #ff2d20 (5,65:1 ; #e10600 n'y fait que 4,23:1)
- gris clairs (#f6f6f6, #f8f8f8) -> blanc #ffffff
- gris foncé #252525 -> noir #000000

2. Structure seule : garde le code, la disposition des sections et blocs et leurs réglages de style ;
retire le contenu de Sacoche Vélo France (templates de ses produits et collections, textes, images,
liens, produits et collections choisis, avis, Liquid personnalisé, apps, logos de marques). Les
réglages retirés reprennent leur valeur par défaut d'Horizon. La section « Ils se sont équipés » est
remplacée par la bande damier (nbr/sections/damier.liquid, copié par-dessus le thème).
Les sections de nbr/append/templates/ sont ajoutées à la fin des templates correspondants.

Usage : python3 build-nbr.py horizon-svf horizon-nbr.zip
"""

import json
import re
import shutil
import sys
import tempfile
import zipfile
from pathlib import Path

RED = "#e10600"
RED_ON_BLACK = "#ff2d20"


def sub_once(text, old, new, path):
    if text.count(old) != 1:
        sys.exit(f"{path} : {text.count(old)} occurrence(s) de {old!r}, 1 attendue")
    return text.replace(old, new)


def recolor_json(text):
    text = re.sub(r'("custom_button_text": *)"#252525"', r'\1"#ffffff"', text, flags=re.I)
    text = re.sub(r"#fcdc00\b", RED, text, flags=re.I)
    # Liquid personnalisé : étoiles en SVG, puis textes et bordures de la section UGC (fond sombre).
    text = re.sub(r'((?:fill|stop-color)=\\")#fbcb05\b', rf"\g<1>{RED}", text, flags=re.I)
    text = re.sub(r"(color: *)#fbcb05\b", rf"\g<1>{RED_ON_BLACK}", text, flags=re.I)
    text = re.sub(r"#fbcb05\b", RED, text, flags=re.I)
    text = re.sub(r"#f[68]f[68]f[68]\b", "#ffffff", text, flags=re.I)
    return re.sub(r"#252525\b", "#000000", text, flags=re.I)


def recolor_settings(text):
    text = recolor_json(text)
    for key, value in {
        "badge_sale_background_color": RED,
        "badge_sale_text_color": "#ffffff",
        "badge_sold_out_background_color": "#000000",
        "badge_sold_out_text_color": "#ffffff",
    }.items():
        text, n = re.subn(rf'("{key}": *)"#[0-9a-fA-F]{{6,8}}"', rf'\1"{value}"', text, count=1)
        if n != 1:
            sys.exit(f"settings_data.json : réglage {key} introuvable")
    return text


SCHEME_2_OLD = """  --color-primary-button-background: #fcdc00;
  --color-primary-button-text: #252525;
  --color-primary-button-border: #000000;
  --color-secondary-button-background: #fcdc00;
  --color-secondary-button-text: #000000;
  --color-secondary-button-border: #000000;"""
SCHEME_2_NEW = f"""  --color-primary-button-background: {RED};
  --color-primary-button-text: #ffffff;
  --color-primary-button-border: {RED};
  --color-secondary-button-background: {RED};
  --color-secondary-button-text: #ffffff;
  --color-secondary-button-border: {RED};"""
SCHEME_3_OLD = """.color-scheme-3 {
  --color-background: #fcdc00;
  --color-foreground: #252525;
  --color-foreground-rgb: 37 37 37;
  --color: #252525;"""
SCHEME_3_NEW = f""".color-scheme-3 {{
  --color-background: {RED};
  --color-foreground: #ffffff;
  --color-foreground-rgb: 255 255 255;
  --color: #ffffff;"""
PROMO_OLD = """.announcement-promo strong {
  margin-right: 0.35em;
  color: #fbcb05;"""
PROMO_NEW = f""".announcement-promo strong {{
  margin-right: 0.35em;
  color: {RED_ON_BLACK};"""


def recolor_css(text, path):
    text = sub_once(text, SCHEME_2_OLD, SCHEME_2_NEW, path)
    text = sub_once(text, SCHEME_3_OLD, SCHEME_3_NEW, path)
    text = sub_once(text, PROMO_OLD, PROMO_NEW, path)
    text = re.sub(r"#(fcdc00|fbcb05)\b", RED, text, flags=re.I)
    text = re.sub(r"#f[68]f[68]f[68]\b", "#ffffff", text, flags=re.I)
    text = re.sub(r"--color-foreground-rgb: 37 37 37;", "--color-foreground-rgb: 0 0 0;", text)
    return re.sub(r"#252525\b", "#000000", text, flags=re.I)


CONTENT_TYPES = {
    "richtext", "inline_richtext", "html", "liquid", "textarea", "image_picker", "video", "video_url",
    "product", "collection", "product_list", "collection_list", "page", "blog", "article",
    "metaobject", "metaobject_list",
}
# Champs texte qui portent du contenu : avis, compte à rebours et paliers de livraison de la boutique d'origine.
CONTENT_TEXT_KEYS = {
    "title", "author", "date", "date_end", "timer_ended_text", "step_completed_text",
    "step1_label", "step1_text", "step2_label", "step2_text", "step3_label", "step3_text",
}
SHOP_TEXT = re.compile(r"sacoche|v[ée]lo|porte-bagage|€|\?", re.I)
REMOVED_SECTIONS = {"custom-liquid"}
# La section « Ils se sont équipés » (Liquid personnalisé svf-ugc) laisse place à la bande damier.
UGC_SECTION = "svf-ugc"
DISABLED_SECTIONS = {"reviews"}
# Réglages vidés explicitement, sinon leur valeur par défaut revient (note « Excellent » 5 étoiles sans avis).
BLANKED_SETTINGS = {"announcement-bar": {"rating_label": ""}}
REMOVED_SETTINGS = {"logo", "logo_inverse", "favicon", "promo_end_date"}
REMOVED_ASSETS = re.compile(r"brand-.*\.webp|sacoche-guidon-velo-hover\.png")
# Posture d'agent : pas de « notre » dans les libellés.
AGENT_LABELS = {"Consultez notre aide": "Consultez l'aide", "Contactez notre support": "Contactez le support"}
KEPT_TEMPLATE = re.compile(r"(product|collection)\.json|(?!(product|collection|page\.app-)).*")


def load_json(path):
    return json.loads(re.sub(r"\A\s*(/\*.*?\*/\s*)+", "", path.read_text(), flags=re.S))


def dump_json(path, data):
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n")


class Schemas:
    def __init__(self, root):
        self.root = root
        self.cache = {}

    def get(self, path):
        if path not in self.cache:
            match = path.exists() and re.search(
                r"{%-?\s*schema\s*-?%}(.*?){%-?\s*endschema\s*-?%}", path.read_text(), re.S
            )
            self.cache[path] = json.loads(match.group(1)) if match else {}
        return self.cache[path]

    def section(self, type_):
        return self.get(self.root / "sections" / f"{type_}.liquid")

    def block(self, type_, parent):
        schema = self.get(self.root / "blocks" / f"{type_}.liquid")
        return schema or next((b for b in parent.get("blocks", []) if b.get("type") == type_), {})


def is_content(setting_type, key, value):
    if isinstance(value, str) and "{{" in value:
        return False
    if setting_type in CONTENT_TYPES:
        return True
    if setting_type == "url":
        return value != "shopify://collections/all"
    if setting_type == "link_list":
        return value not in ("main-menu", "footer")
    if setting_type == "text":
        return key in CONTENT_TEXT_KEYS or bool(SHOP_TEXT.search(str(value)))
    return False


def strip_settings(node, schema):
    types = {s["id"]: s["type"] for s in schema.get("settings", []) if "id" in s}
    settings = node.get("settings", {})
    for key in [k for k, v in settings.items() if is_content(types.get(k), k, v)]:
        del settings[key]
    for key, value in settings.items():
        if value in AGENT_LABELS:
            settings[key] = AGENT_LABELS[value]


def strip_blocks(node, parent_schema, schemas):
    blocks = node.get("blocks", {})
    for block_id in [i for i, b in blocks.items() if b["type"].startswith("shopify://")]:
        del blocks[block_id]
    if "block_order" in node:
        node["block_order"] = [i for i in node["block_order"] if i in blocks]
    for block in blocks.values():
        schema = schemas.block(block["type"], parent_schema)
        strip_settings(block, schema)
        strip_blocks(block, schema, schemas)


def strip_page(path, schemas):
    data = load_json(path)
    sections = data["sections"]
    for section_id, section in sections.items():
        if section["type"] == "custom-liquid" and UGC_SECTION in section["settings"].get("custom_liquid", ""):
            sections[section_id] = {"type": "damier", "settings": {}}
    for section_id in [
        i for i, s in sections.items() if s["type"] in REMOVED_SECTIONS or s["type"].startswith("shopify://")
    ]:
        del sections[section_id]
    data["order"] = [i for i in data["order"] if i in sections]
    for section in sections.values():
        if section["type"] in DISABLED_SECTIONS:
            section["disabled"] = True
        schema = schemas.section(section["type"])
        strip_settings(section, schema)
        section.setdefault("settings", {}).update(BLANKED_SETTINGS.get(section["type"], {}))
        strip_blocks(section, schema, schemas)
    dump_json(path, data)


def strip_content(root):
    for path in (root / "templates").glob("*.json"):
        if not KEPT_TEMPLATE.fullmatch(path.name):
            path.unlink()
    for path in (root / "assets").iterdir():
        if REMOVED_ASSETS.fullmatch(path.name):
            path.unlink()

    schemas = Schemas(root)
    for path in list((root / "templates").glob("*.json")) + list((root / "sections").glob("*.json")):
        strip_page(path, schemas)

    settings_path = root / "config" / "settings_data.json"
    settings = load_json(settings_path)
    current = settings["current"]
    for key in REMOVED_SETTINGS:
        current.pop(key, None)
    current.pop("blocks", None)
    dump_json(settings_path, settings)


# Bannière « image entière » : format de l'image mobile, utilisé par nbr-da.css sous 750 px.
HERO_RATIO_OLD = "--svf-hero-ratio: {{ section.settings.image_1.aspect_ratio }};{% endif %}"
HERO_RATIO_NEW = (
    HERO_RATIO_OLD
    + "{% if section.settings.fit_image and section.settings.custom_mobile_media"
    + " and section.settings.image_1_mobile != blank %}"
    + "--svf-hero-ratio-mobile: {{ section.settings.image_1_mobile.aspect_ratio }};{% endif %}"
)

# DA sombre (footer, FAQ) : polices Anton et Archivo, puis nbr/assets/nbr-da.css.
DA_STYLESHEETS = """<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Anton&family=Archivo:wght@800&display=swap">
{{ 'nbr-da.css' | asset_url | stylesheet_tag }}
"""


def append_sections(root, append_dir):
    """Applique nbr/append/{templates,sections}/ : sections ajoutées en fin de page (« sections », « order »)
    et modifications de sections existantes (« update » : settings, blocks, remove_blocks)."""
    for extra_path in list(append_dir.glob("templates/*.json")) + list(append_dir.glob("sections/*.json")):
        path = root / extra_path.relative_to(append_dir)
        data, extra = load_json(path), load_json(extra_path)
        data["sections"].update(extra.get("sections", {}))
        for section_id, change in extra.get("update", {}).items():
            section = data["sections"][section_id]
            section.setdefault("settings", {}).update(change.get("settings", {}))
            for block_id, block_change in change.get("blocks", {}).items():
                section["blocks"][block_id]["settings"].update(block_change["settings"])
            for block_id in change.get("remove_blocks", []):
                del section["blocks"][block_id]
                if "block_order" in section:
                    section["block_order"].remove(block_id)
        # Une section déjà présente citée dans « order » est déplacée à cette position.
        order = extra.get("order", [])
        data["order"] = [i for i in data["order"] if i not in order] + order
        dump_json(path, data)


def main(src, out):
    src = Path(src)
    overlay = Path(__file__).parent / "nbr"
    with tempfile.TemporaryDirectory() as tmp:
        dst = Path(tmp) / "theme"
        shutil.copytree(src, dst)

        for path in list((dst / "templates").glob("*.json")) + list((dst / "sections").glob("*.json")):
            path.write_text(recolor_json(path.read_text()))

        settings = dst / "config" / "settings_data.json"
        settings.write_text(recolor_settings(settings.read_text()))

        css = dst / "assets" / "svf-identique.css"
        css.write_text(recolor_css(css.read_text(), css))

        bar = dst / "sections" / "announcement-bar.liquid"
        bar.write_text(sub_once(bar.read_text(), "#fbcb05 var(--fill)", f"{RED} var(--fill)", bar))

        strip_content(dst)
        shutil.copytree(overlay, dst, dirs_exist_ok=True, ignore=shutil.ignore_patterns("append"))
        append_sections(dst, overlay / "append")

        hero = dst / "sections" / "hero.liquid"
        hero.write_text(sub_once(hero.read_text(), HERO_RATIO_OLD, HERO_RATIO_NEW, hero))

        styles = dst / "snippets" / "stylesheets.liquid"
        styles.write_text(styles.read_text() + DA_STYLESHEETS)

        with zipfile.ZipFile(out, "w", zipfile.ZIP_DEFLATED) as zf:
            for path in sorted(dst.rglob("*")):
                if path.is_file():
                    zf.write(path, path.relative_to(dst).as_posix())


if __name__ == "__main__":
    main(*sys.argv[1:3])
