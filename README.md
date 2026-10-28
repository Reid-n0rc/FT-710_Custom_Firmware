# FT-710 Custom Firmware

Custom firmware features for the Yaesu FT-710, built on the reverse-engineering in
**[Reid-n0rc/FT-710_Firmware](https://github.com/Reid-n0rc/FT-710_Firmware)**.

| Repository | What lives there |
|---|---|
| [FT-710_Firmware](https://github.com/Reid-n0rc/FT-710_Firmware) ("upstream") | The reverse-engineered firmware: decoded images (rebuilt locally), Ghidra decompiles, and the documentation of how the radio works. The single source of truth for **facts about the stock firmware**. |
| **FT-710_Custom_Firmware** (this repo) | Projects that **change** the radio: designs, patch sources, patch-building tools, test plans and results. Each project builds on upstream facts, pinned to an exact upstream commit. |

The work here is done mostly by AI agents, and every change is reviewed and merged by the repository owner. Nothing is written to a
radio without the owner's explicit approval, each time.

> **Status.** Planning. No patch in this repository has been built or applied to a radio yet.

## Projects

| Project | Issue | Status | Page |
|---|---|---|---|
| FreeDV RADE as a built-in mode | [#1](https://github.com/Reid-n0rc/FT-710_Custom_Firmware/issues/1) | planning | [docs/projects/rade.md](docs/projects/rade.md) |
| US 60 m: 2026 FCC rules (5351.5–5366.5 kHz segment, memories, split, XIT) | [#2](https://github.com/Reid-n0rc/FT-710_Custom_Firmware/issues/2) | planning | [docs/projects/us-60m-2026.md](docs/projects/us-60m-2026.md) |

## Where to start

| You are | Read |
|---|---|
| an AI agent | [AGENTS.md](AGENTS.md) (the rule book), then [docs/workflow.md](docs/workflow.md) |
| a human contributor | [CONTRIBUTING.md](CONTRIBUTING.md) |
| the reviewer | [docs/review.md](docs/review.md) |
| anyone about to touch a radio | [docs/safety.md](docs/safety.md) |

All documentation is indexed in [docs/README.md](docs/README.md).

## Repository layout

```
upstream/            git submodule: Reid-n0rc/FT-710_Firmware, pinned to a reviewed commit (see docs/upstream.md)
docs/                all documentation (index: docs/README.md)
  projects/          one page per project: goal, design, status, decisions, test results
tools/               repository tooling (docs checks); patch tools are added per project
.github/             issue and PR templates, CODEOWNERS, workflows (checks, upstream sync)
```

Clone with the submodule:

```sh
git clone --recurse-submodules https://github.com/Reid-n0rc/FT-710_Custom_Firmware.git
```

## What is never committed

Yaesu's firmware download, decoded or patched firmware images, SFL files and Ghidra databases. Patches are committed as **source**
(patch descriptions, scripts that build them from the official download) plus the SHA-256 of what they produce. See
[docs/safety.md](docs/safety.md#what-is-never-committed).

## Disclaimer

An independent project. Not affiliated with or endorsed by Yaesu; FT-710 and Yaesu are trademarks of their owner. Modified firmware can
damage a radio or make it transmit outside its licence. You are responsible for your equipment and for transmitting only where your
licence allows.
