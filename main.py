#!/usr/bin/env python3
"""Entry program for news-image-20261120 (Python 3.13, standard library only).

The repository holds the front-page image; this program copies it to the
output directory the grader provides ($MAKEFUN_OUTPUT_DIR, else /output).
"""
import hashlib
import os
import shutil
import sys

SOURCE_NAME = "entry.png"


def sha256_of(path):
    digest = hashlib.sha256()
    with open(path, "rb") as handle:
        for chunk in iter(lambda: handle.read(65536), b""):
            digest.update(chunk)
    return digest.hexdigest()


def main():
    here = os.path.dirname(os.path.abspath(__file__))
    source = os.path.join(here, SOURCE_NAME)
    if not os.path.isfile(source):
        sys.exit(f"news-image-20261120: {SOURCE_NAME} is missing next to main.py")
    out_dir = os.environ.get("MAKEFUN_OUTPUT_DIR") or "/output"
    os.makedirs(out_dir, exist_ok=True)
    target = os.path.join(out_dir, SOURCE_NAME)
    shutil.copyfile(source, target)
    if sha256_of(source) != sha256_of(target):
        sys.exit("news-image-20261120: copied entry.png does not match the source")
    print(f"wrote {target} ({os.path.getsize(target)} bytes, "
          f"sha256 {sha256_of(target)[:16]}...)")


if __name__ == "__main__":
    main()
