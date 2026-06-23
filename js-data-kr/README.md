# @dongnae-js/data-kr

> ⚠️ **Experimental — not published to npm.**
> This is a JavaScript port of the [`dongnae`](../py-core/README.md) engine, bundled with the
> Korean (`-kr`) dataset. The API mirrors the Python core and the engine works,
> but it is **unreleased**: there is no npm package yet, the version is `0.1.0`,
> and the surface may change without notice. For production use, prefer the
> Python core. Try the engine in the browser at the
> **[live demo](https://nash-dir.github.io/dongnae/)**.

A dependency-free, self-contained district (*dongnae*) lookup engine for the
browser and edge runtimes. The Korean dataset is baked into the module as a
Structure-of-Arrays payload, so there is no network call, no API key, and no
backend — the same design as the Python core.

## Status

| | |
| :-- | :-- |
| npm | **Not published** (install from source only) |
| Version | `0.1.0` (pre-release) |
| Stability | Experimental — API may change |
| Reference implementation | [`dongnae` (Python)](../py-core/README.md) |

## Install (from source)

Not published to npm, and the repo root has no package manifest — so vendor the
`js-data-kr/src/` directory into your project and import the engine directly:

```js
import { DongnaeEngine } from "./js-data-kr/src/engine.js";
```

It ships as an ES module (`"type": "module"`).

## Usage

```js
// When vendoring, import from the relative path to src/engine.js.
// The "@dongnae-js/data-kr" specifier works once it is an installed package.
import { DongnaeEngine } from "@dongnae-js/data-kr";

const engine = new DongnaeEngine(); // dataset is bundled; no loading step
console.log(`Loaded ${engine.count} dongnaes`);

// Reverse geocoding — nearest neighbourhood to a coordinate
const here = engine.where(37.5665, 126.9780);
console.log(here?.dnname);

// Text search (quasi-geocoding)
const hit = engine.search("강남");
console.log(hit?.dnname);
```

## API

The JavaScript engine mirrors the Python core; outputs match within a coordinate
quantization tolerance (the bundled JS dataset is rounded to 4 decimal places,
~11 m worst case), so distances differ from the Python core at the metre level.
Coordinates are `(lat, lon)` and distances are "boundary distances" in km
(negative = inside the node's radius).

| Method | Returns | Description |
| :-- | :-- | :-- |
| `where(lat, lon)` | `DongnaeResult \| null` | Single nearest dongnae |
| `nearest(lat, lon, k?, radiusKm?)` | `DongnaeResult[]` | K nearest, sorted by distance |
| `within(lat, lon, radiusKm, limit?)` | `DongnaeResult[]` | All dongnaes within a radius |
| `resolve(lat, lon, threshold?)` | `DongnaeResult[]` | Soft geofencing with a tolerance buffer |
| `search(keyword, limit?, bestShot?)` | `DongnaeResult \| DongnaeResult[] \| null` | Keyword search |
| `get(dnid)` | `DongnaeResult \| null` | O(1) lookup by id |
| `howfar(lat, lon, dnid)` | `number \| null` | Boundary distance to a specific dongnae |

> Note: `index.d.ts` types the full public surface, including `resolve` and
> `howfar`.

## License

MIT — see [LICENSE.txt](./LICENSE.txt).
