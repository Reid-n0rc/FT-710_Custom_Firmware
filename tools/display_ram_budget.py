#!/usr/bin/env python3
"""Measure how much of the DISPLAY CPU's on-chip RAM the stock V01-08 firmware uses, offline (Doom step 1, issue #7).

The DISPLAY CPU (RZ/A1H) has 10 MB of on-chip RAM at 0x20000000-0x209FFFFF. This script works out which parts the stock image
uses, from the image alone:

1. Static layout: the armcc scatter-load table (Region$$Table at 0x204286A8). Compressed regions are expanded with the same LZ
   scheme as the image's own `__decompress` (0x20100BFC), so the initialised .data/.data2 contents can be read.
2. The NORTi kernel pool: `__user_initial_stackheap` (0x201172EC) and `kernel_heap_init` (0x201562B4) set it up at 0x20980000. The
   script sums what is allocated from it at boot: every task stack whose create descriptor has stk = NULL (`itron_acre_tsk`
   0x201500F4, named wrapper 0x2014E5B0), the TCBs, and the fixed-size memory pools (0x2014F8B8 via wrapper 0x2014E690).
3. The MMU table that `reset_in_ram` builds (0x20100D48 flat fill, 0x20100E24 cacheable ranges), decoded from the instructions.
4. A reference scan: every 32-bit literal in .text and in the initialised data, plus every ARM and Thumb-2 MOVW/MOVT pair, that
   points into a RAM range the static layout does not assign. Thumb runtime code (0x20154000-0x20165177) is skipped for literals
   because its instruction pairs look like addresses.

Usage:
  python3 -I tools/ghidra_image.py --upstream upstream      # once: rebuilds build/FT-710_DISPLAY_V0108.bin
  python3 -I tools/display_ram_budget.py [build/FT-710_DISPLAY_V0108.bin]

Output: a report on stdout. It only reads the image; it never writes anything and never talks to a radio.
"""
import hashlib
import struct
import sys

SHA256 = "65a9b65479f0551cde1a68dabf7ac305a555f144be26b6426362d81d4ded77bb"  # upstream docs/inputs.sha256
BASE = 0x20100000
TEXT_END = 0x20165178       # upstream docs/memory-maps.md (DISPLAY)
THUMB_RT = 0x20154000       # start of the Thumb C-library / runtime code
REGION_TABLE = 0x204286A8
POOL_BASE, POOL_SIZE = 0x20980000, 0x80000   # __user_initial_stackheap: 0x20980000 + 0x80000 = top of RAM

# Task create descriptors (T_CTSK: attr, exinf, task, itskpri, stksz, stk, name) passed to itron_acre_tsk or the named wrapper
# 0x2014E5B0. Addresses are from the call sites in upstream decomp/display (grep "itron_acre_tsk(" and "FUN_2014e5b0(").
TASK_DESCRIPTORS = [
    0x20165A44, 0x201651C4, 0x201651A8, 0x20165314, 0x20165478, 0x201654A0, 0x201654C8, 0x201654F8, 0x2016552C, 0x20165554,
    0x201655CC, 0x20165594, 0x201655B0, 0x201656A8, 0x201656E4, 0x2016571C, 0x201657DC, 0x2016589C, 0x20165880, 0x201658D8,
    0x20165968, 0x20420088, 0x20165938, 0x2016591C, 0x20165900, 0x2016583C, 0x20165820, 0x20165804, 0x20165700,
    0x201651E0, 0x20808AD4, 0x20808AF0, 0x20808B0C, 0x20808B28, 0x2042053C,
]
# Descriptors whose create function has no caller in V01-08 (dspup_init, test_disp_init): listed, not counted.
NOT_CREATED = {0x20165478, 0x20420088}
# Tasks built at run time on the stack: fwdbg (0x2015D2A8 file, stksz 0x2000 set in code).
RUNTIME_TASKS = [("fwdbg", 0x2000)]
# Fixed-size memory pools (T_CMPF: attr, blkcnt, blksz, mpf) created through wrapper 0x2014E690; mpf = NULL means from the pool.
MPF_DESCRIPTORS = [(0x20427EAC, "fsys_mpf"), (0x20427EC0, "FSYS Work")]
TCB_SIZE = 0x44             # itron_acre_tsk allocates 0x28 or 0x44 bytes; count the larger


