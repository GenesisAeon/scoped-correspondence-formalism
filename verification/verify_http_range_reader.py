#!/usr/bin/env python3
"""HTTP range-request file-like object (DOMAIN_EXPANSION_ROADMAP.md Paket B3b).

Runs entirely against a LOCAL HTTP server (spun up on an ephemeral port,
serving a fixed in-memory byte buffer with genuine Range support) -- no
network access to any external host, matching the repo's requirement that
standard tests need neither network access nor credentials. This exercises
REAL HTTP range-request machinery (not a mock of ``HTTPRangeFile`` itself),
just against a local server instead of the real CAMELS-DE archive on Zenodo.

Checks:

  1. Basic read/seek/tell round-trip against the local server matches the
     known reference buffer exactly, for both small (buffered) and
     larger-than-chunk-size reads.
  2. Random-access reads (out-of-order seeks) match the reference buffer.
  3. zipfile.ZipFile can open a real small ZIP served this way and extract
     a member correctly (CRC-checked internally by zipfile) -- the actual
     use case this module exists for.
  4. RangeNotSupportedError is raised (not a silent full-file fallback)
     when the server does not honor Range requests at all.
"""
from __future__ import annotations

import argparse
import datetime as dt
import http.server
import io
import json
import socketserver
import sys
import threading
import zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from scoped_correspondence.data.http_range_reader import HTTPRangeFile, RangeNotSupportedError  # noqa: E402


def require(cond: bool, msg: str) -> None:
    if not cond:
        raise AssertionError(msg)


class _RangeHandler(http.server.BaseHTTPRequestHandler):
    body: bytes = b""

    def log_message(self, *args):  # silence
        pass

    def _serve(self, include_body: bool) -> None:
        range_header = self.headers.get("Range")
        body = type(self).body
        if range_header and range_header.startswith("bytes="):
            spec = range_header[len("bytes="):]
            start_s, _, end_s = spec.partition("-")
            start = int(start_s) if start_s else max(0, len(body) - int(end_s))
            end = int(end_s) if end_s and start_s else len(body) - 1
            end = min(end, len(body) - 1)
            chunk = body[start:end + 1]
            self.send_response(206)
            self.send_header("Content-Range", f"bytes {start}-{end}/{len(body)}")
            self.send_header("Content-Length", str(len(chunk)))
            self.end_headers()
            if include_body:
                self.wfile.write(chunk)
        else:
            self.send_response(200)
            self.send_header("Content-Length", str(len(body)))
            self.end_headers()
            if include_body:
                self.wfile.write(body)

    def do_HEAD(self):
        self._serve(include_body=False)

    def do_GET(self):
        self._serve(include_body=True)


class _NoRangeHandler(http.server.BaseHTTPRequestHandler):
    body: bytes = b""

    def log_message(self, *args):
        pass

    def do_HEAD(self):
        self.send_response(200)
        self.send_header("Content-Length", str(len(type(self).body)))
        self.end_headers()

    def do_GET(self):
        # Deliberately ignores Range and always returns the full body with 200.
        self.send_response(200)
        self.send_header("Content-Length", str(len(type(self).body)))
        self.end_headers()
        self.wfile.write(type(self).body)


def _start_server(handler_cls, body: bytes):
    handler_cls.body = body
    httpd = socketserver.TCPServer(("127.0.0.1", 0), handler_cls)
    port = httpd.server_address[1]
    thread = threading.Thread(target=httpd.serve_forever, daemon=True)
    thread.start()
    return httpd, port


def check_basic_read_seek_tell():
    reference = bytes((i * 37 + 5) % 256 for i in range(500_000))
    httpd, port = _start_server(_RangeHandler, reference)
    try:
        f = HTTPRangeFile(f"http://127.0.0.1:{port}/data.bin", chunk_size=1024)
        require(f.size == len(reference), f"size mismatch: {f.size} vs {len(reference)}")
        require(f.read(10) == reference[:10], "small read mismatch")
        require(f.tell() == 10, f"tell after small read: {f.tell()}")
        f.seek(0)
        big = f.read(300_000)
        require(big == reference[:300_000], "large (multi-chunk) read mismatch")
        f.seek(-100, whence=2)
        tail = f.read(100)
        require(tail == reference[-100:], "tail read via whence=2 mismatch")
    finally:
        httpd.shutdown()
    return {"size": f.size}


