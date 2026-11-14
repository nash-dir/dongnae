# dongnae

Monorepo: `py-core/` (`dongnae` engine, PyPI), `py-data-kr/` (`dongnae-kr` Korean
dataset, PyPI), `js-data-kr/` (JS port, unpublished), `docs/` (GitHub Pages demo).

## Checks

```bash
pytest                                  # repo root
(cd js-data-kr && npm test)
ruff check py-core tests                # CI pins ruff==0.15.9
python docs/sync_src.py --check         # docs/src must match js-data-kr/src
```

`js-data-kr/src` is the source of truth; `docs/src` is a copy for Pages. After
editing `js-data-kr/src`, run `python docs/sync_src.py` and commit both.

## Releasing to PyPI

Releases go only through `.github/workflows/release.yml` (Trusted Publishing /
OIDC). Never `twine upload` by hand and never store a PyPI token.

| Tag | Publishes | Version source |
| :-- | :-- | :-- |
| `v<version>` | `dongnae` | `py-core/pyproject.toml` |
| `kr-v<version>` | `dongnae-kr` | `py-data-kr/pyproject.toml` |

1. Bump `version` in the package's `pyproject.toml` (`dongnae-kr` is CalVer
   `YYYY.M.D`, no leading zeros) and move the CHANGELOG `[Unreleased]` notes
   under the new version.
2. Commit, push `master`, and wait for CI to pass.
3. Get the user's go-ahead: a pushed tag publishes, and PyPI never accepts the
   same version twice.
4. `git tag -a kr-v2026.11.2 -m "dongnae-kr 2026.11.2"` (or `v<version>`),
   then `git push origin <tag>`.
5. Watch the `Publish to PyPI` run, then confirm on PyPI
   (`https://pypi.org/pypi/<package>/<version>/json`) and with a fresh
   `pip install <package>==<version>`.

The workflow fails before uploading if the tag doesn't match `pyproject.toml`
or if the sdist/wheel holds anything besides the package, its metadata, README
and license. PyPI Trusted Publisher, on both projects: owner `nash-dir`, repo
`dongnae`, workflow `release.yml`, environment `pypi`.

## Updating the Korean dataset

The data is generated in the sibling repo
[korea-bjd-shp-to-csv](https://github.com/nash-dir/korea-bjd-shp-to-csv)
(`bjd_geometry_to_csv.py` → `bjd_csv_to_fulladdress.py` →
`bjd_csv_apply_revisions.py` → `bjd_csv_to_dongnae.py`). To ship a new
`dongnaeKR_<YYMMDD>.csv`:

1. Replace the CSV in `py-data-kr/dongnae_kr/data/` (exactly one CSV) and
   update the filename in `py-data-kr/dongnae_kr/__init__.py`.
2. Copy it into `data/`, set `INPUT_FILENAME` in `data/CSVtoJSON.py`, then run
   `python data/CSVtoJSON.py` and `python data/convert_json_to_js_module.py`.
3. `python docs/sync_src.py`, run the checks, and release with a `kr-v` tag.
