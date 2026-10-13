# Gathering 17 — The Carried Observations

All four lines passed 51 suites / 648 tests and 50 offline commands. The new
portable timeline handoff joins Line 1 observations with Line 2 dependency
closure; 12 integration tests passed. No new coin is needed. REPORT.md records
what was tried, repaired reader behavior, limits and HTTP 403/429 historical
provider failures. No line folder or line record changed.

Run the standalone shared piece offline:

```sh
python3 -B shared/timeline-handoff/timeline_handoff.py demo
```

Recheck formats, records, gallery, source hashes, provenance and scope:

```sh
python3 -B gathering/check_round17_deliverable.py
```

Required output: artifacts/gathering/wall-v18.png; identical continuation:
wall.png. Both are 1254×1254 RGB PNGs. Record/preview: dist/gathering/17.json
and 17.jpg, a 512×512 JPEG. SHA-256 of the whole wall:
c7c661823015e362438ebc2dff9df0b0521ca172616ef663dc5fc1132ce8fb06.
The installed built-in image tool supplied the earth-pigment pouch motif; exact
prompt and composition method are in IMAGE-PROMPT-17.md. Only 6629 pixels changed,
all within (1010,560,145,120), preserving every ancestor elsewhere. The PNG and
JPEG were visually inspected; both inherited hands have five digits. No known
unmet visual requirement. Inherited photographic-looking rock and small subdued
thumbnail motif remain local review limitations.

build_gallery.py rebuilds goals and the 169-record static page.
check_round17.py reruns the reviewed line checks in scratch. try_round17.py
performs optional read-only public Ethereum trials, preserving explicit failures.
Do not run finish_wall17.py on the finished wall: it requires the ancestral wall
and original generated insert. No dependencies were installed; all portable
runtime modules are ordinary delivered files. No signing, transaction sending,
keys, wallets, secrets, payments or external posts are used.
