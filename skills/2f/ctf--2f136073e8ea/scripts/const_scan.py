#!/usr/bin/env python3
"""Scan a binary for crypto/hash magic constants (both endians).

  python3 const_scan.py ./binary [-C]      # -C = also show context bytes

Hits tell you the algorithm before you read any code — pair with
crypto-constants.md for "what next". Table is short on purpose: only
constants with near-zero false-positive rate are included.
"""
import argparse
import struct

TABLE = [
    (0x9E3779B9, "TEA/XTEA/XXTEA delta (also RC5/RC6 Q)"),
    (0x67452301, "MD5/SHA-1 init h0"),
    (0xEFCDAB89, "MD5/SHA-1 init h1"),
    (0x98BADCFE, "MD5/SHA-1 init h2"),
    (0x10325476, "MD5/SHA-1 init h3"),
    (0xC3D2E1F0, "SHA-1 init h4"),
    (0x6A09E667, "SHA-256 init h0"),
    (0x428A2F98, "SHA-256/512 K[0]"),
    (0xD76AA478, "MD5 T[0]"),
    (0xB7E15163, "RC5/RC6 P"),
    (0x5BD1E995, "MurmurHash2/3 constant"),
    (0xCC9E2D51, "MurmurHash3 c1"),
    (0x1B873593, "MurmurHash3 c2"),
    (0xEDB88320, "CRC32 reflected poly"),
    (0x01000193, "FNV-1 32-bit prime"),
    (0x811C9DC5, "FNV-1 32-bit offset basis"),
]

BYTE_PATTERNS = [
    (bytes.fromhex("637c777bf26b6fc53001672bfed7ab76"), "AES S-box"),
    (bytes.fromhex("5209606ad53036a538"), "AES inverse S-box"),
    (bytes.fromhex("c66363a5"), "AES T-table T0[0]"),
    (b"expand 32-byte k", "ChaCha20/Salsa20"),
    (bytes.fromhex("243f6a8885a308d3"), "Blowfish P-array (pi)"),
    (bytes.fromhex("1f8b"), "gzip header magic"),
    (bytes.fromhex("789c"), "zlib header (default)"),
    (bytes.fromhex("77073096"), "CRC32 table[1]"),
]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("file")
    ap.add_argument("-C", "--context", action="store_true",
                    help="show 16 bytes of context per hit")
    args = ap.parse_args()
    data = open(args.file, "rb").read()
    hits = []

    for value, name in TABLE:
        for enc in ("<I", ">I"):
            needle = struct.pack(enc, value)
            off = data.find(needle)
            while off != -1:
                hits.append((off, name, needle.hex()))
                off = data.find(needle, off + 1)

    for needle, name in BYTE_PATTERNS:
        off = data.find(needle)
        while off != -1:
            hits.append((off, name, needle.hex()))
            off = data.find(needle, off + 1)

    if not hits:
        print("[-] no known constants — likely custom/XOR crypto; "
              "see crypto-constants.md 'decompiled shapes' section")
        return
    for off, name, hx in sorted(hits):
        ctx = data[off:off + 16].hex() if args.context else ""
        print("[+] 0x%08x  %-28s  %s %s" % (off, name, hx, ctx))
    print("\n[*] next: crypto-constants.md → 'extraction recipe' "
          "(dump key/IV/mode, decrypt with pycryptodome)")


if __name__ == "__main__":
    main()
