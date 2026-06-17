// Smoke + regression tests for the experimental JS port.
// Zero dependencies: uses Node's built-in test runner (`node --test`).
//
// These pin the behaviours that diverged from the Python reference engine and
// the bbox/large-radius bug, against the real bundled Korean dataset.

import { test } from 'node:test';
import assert from 'node:assert/strict';

import { DongnaeEngine } from '../src/engine.js';

const e = new DongnaeEngine();

// index of the largest-radius node (used by several tests)
let bigIdx = 0;
for (let i = 1; i < e.count; i++) {
    if (e.rads[i] > e.rads[bigIdx]) bigIdx = i;
}

test('dataset loads', () => {
    assert.ok(e.count > 0);
});

test('where / nearest / get basics', () => {
    const here = e.where(37.5665, 126.978);
    assert.ok(here && typeof here.dnname === 'string');

    const near = e.nearest(37.5665, 126.978, 3);
    assert.equal(near.length, 3);

    const id = e.ids[0];
    assert.equal(e.get(id).dnid, id);          // string id
    assert.equal(e.get(Number(id)).dnid, id);  // numeric id coerced via String()
});

test('search: empty / whitespace query returns no match (not everything)', () => {
    assert.equal(e.search(''), null);
    assert.equal(e.search('   '), null);
    assert.deepEqual(e.search('', 10, false), []);
    assert.deepEqual(e.search('   ', 10, false), []);
});

test('search: a real keyword still works', () => {
    const hit = e.search('서울');
    assert.ok(hit && hit.dnname.includes('서울'));
});

test('auto-calibration uses a full scan (matches Python), not 100-stride sampling', () => {
    let mn = 90, mx = -90, mr = 0;
    for (let i = 0; i < e.count; i++) {
        const v = e.lats[i];
        if (v < mn) mn = v;
        if (v > mx) mx = v;
        if (e.rads[i] > mr) mr = e.rads[i];
    }
    const avg = (mn + mx) / 2;
    const expectedCoef = +(111 * Math.cos(avg * (Math.PI / 180))).toFixed(2);
    assert.equal(e.lonCoef, expectedCoef);
    assert.equal(e.maxRadius, mr);
    // The KR dataset really does contain nodes larger than the old fixed 5 km
    // buffer — which is why that buffer was unsound.
    assert.ok(mr > 5, `expected a radius > 5km, got max ${mr}`);
});

test('large-radius node is surfaced by where/nearest (bbox buffer tracks max radius)', () => {
    const id = e.ids[bigIdx];
    const blat = e.lats[bigIdx];
    const blon = e.lons[bigIdx];
    const brad = e.rads[bigIdx];

    // a point ~20 km north of the centre: well inside the big radius, but far
    // outside the old 15 km bbox.
    const qlat = blat + 20 / 111;
    const qlon = blon;

    assert.ok(brad > 20, 'fixture assumption: biggest radius exceeds 20km');
    assert.ok(e.howfar(qlat, qlon, id) < 0, 'howfar must report inside');

    // The node's centre is ~20 km away — outside the old fixed 15 km bbox, so
    // the old engine dropped it entirely. The new buffer must keep it as a
    // candidate. (where() may legitimately return another overlapping large
    // node ranked higher by boundary distance, so we only assert inclusion.)
    const found = e.nearest(qlat, qlon, 50).some(r => r.dnid === id);
    assert.ok(found, 'large-radius node must appear in nearest results');

    // and where() must surface a node we are genuinely inside, not a tiny far one
    assert.ok(e.where(qlat, qlon).distance < 0, 'where result should be a node we are inside');
});

test('howfar returns a raw (unrounded) value, like the Python core', () => {
    // at the exact centre, boundary distance == -radius, raw.
    assert.equal(e.howfar(e.lats[bigIdx], e.lons[bigIdx], e.ids[bigIdx]), -e.rads[bigIdx]);
    assert.equal(e.howfar(0, 0, '___no_such_id___'), null);
});

test('within: limit=0 returns empty, radiusKm=0 does not throw', () => {
    assert.deepEqual(e.within(37.5, 127.0, 100, 0), []);
    assert.doesNotThrow(() => e.nearest(37.5, 127.0, 5, 0));
});

test('where/nearest are total: far-away point still resolves (parity with Python)', () => {
    // A point far outside Korea yields an empty bbox; like the Python core,
    // nearest/where must fall back to a full scan and still return a node.
    const here = e.where(0, 0);
    assert.ok(here && typeof here.dnname === 'string', 'where(0,0) must not be null');
    assert.equal(e.nearest(0, 0, 3).length, 3);
});
