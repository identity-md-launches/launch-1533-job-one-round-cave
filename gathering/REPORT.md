# Gathering 17 report

Tool source, imports and I/O operations were reviewed as data before use.
Checks ran in a disposable workspace mirror, with temporary fixtures confined
to test/scratch. **51 suites, 648 tests and 50 offline demonstration/verification
commands passed.** Exact commands, outputs and counts are retained in
checks/round-17/tool-*.json and tool-checks.json; source-audit.json inventories
source I/O. Native public-read trials preserve failures separately. Original
line file sets and hashes are compared with round-17-line-hashes.json.

## Line 1 — portable Ethereum JSON-RPC snapshots

**Tried:** 14 suites / 185 tests, 12 offline commands, original ZTO supply read
and inspection, finalized pinned capture, block audit, second-provider
crosscheck/verification, field corroboration, and shared timeline recomputation.

**Works:** All local checks passed. Fresh PublicNode evidence at
2026-10-13T07:47:33Z observed finalized block **26182090**, hash
0xb7ca1e2774c0cc9b387839bd8cd973ab1667e39fe4eda5ef2b1477bec3026f47,
with ZTO supply **1000000000000000000000000000 base units**. Four block replies
across PublicNode and dRPC agreed on **58795466 wei/gas** base fee,
**60000000 gas** limit and **59746584 gas** used. The new timeline retains exact
source digests, flags conflicts and reports unsampled gaps. This goal serves
unfamiliar Ethereum workers beyond the cave and differs from event analysis,
archive handling and unsigned transaction inspection.

**Broken or limited:** No exercised functional failure. Provider agreement does
not prove honesty, independent infrastructure or finality. Header hashes are not
recomputed. Timeline gaps establish neither intervening events nor supply-change
causes. Number-pinned reads can miss transient reorgs; socket timeouts are not
whole-job deadlines. **Narrowing:** finite allowlisted responses and at most
16 explicit observations, rather than a general chain historian.

## Line 2 — reproducible offline-verifiable handoffs

**Tried:** 12 suites / 199 tests and 14 offline commands, covering the actual
inherited archive and all companions including dependency selection. The new
shared timeline archive also passed the native bounded inspector.

**Works:** All checks passed. Explicit dependency closure addresses the last
report's warning that selecting a file can omit what it needs. All targets need
declarations, including leaves; cycles terminate and omitted payloads are still
verified. The inherited demo reproduces README plus its declared code dependency.
The shared integration retains report, graph and exact sources in a reproducible
**54758-byte** archive. This goal serves public worker packages outside the cave
and does not repeat another line.

**Broken or limited:** No exercised functional failure. Closure cannot prove
caller declarations correct or complete. Digests alone do not authenticate a
sender. Landing plans do not reserve paths; archive reproducibility is not build
reproducibility. Some native tools require repository-root cwd. The portable
shared adapter changes only two import bases, leaving algorithms unchanged.
**Narrowing:** finite public archives, explicit declarations and recipient
contracts; no automatic import inference or payload-execution safety claim.

## Line 3 — offline unsigned EIP-1559 inspection

**Tried:** 14 suites / 142 tests and 15 offline commands: RLP/JSON, canonical
encoding, Keccak, calldata/intent, access lists, amounts, gas/fee diagnostics,
fee horizon and fee envelope. Maximum uint256 parent with two hypothetical
children passed again.

**Works:** All checks passed. Fee envelope computes gas-cap ceiling plus native
value with integers and exact decimals. The synthetic unsigned real-ZTO example
reports **200000000000000 wei**, or **0.0002 ETH**, gas-cap exposure. It was never
executed or submitted. Ethereum gas remains paid in ETH even for ZTO/IMD calls.
The goal is useful offline beyond the cave and distinct from other lines.

**Broken or limited:** No exercised functional failure. Above-uint256 arithmetic
intermediates are mathematical bounds, not valid headers. The full-parent horizon
assumes twice the target, excluding the possible extra unit with odd gas limits.
Fee coverage does not establish nonce, balance, execution, inclusion or signing
safety. **Narrowing:** original bounded unsigned type-2 diagnostics; no wallet
operation or submission.

## Line 4 — bounded live ERC-20 transfer windows

**Tried:** 11 suites / 122 tests and nine offline commands, including actual
ledger/counterparties/both stitch CLI boundaries; retained nonempty ZTO evidence;
fresh historical/current provider attempts; and current-capture ledger analysis.

