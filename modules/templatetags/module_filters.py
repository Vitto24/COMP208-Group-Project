import hashlib
from django import template

register = template.Library()

# acronyms and short forms that should stay as-is when title-casing module names
KEEP_AS_IS = {
    "AI", "HCI", "UX", "UI", "IT", "IoT", "ML", "NLP",
    "BSc", "BA", "BEng", "MSc", "MA", "MEng", "PhD",
    "UK", "USA", "EU", "US", "UN",
    "3D", "2D", "CAD", "GIS", "GIS", "GPS",
    "TV", "DJ",
}


@register.filter(name="smart_title")
def smart_title(value):
    if not value:
        return value
    words = str(value).split()
    out = []
    for w in words:
        upper = w.upper()
        # keep short functional words lowercase unless at the start
        if out and w.lower() in {"and", "of", "the", "in", "for", "to", "a", "an", "as", "at", "by", "or", "on"}:
            out.append(w.lower())
            continue
        # preserve known acronyms / short forms
        if upper in {k.upper() for k in KEEP_AS_IS}:
            for k in KEEP_AS_IS:
                if k.upper() == upper:
                    out.append(k)
                    break
            continue
        out.append(w.capitalize())
    return " ".join(out)


MODULE_ICONS = ["📘", "📗", "📕", "📙", "📒", "📓"]


@register.filter(name="module_icon")
def module_icon(code):
    # stable per-module icon so COMP208 always looks the same, no clashing across pages
    if not code:
        return MODULE_ICONS[0]
    digest = hashlib.md5(str(code).encode('utf-8')).digest()
    return MODULE_ICONS[digest[0] % len(MODULE_ICONS)]
