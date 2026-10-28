# AGENTS.md — rules for AI agents (and humans) working in FT-710_Custom_Firmware

This file is the single source of instructions for this repository. `CLAUDE.md` points here.

## Purpose

Design, build and test custom firmware features for the Yaesu FT-710. Facts about the **stock** firmware come from
[Reid-n0rc/FT-710_Firmware](https://github.com/Reid-n0rc/FT-710_Firmware) ("upstream"), which is checked out at `upstream/` as a
pinned git submodule. This repository holds what **changes** the radio: project designs, patch sources, tools, test plans and results.

## The hard rules

1. **Never write to a radio without the owner's explicit approval, each time.** That covers flashing, SD-card updates, JTAG/SWD loads,
   EEPROM writes and CAT set-commands. Approval for one write does not cover the next one. Read-only CAT queries also need the owner's
   go-ahead in the session. Before any write, a backup must exist ([docs/safety.md](docs/safety.md#backups)).
2. **Never merge, and never push to `main`.** Every change goes through a pull request. The owner reviews and merges. The branch ruleset
   blocks direct pushes for everyone; do not try to get around it.
3. **Never commit firmware.** No Yaesu download, decoded image, patched image, SFL file or Ghidra database. Patches are committed as
   source plus the SHA-256 of their output ([docs/safety.md](docs/safety.md#what-is-never-committed)).
4. **Custom firmware installs through the standard update, and factory firmware always overwrites it.** Every custom image is
   delivered as an ordinary `.SFL` update file that the radio's own SD-card update installs, with no tools or hardware. Nothing may
   change the update path: the updater code on DISPLAY, the SFL checks, the bank switching, the MAIN/IFDSP/SDR programming routines
   and the version handling stay as in stock, so installing a factory `.SFL` always restores stock firmware. Every patch is tested
   offline for this, and its first radio test ends by reinstalling stock
   ([docs/safety.md](docs/safety.md#delivery-and-the-way-back-to-stock)).
   **Two-stage install (allowed, decided 2026-10-28):** large data that doesn't fit in an image (for example RADE's neural-network
   weights) may be written by custom firmware on first boot from a separate data file on the SD card, but only if all three hold:
   (a) all code arrives through the standard update (stage 1); (b) stage 2 writes only flash that the standard update and stock
   firmware never touch; (c) installing factory `.SFL` files still fully restores stock behaviour. Requirements S1–S8 in
   [docs/safety.md](docs/safety.md#34-two-stage-install-large-data-on-first-boot).
5. **Lock bits and option settings are never set or changed from stock.** That includes the RX651 option-setting memory and ID code,
   RT685 OTP fuses and boot configuration, FPGA bitstream security options and configuration-flash protection, and any flash
   write-protect or debug-lock setting on any chip. The bytes are compared with stock for every image before a pull request
   ([docs/safety.md](docs/safety.md#locks-and-option-settings-never-change)).

## How work flows

The full process, with a diagram, is in [docs/workflow.md](docs/workflow.md). In short:

1. **Start from an issue.** Every piece of work has an issue in this repository. If none exists, open one with a template and stop
   for the owner's go-ahead when the work is large, risky or needs a decision (label `needs-owner`).
2. **Plan in the docs first.** Before writing code or patches, write or update the project page in `docs/projects/` with the approach,
   and push it on your branch. Large work is split into steps, each with one verifiable result.
3. **Branch.** `agent/<issue>-<short-name>`, e.g. `agent/2-us60m-tx-table`. One branch per pull request.
4. **Do the work, documenting as you go** ([documentation standard](docs/documentation-standard.md)).
5. **Open a pull request** with the template. Link the issue (`Closes #N` or `Refs #N`), fill in every section, add the `needs-review`
   label, and stop. Answer review comments on the same branch.
6. **The owner reviews and merges** ([docs/review.md](docs/review.md)).

## Documentation is part of every change

"Everything needs detailed documentation" is a hard requirement, checked by the `docs-check` workflow:

- Every pull request that changes anything outside `docs/` must also change `docs/`.
- Every project has a page in `docs/projects/` with the required sections (goal, background, design, upstream references, risks and
  paths back, plan, status, decisions, test results). See [docs/documentation-standard.md](docs/documentation-standard.md).
- Every claim about the stock firmware cites upstream: a file in `upstream/` and the upstream commit, or an address with a
  `decomp/` file. Tag claims **[fact]**, **[inference]** or **[guess]**, as upstream does.
- Every patch documents: what it changes (addresses, old and new bytes), why, how it was verified offline, the SHA-256 of the input
  image and of the result, and how to go back to stock.
- Every radio test documents: the owner's approval (date, what was approved), the backup taken, the exact steps, the result and any
  surprise.

## Upstream

- `upstream/` is pinned to one upstream commit. Always cite that commit when you rely on an upstream fact. Check it with
  `git -C upstream log -1 --format='%H %s'`.
- The `upstream-sync` workflow opens a pull request when upstream moves. Do not bump the pin by hand in an unrelated pull request.
- **Findings about the stock firmware belong upstream.** If you discover or correct a fact about how the stock firmware works, open
  an issue (or a pull request) in FT-710_Firmware and link it here with the `upstream-finding` label. Do not document stock-firmware
  facts only in this repository.
- Details: [docs/upstream.md](docs/upstream.md).

## Safety and licence

- Read [docs/safety.md](docs/safety.md) before any work that could reach a radio.
- Transmit-path changes (band limits, power, filters, modes) must keep the radio within the operator's licence conditions (FCC Part 97
  in the US). Test transmit changes into a dummy load first.
- Every patch must have a documented path back to stock firmware before it is tested.

## Writing style

Same as upstream: plain English, short sentences, one idea per paragraph, Mermaid diagrams for flows (about 25 nodes or fewer),
tables for lists of facts. Use they/them for people unless their pronouns are known.

## Git

- Branch names: `agent/<issue>-<short-name>`; humans may use any name.
- Commit messages: imperative summary line, then what and why. End agent commits with the attribution line the agent's tool provides.
- Signing commits is recommended, not required.
- Never force-push a branch someone else is reviewing; push new commits instead.