class Image:
    def __init__(self, path):
        self.d = open(path, "rb").read()
        if hashlib.sha256(self.d).hexdigest() != SHA256:
            raise SystemExit(f"{path}: not DISPLAY V01-08 (SHA-256 mismatch)")
        self.mem = {BASE: self.d}
        self.regions = []
        for i in range(8):
            src, dst, n, fn = struct.unpack("<4I", self.d[REGION_TABLE - BASE + 16 * i:REGION_TABLE - BASE + 16 * i + 16])
            if fn == 0x20100BFC:
                self.mem[dst] = self.lz(src, n)
                self.regions.append((dst, n, "LZ init"))
            elif fn == 0x20100C60:
                self.mem[dst] = bytes(n)
                self.regions.append((dst, n, "zero init"))
            else:
                break

    def lz(self, src, n):
        """armcc __decompress (0x20100BFC), re-implemented from the instructions."""
        d, s, o = self.d, src - BASE, bytearray()
        r3 = d[s]
        s += 1
        while True:
            lit = r3 & 3
            if lit == 0:
                lit, s = d[s], s + 1
            run = r3 >> 4
            if run == 0:
                run, s = d[s], s + 1
            o += d[s:s + lit - 1]
            s += lit - 1
            if run:
                p = len(o) - d[s]
                s += 1
                if r3 & 0xC == 0xC:
                    p, s = p - (d[s] << 8), s + 1
                else:
                    p -= (r3 & 0xC) << 6
                for _ in range(run + 2):
                    o.append(o[p])
                    p += 1
            if len(o) >= n:
                return bytes(o[:n])
            r3, s = d[s], s + 1

    def read(self, addr, n):
        for base, blob in self.mem.items():
            if base <= addr < base + len(blob):
                return blob[addr - base:addr - base + n]
        raise KeyError(hex(addr))

    def u32(self, addr, n=1):
        return struct.unpack(f"<{n}I", self.read(addr, 4 * n))

    def cstr(self, addr):
        try:
            return self.read(addr, 32).split(b"\0")[0].decode("latin1")
        except KeyError:
            return "?"


def pool_report(img):
    rows, total = [], 0
    for a in TASK_DESCRIPTORS:
        attr, _, entry, pri, stksz, stk, name = img.u32(a, 7)
        size = (stksz if stk == 0 else 0) + TCB_SIZE
        label = img.cstr(name) if name else f"task@{entry:08x}"
        if a in NOT_CREATED:
            rows.append((label, "never created (no caller)", 0))
            continue
        rows.append((label, f"stack 0x{stksz:x} + TCB", size))
        total += size
    for name, stksz in RUNTIME_TASKS:
        rows.append((name, f"stack 0x{stksz:x} + TCB", stksz + TCB_SIZE))
        total += stksz + TCB_SIZE
    for a, name in MPF_DESCRIPTORS:
        _, cnt, blksz, mpf = img.u32(a, 4)
        size = cnt * ((blksz + 3) & ~3) if mpf == 0 else 0
        rows.append((name, f"memory pool {cnt} x 0x{blksz:x}", size))
        total += size
    return rows, total


def mmu_report(img):
    """Decode reset_in_ram's MMU set-up: flat fill (0x20100D48), then cacheable ranges (0x20100E24, r0 = base, r1 = size)."""
    fill = img.u32(0x20100D50 + 8 + 0x430)[0]           # ldr r0, [pc, #0x430] at 0x20100D50: section template
    ranges, r0, r1, skip_to = [], None, None, 0
    a = 0x201000E8
    while a < 0x20100128:
        w = img.u32(a)[0]
        if (w & 0xFF000000) == 0xEA000000:              # unconditional branch over the following calls
            skip_to = a + 8 + ((((w & 0xFFFFFF) ^ 0x800000) - 0x800000) << 2)
            ranges.append((f"b 0x{skip_to:08X} at 0x{a:08X} jumps over", None, None))
        elif (w & 0x0F000000) == 0x0B000000:            # bl 0x20100E24
            ranges.append(("skipped" if a < skip_to else "cacheable", r0, r1))
        elif (w & 0x0FFF0000) == 0x059F0000:            # ldr rX, [pc, #imm]
            v = img.u32(a + 8 + (w & 0xFFF))[0]
            r0, r1 = (v, r1) if (w >> 12) & 0xF == 0 else (r0, v)
        elif (w & 0x0FEF0000) == 0x03A00000:            # mov rX, #imm (rotated)
            rot = 2 * ((w >> 8) & 0xF)
            v = ((w & 0xFF) >> rot | (w & 0xFF) << (32 - rot)) & 0xFFFFFFFF if rot else w & 0xFF
            r0, r1 = (v, r1) if (w >> 12) & 0xF == 0 else (r0, v)
        a += 4
    return fill, ranges


