#!/usr/bin/env python3
"""Mirror sources marked "mirror": "release" as assets of the rolling
GitHub Release `mirror-latest`. These files are too large for git history
(GitHub blocks files over 100 MB), so they live as release assets instead.

An asset is (re)uploaded when check_updates.py reported the source as changed
or when the asset is missing. Files above 1.9 GB are split into .partNN
pieces because a release asset is capped at 2 GB; rejoin with `cat`.

Requires the `gh` CLI and GH_TOKEN. Standard library only.
"""
import json
import os
import pathlib
import subprocess
import sys
import tempfile

ROOT = pathlib.Path(__file__).resolve().parent.parent
TAG = "mirror-latest"
PART_BYTES = 1900 * 1024 * 1024


def gh(*args, check=True):
    return subprocess.run(["gh", *args], check=check, capture_output=True, text=True)


def existing_assets():
    res = gh("release", "view", TAG, "--json", "assets", check=False)
    if res.returncode != 0:
        gh("release", "create", TAG, "--title", "Latest mirrored datasets",
           "--notes", "Rolling mirror of the large upstream files. Assets are overwritten "
                      "whenever upstream changes; see manifest.json for versions. "
                      "Rejoin split files with: cat NAME.part* > NAME")
        return set()
    return {a["name"] for a in json.loads(res.stdout)["assets"]}


def split(path):
    if path.stat().st_size <= PART_BYTES:
        return [path]
    parts = []
    with path.open("rb") as src:
        index = 0
        while chunk := src.read(PART_BYTES):
            part = path.with_name(f"{path.name}.part{index:02d}")
            part.write_bytes(chunk)
            parts.append(part)
            index += 1
    path.unlink()
    return parts


def main():
    sources = json.loads((ROOT / "sources.json").read_text())
    manifest = json.loads((ROOT / "manifest.json").read_text())
    changed_file = os.environ.get("CHANGED_FILE")
    changed = set(pathlib.Path(changed_file).read_text().split()) if changed_file and os.path.exists(changed_file) else set()
    assets = existing_assets()
    failures = 0

    for s in sources:
        if s.get("mirror") != "release":
            continue
        name = s["filename"]
        present = name in assets or f"{name}.part00" in assets
        if present and s["id"] not in changed:
            print(f"keep    {name}")
            continue
        url = manifest[s["id"]]["resolved_url"]
        with tempfile.TemporaryDirectory() as tmp:
            target = pathlib.Path(tmp) / name
            print(f"fetch   {url}")
            dl = subprocess.run(["curl", "-fL", "--retry", "5", "--retry-delay", "10", "-sS",
                                 "-A", "typo-db-tracker/1.0", "-o", str(target), url])
            if dl.returncode != 0:
                print(f"ERROR   download failed: {name}", file=sys.stderr)
                failures += 1
                continue
            files = split(target)
            # Drop old pieces first so a shrinking file leaves no orphan parts behind.
            for old in sorted(a for a in assets if a == name or a.startswith(f"{name}.part")):
                gh("release", "delete-asset", TAG, old, "--yes", check=False)
            for f in files:
                gh("release", "upload", TAG, str(f), "--clobber")
                print(f"upload  {f.name}")
    return 1 if failures else 0


if __name__ == "__main__":
    sys.exit(main())
