# Documentation index

| Page | What it covers |
|---|---|
| [../README.md](../README.md) | what this repository is, the projects, where to start |
| [../AGENTS.md](../AGENTS.md) | the rule book for agents and humans: hard rules, workflow, documentation, upstream, safety |
| [../CONTRIBUTING.md](../CONTRIBUTING.md) | how humans contribute |
| [workflow.md](workflow.md) | how work moves from an issue to `main`, with the diagram |
| [review.md](review.md) | the owner's review checklist and how merging works |
| [safety.md](safety.md) | radio approvals, backups, delivery through the standard update, the way back to stock, locks and options, what is never committed |
| [upstream.md](upstream.md) | the `upstream/` pin, the daily sync, citing upstream, reporting findings upstream |
| [documentation-standard.md](documentation-standard.md) | what every change, project page, patch, tool and radio test must document |

## Projects

| Project | Issue | Page |
|---|---|---|
| FreeDV RADE as a built-in mode | [#1](https://github.com/Reid-n0rc/FT-710_Custom_Firmware/issues/1) | [projects/rade.md](projects/rade.md) |
| US 60 m: 2026 FCC rules | [#2](https://github.com/Reid-n0rc/FT-710_Custom_Firmware/issues/2) | [projects/us-60m-2026.md](projects/us-60m-2026.md) |

## Tools

| Tool | What it does |
|---|---|
| [`tools/check_docs.py`](../tools/check_docs.py) | the `docs-check` CI check: docs travel with changes, project pages have the required sections, relative links resolve |
| `upstream/tools/sfl_decode.py`, `sfl_encode.py` | decode the official `.SFL` files, build and `--check` new ones (upstream) |
| `upstream/tools/cat_backup.py` | read-only backup of a radio, including the full EEPROM (upstream) |
