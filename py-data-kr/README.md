# dongnae-kr

Korean dataset plugin for the [`dongnae`](https://github.com/nash-dir/dongnae) engine.

`dongnae-kr` bundles a ready-to-use Korean district (*dongnae* / 법정동) dataset
so you can use the engine without supplying your own CSV. It pulls in the
pure-Python [`dongnae`](https://pypi.org/project/dongnae/) core as a dependency
and pre-loads the data on construction.

* **Dataset**: ~21,700 Korean dongnae nodes (id, name, lat/lon, effective radius)
* **Version**: CalVer `YYYY.MM.DD` — the version tracks the **dataset vintage**
  (currently `2025.11.30`), not an API. The engine itself uses SemVer.

## Install

```bash
pip install dongnae-kr
```

This installs the `dongnae` engine as a dependency.

## Usage

```python
from dongnae_kr import dongnaekr

engine = dongnaekr()          # dataset is loaded automatically
town = engine.where(37.5665, 126.9780)
print(town["dnname"])         # nearest neighbourhood

for n in engine.nearest(37.5665, 126.9780, k=3):
    print(f"- {n['dnname']} ({n['distance']} km)")
```

`dongnaekr` is a `DongnaeEngine` subclass with the Korean CSV pre-loaded, so the
full engine API — `where`, `nearest`, `within`, `resolve`, `search`, `get`,
`howfar` — is available. See the
[engine documentation](https://github.com/nash-dir/dongnae/blob/main/py-core/README.md)
for the complete API reference.

## License

MIT — see [LICENSE.txt](./LICENSE.txt).
