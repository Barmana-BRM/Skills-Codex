#!/usr/bin/env python3
"""XOR recovery toolkit for RE challenges: single-byte brute, known-plaintext
keystream derivation, and repeating-key solving by printable scoring.

  python3 xor_solve.py blob.bin                        # single-byte brute
  python3 xor_solve.py blob.bin --pt 'flag{'           # derive key from known prefix
  python3 xor_solve.py blob.bin --repeat               # search period 1..64
  python3 xor_solve.py blob.bin --pt 'flag{' --repeat  # derive keystream, extend
"""
import argparse
import re
import string

PRINTABLE = set(string.printable.encode())
FLAG_RE = re.compile(rb"[A-Za-z0-9_]{0,16}\{(?:[ -~]{4,})\}|flag\{[^}]+\}")


def load(path):
    return open(path, "rb").read()


def score(data):
    return sum(b in PRINTABLE for b in data) / max(len(data), 1)


def show(tag, data):
    hits = FLAG_RE.findall(data)
    extra = ("  FLAG? " + b", ".join(hits).decode(errors="replace")) if hits else ""
    print("[%-4s] %.2f %r%s" % (tag, score(data), data[:96], extra))


def single_byte(ct):
    best = []
    for k in range(256):
        pt = bytes(b ^ k for b in ct)
        best.append((score(pt), k, pt))
    best.sort(reverse=True)
    for s, k, pt in best[:3]:
        show(str(k), pt)


def known_plaintext(ct, pt):
    ks = bytes(c ^ p for c, p in zip(ct, pt.encode()))
    print("[key] %r" % ks)
    show("pt", bytes(c ^ k for c, k in zip(ct, (ks * len(ct))[:len(ct)])))


def repeating(ct):
    best = (0, 1, b"")
    for period in range(1, 65):
        key = bytearray(period)
        # per-position best byte by column printability
        for i in range(period):
            col = ct[i::period]
            cand = max(((score(bytes(b ^ k for b in col)), k) for k in range(256)))
            key[i] = cand[1]
        pt = bytes(c ^ key[i % period] for i, c in enumerate(ct))
        s = score(pt)
        if s > best[0]:
            best = (s, period, pt)
    print("[period=%d]" % best[1])
    show("rep", best[2])


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("file")
    ap.add_argument("--pt", help="known plaintext prefix, e.g. 'flag{'")
    ap.add_argument("--repeat", action="store_true",
                    help="search repeating-key period 1..64")
    args = ap.parse_args()
    ct = load(args.file)
    if args.pt:
        known_plaintext(ct, args.pt)
    if args.repeat:
        repeating(ct)
    if not args.pt and not args.repeat:
        single_byte(ct)


if __name__ == "__main__":
    main()
