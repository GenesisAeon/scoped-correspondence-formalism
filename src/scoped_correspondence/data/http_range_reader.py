"""Minimal buffered HTTP range-request file-like object for selective ZIP access (DOMAIN_EXPANSION_ROADMAP.md Paket B3b).

Response to prompts/Answers/nicht_stationäre_Treiber/SCF_Review_fcc9a43.md,
finding R7: the earlier assessment that the CAMELS-DE data pilot was
blocked (the archive is a single ~2.18GB Zenodo file with no per-catchment
download) was WRONG -- Astra independently demonstrated that the archive's
HTTP server honors byte-range requests (HTTP 206, exact `Content-Range`),
letting `zipfile.ZipFile` read the central directory and extract individual
members without downloading the whole archive.

``HTTPRangeFile`` is a small buffered file-like object (``read``/``seek``/
``tell``) backed by HTTP Range GET requests, suitable as the ``file``
argument to ``zipfile.ZipFile`` (which needs a real seekable object to
locate the end-of-central-directory record and per-member local headers --
handing it only a byte-range SLICE of the archive would NOT work, since the
central directory's ``header_offset`` fields are absolute positions in the
FULL original file). Requests smaller than ``chunk_size`` are served from an
internal read-ahead buffer to avoid one HTTP round trip per small read
(``zipfile`` does many small reads while parsing headers).

**Explicit safety check (plan's own instruction for this exact situation):**
if the server does not actually honor a Range request (returns ``200`` with
the full body instead of ``206`` with an exact ``Content-Range``), this
raises immediately rather than silently falling back to downloading the
entire file.
"""

from __future__ import annotations

import urllib.error
import urllib.request


class RangeNotSupportedError(RuntimeError):
    """Raised when the server does not honor HTTP Range requests as expected."""


class HTTPRangeFile:
    def __init__(self, url: str, chunk_size: int = 1 << 18, timeout: float = 60.0):
        self.url = url
        self.chunk_size = chunk_size
        self.timeout = timeout
        self._pos = 0
        self.size = self._get_size()
        self._buf_start = -1
        self._buf = b""
        self._verify_range_support()

    def _get_size(self) -> int:
        req = urllib.request.Request(self.url, method="HEAD")
        with urllib.request.urlopen(req, timeout=self.timeout) as resp:
            return int(resp.headers["Content-Length"])

    def _verify_range_support(self) -> None:
        req = urllib.request.Request(self.url, headers={"Range": "bytes=0-15"})
        try:
            with urllib.request.urlopen(req, timeout=self.timeout) as resp:
                status, content_range, body = resp.status, resp.headers.get("Content-Range"), resp.read()
        except urllib.error.HTTPError as e:
            if e.code != 206:
                raise
            status, content_range, body = 206, e.headers.get("Content-Range"), e.read()
        if status != 206 or not content_range:
            raise RangeNotSupportedError(
                f"server did not honor a Range request (status={status}, "
                f"Content-Range={content_range!r}) -- aborting rather than silently "
                f"falling back to downloading the entire file"
            )
        if len(body) != 16:
            raise RangeNotSupportedError(f"expected exactly 16 bytes for 'bytes=0-15'; got {len(body)}")

    def _fetch_range(self, start: int, end: int) -> bytes:
        req = urllib.request.Request(self.url, headers={"Range": f"bytes={start}-{end}"})
        try:
            with urllib.request.urlopen(req, timeout=self.timeout) as resp:
                if resp.status != 206:
                    raise RangeNotSupportedError(f"expected HTTP 206 for a range fetch; got {resp.status}")
                return resp.read()
        except urllib.error.HTTPError as e:
            if e.code == 206:
                return e.read()
            raise

    def seek(self, offset: int, whence: int = 0) -> int:
        if whence == 0:
            self._pos = offset
        elif whence == 1:
            self._pos += offset
        elif whence == 2:
            self._pos = self.size + offset
        else:
            raise ValueError(f"invalid whence: {whence!r}")
        return self._pos

    def tell(self) -> int:
        return self._pos

    def seekable(self) -> bool:
        return True

    def readable(self) -> bool:
        return True

    def writable(self) -> bool:
        return False

    def read(self, n: int = -1) -> bytes:
        if n is None or n < 0:
            data = self._fetch_range(self._pos, self.size - 1)
            self._pos += len(data)
            return data
        if n == 0:
            return b""
        end_needed = self._pos + n - 1
        if self._buf_start != -1 and self._buf_start <= self._pos and end_needed < self._buf_start + len(self._buf):
            off = self._pos - self._buf_start
            data = self._buf[off:off + n]
            self._pos += len(data)
            return data
        fetch_len = max(n, self.chunk_size)
        start = self._pos
        end = min(start + fetch_len - 1, self.size - 1)
        if start > end:
            return b""
        data_all = self._fetch_range(start, end)
        self._buf_start = start
        self._buf = data_all
        out = data_all[:n]
        self._pos += len(out)
        return out

    def close(self) -> None:
        pass


__all__ = ["HTTPRangeFile", "RangeNotSupportedError"]
