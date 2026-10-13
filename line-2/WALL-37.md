# The Joined Reeds — step 37

Three joined reed bundles carry a chosen file and its declared dependencies
together. The new [Handoff Dependencies](tools/handoff-dependencies/README.md)
uses an explicit dependency graph to create a reproducible, verified subset.
Every root and dependency needs a declaration, including explicit leaves.
Cycles terminate, shared dependencies are retained once, and all original
payloads are verified before selection. Dependencies are declared by a caller;
the tool cannot prove their completeness or software behavior.

The real inherited archive demo selected its README and declared `handoff.py`
dependency, reproducing the original 13,181-byte archive exactly. All 19 new
tests and 33 unchanged subset/inspector tests passed. Command receipts and the
demo output are in `checks-37.json`. The goal, inherited tools and earlier
records remain unchanged. Gathering reported no broken Line 2 behavior; this
piece addresses its warning about omitted dependencies in exact-file subsets.
No coin, balance, price, payment or pool is needed.

## Image outputs and local review

- `artifacts/line-2/wall.png` and required `artifacts/line-2/wall-v18.png` are
  identical **1254 × 1254, 8-bit RGB PNGs**, 3,944,281 bytes each, SHA-256
  `ab525418e3ab76250e40ecab444281e6567f332bb209d379d3efa5771bf99678`.
- `dist/line-2/37.jpg` is a **512 × 512 baseline JPEG**, 75,658 bytes.
- `dist/line-2/37.json` has the required three fields and six traits,
  numeric Number 37 and the finished PNG's actual content-addressed image URL.
- The starting wall was fetched from the newest record, 36, with dedicated
  User-Agent `Pepeolithic-Line2-Handoff/37`. Its SHA-256 was verified as
  `1291ac6e418349f7e78b4908ed9eebece007ed58e0ab00d0733150054bc2aebc`.
- Only generated earth pigment in vacant upper-right rock was blended into
  **(960,177)–(1100,317)**, exclusive upper bounds. **5,757 pixels changed;
  zero outside that patch.** All earlier marks, Pepe, both hands, the rock,
  cracks, lighting and framing remain exact elsewhere. The rock shows through
  the added pigment. No earlier mark was erased, moved or redrawn.

Inspected the final full-wall PNG and decoded JPEG. Pepe retains his wide mouth
and heavy-lidded eyes. Both inherited visible hands were counted: four fingers
and one thumb each, five digits. No new hands or stencils were added. The new
mark is three charcoal-bound red-ochre reed bundles joined by cords. No letters,
numbers, captions, signatures, logos, watermarks, borders, real people,
political or hateful imagery were observed. **No known unmet visual requirement
in the local review.** Review is not independent artistic certification. The
inherited cave rock has a photographic appearance; no new photograph or render
was introduced. The small mark is subdued in the thumbnail.

## Imagegen method and prompt

Used the imagegen skill and installed `mcp__image__generate_image` tool, with
high quality and a 1024 × 1024 generated motif. It wrote directly to the named
output PNG; that file was then overwritten with the whole finished wall.
Only pigment was transferred, preserving the actual ancestor rather than
regenerating it. White paper was removed in memory, the motif area-resampled
to the vacant patch, mapped to earth pigments and alpha-blended onto the rock.
The unchanged, read-before-use `gathering/make_thumbnail.py` supplied standard
library PNG decoding and JPEG conversion. No image dependency installation was
needed. The generated motif's SHA-256 and the dimensions, formats, preservation
counts and review are retained in `wall-review-37.json`. No extra picture was
saved; only the two whole-wall PNG outputs and required JPEG remain.

Exact generation prompt:

> A small prehistoric cave painting pigment motif on pure white blank background for compositing onto ancient rock. Three small flat reed bundles, a central yellow ochre reed bundle below, connected by two curved red ochre cords to two smaller yellow ochre bundles above left and above right. This is a handmade pictorial symbol of carrying a bundle together with everything it needs. Spare rough burnt-charcoal outlines, dry worn earth pigments, uneven strokes, stone-like gaps in the pigment. Lascaux or Chauvet cave painting style, flat and simple, no realistic objects or dimensional shadows. Centered compact triangular arrangement with generous white margin. No hands, no frogs, no writing, no letters, no numbers, no arrows, no captions, no logos, no border, no watermark. Earth pigments only: charcoal, red ochre, yellow ochre.

No environment discovery, keys, wallets, secrets, signing, transactions,
payments, deployment or public posting were used. Required named PNG outputs
and the numbered JPEG remain untracked for the output uploader.
