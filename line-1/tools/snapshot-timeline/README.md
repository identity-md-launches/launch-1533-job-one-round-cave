# Snapshot timeline

This standard-library tool validates up to 16 saved, block-pinned ZTO
`totalSupply` snapshots and makes one offline-readable JSON timeline. It sorts
observations by block, binds each to its exact input SHA-256, reports exact
base-unit supply differences across unambiguous observed heights, and flags
different hashes at one height, conflicting headers or supplies for one hash,
and a broken parent link between *consecutive sampled* heights. Gaps remain
explicitly unsampled. It reads only workspace files through the existing bounded,
no-follow snapshot reader.

From the repository root, one command shows it working on two retained real
PublicNode-named ZTO observations:

```sh
python3 -B line-1/tools/snapshot-timeline/snapshot_timeline.py demo
```

I tried that command offline. It validated observations at Ethereum blocks
**26177368** and **26180977**, found the same ZTO supply of
**1000000000000000000000000000 base units**, and reported a zero delta with
**3608 unsampled blocks** between them. It made no network request. The saved
observations are dated 2026-10-12 and 2026-10-13; this is no claim about current
state. The demo uses sibling `pinned-snapshot`, `snapshot-seal`, and
`rpc-snapshot` code, so keep those folders when copying the tool.

Use your own validated captures with:

```sh
python3 -B line-1/tools/snapshot-timeline/snapshot_timeline.py report first.json second.json
```

The tool prints JSON to standard output. Exit status is 0 for structurally
consistent observations, 2 for reported conflicts, and 1 for invalid inputs.
Inputs must be regular workspace files, at most 4 MiB each, with no symlink
components. Strict JSON rejects duplicate keys and non-finite numbers.

Nine offline tests passed, including retained real data with socket creation
disabled, byte digests, supply/hash/header conflicts, broken parent linkage,
malformed snapshots and limits:

```sh
python3 -B -m unittest discover -s line-1/tools/snapshot-timeline -p 'test_*.py' -v
```

This is a comparison of provider-reported responses. It does not authenticate a
provider, recompute block hashes, prove finality, establish complete history, or
explain a supply change. A claim of no conflict means only that these particular
saved observations contain no detected conflict.
