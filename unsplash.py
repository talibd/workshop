import os
from typing import List, Dict, Optional

try:
    import requests
except ImportError:  # pragma: no cover - requests may not be installed in CI
    requests = None

UNSPLASH_ACCESS_KEY = os.getenv("UNSPLASH_ACCESS_KEY")


def _fetch_image(keyword: str) -> Optional[str]:
    """Fetch a single image URL for the given keyword using the Unsplash API."""
    if not (requests and UNSPLASH_ACCESS_KEY):
        return None

    url = "https://api.unsplash.com/photos/random"
    headers = {"Authorization": f"Client-ID {UNSPLASH_ACCESS_KEY}"}
    params = {"query": keyword, "orientation": "landscape"}
    try:
        resp = requests.get(url, headers=headers, params=params, timeout=5)
    except Exception:
        return None
    if resp.status_code != 200:
        return None
    data = resp.json()
    return data.get("urls", {}).get("regular")


def fetch_images(keywords: List[str]) -> Dict[str, Optional[str]]:
    """Return a mapping of each keyword to a single image URL."""
    images: Dict[str, Optional[str]] = {}
    for kw in keywords:
        images[kw] = _fetch_image(kw)
    return images
