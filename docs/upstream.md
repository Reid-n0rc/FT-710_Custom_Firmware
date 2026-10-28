# Upstream: how this repository follows FT-710_Firmware

[Reid-n0rc/FT-710_Firmware](https://github.com/Reid-n0rc/FT-710_Firmware) ("upstream") is where the stock firmware is reverse
engineered: decompiles, memory maps, protocols, CAT commands, the update path and the tools. This repository builds on it and must
keep up with it.

## The pin

`upstream/` is a **git submodule** pinned to one upstream commit.

```sh
git submodule update --init                              # after cloning without --recurse-submodules
git -C upstream log -1 --format='%H %s'                  # which upstream commit this checkout uses
```

Why a pin rather than "latest": a project's design, patch addresses and test results are only valid for the upstream facts they were
made with. The pin makes that exact and reviewable. Upstream's decoded images are not in git (Yaesu's copyright); build them inside
`upstream/` with its bootstrap when a project needs them (`upstream/docs/getting-started.md`).

## Keeping up: the upstream-sync workflow

`.github/workflows/upstream-sync.yml` runs every day at 06:00 UTC and on demand (Actions → upstream-sync → Run workflow):

1. It fetches upstream `main` and compares it with the pin.
2. If upstream has moved, it creates the branch `upstream-sync/<short sha>`, moves the pin, and opens a pull request labelled
   `upstream-sync` with:
   - the list of new upstream commits;
   - the upstream files that changed, with the docs (`docs/`) listed first;
   - a reminder to check the project pages that cite changed files.
3. If a sync pull request is already open, it updates that pull request instead of opening another.

The owner reviews and merges it like any other pull request ([review.md](review.md)). Pull requests opened by the workflow's token
do not trigger other workflows, so their checks don't run; the owner merges them through the bypass after reading the list.

## Citing upstream

When a document here relies on an upstream fact, cite:

- the upstream file path (`upstream/docs/code/main/tx-protection.md`), section or address; and
- the pinned commit when the pin moves later than the document (`upstream@996c23c`).

Example: "US 60 m rows are `[f, f+1)` **[fact]** (`upstream/docs/code/main/tx-protection.md`, upstream@4cfa6a2)."

## Findings flow back upstream

Facts about the stock firmware belong upstream, so everyone shares one corrected picture:

1. Open an issue (or a pull request) in FT-710_Firmware with the finding and its evidence.
2. Link it from the issue or pull request here and add the label `upstream-finding`.
3. Once it is merged upstream and the pin has moved, cite the upstream document instead of repeating the finding here.

Design, patches and test results of a custom feature stay here.

## Related upstream documents

| Topic | Upstream document |
|---|---|
| Whole-radio overview | `upstream/docs/code/system.md`, the illustrated guide (`upstream/docs/guide/README.md`) |
| Custom-firmware feasibility, debug headers, risk ladder | `upstream/docs/custom-firmware.md`, guide chapter 8 |
| Update path (what the SD-card update checks) | `upstream/docs/code/display/update.md` |
| SFL file format and tools | `upstream/docs/sfl-format.md`, `upstream/tools/sfl_decode.py`, `upstream/tools/sfl_encode.py` |
| Earlier patch work (T16) | `upstream/docs/patches/README.md`, `upstream/tools/t16_patches.py` |
| CAT commands and backups | `upstream/docs/cat-commands.md`, `upstream/docs/cat-undocumented.md`, `upstream/tools/cat_backup.py` |
| Open Ghidra gaps | upstream issue [#97](https://github.com/Reid-n0rc/FT-710_Firmware/issues/97) |
