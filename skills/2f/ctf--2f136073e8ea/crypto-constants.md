# Crypto Constant Fingerprints: Identify Crypto Before Reversing It

Most "custom crypto" in CTF binaries is standard crypto (or a near-variant).
Identify the algorithm from magic constants and table bytes in minutes, then
extract the key and decrypt with a library — no need to reimplement rounds.

Scan first, read code second. Run
[scripts/const_scan.py](scripts/const_scan.py) for one-shot detection:

```bash
python3 scripts/const_scan.py ./binary
```

## Constant / table fingerprints

| Bytes or constant | Algorithm | Where you see it |
|---|---|---|
| `9e 37 79 b9` (0x9E3779B9) | TEA / XTEA / XXTEA | `sum += 0x9E3779B9` in a 32-round loop |
| 0x67452301, 0xEFCDAB89, 0x98BADCFE, 0x10325476 | MD5 (SHA-1 adds 0xC3D2E1F0) | init of state array `h[0..4]` |
| 0x428A2F98, 0x71374491, ... (64 words) | SHA-256/SHA-512 `K` table | constant array in `.rodata` |
| 0x6A09E667, 0xBB67AE85, ... | SHA-256 init | state init |
| `"expand 32-byte k"` (`65 78 70 61 6e 64 20 33 32 2d 62 79 74 65 20 6b`), round const 0x0000000000000001 | ChaCha20 / Salsa20 (Keccak/SHA-3 shares the round-const start) | 16-word state setup |
| `63 7c 77 7b f2 6b 6f c5 30 01 67 2b fe d7 ab 76` | AES S-box (first 16 of 256) | `.rodata` table, `sub_bytes` lookups |
| `52 09 6a d5 30 36 a5 38` | AES **inverse** S-box | decryption routine |
| `c6 63 63 a5` (0xC66363A5) | AES T-table (T0[0]) | x86 AES with tables |
| table[1]=0x77073096, or poly 0xEDB88320 | CRC32 | table build loop or table blob |
| 0xD76AA478, 0xE8C7B756, ... (64 words) | MD5 `T` table | round function constants |
| 0xB7E15163 (P32), 0x9E3779B9 (Q32) | RC5 / RC6 | key schedule |
| `24 3f 6a 88 85 a3 08 d3` (pi digits, 18 dwords) | Blowfish P-array | key schedule init |
| 0x5BD1E995 (32-bit), finalizers 0xCC9E2D51 / 0x1B873593 | MurmurHash 2/3 | hash function, not crypto |
| 0x01000193 / 0x811C9DC5 (32-bit), 0x100000001B3 / 0xCBF29CE484222325 (64-bit) | FNV-1/1a | hash function |
| `ABCDEFGHJKLMNPQRSTUVWXYZ234567` vs `ABCDEFGHIJKLMNOPQRSTUVWXYZ234567` | custom vs standard Base32 | decode routine's alphabet string |
| `1f 8b` header, or zlib header `0x78 0x9c/0x01/0xda` | gzip / zlib | decompression before the check |
| DES S1 box first row (decimal): `14 4 13 1 2 15 11 8 3 10 6 12 5 9 0 7` | DES | 8 S-boxes + P-permutation tables |

Notes: constants appear little-endian on x86/ARM LE targets — search **both**
encodings (a `9e 37 79 b9` search misses a `b9 79 37 9e` file embedding).

## What standard crypto looks like decompiled

Transcribe nothing until you recognize the shape:

- **TEA/XTEA:** `v0 += ((v1 << 4) + k0) ^ (v1 + sum) ^ ((v1 >> 5) + k1);` in a
  32-iteration loop. Key = 4 dwords loaded right before.
- **RC4:** KSA = `for (i = 0; i < 256; i++) S[i] = i;` followed by a 256-round
  swap loop using `key[i % keylen]`; then PRGA XOR loop. No constants — detect
  by the double-256 structure.
- **AES:** 10/12/14 rounds of table lookups XOR-shifted into a 16-byte state;
  with AES-NI it's `aesenc` instructions (recognize in disasm, not decompile).
- **MD5/SHA:** 4-byte state words rotated through 64 rounds with the T-table
  words visible as immediates.
- **XOR-with-position:** `(buf[i] ^ i)` or `^ (i * 0x37)` — no fingerprint,
  obvious in decompile. Try [scripts/xor_solve.py](scripts/xor_solve.py).

## After identification: the extraction recipe

1. **Find the key**: constants are algorithm; the *key* is data. Look at what
   feeds the round function — a hardcoded blob, a string, or a value derived
   from your input (keygenme!). Dump it with the debugger right before the
   first round.
2. **Find the mode**: ECB = independent 16-byte blocks; CBC = state XOR
   chained; CTR = a counter encrypted and XORed. In CTF, default guesses in
   order: ECB, CBC with zero IV, CTR from 0.
3. **Use a library, don't retranscribe rounds**: `pip install pycryptodome`,
   then decrypt with the dumped key/IV. If output is garbage in the first
   block but valid after, you got the mode/IV wrong, not the algorithm.
4. **Custom tables**: if the shape matches but constants differ, the author
   swapped tables (common: AES with a permuted S-box). **Extract the table
   from the binary** — dump the 256 bytes the code actually reads — and pass
   it to the library's raw primitive or a Python reimplementation. Never
   assume the standard table.

## RSA / bignum detection (no constants)

- Loops doing `x = x*x`, `x = x % n` on arrays of 32/64-bit limbs with sizes
  like 1024/2048 bits = textbook modexp. Constants live in the *n* and *e*
  blobs. RSA in a CTF is usually crackable by structure (small e, shared
  factors), not by reversing — pivot to [ctf-crypto] once confirmed.
