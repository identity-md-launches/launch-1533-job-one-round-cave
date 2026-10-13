# Bounded capture reader

Load a public saved ERC-20 transfer observation without reading outside the
workspace or allocating an unbounded input buffer. This standard-library
Python tool repairs the activity, coverage and receipt readers identified in
the Gathering 14 report. Activity, coverage, receipt, ledger, counterparties and stitch now use this
shared loader; their report formats and raw-log validation remain unchanged.

From the repository root, one command works offline:

```sh
python3 -B line-4/tools/bounded-capture-reader/reader.py --demo
```

Tried on 2026-10-13: it revalidated the retained real PublicNode ZTO capture,
blocks 26177298–26177309, and reported three transfers. The activity, coverage
and receipt demos also passed. This is dated chain evidence, not a fresh RPC
observation. No network call, installation, wallet, key or environment lookup
is needed. Keep the sibling `transfer-crosscheck` and `erc20-transfer-window`
folders when copying this tool; all runtime dependencies are ordinary Python
files already in this repository.

To inspect a public capture you selected inside this workspace:

```sh
python3 -B line-4/tools/bounded-capture-reader/reader.py --capture saved-window.json
```

The shared `read_capture(path, max_bytes=16777216)` function accepts a regular
file, bounds its actual read to limit + 1 bytes, and rejects excessive size
before JSON parsing. It refuses outside paths, `..` traversal, symlinks in
any path component, directories and FIFOs. Directory-relative no-follow
opens prevent symlink replacement between checking and opening. It uses
POSIX file flags and fails closed on unsupported platforms. The installation
root is trusted; this is not a sandbox against processes that can rename
already-open directories, make hard links, or rewrite workspace contents.
Do not select files containing secrets.

Strict UTF-8 JSON parsing refuses duplicate keys, non-finite numbers (including
exponent overflow), malformed input and nesting above 64 levels. The parser
accepts JSON values; the CLI and consumer tools separately require a valid
capture and rebuild its events from raw logs. These checks do not establish
provider honesty, chain completeness, current balances or finality.

Tests:

```sh
python3 -B line-4/tools/bounded-capture-reader/test_reader.py
```

All 15 focused tests passed, including exact-size limits, a simulated file
growing after stat, symlink components, traversal rejected before open, FIFO
refusal with a timeout, malformed/deep JSON, each consumer's restrictions,
and real ZTO demos. The three repaired consumer suites add 14 passing tests
(29 total). The initial deep-nesting test showed that the runtime accepted
2,000 levels; an explicit pre-parse 64-level bound fixed that issue. Fixtures
are created only beneath `test/scratch/` and no network is used in tests.

## Round 37: the remaining file readers

Ledger now delegates directly to this reader with its existing 16 MiB limit.
Counterparties passes the original path through the activity reader, without
resolving away symlink or traversal components first. Stitch inherits the
ledger change for both inputs. These changes close the separate-reader drift
noted in Gathering 16; valid capture report formats are unchanged. Previously
ledger followed workspace symlinks, could wait indefinitely on FIFOs and
accepted non-finite JSON; counterparties resolved symlinks before the shared
reader saw them. Those paths now fail cleanly with no report.

One command checks the actual four CLI input positions offline:

```sh
python3 -B line-4/tools/bounded-capture-reader/test_companions.py
```

Tried on 2026-10-13: all 12 new tests passed, including retained real ZTO
inputs, file and directory symlinks, traversal, outside paths, FIFOs,
directories, duplicate keys, non-finite numbers, exponent overflow, deep
nesting, invalid UTF-8 and sparse oversized inputs. All 11 Line 4 suites
passed (122 tests). Fixtures live in `test/scratch/` and are removed by the
suite. Existing demos still run offline with three retained real ZTO events.

A fresh read of historical blocks 26177298–26177309 at 07:41:36 UTC returned
three ZTO transfers through the provided mainnet relay, publicly attributed
to https://ethereum-rpc.publicnode.com. Ledger and counterparties accepted it;
stitch agreed with the retained PublicNode observation over the same range.
`round-37-live-zto.json` retains the dated evidence. Inspect it offline:

```sh
python3 -B line-4/tools/bounded-capture-reader/reader.py --capture line-4/tools/bounded-capture-reader/round-37-live-zto.json
```

No key, wallet, environment lookup, signing or transaction submission was
involved. This does not establish complete logs, current balances, holders,
pool activity or finality. Keep the sibling strict-rpc-json folder as well:
it is now a transitive dependency of the original transfer-window reader.