def check_random_access():
    reference = bytes((i * 13 + 1) % 256 for i in range(200_000))
    httpd, port = _start_server(_RangeHandler, reference)
    try:
        f = HTTPRangeFile(f"http://127.0.0.1:{port}/data.bin", chunk_size=2048)
        import random
        rng = random.Random(20260924)
        for _ in range(30):
            pos = rng.randint(0, len(reference) - 50)
            n = rng.randint(1, 50)
            f.seek(pos)
            got = f.read(n)
            require(got == reference[pos:pos + n], f"random access mismatch at pos={pos}, n={n}")
    finally:
        httpd.shutdown()
    return {"checked": 30}


def check_zipfile_extraction():
    buf = io.BytesIO()
    with zipfile.ZipFile(buf, "w", zipfile.ZIP_DEFLATED) as zf:
        zf.writestr("a.txt", "hello world " * 1000)
        zf.writestr("dir/b.csv", "col1,col2\n1,2\n3,4\n")
    body = buf.getvalue()

    httpd, port = _start_server(_RangeHandler, body)
    try:
        f = HTTPRangeFile(f"http://127.0.0.1:{port}/archive.zip", chunk_size=256)
        zf = zipfile.ZipFile(f)
        names = zf.namelist()
        require(set(names) == {"a.txt", "dir/b.csv"}, f"got {names}")
        a = zf.read("a.txt").decode()
        require(a == "hello world " * 1000, "a.txt content mismatch")
        b = zf.read("dir/b.csv").decode()
        require(b == "col1,col2\n1,2\n3,4\n", "dir/b.csv content mismatch")
    finally:
        httpd.shutdown()
    return {"members": names}


def check_range_not_supported_raises():
    body = b"x" * 10_000
    httpd, port = _start_server(_NoRangeHandler, body)
    try:
        try:
            HTTPRangeFile(f"http://127.0.0.1:{port}/data.bin")
            raise AssertionError("should raise RangeNotSupportedError when the server ignores Range")
        except RangeNotSupportedError:
            pass
    finally:
        httpd.shutdown()
    return {"checked": 1}


CHECKS = [
    ("basic_read_seek_tell", check_basic_read_seek_tell),
    ("random_access", check_random_access),
    ("zipfile_extraction", check_zipfile_extraction),
    ("range_not_supported_raises", check_range_not_supported_raises),
]


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--json-out", type=Path, default=Path(__file__).with_name("verify_http_range_reader_results.json"))
    args = parser.parse_args()

    report = {
        "package": "DOMAIN_EXPANSION_ROADMAP.md Paket B3b (HTTP range reader, local-server-only CI check)",
        "timestamp": dt.datetime.now().astimezone().isoformat(timespec="seconds"),
        "python": sys.version.split()[0],
        "checks": {},
    }

    all_ok = True
    for name, fn in CHECKS:
        try:
            detail = fn()
            report["checks"][name] = {"status": "pass", "detail": detail}
            print(f"PASS  {name}")
        except AssertionError as e:
            all_ok = False
            report["checks"][name] = {"status": "fail", "error": str(e)}
            print(f"FAIL  {name}: {e}")
        except Exception as e:  # noqa: BLE001
            all_ok = False
            report["checks"][name] = {"status": "error", "error": f"{type(e).__name__}: {e}"}
            print(f"ERROR {name}: {type(e).__name__}: {e}")

    args.json_out.write_text(json.dumps(report, indent=2, default=str), encoding="utf-8")
    print(f"\n{sum(1 for c in report['checks'].values() if c['status'] == 'pass')}/{len(CHECKS)} checks passed")
    print(f"Report written to {args.json_out}")
    return 0 if all_ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
