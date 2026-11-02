"""
Copy the JS engine from js-data-kr/src into docs/src for the live demo.

GitHub Pages serves only the docs/ folder, so the demo cannot import
js-data-kr directly and keeps its own copy. js-data-kr/src is the source of
truth: edit files there, then run this script.

    python docs/sync_src.py          # copy js-data-kr/src -> docs/src
    python docs/sync_src.py --check  # exit 1 if the copies differ (CI)
"""

import filecmp
import os
import shutil
import sys

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
SRC_DIR = os.path.join(BASE_DIR, '..', 'js-data-kr', 'src')
DST_DIR = os.path.join(BASE_DIR, 'src')

FILES = ['engine.js', 'dongnae_data.js', 'index.d.ts']


def main() -> int:
    check = '--check' in sys.argv[1:]
    stale = []

    for name in FILES:
        src = os.path.join(SRC_DIR, name)
        dst = os.path.join(DST_DIR, name)
        if os.path.exists(dst) and filecmp.cmp(src, dst, shallow=False):
            continue
        stale.append(name)
        if not check:
            os.makedirs(DST_DIR, exist_ok=True)
            shutil.copyfile(src, dst)
            print(f"synced: docs/src/{name}")

    if check and stale:
        print("docs/src is out of sync with js-data-kr/src: " + ", ".join(stale))
        print("Run `python docs/sync_src.py` and commit the result.")
        return 1
    if not stale:
        print("docs/src is up to date.")
    return 0


if __name__ == '__main__':
    sys.exit(main())
