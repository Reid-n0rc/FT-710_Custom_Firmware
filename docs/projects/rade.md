# Project: FreeDV RADE as a built-in mode

## Summary

Run FreeDV **RADE** (Radio Autoencoder digital voice) inside the FT-710 as a normal operating mode, selected like AM, FM or SSB
(MODE key, touch popup, band stack, memory channels, CAT `MD`), with no PC or external box. RADE V1 first; V2 once FreeDV declares it
stable.

- Issue: [#1](https://github.com/Reid-n0rc/FT-710_Custom_Firmware/issues/1) (moved from FT-710_Firmware #102 on 2026-10-28). The
  issue holds the full feasibility study, the 15-risk table and the phased plan; this page is the source of truth for the design and
  status from now on.
- Status: **planning**. Nothing built; nothing tested on a radio.

## Status

| Step | State | Pull request |
|---|---|---|
| Phase 0.1 HiFi4 audio routing (`docs/code/ifdsp/audio-path.md` upstream) | todo | – |
| Phase 0.2 HiFi4 toolchain | todo | – |
| Phase 0.3 Mode-15 audit (MAIN) | todo | – |
| Phase 0.4 DISPLAY mode UI | todo | – |
| Phase 0.5 Resources (SRAM, idle time, flash space) | todo | – |
| Phase 0.6 Ghidra FLIX decoding | tracked upstream: [FT-710_Firmware#97](https://github.com/Reid-n0rc/FT-710_Firmware/issues/97) | – |
| Phase 1 RADE on the host | todo | – |
| Phase 2 RADE audio path in DATA-U | todo | – |
| Phase 3 RADE as mode 15 | todo | – |
| Phase 4 RADE V2 and polish | todo | – |

## Background

Upstream facts (FT-710_Firmware at the pinned commit; see the issue for every citation):

- **RADE:** [`freedv/rade_c`](https://github.com/freedv/rade_c) is a BSD-2-Clause C library for V1 and V2; speech at 16 kHz, modem IQ at
  8 kHz complex; about 1 MB of 8-bit weights each for encoder and decoder; about 330 MMAC/s for receive, dominated by the FARGAN vocoder
  ([RADE paper](https://arxiv.org/pdf/2505.06671)).
- **IF DSP:** RT685 HiFi4 at 594 MHz, 4.5 MB on-chip SRAM, 16 MB QSPI **[fact]** (`upstream/docs/code/ifdsp/m33-platform.md`). Its
  code is known from `upstream/decomp/ifdsp/hifi4/flix.dis`; Ghidra can't decode it yet
  ([FT-710_Firmware#97](https://github.com/Reid-n0rc/FT-710_Firmware/issues/97)).
- **DISPLAY:** RZ/A1H Cortex-A9 with VFP/NEON, free GCC; a 16 kHz stereo PCM link in both directions with the DSP (REC/PLAY)
  **[fact]** (`upstream/docs/code/display/spi-links.md`).
- **Modes:** a 4-bit mode field with modes 0–14 used; index 15 looks unused **[inference]**; 113 `vfo_mode` call sites in MAIN
  **[fact]** (`upstream/docs/code/main/radio-control.md`).
- **Update path limits** (`upstream/docs/code/display/update.md`): the IFDSP erase region is fixed at **640 KiB**; a DISPLAY bank is
  **6 MiB**, and the stock DISPLAY image is about 3.3 MB **[fact]**.

## Design

Recommended route (from the issue): run `rade_c` on the **DISPLAY Cortex-A9** (option B) or split the work so the A9 runs RADE and
the HiFi4 only routes audio (option C). Move to the HiFi4 (option A) only if the A9 can't keep up. Make RADE **mode 15** in MAIN,
add it to the DISPLAY mode popup and label, and give the DSP a new mode signal. The SDR FPGA is unchanged.

Alternatives considered: a PC or ezDV over USB audio (works today, no firmware change, but not built in); a DATA-U sub-mode only (Phase 2
is exactly that, as a stepping stone).

## Delivery and the way back

- **Images changed:** MAIN (mode 15), DISPLAY (UI, and the RADE engine for B/C), IFDSP (audio routing). All delivered as standard
  `.SFL` files through the SD-card update ([safety.md](../safety.md) D1–D8).
- **Size constraint from the update path (D4):** the RADE weights (about 2 MB for both directions, 8-bit) **cannot** go into the IFDSP
  image, whose update region is 640 KiB. Options B/C keep them in the DISPLAY image: about 3.3 MB stock plus about 2 MB of weights plus
  code must stay below the 6 MiB bank. To be measured in Phase 0.5. Option A would have to load the weights from DISPLAY at run time.
- **Update path untouched (D3):** the DISPLAY changes must leave every update function byte-identical; the RADE engine and UI go in
  free space or replace unrelated code only.
- **Locks and options (§4):** no change in any image; the MAIN option-setting area stays all `0xFF`.
- **If something goes wrong:**

| Situation | Path back |
|---|---|
| RADE build works but is unwanted | install the factory MAIN, DISPLAY and IFDSP `.SFL` files of the base versions |
| DISPLAY does not boot | the stock bank is still in flash; maintenance/loader mode or JTAG J6003 (exact steps to be written before the first DISPLAY test) |
| MAIN does not start | DISPLAY writes the factory MAIN by serial boot from the SD card |
| IFDSP does not start | DISPLAY reprograms it from the factory file; SWD J2009 as a last resort |
| Wrong transmit behaviour in mode 15 | dummy load only until verified; reinstall stock |

## Risks

The full table (15 risks with likelihood, impact, mitigation and path back) is in issue #1. The top two: a broken DISPLAY image, and
wrong transmit behaviour in mode 15 from a missed `vfo_mode` default. Added here: the **size constraint** above (likelihood M, impact
H: it decides between options), and the **update-path rule** (any DISPLAY patch that touches the updater is refused in review).

## Plan

As in issue #1, Phases 0–4, with Phase 0.5 now also measuring the free space in the DISPLAY bank against the RADE weights.

## Test log

None yet.

## Decisions

| Date | Decision | By |
|---|---|---|
| 2026-10-28 | Project moved from FT-710_Firmware #102 to this repository | owner |
| 2026-10-28 | Delivery only through the standard SD-card update; factory firmware must always overwrite; no lock or option changes | owner |
| 2026-10-28 | Ghidra FLIX decoding tracked upstream ([FT-710_Firmware#97](https://github.com/Reid-n0rc/FT-710_Firmware/issues/97)) | owner |

## Open questions

- Is mode index 15 really unused? → Phase 0.3.
- Can the A9 run FARGAN in real time next to the GUI? → Phases 0.5 and 1.
- Do the RADE weights plus code fit in the 6 MiB DISPLAY bank? → Phase 0.5.
- Is the Xtensa toolchain needed and obtainable (only for option A)? → Phase 0.2.
- Which CAT `MD` character for RADE, and how do logging programs react? → Phase 3.
