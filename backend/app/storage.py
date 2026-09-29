"""Server-side access to Supabase Storage.

Both buckets are private. API routes decide which application users may read
objects; the service role key must never be sent to a browser.
"""
from urllib.parse import quote

import httpx

from app.config import SUPABASE_SERVICE_ROLE_KEY, SUPABASE_URL


class StorageError(RuntimeError):
    pass


def is_configured() -> bool:
    return bool(SUPABASE_URL and SUPABASE_SERVICE_ROLE_KEY)


def _request(method: str, bucket: str, path: str = "", **kwargs) -> httpx.Response:
    if not is_configured():
        raise StorageError("Supabase Storage is not configured")
    safe_bucket = quote(bucket, safe="")
    safe_path = quote(path, safe="/")
    base = f"{SUPABASE_URL.rstrip('/')}/storage/v1/object/{safe_bucket}"
    url = f"{base}/{safe_path}" if path else base
    headers = {
        "apikey": SUPABASE_SERVICE_ROLE_KEY,
        "Authorization": f"Bearer {SUPABASE_SERVICE_ROLE_KEY}",
    }
    headers.update(kwargs.pop("headers", {}))
    try:
        response = httpx.request(method, url, headers=headers, timeout=30, **kwargs)
        response.raise_for_status()
    except httpx.HTTPStatusError as exc:
        if exc.response.status_code == 404:
            raise FileNotFoundError(path) from exc
        raise StorageError(f"Supabase Storage returned HTTP {exc.response.status_code}") from exc
    except httpx.RequestError as exc:
        raise StorageError("Unable to reach Supabase Storage") from exc
    return response


def upload(bucket: str, filename: str, data: bytes, content_type: str) -> None:
    _request(
        "POST", bucket, filename,
        files={"file": (filename, data, content_type)},
        headers={"x-upsert": "false"},
    )


def download(bucket: str, filename: str) -> bytes:
    return _request("GET", bucket, filename).content


def remove(bucket: str, filename: str) -> None:
    if not is_configured():
        raise StorageError("Supabase Storage is not configured")
    # Storage's remove API takes bucket at /object/{bucket} and object paths in JSON.
    _request("DELETE", bucket, json={"prefixes": [filename]})
