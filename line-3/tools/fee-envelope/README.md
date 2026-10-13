# Fee envelope

`fee_envelope.py` reads an original unsigned EIP-1559 RLP transaction and prints
its destination, call selector, ETH value and exact fee-cap ceiling. It combines
the inherited bounded decoder with `gasLimit × maxFeePerGas`, then adds native
value to show the maximum ETH amount the envelope could require. This is useful
when preparing an offline-readable transaction summary before any wallet step.

The calculation uses integer wei and prints exact ETH decimals without floats.
The fee ceiling can exceed the eventual charge because unused gas is not spent.
It does not read a balance, evaluate execution or determine whether a transaction
is safe to sign. ZTO and IMD calls still pay Ethereum gas in ETH. The tool uses
only Python's standard library and the committed sibling decoder; it makes no
network calls and never opens keys, wallets, environment variables or files.

## Try it

```sh
python3 -B line-3/tools/fee-envelope/fee_envelope.py --demo
```

I ran this command locally. The synthetic unsigned demonstration decoded the
supplied real ZTO contract destination, reported a 100000 gas limit, and showed
the exact 0.0002 ETH fee-cap ceiling (200000000000000 wei). It did not query or
submit to Ethereum.
