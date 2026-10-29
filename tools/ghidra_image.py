#!/usr/bin/env python3
"""Rebuild a decoded firmware image from upstream's committed Ghidra project, without Ghidra.

Upstream (FT-710_Firmware) commits its Ghidra projects (`ghidra/FT710_*.rep`) but not the decoded images (`build/*.bin`), and the
official Yaesu download is not reachable from every machine. A Ghidra program database keeps the original file bytes in a
"FileBytes" chained buffer, so the image can be read back from the `.gbf` file:

- The `.gbf` file is a sequence of 16 KiB blocks. Block 0 is the file header; block n+1 holds buffer id n. Each block starts with a
  5-byte prefix (1 flag byte, 4-byte buffer id).
- An indexed chained buffer starts with an index node: node type (1 byte), data length (4 bytes, big-endian; the top bit set means
  the data is XOR-obfuscated), next index node id (4 bytes, -1 at the end), then data buffer ids (4 bytes each, -1 = unused).
- A data node is a node-type byte followed by data. Obfuscated data is XORed with Ghidra's 128-byte `XOR_MASK_BYTES` table
  (`Ghidra/Framework/DB/src/main/java/db/ChainedBuffer.java`, Apache-2.0), indexed by the offset inside the node.

The script finds the index node whose length equals the expected image size, rebuilds the bytes and checks them against the SHA-256 in
upstream's `docs/inputs.sha256`. It refuses to write a file that does not match.

Usage:
  python3 -I tools/ghidra_image.py --upstream upstream --image DISPLAY --out build/FT-710_DISPLAY_V0108.bin

Inputs: an upstream checkout (default `upstream/`). Output: the decoded image, which must stay in `build/` (gitignored; rule 3: never
commit firmware). It only reads the Ghidra project; it never writes to it, and never talks to a radio.
"""
import argparse
import hashlib
import os
import struct
import sys

# Ghidra ChainedBuffer.XOR_MASK_BYTES (Apache-2.0, NationalSecurityAgency/ghidra).
XOR_MASK = bytes.fromhex(
    "59ea6723dab800b8c348dd8b21d69478" "35ab2b7eb24f824e0e16c457128e7ee6" "b6bd56915772e691dc522ef21ab7d66f" "dadee848b1bb506f"
    "f4dd11eef267fe48" "8dae691ae0268c248e177651e260d7e6" "8365d5f07ff2a0d64bbd24d8abea9ea6" "48943e7b2cf4cedc6911f83ca73f5d77"
    "943fe48e4820db5632c187012ee37f40")
BLOCK = 0x4000
PREFIX = 5

IMAGES = {  # name: (Ghidra project, file name in build/)
    "DISPLAY": ("FT710_DISPLAY", "FT-710_DISPLAY_V0108.bin"),
    "MAIN": ("FT710_MAIN", "FT-710_MAIN_V0112.bin"),
    "IFDSP": ("FT710_IFDSP", "FT-710_IFDSP_V0101.bin"),
}


def expected_hash(upstream, build_name):
    for line in open(os.path.join(upstream, "docs", "inputs.sha256"), encoding="utf-8"):
        parts = line.split()
        if len(parts) == 2 and parts[1] == "build/" + build_name:
            return parts[0]
    raise SystemExit(f"no SHA-256 for build/{build_name} in upstream docs/inputs.sha256")


def find_gbf(upstream, project):
    rep = os.path.join(upstream, "ghidra", project + ".rep")
    found = [os.path.join(r, f) for r, _, fs in os.walk(rep) for f in fs if f.endswith(".gbf")]
    if not found:
        raise SystemExit(f"no .gbf file under {rep}")
    return found


def rebuild(data, index_block):
    def block(n):
        return data[n * BLOCK:(n + 1) * BLOCK]

    node = block(index_block)
    length = struct.unpack(">I", node[PREFIX + 1:PREFIX + 5])[0]
    obfuscated, length = bool(length & 0x80000000), length & 0x7FFFFFFF
    ids = []
    while True:
        nxt = struct.unpack(">i", node[PREFIX + 5:PREFIX + 9])[0]
        for k in range((BLOCK - PREFIX - 9) // 4):
            v = struct.unpack(">i", node[PREFIX + 9 + 4 * k:PREFIX + 13 + 4 * k])[0]
            if v >= 0:
                ids.append(v)
        if nxt < 0:
            break
        node = block(nxt + 1)
    out = bytearray()
    for i in ids:
        chunk = block(i + 1)[PREFIX + 1:]
        out += bytes(c ^ XOR_MASK[j % 128] for j, c in enumerate(chunk)) if obfuscated else chunk
        if len(out) >= length:
            break
    return bytes(out[:length])


def main():
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--upstream", default="upstream", help="FT-710_Firmware checkout (default: upstream/)")
    ap.add_argument("--image", default="DISPLAY", choices=sorted(IMAGES))
    ap.add_argument("--out", help="output file (default: build/<image file name>)")
    a = ap.parse_args()
    project, build_name = IMAGES[a.image]
    want = expected_hash(a.upstream, build_name)
    out = a.out or os.path.join("build", build_name)
    for gbf in find_gbf(a.upstream, project):
        data = open(gbf, "rb").read()
        for n in range(1, len(data) // BLOCK):
            b = data[n * BLOCK:(n + 1) * BLOCK]
            if b[PREFIX] != 8:  # indexed-node type byte seen in Ghidra 12 databases
                continue
            img = rebuild(data, n)
            if hashlib.sha256(img).hexdigest() == want:
                os.makedirs(os.path.dirname(out) or ".", exist_ok=True)
                open(out, "wb").write(img)
                print(f"{out}: {len(img)} bytes, SHA-256 {want} (matches upstream docs/inputs.sha256; index node block {n})")
                return 0
    print(f"no chained buffer in {project} matches SHA-256 {want}", file=sys.stderr)
    return 1


if __name__ == "__main__":
    sys.exit(main())
