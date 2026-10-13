#!/usr/bin/env python3
"""Summarize an unsigned EIP-1559 envelope and its maximum ETH reservation."""
import argparse
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "zto-eip1559-decoder"))
import tx_decode

MAX_INPUT_CHARS = 2 * tx_decode.MAX_TRANSACTION_BYTES + 2


def eth(wei):
    """Render nonnegative wei exactly, without floats or rounded digits."""
    whole, fraction = divmod(wei, 10**18)
    if not fraction:
        return str(whole)
    return f"{whole}.{fraction:018d}".rstrip("0")


def summarize(transaction_hex):
    """Decode original unsigned bytes and report the ETH fee-cap exposure."""
    tx = tx_decode.decode(transaction_hex)
    gas_ceiling = tx["gasLimit"] * tx["maxFeePerGas"]
    value_and_ceiling = tx["value"] + gas_ceiling
    destination = tx["to"] or "contract creation"
    selector = tx["calldataSelector"] or "none (empty or short calldata)"
    return {
        "type": tx["type"],
        "chainId": tx["chainId"],
        "nonce": tx["nonce"],
        "destination": destination,
        "calldataSelector": selector,
        "nativeValueWei": str(tx["value"]),
        "nativeValueEth": eth(tx["value"]),
        "gasLimit": str(tx["gasLimit"]),
        "maxFeePerGasWei": str(tx["maxFeePerGas"]),
        "maxPriorityFeePerGasWei": str(tx["maxPriorityFeePerGas"]),
        "feeCapCeilingWei": str(gas_ceiling),
        "feeCapCeilingEth": eth(gas_ceiling),
        "valuePlusFeeCeilingWei": str(value_and_ceiling),
        "valuePlusFeeCeilingEth": eth(value_and_ceiling),
        "accessListEntries": len(tx["accessList"]),
        "interpretation": [
            "The ceiling uses gasLimit multiplied by maxFeePerGas; actual gas use may be lower.",
            "This is an unsigned-envelope arithmetic summary, not a balance or execution check.",
            "Ethereum gas is paid in ETH, including calls to ZTO and IMD.",
            "No network, wallet, key, environment, signing or transaction submission is used.",
        ],
    }


def main(argv):
    parser = argparse.ArgumentParser(description=__doc__)
    source = parser.add_mutually_exclusive_group(required=True)
    source.add_argument("--demo", action="store_true")
    source.add_argument("--transaction", help="original unsigned type-2 RLP as 0x hex")
    source.add_argument("--stdin", action="store_true", help="read 0x hex from standard input")
    args = parser.parse_args(argv)
    try:
        if args.demo:
            raw = tx_decode.demo_transaction()
        elif args.stdin:
            raw = sys.stdin.read(MAX_INPUT_CHARS + 1).strip()
            if len(raw) > MAX_INPUT_CHARS:
                raise ValueError("transaction text exceeds the 128 KiB envelope limit")
        else:
            raw = args.transaction
        report = summarize(raw)
    except (ValueError, UnicodeError) as error:
        print("error: " + str(error), file=sys.stderr)
        return 2

    print("Unsigned EIP-1559 fee envelope")
    print(f"Chain / nonce: {report['chainId']} / {report['nonce']}")
    print(f"To: {report['destination']}")
    print(f"Calldata selector: {report['calldataSelector']}")
    print(f"Native value: {report['nativeValueEth']} ETH ({report['nativeValueWei']} wei)")
    print(f"Gas limit: {report['gasLimit']}")
    print(f"Fee caps: {report['maxFeePerGasWei']} wei max, "
          f"{report['maxPriorityFeePerGasWei']} wei priority")
    print(f"Fee-cap ceiling: {report['feeCapCeilingEth']} ETH "
          f"({report['feeCapCeilingWei']} wei)")
    print(f"Value + fee-cap ceiling: {report['valuePlusFeeCeilingEth']} ETH "
          f"({report['valuePlusFeeCeilingWei']} wei)")
    print(f"Access-list entries: {report['accessListEntries']}")
    for note in report["interpretation"]:
        print(f"Note: {note}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