def ref_scan(img):
    ranges = [("0x20000000-0x200FFFFF (below the image)", 0x20000000, 0x20100000),
              ("0x204FC5F4-0x207FFFFF (after .bss)", 0x204FC5F4, 0x20800000),
              ("0x2091D570-0x2097FFFF (after .bss2)", 0x2091D570, 0x20980000),
              ("0x20980000-0x209FFFFF (kernel pool)", 0x20980000, 0x20A00000),
              ("0x60000000-0x609FFFFF (frame buffers, DMA)", 0x60000000, 0x60A00000)]
    hits = {r[0]: set() for r in ranges}

    def add(v, where):
        for name, lo, hi in ranges:
            if lo <= v < hi:
                hits[name].add((v, where))

    for base, blob in img.mem.items():
        if base >= 0x60000000:
            continue
        end = (THUMB_RT - BASE) if base == BASE else len(blob)
        for o in range(0, end - 3, 4):
            add(struct.unpack("<I", blob[o:o + 4])[0], base + o)
    text = img.d[:TEXT_END - BASE]
    last = {}
    for o in range(0, len(text), 4):                   # ARM MOVW / MOVT
        w = struct.unpack("<I", text[o:o + 4])[0]
        imm = ((w >> 4) & 0xF000) | (w & 0xFFF)
        if (w & 0x0FF00000) == 0x03000000:
            last[(w >> 12) & 0xF] = (imm, o)
        elif (w & 0x0FF00000) == 0x03400000 and (w >> 12) & 0xF in last:
            add((imm << 16) | last[(w >> 12) & 0xF][0], BASE + o)
    lastt = {}
    for o in range(0, len(text) - 3, 2):               # Thumb-2 MOVW / MOVT
        h1, h2 = struct.unpack("<HH", text[o:o + 4])
        imm = ((h1 & 0xF) << 12) | ((h1 >> 10 & 1) << 11) | ((h2 >> 12 & 7) << 8) | (h2 & 0xFF)
        if (h1 & 0xFBF0) == 0xF240 and not h2 & 0x8000:
            lastt[(h2 >> 8) & 0xF] = (imm, o)
        elif (h1 & 0xFBF0) == 0xF2C0 and not h2 & 0x8000 and (h2 >> 8) & 0xF in lastt:
            add((imm << 16) | lastt[(h2 >> 8) & 0xF][0], BASE + o)
    return hits


def main():
    img = Image(sys.argv[1] if len(sys.argv) > 1 else "build/FT-710_DISPLAY_V0108.bin")
    print("## Scatter-load regions (Region$$Table 0x204286A8)")
    for dst, n, kind in img.regions:
        print(f"  0x{dst:08X}-0x{dst + n - 1:08X}  {n:9,d} B  {kind}")
    rows, total = pool_report(img)
    print(f"\n## Kernel pool 0x{POOL_BASE:08X}-0x{POOL_BASE + POOL_SIZE - 1:08X} ({POOL_SIZE:,d} B): boot-time allocations")
    for name, what, size in rows:
        print(f"  {name:16s} {what:28s} {size:9,d} B")
    print(f"  {'total':16s} {'':28s} {total:9,d} B  -> free at most {POOL_SIZE - total:,d} B (before semaphores, flags, mailboxes)")
    fill, ranges = mmu_report(img)
    print(f"\n## MMU: 4096 flat 1 MB sections (VA = PA), template 0x{fill:08X} = "
          f"AP {fill >> 10 & 3}, TEX {fill >> 12 & 7}, C {fill >> 3 & 1}, B {fill >> 2 & 1}, S {fill >> 16 & 1}"
          " (C = B = 0, TEX 0: strongly ordered)")
    for kind, base, size in ranges:
        if base is None:
            print(f"  {kind}:")
        elif kind == "skipped":
            print(f"    0x{base:08X}-0x{base + size - 1:08X}  never set (stays strongly ordered)")
        else:
            print(f"  0x{base:08X}-0x{base + size - 1:08X}  made write-back cacheable (C = B = 1)")
    print("\n## Address constants pointing into unassigned or shared RAM")
    for name, hs in ref_scan(img).items():
        print(f"  {name}: {len(hs)}")
        for v, where in sorted(hs):
            raw = struct.pack("<I", v)
            ascii_ = all(32 <= c < 127 for c in raw) and 0x204FC5F4 <= v < 0x20800000
            note = f'  ASCII "{raw.decode()}", not an address' if ascii_ else ""
            if THUMB_RT <= where < TEXT_END or 0x20100CB4 <= where < 0x20100CDC:
                note = "  inside Thumb code: an instruction pair, not an address"
            elif v == 0x60687078:
                note = '  ASCII "xph`" in a string table, not an address'
            print(f"    0x{v:08X}  at 0x{where:08X}{note}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
