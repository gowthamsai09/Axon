"""Regenerates corpus/ssrf/urls.json: URLs every fetching guard must block or allow (spec 10.1).

  python scripts/make_ssrf_corpus.py [--out corpus/ssrf]

Each case: id, url, expect ("blocked" | "allowed"), category and `dns` (host -> addresses) that a test
resolver or a patched getaddrinfo answers with. Numeric-looking hosts map to a PUBLIC address on purpose:
they must be refused whatever DNS says. Consumed by axon-template (digest/safe_http.py) and axon-feed
(collectors/http.py). The gateway never fetches a caller-supplied URL and tests its config rules itself."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

PUBLIC = "93.184.216.34"
CASES: list[dict[str, Any]] = []


def add(cid: str, url: str, expect: str, category: str, dns: dict[str, list[str]] | None = None) -> None:
    CASES.append({"id": cid, "url": url, "expect": expect, "category": category, "dns": dns or {}})


def allowed(cid: str, url: str, dns: dict[str, list[str]] | None = None) -> None:
    add(cid, url, "allowed", "allowed", dns)


def blocked(category: str, cid: str, url: str, dns: dict[str, list[str]] | None = None) -> None:
    add(cid, url, "blocked", category, dns)


allowed("allow-domain", "https://example.com/", {"example.com": [PUBLIC]})
allowed("allow-port", "http://example.com:8080/feed", {"example.com": [PUBLIC]})
allowed("allow-highest-port", "http://example.com:65535/", {"example.com": [PUBLIC]})
allowed("allow-uppercase-host", "https://EXAMPLE.com/", {"example.com": [PUBLIC]})
allowed("allow-uppercase-scheme", "HTTP://EXAMPLE.COM/", {"example.com": [PUBLIC]})
allowed("allow-trailing-dot", "https://example.com./", {"example.com": [PUBLIC]})
allowed("allow-query-fragment", "https://sub.example.com/a?b=c#d", {"sub.example.com": [PUBLIC]})
allowed("allow-public-ipv4", "http://8.8.8.8/")
allowed("allow-public-ipv6", "https://[2606:4700:4700::1111]/")
allowed("allow-idn", "https://münchen.de/", {"münchen.de": [PUBLIC]})
allowed("allow-two-public-answers", "https://multi.example/", {"multi.example": [PUBLIC, "2606:4700:4700::1111"]})

for cid, url in [
    ("ftp", "ftp://example.com/"), ("file", "file:///etc/passwd"), ("gopher", "gopher://example.com/"),
    ("javascript", "javascript:alert(1)"), ("data", "data:text/plain,x"), ("ws", "ws://example.com/"),
    ("scheme-relative", "//example.com/x"), ("no-scheme", "example.com/x"), ("empty", ""),
    ("no-host", "http:///nohost"), ("bare-scheme", "http://"), ("bad-ipv6-bracket", "http://[::1/"),
]:  # fmt: skip
    blocked("scheme", f"scheme-{cid}", url, {"example.com": [PUBLIC]})

for cid, url in [
    ("loopback", "http://127.0.0.1/"), ("loopback-port", "http://127.0.0.1:8080/x"),
    ("loopback-high", "http://127.255.255.254/"), ("ten-low", "http://10.0.0.1/"),
    ("ten-high", "http://10.255.255.255/"), ("172-16", "http://172.16.0.1/"),
    ("172-31", "http://172.31.255.255/"), ("192-168", "http://192.168.1.1/"),
    ("metadata", "http://169.254.169.254/latest/meta-data"), ("link-local", "http://169.254.0.1/"),
    ("cgnat", "http://100.64.0.1/"), ("unspecified", "http://0.0.0.0/"),
    ("broadcast", "http://255.255.255.255/"), ("multicast", "http://224.0.0.1/"),
    ("test-net-1", "http://192.0.2.1/"), ("benchmark", "http://198.18.0.1/"),
    ("test-net-2", "http://198.51.100.1/"), ("test-net-3", "http://203.0.113.1/"),
]:  # fmt: skip
    blocked("ipv4", f"ipv4-{cid}", url)

for cid, url in [
    ("loopback", "http://[::1]/"), ("unspecified", "http://[::]/"), ("link-local", "http://[fe80::1]/"),
    ("zone-id", "http://[fe80::1%25eth0]/"), ("ula-fd", "http://[fd00::1]/"), ("ula-fc", "http://[fc00::1]/"),
    ("mapped-loopback", "http://[::ffff:127.0.0.1]/"), ("mapped-private", "http://[::ffff:10.0.0.1]/"),
    ("mapped-metadata", "http://[::ffff:169.254.169.254]/"), ("mapped-hex", "http://[::ffff:7f00:1]/"),
    ("multicast", "http://[ff02::1]/"),
]:  # fmt: skip
    blocked("ipv6", f"ipv6-{cid}", url)

for cid, url in [
    ("decimal", "http://2130706433/"), ("hex", "http://0x7f000001/"), ("hex-dotted", "http://0x7f.0.0.1/"),
    ("octal", "http://017700000001/"), ("octal-dotted", "http://0177.0.0.1/"), ("short-127-1", "http://127.1/"),
    ("short-127-0-1", "http://127.0.1/"), ("zero", "http://0/"), ("decimal-192-168", "http://3232235777/"),
    ("mixed-metadata", "http://169.254.43518/"), ("hex-metadata", "http://0xa9fea9fe/"),
    ("trailing-dot", "http://127.0.0.1./"), ("fullwidth-digits", "http://１２７.０.０.１/"),
    ("percent-encoded", "http://%31%32%37.0.0.1/"),
]:  # fmt: skip
    host = url.split("//", 1)[1].split("/", 1)[0]
    blocked("numeric-host", f"numeric-{cid}", url, {host.rstrip(".").lower(): [PUBLIC]})

blocked("host-syntax", "host-with-space", "http://exa mple.com/", {"exa mple.com": [PUBLIC]})

for cid, url in [
    ("user-pass", "http://user:pass@example.com/"), ("user-only", "http://user@example.com/"),
    ("host-as-user", "http://example.com@127.0.0.1/"), ("ip-as-user", "http://127.0.0.1@example.com/"),
    ("empty-userinfo", "http://:@example.com/"), ("encoded-at", "http://example.com%40127.0.0.1/"),
    ("backslash-at", "http://example.com\\@127.0.0.1/"),
]:  # fmt: skip
    blocked("userinfo", f"userinfo-{cid}", url, {"example.com": [PUBLIC], "example.com%40127.0.0.1": [PUBLIC]})

for cid, url in [
    ("too-high", "http://example.com:99999/"), ("letters", "http://example.com:abc/"),
    ("negative", "http://example.com:-1/"), ("65536", "http://example.com:65536/"),
]:  # fmt: skip
    blocked("port", f"port-{cid}", url, {"example.com": [PUBLIC]})

dns_private: dict[str, list[str]] = {
    "localhost": ["127.0.0.1"], "foo.localhost": ["127.0.0.1"], "metadata.google.internal": ["169.254.169.254"],
    "internal.example": ["10.1.2.3"], "rebind.example": [PUBLIC, "10.0.0.5"], "v6.example": ["::1"],
    "mapped.example": ["::ffff:10.0.0.1"], "ula.example": ["fd00::5"],
}  # fmt: skip
for cid, url in [
    ("localhost", "http://localhost/"), ("localhost-dot", "http://localhost./"), ("localhost-upper", "http://LOCALHOST/"),
    ("localhost-subdomain", "http://foo.localhost/"), ("metadata-name", "http://metadata.google.internal/"),
    ("private-answer", "http://internal.example/"), ("mixed-answers", "http://rebind.example/"),
    ("ipv6-loopback-answer", "http://v6.example/"), ("mapped-answer", "http://mapped.example/"),
    ("ula-answer", "http://ula.example/"),
]:  # fmt: skip
    blocked("dns", f"dns-{cid}", url, dns_private)


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--out", type=Path, default=Path("corpus/ssrf"))
    args = ap.parse_args(argv)
    args.out.mkdir(parents=True, exist_ok=True)
    text = json.dumps(CASES, indent=1, sort_keys=True, ensure_ascii=True) + "\n"
    (args.out / "urls.json").write_text(text, encoding="utf-8", newline="\n")
    print(f"wrote {len(CASES)} cases to {args.out / 'urls.json'}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
