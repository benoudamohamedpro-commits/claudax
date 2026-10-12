"""Recolorise la copie du thème Horizon de Sacoche Vélo France en noir, blanc et rouge vif.

Règles :
- jaune (#fcdc00, #fbcb05) -> rouge #e10600 ; texte posé sur ce rouge -> blanc (contraste 4,97:1)
- texte rouge sur fond noir (bandeau d'annonce) -> #ff2d20 (5,65:1 ; #e10600 n'y fait que 4,23:1)
- gris clairs (#f6f6f6, #f8f8f8) -> blanc #ffffff
- gris foncé #252525 -> noir #000000

Usage : python3 recolor-nbr.py horizon-svf horizon-nbr.zip
"""

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


def main(src, out):
    src = Path(src)
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

        with zipfile.ZipFile(out, "w", zipfile.ZIP_DEFLATED) as zf:
            for path in sorted(dst.rglob("*")):
                if path.is_file():
                    zf.write(path, path.relative_to(dst).as_posix())


if __name__ == "__main__":
    main(*sys.argv[1:3])
