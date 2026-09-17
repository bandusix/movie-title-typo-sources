#!/usr/bin/env python3
"""Check every source in sources.json for a new upstream version.

Large or non-redistributable sources are tracked by HTTP metadata only
(ETag / Last-Modified / Content-Length). Sources with "mirror": true are
downloaded into data/ and versioned by SHA-256.

Writes manifest.json, prepends to CHANGELOG.md and regenerates the status
table in README.md. Standard library only.
"""
import datetime as dt
import email.utils
import hashlib
import json
import pathlib
import sys
import urllib.error
import urllib.request

ROOT = pathlib.Path(__file__).resolve().parent.parent
SOURCES = ROOT / "sources.json"
MANIFEST = ROOT / "manifest.json"
CHANGELOG = ROOT / "CHANGELOG.md"
README = ROOT / "README.md"
DATA = ROOT / "data"
UA = "typo-db-tracker/1.0 (+https://github.com/)"
TIMEOUT = 60
TABLE_START = "<!-- STATUS:START -->"
TABLE_END = "<!-- STATUS:END -->"


def candidate_urls(template, today):
    """Dated URLs (TMDB) may not be published yet today, so fall back up to 2 days."""
    if "{" not in template:
        return [template]
    days = [today - dt.timedelta(days=n) for n in range(3)]
    return [
        template.format(MM=f"{d.month:02d}", DD=f"{d.day:02d}", YYYY=d.year)
        for d in days
    ]


def request(url, method):
    req = urllib.request.Request(url, method=method, headers={"User-Agent": UA})
    return urllib.request.urlopen(req, timeout=TIMEOUT)


def head(url):
    with request(url, "HEAD") as resp:
        h = resp.headers
        return {
            "etag": h.get("ETag"),
            "last_modified": h.get("Last-Modified"),
            "size": int(h["Content-Length"]) if h.get("Content-Length") else None,
        }


def check(source, today, known_url=None):
    last_error = None
    urls = candidate_urls(source["url"], today)
    # Never fall back past the dated file we already recorded, or a transient
    # error on today's file would look like an "update" to yesterday's.
    if known_url in urls:
        urls = urls[: urls.index(known_url) + 1]
    for url in urls:
        try:
            if source.get("mirror"):
                with request(url, "GET") as resp:
                    body = resp.read()
                    last_modified = resp.headers.get("Last-Modified")
                DATA.mkdir(exist_ok=True)
                (DATA / source["filename"]).write_bytes(body)
                return {
                    "resolved_url": url,
                    "sha256": hashlib.sha256(body).hexdigest(),
                    "size": len(body),
                    "last_modified": last_modified,
                }
            return {"resolved_url": url, **head(url)}
        except (urllib.error.URLError, TimeoutError, OSError) as exc:
            last_error = exc
    raise RuntimeError(str(last_error))


def fingerprint(entry, mirror):
    if mirror:
        return entry.get("sha256")
    return (entry.get("resolved_url"), entry.get("etag"), entry.get("last_modified"), entry.get("size"))


def is_older(new, old):
    """True when a stale CDN edge serves a copy older than the one already recorded."""
    try:
        return email.utils.parsedate_to_datetime(new["last_modified"]) < email.utils.parsedate_to_datetime(old["last_modified"])
    except (KeyError, TypeError, ValueError):
        return False


def human_size(n):
    if n is None:
        return "?"
    for unit in ("B", "KB", "MB", "GB"):
        if n < 1024:
            return f"{n:.0f} {unit}" if unit == "B" else f"{n:.1f} {unit}"
        n /= 1024
    return f"{n:.1f} TB"


def render_table(sources, manifest):
    rows = [
        "| Source | Category | Size | Upstream last modified | Last change detected | Mirrored | Download |",
        "|---|---|---|---|---|---|---|",
    ]
    for s in sources:
        e = manifest.get(s["id"], {})
        mirrored = f"[data/{s['filename']}](data/{s['filename']})" if s.get("mirror") else "no"
        rows.append(
            f"| [{s['name']}]({s['homepage']}) | {s['category']} | {human_size(e.get('size'))} "
            f"| {e.get('last_modified') or '?'} | {e.get('changed_at', '?')} | {mirrored} "
            f"| [link]({e.get('resolved_url', s['url'])}) |"
        )
    return "\n".join(rows)


def main():
    now = dt.datetime.now(dt.timezone.utc)
    stamp = now.strftime("%Y-%m-%d")
    sources = json.loads(SOURCES.read_text())
    manifest = json.loads(MANIFEST.read_text()) if MANIFEST.exists() else {}
    changes, errors = [], []

    for s in sources:
        old = manifest.get(s["id"], {})
        try:
            new = check(s, now.date(), old.get("resolved_url"))
        except RuntimeError as exc:
            errors.append(f"{s['id']}: {exc}")
            print(f"ERROR   {s['id']}: {exc}", file=sys.stderr)
            continue
        mirror = bool(s.get("mirror"))
        if is_older(new, old):
            print(f"stale   {s['id']} (edge served an older copy, keeping recorded version)")
            continue
        if fingerprint(old, mirror) != fingerprint(new, mirror):
            new["changed_at"] = stamp
            verb = "added" if not old else "updated"
            changes.append(f"- **{s['id']}** {verb}: {new['resolved_url']} ({human_size(new.get('size'))})")
            print(f"CHANGED {s['id']}")
        else:
            new["changed_at"] = old.get("changed_at", stamp)
            print(f"same    {s['id']}")
        manifest[s["id"]] = new

    MANIFEST.write_text(json.dumps(manifest, indent=2, sort_keys=True) + "\n")

    if changes:
        header = "# Changelog\n\n"
        previous = CHANGELOG.read_text()[len(header):] if CHANGELOG.exists() else ""
        CHANGELOG.write_text(header + f"## {stamp}\n\n" + "\n".join(changes) + "\n\n" + previous)

    readme = README.read_text()
    if TABLE_START in readme and TABLE_END in readme:
        before = readme.split(TABLE_START)[0]
        after = readme.split(TABLE_END)[1]
        README.write_text(f"{before}{TABLE_START}\n{render_table(sources, manifest)}\n{TABLE_END}{after}")

    print(f"\n{len(changes)} changed, {len(errors)} errors")
    # Fail only when every source is unreachable, so one flaky host doesn't block the rest.
    return 1 if errors and len(errors) == len(sources) else 0


if __name__ == "__main__":
    sys.exit(main())
