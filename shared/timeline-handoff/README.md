# Timeline handoff

Carry a bounded ZTO supply timeline together with every exact source observation
needed to recompute it. This joins Line 1's snapshot timeline to Line 2's new
explicit dependency closure. A receiver verifies all HANDOFF v1 payloads,
requires the fixed evidence graph, recomputes the timeline, compares exact
canonical report bytes, and reproduces the archive. Nothing is extracted;
archive code is never imported or executed.

One command works offline from any workspace containing this complete folder:

```sh
python3 -B shared/timeline-handoff/timeline_handoff.py demo
```

Python 3.10+ standard library only. No install or line folders needed. Eight
ordinary runtime modules are vendored with exact source/copy SHA-256 provenance.
Six are unchanged; two only adapt trusted sibling import paths to the portable
folder. The RPC module includes public-read functions, but this kit never calls
them. No environment, secret, key, wallet, signing, payment, transaction sending
or external posting is involved.

The demo preserves a dated, compact PublicNode observation from
2026-10-13T02:02:46Z and a fresh full native capture from this gathering. The
older source was already a projection retaining block identity and supply;
the kit preserves those received bytes exactly, without projecting further.
Blocks 26180371 and 26182090 have equal ZTO supply of
1000000000000000000000000000 base units, with 1718 unsampled blocks between.
This is dated provider evidence, not a claim about the present chain head.
`examples/zto-timeline.zip` is the reproducible 54,758-byte archive.

Package explicitly selected public captures into a new file, then check it:

```sh
python3 -B shared/timeline-handoff/timeline_handoff.py pack new.zip first.json second.json
python3 -B shared/timeline-handoff/timeline_handoff.py check new.zip
```

`check --sha256 DIGEST` accepts an independently obtained expected archive
digest. Without that, integrity checks cannot authenticate a sender. Even an
expected digest says nothing about provider honesty.

There are 1–16 inputs. Each file, combined payload and archive is limited to
99,000 bytes, including ZIP overhead for the archive; two large captures may
therefore be refused. Manifest and metadata limits are 8192 bytes each, with
at most 18 payload files. Reports and the declaration graph have canonical
ASCII JSON bytes. Original source bytes are retained separately and hashed.
Inputs must be relative workspace regular files without traversal or symlinks.
Descriptor-relative no-follow reads require POSIX flags and refuse FIFOs without
waiting. Output creation is exclusive and refuses an existing target; inherited
output path checks do not protect against concurrent ancestor replacement.

Exit 0 means internally consistent observations. Exit 2 preserves detected
timeline conflicts as review evidence; `pack` still creates that diagnostic
archive, so it is not a readiness assertion. Exit 1 refuses invalid inputs with
no JSON receipt. Argument syntax errors also use exit 2. An interrupted output
write may leave a partial file: inspect it before retrying.

Tried: the demo and native Line 2 inspector passed. Twelve integration tests
passed, including exact source bytes, offline operation, determinism, fixed
dependency closure, rehashed false reports, missing/extra files, digest mismatch,
conflicting supplies, malformed/signed inputs, size limits, provenance,
workspace boundaries, standalone copied-folder CLI use and exclusive output.

```sh
python3 -B shared/timeline-handoff/test_timeline_handoff.py
```

The first test run exposed an absolute temporary-fixture path in a test that
was intended to exercise a relative input. The test was corrected; the reader
properly refused the absolute path. All tests then passed.

The dependency graph binds evidence, not runnable software dependencies.
Recomputation validates the saved observations and detects their internal
conflicts; it does not prove provider independence, recompute block hashes,
establish finality, complete history, balances, or explain supply changes.
Gaps remain explicitly unsampled. Copy the whole kit when you need the receiver
implementation as well as an archive.
