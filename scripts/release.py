"""Build, check, package and publish a release.

    .venv/bin/python scripts/release.py              build, verify, zip into build/dist
    .venv/bin/python scripts/release.py --publish    the same, then tag and create
                                                     the GitHub release (needs gh)
    .venv/bin/python scripts/release.py --no-build   zip what is already built

The release version is the file VERSION.  It must match the versions in
design-system.json and symbols/symbol-system.json and have a section in
CHANGELOG.md.  --publish also requires a clean, pushed main branch, so the tag
names exactly the sources and binaries that were built.

Zip entries are sorted and carry a fixed time stamp: the same files give the
same zip.
"""

from __future__ import annotations

import argparse
import hashlib
import re
import subprocess
import sys
import time
import zipfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from build import SOURCE_DATE_EPOCH  # noqa: E402
from pfsans.system import ROOT, load  # noqa: E402
from pfsymbols.kit import symbol_system  # noqa: E402

DIST = ROOT / "build" / "dist"
BUILD = ("build.py", "build_mono.py", "build_symbols.py", "specimen.py")
CHECKS = ("verify.py", "verify_optical.py", "verify_variable.py")


def sh(*cmd, capture=False) -> str:
    cmd = [str(c) for c in cmd]
    if not capture:
        print("+", " ".join(cmd), flush=True)
    done = subprocess.run(cmd, check=True, cwd=ROOT, text=True, stdout=subprocess.PIPE if capture else None)
    return (done.stdout or "").strip()


def release_version() -> str:
    version = (ROOT / "VERSION").read_text().strip()
    major, minor, _ = version.split(".")
    font = f"{major}.{int(minor) * 100:03d}"
    found = {
        "design-system.json meta.version": (load().meta.version, font),
        "design-system.json mono.version": (load("Regular", mono=True).meta.version, font),
        "symbols/symbol-system.json": (symbol_system()["meta"]["version"], version),
    }
    wrong = [f"{where} is {have}, expected {want}" for where, (have, want) in found.items() if have != want]
    if wrong:
        sys.exit(f"version {version}: " + "; ".join(wrong))
    return version


def notes(version: str) -> str:
    text = (ROOT / "CHANGELOG.md").read_text(encoding="utf-8")
    match = re.search(rf"^## {re.escape(version)}\b[^\n]*\n(.*?)(?=^## |\Z)", text, re.M | re.S)
    if not match:
        sys.exit(f"CHANGELOG.md has no section '## {version}'")
    return match[1].strip() + "\n"


def tree(folder: Path, into: str, pattern: str = "**/*") -> dict[str, bytes]:
    files = {f"{into}/{p.relative_to(folder).as_posix()}": p.read_bytes()
             for p in sorted(folder.glob(pattern)) if p.is_file() and p.name != ".DS_Store"}
    if not files:
        sys.exit(f"nothing to package in {folder.relative_to(ROOT)}; build first")
    return files


def zip_(name: str, files: dict[str, bytes]) -> Path:
    stamp = time.gmtime(int(SOURCE_DATE_EPOCH))[:6]
    out = DIST / f"{name}.zip"
    with zipfile.ZipFile(out, "w") as z:
        for entry in sorted(files):
            info = zipfile.ZipInfo(f"{name}/{entry}", stamp)
            info.external_attr = 0o644 << 16
            info.compress_type = zipfile.ZIP_DEFLATED
            z.writestr(info, files[entry], compresslevel=9)
    print(f"{out.relative_to(ROOT)}  {out.stat().st_size:,} bytes, {len(files)} files")
    return out


def package(version: str) -> list[Path]:
    fonts = ROOT / "fonts"
    ofl = {"LICENSE.txt": (ROOT / "LICENSE.txt").read_bytes()}
    weights = len(load().masters)

    sans = dict(ofl)
    for folder, ext in (("OTF", "otf"), ("TTF", "ttf"), ("WOFF2", "woff2")):
        sans |= tree(fonts / ext, folder, f"PFSans-*.{ext}")
    for ext in ("ttf", "woff2"):
        sans |= tree(fonts / "variable", "Optical", f"PFSansOptical-*.{ext}")
        sans |= tree(fonts / "variable", "Variable", f"PFSansVariable.{ext}")
    mono = dict(ofl)
    for folder, ext in (("OTF", "otf"), ("TTF", "ttf"), ("WOFF2", "woff2")):
        mono |= tree(fonts / "mono" / ext, folder, f"PFMono-*.{ext}")
    # 3 static formats and the optical TTF/WOFF2 per weight, plus the variable pair.
    assert len(sans) == 1 + 5 * weights + 2, f"Sans: {len(sans)} files"
    assert len(mono) == 1 + 3 * 2, f"Mono: {len(mono)} files"

    symbols = dict(ofl)
    for name in ("manifest.json", "preview.html"):
        symbols[name] = (ROOT / "symbols" / name).read_bytes()
    for sub in ("svg", "sprites"):
        symbols |= tree(ROOT / "symbols" / sub, sub)

    DIST.mkdir(parents=True, exist_ok=True)
    for old in DIST.iterdir():
        old.unlink()
    zips = [zip_(f"PFSans-{version}", sans), zip_(f"PFMono-{version}", mono), zip_(f"PFSymbols-{version}", symbols)]
    sums = DIST / "SHA256SUMS.txt"
    sums.write_text("".join(f"{hashlib.sha256(p.read_bytes()).hexdigest()}  {p.name}\n" for p in zips))
    return zips + [sums]


def require_publishable(tag: str) -> None:
    if sh("git", "status", "--porcelain", capture=True):
        sys.exit("commit (or discard) all changes before --publish; a build that changes tracked files counts")
    if sh("git", "branch", "--show-current", capture=True) != "main":
        sys.exit("publish from main")
    sh("git", "fetch", "--quiet", "origin", "main")
    if sh("git", "rev-parse", "HEAD", capture=True) != sh("git", "rev-parse", "origin/main", capture=True):
        sys.exit("push main before --publish")
    if sh("git", "ls-remote", "--tags", "origin", f"refs/tags/{tag}", capture=True):
        sys.exit(f"tag {tag} already exists on origin")


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--publish", action="store_true", help="tag and create the GitHub release")
    ap.add_argument("--no-build", action="store_true", help="package the files already built")
    args = ap.parse_args()
    version = release_version()
    body, tag = notes(version), f"v{version}"
    if args.publish:
        require_publishable(tag)
    if not args.no_build:
        for script in BUILD + CHECKS:
            sh(sys.executable, ROOT / "scripts" / script)
    assets = package(version)
    if not args.publish:
        print(f"release {version} is in build/dist (not published)")
        return
    require_publishable(tag)  # again: the build must not have changed anything
    notes_file = ROOT / "build" / "release-notes.md"
    notes_file.write_text(body, encoding="utf-8")
    sh("git", "tag", "-a", tag, "-m", f"Porto Faifo {version}")
    sh("git", "push", "origin", tag)
    sh("gh", "release", "create", tag, *assets, "--verify-tag", "--title", f"Porto Faifo {version}",
       "--notes-file", notes_file)


if __name__ == "__main__":
    main()