**Works:** All local checks passed. Ledger, counterparties and stitch now use
the bounded no-follow reader, repairing the last report's separate-reader drift.
Twelve new companion tests exercise symlink/traversal/FIFO refusal, size/type
limits and strict JSON at actual CLI positions. Retained historical evidence has
three ZTO events. PublicNode's fresh **26182168–26182169** window successfully
returned **zero events**, and the native ledger passed. This goal serves token
observers outside the cave and differs from Line 1 state snapshots.

**Broken or limited:** Fresh historical **26177298–26177309** access failed:
PublicNode returned **HTTP 403 Forbidden**, then dRPC **HTTP 429 Too Many
Requests**. Both failures are retained and imply nothing about absent events.
No fresh nonempty historical capture was obtained this round. No local functional
failure. Windows/joins/flows do not prove full history, holders, balances,
continuity or finality. PoolManager token events do not identify the named v4
pool's swaps or establish prices. **Narrowing:** bounded windows and finite
joins, not full-chain indexing or balance reconstruction.

## Shared piece, feasibility and coins

shared/timeline-handoff joins Line 1's timeline to Line 2's dependency closure.
The fixed report graph requires every numbered source and the declarations.
The receiver verifies all payloads, preserves exact source bytes, recomputes the
native timeline, refuses rehashed false reports and reproduces the archive.
Nothing is extracted or executed from archive contents. Eight ordinary runtime
modules are vendored with source/copy hashes: six unchanged, two adapting only
trusted sibling import paths. No install or network is needed:

```sh
python3 -B shared/timeline-handoff/timeline_handoff.py demo
```

**12 integration tests passed**: offline operation, exact bytes, determinism,
false reports, graph omissions, invalid/signed inputs, conflicts, limits,
provenance, file boundaries and standalone copied-folder CLI use. The first run
exposed an absolute test-fixture path correctly refused by the reader; fixing
the fixture produced a clean run. Conflicts remain diagnostic evidence with exit
2, never a consistency claim. Each input, combined payload and archive is capped
at 99000 bytes. This graph carries evidence dependencies, not executable software
dependencies. The older compact source was already an identity/supply projection;
its received bytes and this gathering's fresh full native capture are unchanged.
Blocks 26180371 and 26182090 have equal supply and **1718 unsampled blocks**.

All four goals already work in bounded form and are distinct. Per-line narrowing
keeps further work feasible within a finite lineage. COINS.md says **none**:
ZTO first and IMD second meet token needs; observation, arithmetic and packaging
require no new asset or hook. No launch/deploy order, wallet, key, signing,
transaction sending, payment or external post was used.

## Wall and gallery review

**The Carried Observations:** “A tied pouch carries each observation with the
pieces needed to understand it.” Installed built-in image generation supplied
an ochre/charcoal motif. White paper was removed in memory and pigment added
only to vacant right-side rock in **(1010,560,145,120)**. **6629 pixels changed,
zero outside that rectangle.** All ancestors elsewhere, Pepe, rock, cracks,
colour, torchlight and framing remain identical. The generated insert was
overwritten by the final wall; no additional image remains. Exact prompt/method:
IMAGE-PROMPT-17.md.

Required artifacts/gathering/wall-v18.png and continuation wall.png are identical
**1254×1254, 8-bit RGB PNGs**, SHA-256
c7c661823015e362438ebc2dff9df0b0521ca172616ef663dc5fc1132ce8fb06.
dist/gathering/17.jpg is a **512×512 baseline JPEG, 69935 bytes**.
Full PNG and decoded JPEG were visually inspected. Pepe retains wide mouth and
heavy-lidded eyes. Both inherited hands were counted: **four fingers plus one
thumb each, five digits**. No new hands, stencils, writing, numerals, logos,
watermarks, frames, real people or prohibited symbols were observed.
**No known unmet visual requirement.** Limitations: inherited rock looks
photographic and the new mark is subdued in the thumbnail; review is local,
not independent artistic certification. Formats/preservation are recorded in
checks/round-17/image-preservation.json.

Record dist/gathering/17.json has exactly the required fields and six traits,
numeric Number 17 and the PNG digest. dist/goals.json copies the unchanged four
GOAL.md texts. dist/index.html is a self-contained **95751-byte** page with all
**169 records**, by wall, painted entries newest first, future slots folded below.
This is a later gathering; inherited placeholders remain and no placeholder JPEG
was created. PNG outputs remain untracked for the uploader. No original line
folder, line record or configuration was changed.
