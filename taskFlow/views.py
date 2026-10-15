"""Serwowanie zbudowanej aplikacji React (SPA)."""

import json

from django.conf import settings
from django.shortcuts import render
from django.views.decorators.csrf import ensure_csrf_cookie

MANIFEST_RELATIVE_PATH = "spa/.vite/manifest.json"

def _load_assets():

    manifest_path = settings.BASE_DIR / "static" / MANIFEST_RELATIVE_PATH
    try:
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return [], []

    base = settings.STATIC_URL + "spa/"

    def chunk_files(name, seen=None):
        seen = seen if seen is not None else set()
        if name in seen:
            return [], []
        seen.add(name)
        chunk = manifest.get(name, {})
        files = [base + chunk["file"]] if "file" in chunk else []
        styles = [base + css for css in chunk.get("css", [])]
        for import_name in chunk.get("imports", []):
            import_files, import_styles = chunk_files(import_name, seen)
            files = import_files + files
            styles = import_styles + styles
        return files, styles

    scripts, styles = [], []
    for name, chunk in manifest.items():
        if chunk.get("isEntry"):
            chunk_scripts, chunk_styles = chunk_files(name)
            scripts.extend(chunk_scripts)
            styles.extend(chunk_styles)
    return scripts, styles

@ensure_csrf_cookie
def spa(request):
    scripts, styles = _load_assets()
    if not scripts:
        return render(request, "spa_not_built.html", status=503)
    return render(
        request,
        "spa.html",
        {"spa_scripts": scripts, "spa_styles": styles},
    )
