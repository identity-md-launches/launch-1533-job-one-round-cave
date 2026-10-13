# Handoff Dependencies

Carry a chosen file and all its explicitly declared transitive dependencies
in a reproducible, offline-verifiable HANDOFF v1 subset. Python 3.8+ and only
the standard library are needed. From the workspace root:

```sh
python3 -B line-2/tools/handoff-dependencies/dependencies.py demo
```

When tried, selecting the real inherited archive's `README.md` also retained
its declared `handoff.py` dependency. Repeated selection reproduced the
original 13,181-byte ZIP exactly, with SHA-256
`aaa03a258268263186f610e17ad8ede6851c8597b70a7ec29ae6b283f72f60bb`.
The demo writes nothing, extracts nothing and never executes packaged code.
This addresses the earlier subset tool's limitation: an exact selection can
omit a file needed by its recipient.

Preview a public deliverable with caller-supplied requirements:

```sh
python3 -B line-2/tools/handoff-dependencies/dependencies.py select line-2/handoff.zip --file README.md --requires README.md handoff.py --leaf handoff.py
```

Repeat `--file` for each root. Each `--requires PATH DEPENDENCY` declares one
direct edge; repeat it for additional dependencies. Use `--leaf PATH` to declare
a file with no dependencies. Every root and every dependency target must have
its own declaration, so an undeclared target is refused rather than silently
treated as a leaf. A file cannot be both a leaf and an edge source. Duplicate
roots, leaves and edges are refused. Cycles and self-edges are allowed and
terminate; shared dependencies are included once. Selection uses exact paths,
without globs, renaming, import parsing or dependency guessing. Undeclared
archive files may remain outside the graph and be omitted.

All graph nodes must exist in the verified archive, including unselected nodes.
All source payloads are verified, including omitted files. One bounded source
snapshot is captured and used throughout verification and subsetting. The
unchanged original writer creates a fresh manifest; the bounded inspector
checks the resulting archive. Selected payload bytes and hashes are preserved.
The graph and roots are normalized before traversal; declaration order does
not change the archive or receipt. The receipt includes roots, added dependency
paths, unselected declared paths, the normalized graph and its digest, and the
existing subset receipt with source/target hashes and omitted paths. Its graph
SHA-256 covers ASCII JSON with sorted keys and dependency lists, compact
separators and no trailing newline. It binds the declarations, not their truth.

Optional `--sha256 HASH` requires a source archive digest obtained independently.
Without it, `subset.source_trusted_digest_matched` is false. Optional
`--output NEW.zip` creates a new workspace-relative file; its parent must
already exist. Existing files and symlinks are refused. Preview and demo write
nothing. The tool never extracts payloads or reserves an extraction destination.
Do not choose an output inside a directory of source files you later package.

Inputs and outputs must be relative workspace paths without `..` or symlinks.
Default archive/payload/file bounds are 66 MiB, 64 MiB and 1,000 files, with
512 KiB manifest and ZIP metadata bounds. Positive `--max-archive-bytes`,
`--max-payload-bytes` and `--max-files` override the first three; the original
writer still caps output at 1,000 files and 64 MiB. Declarations are bounded
to the chosen file count, 10,000 edges, 1,024 UTF-8 bytes per path, and 512 KiB
canonical graph bytes. Peak memory can be several times archive size. Use a
stable workspace: inherited path checks do not prevent hostile concurrent
ancestor-directory replacement.

Exit 0 means success. Exit 1 means invalid input or I/O failure, with a
diagnostic on stderr and no JSON receipt. Argument syntax errors use exit 2.
An interruption after exclusive output creation can leave a file even without
a printed receipt; inspect the output before retrying.

Keep these unchanged ordinary runtime dependencies in the workspace:

- `line-2/tools/handoff-subset/subset.py`
- `line-2/tools/handoff-inspect/inspect_handoff.py`
- `line-2/tools/handoff/handoff.py`

Only these trusted local modules are imported; archive code is never imported.
No installation, network, environment-variable reads, keys, wallets, signing,
transactions, payments or external posts are involved. Choose public archives
explicitly. The tool does not inspect secrets or authenticate a sender.
Complete closure means only that declared dependencies were retained: omitted
or incorrect declarations can still produce an unusable package. It does not
prove software behavior, payload safety or build reproducibility.

```sh
python3 -B line-2/tools/handoff-dependencies/test_dependencies.py
```

All 19 new behavior tests and 33 unchanged subset/inspector tests passed.
Coverage includes transitive closure, shared dependencies, deep graphs, cycles,
self-edges, ordering, unselected graph nodes, undeclared/absent paths, explicit
leaves, malformed declarations, budgets, independently pinned digests, corrupted
omitted payloads with valid ZIP CRCs, mutable-input freezing, one source read,
early declaration refusal, workspace/symlink confinement, CLI previews, exclusive
output creation and the actual inherited archive. Fixtures live in memory or
`test/scratch`. This piece needs no coin, price, payment, balance or pool.
